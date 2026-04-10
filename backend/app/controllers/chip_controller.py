from fastapi import APIRouter, HTTPException, Query

from app.schemas.chip_schema import ChipResponseSchema
from app.services.ccass_service import fetch_chip_data

router = APIRouter()


@router.get("/chips", response_model=ChipResponseSchema)
def get_chips(
    stock_code: str = Query(..., min_length=1, max_length=8, description="股票代號，例如 00700"),
    date: str = Query(..., regex=r"^\d{4}-\d{2}-\d{2}$", description="查詢日期，格式 YYYY-MM-DD"),
) -> dict:
    try:
        return fetch_chip_data(stock_code=stock_code, date=date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
