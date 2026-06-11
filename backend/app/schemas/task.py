from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.enums import VerificationType


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    xp_reward: int = Field(10, ge=1, le=10_000)
    verification_type: VerificationType = VerificationType.MANUAL
    required_channel: Optional[str] = Field(None, max_length=255)

    @field_validator("required_channel")
    @classmethod
    def validate_channel(cls, v: Optional[str], info) -> Optional[str]:
        vtype = info.data.get("verification_type")
        if vtype == VerificationType.CHANNEL_SUBSCRIPTION and not v:
            raise ValueError(
                "required_channel must be set for channel_subscription tasks"
            )
        return v


class TaskResponse(BaseModel):
    id: int
    event_id: int
    title: str
    description: Optional[str]
    xp_reward: int
    verification_type: VerificationType
    required_channel: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
