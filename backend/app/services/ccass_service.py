from __future__ import annotations

import datetime
import logging
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.config import CCASS_BASE_URL, REQUEST_TIMEOUT
from app.core.exceptions import CCASSParseError, CCASSNotFoundError
from app.utils.date_utils import normalize_date
from app.utils.stock_utils import normalize_stock_code
from app.utils.html_utils import clean_html

logger = logging.getLogger(__name__)


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


def _extract_form_data(html: str) -> tuple[dict[str, str], str]:
    soup = BeautifulSoup(html, "html.parser")
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


def fetch_chip_data(stock_code: str, date: str) -> dict[str, object]:
    stock_code_normalized = normalize_stock_code(stock_code)
    query_date = normalize_date(date)
    query_date_formatted = _format_query_date(date)
    today = datetime.date.today().strftime("%Y%m%d")

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            )
        }
    )

    try:
        initial_response = session.get(CCASS_BASE_URL, timeout=REQUEST_TIMEOUT)
        initial_response.raise_for_status()
    except requests.Timeout as exc:
        raise TimeoutError("CCASS 初始連線超時，請稍後重試。") from exc
    except requests.RequestException as exc:
        raise ConnectionError("無法連線到 CCASS 服務，請檢查網路或 URL 設定。") from exc

    form_fields, action_url = _extract_form_data(clean_html(initial_response.text))
    action_url = urljoin(initial_response.url, action_url)
    payload = form_fields.copy()
    payload.update(
        {
            "__EVENTTARGET": "btnSearch",
            "__EVENTARGUMENT": "",
            "today": today,
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

    post_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www3.hkexnews.hk",
        "Referer": "https://www3.hkexnews.hk/sdw/search/searchsdw.aspx",
        "User-Agent": session.headers["User-Agent"],
    }

    try:
        response = session.post(
            action_url,
            data=payload,
            headers=post_headers,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.Timeout as exc:
        raise TimeoutError("CCASS 查詢請求超時，請稍後重試。") from exc
    except requests.RequestException as exc:
        raise ConnectionError("無法連線到 CCASS 服務，請檢查網路或 URL 設定。") from exc

    logger.debug(
        "CCASS 查詢回應 status=%s url=%s length=%s",
        response.status_code,
        response.url,
        len(response.text),
    )

    html = clean_html(response.text)
    soup = BeautifulSoup(html, "html.parser")
    table = _find_result_table(soup)
    if table is None:
        raise CCASSParseError(
            "找不到 CCASS 交易資料表格，網站格式可能已變更。"
        )

    if _is_mobile_table(table):
        mobile_rows = _extract_mobile_rows(table)
        if not mobile_rows:
            raise CCASSParseError("CCASS 行動版資料表格無法解析。")

        first_row = mobile_rows[0]
        name_key = _find_mobile_heading(
            list(first_row.keys()),
            ["name of ccass participant", "participant name", "participant", "名稱", "參與者"],
        )
        share_key = _find_mobile_heading(
            list(first_row.keys()),
            ["shareholding", "shareholding:", "shareholding", "持股", "股數"],
        )
        percentage_key = _find_mobile_heading(
            list(first_row.keys()),
            ["percentage", "%", "佔比", "持股比例", "比例"],
        )

        participants = []
        for row in mobile_rows[:10]:
            name = row.get(name_key) if name_key else None
            if not name:
                name = row.get(_find_mobile_heading(list(row.keys()), ["participant id", "participant name", "participant", "名稱", "參與者"]))
            share = _normalize_numeric(row.get(share_key, "0")) if share_key else 0.0
            percentage = _normalize_numeric(row.get(percentage_key, "0")) if percentage_key else 0.0
            participants.append({
                "name": name or "Unknown",
                "share": share,
                "percentage": percentage,
            })

        total_top_share_ratio = sum(item["percentage"] for item in participants)
        return {
            "stock_code": stock_code_normalized,
            "date": query_date,
            "top_participants": participants,
            "total_top_share_ratio": total_top_share_ratio,
            "raw_columns": list(first_row.keys()),
        }

    rows = _extract_table_rows(table)
    if len(rows) <= 1:
        raise CCASSNotFoundError("查無該股票指定日期的 CCASS 資料。")

    header = rows[0]
    data_rows = [row for row in rows[1:] if len(row) == len(header)]
    if not data_rows:
        raise CCASSParseError("CCASS 表格資料不完整或欄位格式異常。")

    df = pd.DataFrame(data_rows, columns=header)
    df = df.dropna(how="all", axis=1)

    name_index = _find_column_index(header, ["名稱", "參與者", "券商", "機構"])
    share_index = _find_column_index(header, ["持股", "股數", "持股量"])
    percentage_index = _find_column_index(header, ["%", "佔比", "持股比例", "比例"])

    if percentage_index is None and share_index is None:
        raise CCASSParseError(
            "找不到有效的持股或持股比例欄位，可能是網站結構已變更。"
            f" 表頭: {header}"
        )

    participants: list[dict[str, object]] = []
    for row in data_rows[:10]:
        name = row[name_index] if name_index is not None else row[0]
        share = _normalize_numeric(row[share_index]) if share_index is not None else 0.0
        percentage = _normalize_numeric(row[percentage_index]) if percentage_index is not None else 0.0
        participants.append({
            "name": name,
            "share": share,
            "percentage": percentage,
        })

    if percentage_index is not None:
        total_top_share_ratio = sum(item["percentage"] for item in participants)
    else:
        total_top_share_ratio = 0.0

    return {
        "stock_code": stock_code_normalized,
        "date": query_date,
        "top_participants": participants,
        "total_top_share_ratio": total_top_share_ratio,
        "raw_columns": df.columns.tolist(),
    }
