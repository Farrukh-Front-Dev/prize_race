from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models import EventStatus


class UserBase(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    wallet_address: Optional[str] = None
    username: Optional[str] = None


class UserResponse(UserBase):
    id: int
    wallet_address: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    xp_reward: int = 10
    verification_type: str = "manual"
    required_channel: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: int
    event_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    top_n_winners: int = 10
    total_prize_pool: float
    start_date: datetime
    end_date: datetime


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    top_n_winners: Optional[int] = None
    total_prize_pool: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class EventResponse(EventBase):
    id: int
    organizer_id: int
    status: EventStatus
    tx_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ParticipantResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    total_xp: int
    joined_at: datetime

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: Optional[str]
    total_xp: int
    wallet_address: Optional[str] = None


class TaskCompletionResponse(BaseModel):
    id: int
    user_id: int
    task_id: int
    completed_at: datetime
    verified: bool

    class Config:
        from_attributes = True
