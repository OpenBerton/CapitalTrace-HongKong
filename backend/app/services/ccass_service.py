from __future__ import annotations

import asyncio
import copy
import datetime
import logging
import re
import time

import httpx
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.config import CCASS_BASE_URL, REQUEST_TIMEOUT
from app.core.exceptions import CCASSParseError, CCASSNotFoundError
from app.services.trading_day_service import get_trading_days
from app.utils.date_utils import normalize_date
from app.utils.stock_utils import normalize_stock_code
from app.utils.html_utils import clean_html

logger = logging.getLogger(__name__)
CACHE_TTL_SECONDS = 3 * 3600
_CACHE: dict[tuple[str, str], tuple[float, dict[str, object]]] = {}
_CACHE_LOCK = asyncio.Lock()
FORM_CACHE_TTL_SECONDS = 6 * 3600
_FORM_CACHE: tuple[float, dict[str, str], str] | None = None
_FORM_CACHE_LOCK = asyncio.Lock()
ENRICHMENT_TIMEOUT_SECONDS = 6
ENRICHMENT_TIMEOUT_SECONDS_ENRICHED = 20
TOP_PARTICIPANTS_LIMIT = 20


def _normalize_numeric(value: str) -> float:
    """清洗數值欄位，移除逗號、百分號與全形空白後轉換為浮點數。"""
    cleaned = (
        str(value)
        .replace(",", "")
        .replace("%", "")
        .replace("\u3000", "")
        .strip()
    )
    return float(pd.to_numeric(cleaned, errors="coerce") or 0.0)


def _extract_table_rows(table) -> list[list[str]]:
    rows: list[list[str]] = []
    for tr in table.find_all("tr"):
        cells = [cell.get_text(strip=True) for cell in tr.find_all(["th", "td"])]
        if cells:
            rows.append(cells)
    return rows


def _find_column_index(columns: list[str], keywords: list[str]) -> int | None:
    lower_columns = [col.lower() for col in columns]
    for keyword in keywords:
        for index, col in enumerate(lower_columns):
            if keyword in col:
                return index
    return None


def _is_valid_header_row(header: list[str]) -> bool:
    keywords = [
        "participant",
        "參與者",
        "券商",
        "機構",
        "shareholding",
        "股數",
        "持股",
        "%",
        "percentage",
        "佔比",
        "持股比例",
        "比例",
    ]
    for cell in header:
        if not cell:
            continue
        if len(cell) > 120:
            continue
        if _find_column_index([cell], keywords) is not None:
            return True
    return False


def _extract_mobile_rows(table) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for tr in table.find_all("tr"):
        row: dict[str, str] = {}
        for td in tr.find_all("td"):
            heading = td.find(class_=re.compile(r"mobile-list-heading", re.I))
            body = td.find(class_=re.compile(r"mobile-list-body", re.I))
            if heading and body:
                row[heading.get_text(strip=True)] = body.get_text(strip=True)
        if row:
            rows.append(row)
    return rows


def _find_mobile_heading(columns: list[str], keywords: list[str]) -> str | None:
    for keyword in keywords:
        for column in columns:
            if keyword in column.lower():
                return column
    return None


def _is_mobile_table(table) -> bool:
    return table.find(class_=re.compile(r"mobile-list-heading", re.I)) is not None


def _find_result_table(soup: BeautifulSoup) -> BeautifulSoup | None:
    candidate_table = None
    for table in soup.find_all("table"):
        if _is_mobile_table(table):
            mobile_rows = _extract_mobile_rows(table)
            if mobile_rows:
                return table

        classes = table.get("class", []) or []
        if any(isinstance(c, str) and ("search-result-table" in c or "table-scroll" in c) for c in classes):
            candidate_table = table
            continue

        rows = _extract_table_rows(table)
        if len(rows) <= 1:
            continue
        header = rows[0]
        if _is_valid_header_row(header):
            return table

    return candidate_table


def _format_query_date(date_str: str) -> str:
    """將 YYYY-MM-DD 格式轉換為 ASP.NET 表單需要的 YYYY/MM/DD。"""
    try:
        parsed = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return parsed.strftime("%Y/%m/%d")
    except ValueError as exc:
        raise ValueError("日期格式不正確，請使用 YYYY-MM-DD。") from exc


