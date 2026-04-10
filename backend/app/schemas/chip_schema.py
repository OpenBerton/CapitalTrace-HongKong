from __future__ import annotations

from pydantic import BaseModel


class ParticipantSchema(BaseModel):
    name: str
    share: float | int
    percentage: float | int


class ChipResponseSchema(BaseModel):
    stock_code: str
    date: str
    top_participants: list[ParticipantSchema]
    total_top_share_ratio: float
    raw_columns: list[str]
