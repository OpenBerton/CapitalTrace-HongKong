from __future__ import annotations

import asyncio
import datetime
import logging
import time

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

TRADING_DAYS_BASE_TICKER = "0700.HK"
TRADING_DAYS_TTL_SECONDS = 24 * 3600
_TRADING_DAYS_CACHE: tuple[float, list[str]] | None = None
_TRADING_DAYS_CACHE_LOCK = asyncio.Lock()


def _normalize_trading_days(index_values) -> list[str]:
    days = sorted({pd.to_datetime(item).date().isoformat() for item in index_values})
    return days


def _fetch_trading_days_from_yahoo() -> list[str]:
    history = yf.Ticker(TRADING_DAYS_BASE_TICKER).history(
        period="1y",
        interval="1d",
        actions=False,
    )
    if history.empty:
        raise RuntimeError("無法從 Yahoo 取得港股交易日資料。")

    trading_days = _normalize_trading_days(history.index)
    if not trading_days:
        raise RuntimeError("Yahoo 回傳資料為空，無法生成交易日清單。")
    return trading_days


def _is_cache_valid(timestamp: float) -> bool:
    return time.time() - timestamp < TRADING_DAYS_TTL_SECONDS


async def get_trading_days(force_refresh: bool = False) -> list[str]:
    global _TRADING_DAYS_CACHE

    async with _TRADING_DAYS_CACHE_LOCK:
        if not force_refresh and _TRADING_DAYS_CACHE is not None:
            cache_ts, cache_days = _TRADING_DAYS_CACHE
            if _is_cache_valid(cache_ts):
                return cache_days.copy()

    try:
        fresh_days = await asyncio.to_thread(_fetch_trading_days_from_yahoo)
    except Exception as exc:
        async with _TRADING_DAYS_CACHE_LOCK:
            if _TRADING_DAYS_CACHE is not None:
                logger.warning("Trading days refresh failed, fallback to stale cache: %s", exc)
                return _TRADING_DAYS_CACHE[1].copy()
        raise RuntimeError("交易日資料暫時無法取得，請稍後再試。") from exc

    async with _TRADING_DAYS_CACHE_LOCK:
        _TRADING_DAYS_CACHE = (time.time(), fresh_days)
        return fresh_days.copy()


async def warm_trading_days_cache() -> None:
    try:
        days = await get_trading_days()
        logger.info("Trading days warmup completed, days=%s latest=%s", len(days), days[-1] if days else "n/a")
    except Exception as exc:
        logger.warning("Trading days warmup skipped: %s", exc)
