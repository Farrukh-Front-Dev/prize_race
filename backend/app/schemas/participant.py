from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ParticipantResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    total_xp: int
    joined_at: datetime

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: Optional[str]
    total_xp: int
    wallet_address: Optional[str] = None
