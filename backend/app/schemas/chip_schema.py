from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ParticipantSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    participant_id: str | None = Field(default=None, alias="participantId")
    name: str
    share: float | int
    percentage: float | int
    delta_shares: float | int | None = Field(default=None, alias="deltaShares")


class ChipResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    stock_code: str
    date: str
    ccass_settlement_date: str
    close_price: float | None = Field(default=None, alias="closePrice")
    top_participants: list[ParticipantSchema]
    total_top_share_ratio: float
    raw_columns: list[str]