def _hk_yahoo_ticker(stock_code: str) -> str:
    # Yahoo Finance HK equities generally use 4-digit codes, e.g. 0700.HK.
    digits = "".join(ch for ch in stock_code if ch.isdigit())
    if not digits:
        return f"{stock_code}.HK"
    return f"{int(digits):04d}.HK"


def _hk_yahoo_ticker_candidates(stock_code: str) -> list[str]:
    # HK equities on Yahoo normally use 4-digit codes, e.g. 0700.HK.
    return [_hk_yahoo_ticker(stock_code)]


def _fetch_close_price(stock_code: str, query_date: str) -> float | None:
    try:
        target_date = datetime.datetime.strptime(query_date, "%Y-%m-%d").date()
        ticker = yf.Ticker(_hk_yahoo_ticker(stock_code))
        start_date = target_date - datetime.timedelta(days=14)
        end_date = target_date + datetime.timedelta(days=1)
        hist = ticker.history(
            start=start_date.isoformat(),
            end=end_date.isoformat(),
            interval="1d",
            actions=False,
        )
        if hist.empty:
            return None

        dates = [dt.date() for dt in pd.to_datetime(hist.index)]
        if target_date in dates:
            return float(hist.loc[pd.to_datetime(target_date).strftime("%Y-%m-%d"), "Close"])

        prior_dates = [d for d in dates if d < target_date]
        if prior_dates:
            nearest = max(prior_dates)
            return float(hist.loc[pd.to_datetime(nearest).strftime("%Y-%m-%d"), "Close"])
        return None
    except Exception:
        return None


def _get_previous_trading_date(stock_code: str, query_date: str) -> str | None:
    try:
        target_date = datetime.datetime.strptime(query_date, "%Y-%m-%d").date()
        ticker = yf.Ticker(_hk_yahoo_ticker(stock_code))
        start_date = target_date - datetime.timedelta(days=30)
        end_date = target_date + datetime.timedelta(days=1)
        hist = ticker.history(
            start=start_date.isoformat(),
            end=end_date.isoformat(),
            interval="1d",
            actions=False,
        )
        if hist.empty:
            return None

        trade_dates = sorted({dt.date() for dt in pd.to_datetime(hist.index)})
        if target_date in trade_dates:
            index = trade_dates.index(target_date)
            return trade_dates[index - 1].isoformat() if index > 0 else None

        prior_dates = [d for d in trade_dates if d < target_date]
        return prior_dates[-1].isoformat() if prior_dates else None
    except Exception:
        return None


def _normalize_participant_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


async def _resolve_ccass_dates_for_query_date(query_date: str) -> tuple[str, str]:
    trading_days = await get_trading_days()
    if query_date not in trading_days:
        raise ValueError("查詢日期不是有效港股交易日。")

    query_idx = trading_days.index(query_date)
    target_idx = query_idx + 2
    compare_idx = query_idx + 1

    if target_idx >= len(trading_days):
        raise ValueError("T+2 日的 CCASS 數據尚未公佈。")

    return trading_days[compare_idx], trading_days[target_idx]


