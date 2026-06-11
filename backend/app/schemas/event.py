from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.enums import EventStatus


class EventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    top_n_winners: int = Field(10, ge=1, le=1000)
    # Decimal for monetary precision — float has rounding errors
    total_prize_pool: Decimal = Field(..., gt=0, decimal_places=9)
    start_date: datetime
    end_date: datetime

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v: datetime, info) -> datetime:
        start = info.data.get("start_date")
        if start and v <= start:
            raise ValueError("end_date must be after start_date")
        return v


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    top_n_winners: Optional[int] = Field(None, ge=1, le=1000)
    total_prize_pool: Optional[Decimal] = Field(None, gt=0, decimal_places=9)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class EventResponse(BaseModel):
    id: int
    organizer_id: int
    title: str
    description: Optional[str]
    status: EventStatus
    top_n_winners: int
    total_prize_pool: Decimal
    start_date: datetime
    end_date: datetime
    tx_hash: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
