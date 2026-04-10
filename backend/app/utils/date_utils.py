from __future__ import annotations

from datetime import datetime


def normalize_date(date_str: str) -> str:
    """將日期字串轉換為 YYYY-MM-DD 格式，若格式不正確則丟出例外。"""
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d")
        return parsed.strftime("%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("日期格式不正確，請使用 YYYY-MM-DD。") from exc