async def _fetch_ccass_participants_for_date(
    client: httpx.AsyncClient,
    action_url: str,
    form_fields: dict[str, str],
    stock_code_normalized: str,
    query_date_formatted: str,
) -> dict[str, object] | None:
    payload = form_fields.copy()
    payload.update(
        {
            "__EVENTTARGET": "btnSearch",
            "__EVENTARGUMENT": "",
            "today": datetime.date.today().strftime("%Y%m%d"),
            "sortBy": "shareholding",
            "sortDirection": "desc",
            "txtShareholdingDate": query_date_formatted,
            "txtStockCode": stock_code_normalized,
            "txtStockName": "",
            "txtParticipantID": "",
            "txtParticipantName": "",
            "txtSelPartID": "",
        }
    )

    headers = _build_ccass_headers(client)

    try:
        response = await client.post(
            action_url,
            data=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except httpx.TimeoutException:
        logger.warning("CCASS query timeout for date=%s", query_date_formatted)
        return None
    except httpx.HTTPError as exc:
        logger.warning("CCASS query failed for date=%s: %s", query_date_formatted, exc)
        return None

    html = clean_html(response.text)
    soup = BeautifulSoup(html, "lxml")
    table = _find_result_table(soup)
    if table is None:
        return None

    if _is_mobile_table(table):
        mobile_rows = _extract_mobile_rows(table)
        if not mobile_rows:
            return None

        name_key = _find_mobile_heading(
            list(mobile_rows[0].keys()),
            ["name of ccass participant", "participant name", "participant", "名稱", "參與者"],
        )
        share_key = _find_mobile_heading(
            list(mobile_rows[0].keys()),
            ["shareholding", "shareholding:", "shareholding", "持股", "股數"],
        )
        percentage_key = _find_mobile_heading(
            list(mobile_rows[0].keys()),
            ["percentage", "%", "佔比", "持股比例", "比例"],
        )

        participants: list[dict[str, object]] = []
        for row in mobile_rows[:TOP_PARTICIPANTS_LIMIT]:
            name = row.get(name_key) if name_key else None
            if not name:
                name = row.get(
                    _find_mobile_heading(
                        list(row.keys()),
                        ["participant id", "participant name", "participant", "名稱", "參與者"],
                    )
                )
            share = _normalize_numeric(row.get(share_key, "0")) if share_key else 0.0
            percentage = _normalize_numeric(row.get(percentage_key, "0")) if percentage_key else 0.0
            participants.append({
                "name": name or "Unknown",
                "share": share,
                "percentage": percentage,
            })

        return {
            "participants": participants,
            "raw_columns": list(mobile_rows[0].keys()),
        }

    rows = _extract_table_rows(table)
    if len(rows) <= 1:
        return None

    header = rows[0]
    data_rows = [row for row in rows[1:] if len(row) == len(header)]
    if not data_rows:
        return None

    name_index = _find_column_index(header, ["名稱", "參與者", "券商", "機構"])
    share_index = _find_column_index(header, ["持股", "股數", "持股量"])
    percentage_index = _find_column_index(header, ["%", "佔比", "持股比例", "比例"])

    if share_index is None:
        return None

    participants: list[dict[str, object]] = []
    for row in data_rows[:TOP_PARTICIPANTS_LIMIT]:
        name = row[name_index] if name_index is not None else row[0]
        share = _normalize_numeric(row[share_index])
        percentage = _normalize_numeric(row[percentage_index]) if percentage_index is not None else 0.0
        participants.append({
            "name": name,
            "share": share,
            "percentage": percentage,
        })

    return {
        "participants": participants,
        "raw_columns": header,
    }


def _extract_form_data(html: str) -> tuple[dict[str, str], str]:
    soup = BeautifulSoup(html, "lxml")
    form = soup.find("form")
    if form is None:
        raise CCASSParseError("無法取得 CCASS 頁面表單，網站格式可能已變更。")

    action = form.get("action") or CCASS_BASE_URL
    hidden_fields = {
        inp["name"]: inp.get("value", "")
        for inp in form.find_all("input", attrs={"type": "hidden"})
        if inp.get("name")
    }

    submit_button = form.find("input", attrs={"type": "submit", "name": "btnSearch"})
    if submit_button is None:
        submit_button = form.find("button", attrs={"name": "btnSearch"})
    if submit_button is not None and submit_button.get("name"):
        hidden_fields[submit_button["name"]] = submit_button.get("value", "")

    return hidden_fields, action


def _fetch_yahoo_history(stock_code: str, query_date: str) -> tuple[float | None, str | None]:
    target_date = datetime.datetime.strptime(query_date, "%Y-%m-%d").date()
    start_date = target_date - datetime.timedelta(days=30)
    end_date = target_date + datetime.timedelta(days=1)

    try:
        for ticker_symbol in _hk_yahoo_ticker_candidates(stock_code):
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(
                start=start_date.isoformat(),
                end=end_date.isoformat(),
                interval="1d",
                actions=False,
            )
            if hist.empty:
                # Fallback for dates outside immediately available range.
                hist = ticker.history(period="6mo", interval="1d", actions=False)
            if hist.empty:
                continue

            dates = [dt.date() for dt in pd.to_datetime(hist.index)]
            close_price = None
            if target_date in dates:
                close_price = float(hist.loc[pd.to_datetime(target_date).strftime("%Y-%m-%d"), "Close"])
            else:
                prior_dates = [d for d in dates if d < target_date]
                if prior_dates:
                    nearest = max(prior_dates)
                    close_price = float(hist.loc[pd.to_datetime(nearest).strftime("%Y-%m-%d"), "Close"])

            trade_dates = sorted({dt.date() for dt in pd.to_datetime(hist.index)})
            prev_trade_date = None
            if target_date in trade_dates:
                index = trade_dates.index(target_date)
                prev_trade_date = trade_dates[index - 1].isoformat() if index > 0 else None
            else:
                prior_dates = [d for d in trade_dates if d < target_date]
                prev_trade_date = prior_dates[-1].isoformat() if prior_dates else None

            return close_price, prev_trade_date

        return None, None
    except Exception as exc:
        logger.warning("Yahoo finance fetch failed for %s %s: %s", stock_code, query_date, exc)
        return None, None


async def _fetch_yahoo_history_async(stock_code: str, query_date: str) -> tuple[float | None, str | None]:
    return await asyncio.to_thread(_fetch_yahoo_history, stock_code, query_date)


def _is_cache_valid(timestamp: float) -> bool:
    return time.time() - timestamp < CACHE_TTL_SECONDS


async def _get_cached_chip_data(stock_code: str, date: str) -> dict[str, object] | None:
    cache_key = (stock_code, date)
    async with _CACHE_LOCK:
        cached = _CACHE.get(cache_key)
        if cached and _is_cache_valid(cached[0]):
            return copy.deepcopy(cached[1])
    return None


async def _set_cached_chip_data(stock_code: str, date: str, data: dict[str, object]) -> None:
    cache_key = (stock_code, date)
    async with _CACHE_LOCK:
        _CACHE[cache_key] = (time.time(), copy.deepcopy(data))


def _is_form_cache_valid(timestamp: float) -> bool:
    return time.time() - timestamp < FORM_CACHE_TTL_SECONDS


async def _get_cached_form_metadata() -> tuple[dict[str, str], str] | None:
    async with _FORM_CACHE_LOCK:
        if _FORM_CACHE is None:
            return None
        timestamp, form_fields, action_url = _FORM_CACHE
        if not _is_form_cache_valid(timestamp):
            return None
        return form_fields.copy(), action_url


async def _set_cached_form_metadata(form_fields: dict[str, str], action_url: str) -> None:
    global _FORM_CACHE
    async with _FORM_CACHE_LOCK:
        _FORM_CACHE = (time.time(), form_fields.copy(), action_url)


async def _fetch_form_metadata(client: httpx.AsyncClient) -> tuple[dict[str, str], str]:
    cached = await _get_cached_form_metadata()
    if cached is not None:
        return cached

    try:
        initial_response = await client.get(CCASS_BASE_URL)
        initial_response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise TimeoutError("CCASS 初始連線超時，請稍後重試。") from exc
    except httpx.HTTPError as exc:
        raise ConnectionError("無法連線到 CCASS 服務，請檢查網路或 URL 設定。") from exc

    form_fields, action_url = _extract_form_data(clean_html(initial_response.text))
    action_url = urljoin(str(initial_response.url), action_url)
    await _set_cached_form_metadata(form_fields, action_url)
    return form_fields, action_url


async def warm_ccass_form_cache() -> None:
    """Preload CCASS form metadata to reduce first-request latency after service startup."""
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        client.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
                )
            }
        )
        try:
            await _fetch_form_metadata(client)
            logger.info("CCASS form metadata warmup completed")
        except Exception as exc:
            logger.warning("CCASS form metadata warmup skipped: %s", exc)


