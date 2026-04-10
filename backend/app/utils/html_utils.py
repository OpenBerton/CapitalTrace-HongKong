from __future__ import annotations


def clean_html(raw_html: str) -> str:
    """對 HTML 原始碼進行基本清洗，移除無用字元與空白。"""
    return raw_html.replace("\r", "").replace("\t", "").strip()
