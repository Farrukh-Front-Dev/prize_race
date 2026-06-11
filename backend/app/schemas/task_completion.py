from datetime import datetime

from pydantic import BaseModel


class TaskCompletionResponse(BaseModel):
    id: int
    user_id: int
    task_id: int
    completed_at: datetime
    verified: bool

    model_config = {"from_attributes": True}