async def _enrich_with_market_data(
    client: httpx.AsyncClient,
    action_url: str,
    form_fields: dict[str, str],
    stock_code_normalized: str,
    query_date: str,
    ccass_compare_date: str,
    timeout_seconds: int = ENRICHMENT_TIMEOUT_SECONDS,
) -> tuple[float | None, dict[str, float]]:
    close_price: float | None = None
    prev_share_map: dict[str, float] = {}

    yahoo_task = asyncio.create_task(
        _fetch_yahoo_history_async(stock_code_normalized, query_date)
    )
    prev_task = asyncio.create_task(
        _fetch_ccass_participants_for_date(
            client,
            action_url,
            form_fields,
            stock_code_normalized,
            _format_query_date(ccass_compare_date),
        )
    )

    try:
        yahoo_result, prev_result = await asyncio.wait_for(
            asyncio.gather(
                asyncio.gather(yahoo_task, return_exceptions=True),
                asyncio.gather(prev_task, return_exceptions=True),
            ),
            timeout=timeout_seconds,
        )
    except asyncio.TimeoutError:
        logger.warning("Enrichment timeout for %s %s", stock_code_normalized, query_date)
        return close_price, prev_share_map

    yahoo_value = yahoo_result[0]
    if isinstance(yahoo_value, Exception):
        logger.warning("Yahoo finance fetch task failed: %s", yahoo_value)
    else:
        close_price, _ = yahoo_value

    prev_value = prev_result[0]
    if isinstance(prev_value, Exception):
        logger.warning("T+1 CCASS fetch task failed: %s", prev_value)
        return close_price, prev_share_map

    if prev_value is None:
        return close_price, prev_share_map

    for prev_item in prev_value["participants"]:
        prev_share_map[_normalize_participant_name(prev_item["name"])] = float(prev_item.get("share", 0.0))

    return close_price, prev_share_map


