from __future__ import annotations

from pydantic import BaseModel


class ParticipantSchema(BaseModel):
    name: str
    share: float | int
    percentage: float | int
    deltaShares: float | int | None = None


class ChipResponseSchema(BaseModel):
    stock_code: str
    date: str
    ccass_settlement_date: str
    closePrice: float | None = None
    top_participants: list[ParticipantSchema]
    total_top_share_ratio: float
    raw_columns: list[str]
