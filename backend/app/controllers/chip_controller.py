from fastapi import APIRouter, HTTPException, Query

from app.controllers.error_mapper import map_chip_service_exception, map_trading_days_exception
from app.schemas.chip_schema import ChipResponseSchema
from app.services.ccass_service import fetch_chip_data, fetch_chip_data_enriched
from app.services.trading_day_service import get_trading_days

router = APIRouter()


@router.get("/chips", response_model=ChipResponseSchema)
async def get_chips(
    stock_code: str = Query(..., min_length=1, max_length=8, description="股票代號，例如 00700"),
    date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$", description="查詢日期，格式 YYYY-MM-DD"),
) -> dict:
    try:
        return await fetch_chip_data(stock_code=stock_code, date=date)
    except Exception as exc:
        raise map_chip_service_exception(exc) from exc


@router.get("/trading-days", response_model=list[str])
async def get_valid_trading_days() -> list[str]:
    try:
        return await get_trading_days()
    except Exception as exc:
        raise map_trading_days_exception(exc) from exc


@router.get("/chips/enriched", response_model=ChipResponseSchema)
async def get_chips_enriched(
    stock_code: str = Query(..., min_length=1, max_length=8, description="股票代號，例如 00700"),
    date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$", description="查詢日期，格式 YYYY-MM-DD"),
) -> dict:
    try:
        return await fetch_chip_data_enriched(stock_code=stock_code, date=date)
    except Exception as exc:
        raise map_chip_service_exception(exc) from exc