def _build_ccass_headers(client: httpx.AsyncClient) -> dict[str, str]:
    return {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www3.hkexnews.hk",
        "Referer": "https://www3.hkexnews.hk/sdw/search/searchsdw.aspx",
        "User-Agent": client.headers.get("User-Agent", "Mozilla/5.0"),
    }


async def fetch_chip_data(stock_code: str, date: str) -> dict[str, object]:
    stock_code_normalized = normalize_stock_code(stock_code)
    query_date = normalize_date(date)
    ccass_compare_date, ccass_target_date = await _resolve_ccass_dates_for_query_date(query_date)
    ccass_target_date_formatted = _format_query_date(ccass_target_date)

    cached = await _get_cached_chip_data(stock_code_normalized, query_date)
    if cached is not None:
        return cached

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        client.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
                )
            }
        )

        form_fields, action_url = await _fetch_form_metadata(client)

        current_task = asyncio.create_task(
            _fetch_ccass_participants_for_date(
                client,
                action_url,
                form_fields,
                stock_code_normalized,
                ccass_target_date_formatted,
            )
        )
        current_value = await asyncio.gather(current_task, return_exceptions=True)
        current_value = current_value[0]

        if isinstance(current_value, Exception):
            raise CCASSParseError("CCASS 取得失敗，請稍後重試。") from current_value

        if not current_value or not isinstance(current_value, dict):
            raise CCASSNotFoundError("查無該股票指定日期的 CCASS 資料。")

        current_participants = current_value["participants"]
        raw_columns = current_value.get("raw_columns", [])

        for item in current_participants:
            item["deltaShares"] = None

        total_top_share_ratio = sum(item["percentage"] for item in current_participants)
        result = {
            "stock_code": stock_code_normalized,
            "date": query_date,
            "ccass_settlement_date": ccass_target_date,
            "closePrice": None,
            "top_participants": current_participants,
            "total_top_share_ratio": total_top_share_ratio,
            "raw_columns": raw_columns,
        }

        await _set_cached_chip_data(stock_code_normalized, query_date, result)
        return result


async def fetch_chip_data_enriched(stock_code: str, date: str) -> dict[str, object]:
    stock_code_normalized = normalize_stock_code(stock_code)
    query_date = normalize_date(date)
    ccass_compare_date, ccass_target_date = await _resolve_ccass_dates_for_query_date(query_date)

    base_data = await _get_cached_chip_data(stock_code_normalized, query_date)
    if base_data is None:
        base_data = await fetch_chip_data(stock_code=stock_code_normalized, date=query_date)

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        client.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
                )
            }
        )

        form_fields, action_url = await _fetch_form_metadata(client)
        close_price, prev_share_map = await _enrich_with_market_data(
            client,
            action_url,
            form_fields,
            stock_code_normalized,
            query_date,
            ccass_compare_date,
            timeout_seconds=ENRICHMENT_TIMEOUT_SECONDS_ENRICHED,
        )

    participants = copy.deepcopy(base_data["top_participants"])
    for item in participants:
        if not prev_share_map:
            item["deltaShares"] = None
        else:
            prev_share = prev_share_map.get(_normalize_participant_name(item["name"]), 0.0)
            item["deltaShares"] = float(item["share"]) - prev_share

    result = {
        "stock_code": base_data["stock_code"],
        "date": base_data["date"],
        "ccass_settlement_date": ccass_target_date,
        "closePrice": close_price,
        "top_participants": participants,
        "total_top_share_ratio": base_data["total_top_share_ratio"],
        "raw_columns": base_data["raw_columns"],
    }

    await _set_cached_chip_data(stock_code_normalized, query_date, result)
    return result
