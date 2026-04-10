from __future__ import annotations


def normalize_stock_code(stock_code: str) -> str:
    """將股票代號標準化為 5-6 碼字串，並檢查是否為數字。"""
    normalized = stock_code.strip().upper()
    if not normalized.isdigit():
        raise ValueError("股票代號必須為數字，例如 00700。")
    return normalized.zfill(5)
