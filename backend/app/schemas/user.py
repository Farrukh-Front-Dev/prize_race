from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    telegram_id: str = Field(..., max_length=50)
    username: Optional[str] = Field(None, max_length=255)
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)


class UserUpdate(BaseModel):
    # wallet_address is intentionally NOT here — use PUT /wallet/connect
    # which validates ownership before storing the address.
    username: Optional[str] = Field(None, max_length=255)


class UserResponse(BaseModel):
    id: int
    telegram_id: str
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    wallet_address: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
