from __future__ import annotations

import datetime
import re

import pandas as pd
from bs4 import BeautifulSoup

from app.config import CCASS_BASE_URL
from app.core.exceptions import CCASSParseError


def normalize_numeric(value: str) -> float:
    """清洗數值欄位，移除逗號、百分號與全形空白後轉換為浮點數。"""
    cleaned = (
        str(value)
        .replace(",", "")
        .replace("%", "")
        .replace("\u3000", "")
        .strip()
    )
    return float(pd.to_numeric(cleaned, errors="coerce") or 0.0)


def extract_table_rows(table) -> list[list[str]]:
    rows: list[list[str]] = []
    for tr in table.find_all("tr"):
        cells = [cell.get_text(strip=True) for cell in tr.find_all(["th", "td"])]
        if cells:
            rows.append(cells)
    return rows


def find_column_index(columns: list[str], keywords: list[str]) -> int | None:
    lower_columns = [col.lower() for col in columns]
    for keyword in keywords:
        for index, col in enumerate(lower_columns):
            if keyword in col:
                return index
    return None


def is_valid_header_row(header: list[str]) -> bool:
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
        if find_column_index([cell], keywords) is not None:
            return True
    return False


def extract_mobile_rows(table) -> list[dict[str, str]]:
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


def find_mobile_heading(columns: list[str], keywords: list[str]) -> str | None:
    for keyword in keywords:
        for column in columns:
            if keyword in column.lower():
                return column
    return None


def is_mobile_table(table) -> bool:
    return table.find(class_=re.compile(r"mobile-list-heading", re.I)) is not None


def find_result_table(soup: BeautifulSoup) -> BeautifulSoup | None:
    candidate_table = None
    for table in soup.find_all("table"):
        if is_mobile_table(table):
            mobile_rows = extract_mobile_rows(table)
            if mobile_rows:
                return table

        classes = table.get("class", []) or []
        if any(isinstance(c, str) and ("search-result-table" in c or "table-scroll" in c) for c in classes):
            candidate_table = table
            continue

        rows = extract_table_rows(table)
        if len(rows) <= 1:
            continue
        header = rows[0]
        if is_valid_header_row(header):
            return table

    return candidate_table


def format_query_date(date_str: str) -> str:
    """將 YYYY-MM-DD 格式轉換為 ASP.NET 表單需要的 YYYY/MM/DD。"""
    try:
        parsed = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return parsed.strftime("%Y/%m/%d")
    except ValueError as exc:
        raise ValueError("日期格式不正確，請使用 YYYY-MM-DD。") from exc


def extract_form_data(html: str) -> tuple[dict[str, str], str]:
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
