"""
app/repositories/task_repository.py
─────────────────────────────────────
All DB queries related to Task and UserTaskCompletion.
"""
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.task_completion import UserTaskCompletion
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):

    def __init__(self, db: Session) -> None:
        super().__init__(Task, db)

    def list_by_event(self, event_id: int) -> List[Task]:
        return (
            self.db.query(Task).filter(Task.event_id == event_id).all()
        )


class TaskCompletionRepository(BaseRepository[UserTaskCompletion]):

    def __init__(self, db: Session) -> None:
        super().__init__(UserTaskCompletion, db)

    def get_completion(
        self, user_id: int, task_id: int
    ) -> Optional[UserTaskCompletion]:
        return (
            self.db.query(UserTaskCompletion)
            .filter(
                UserTaskCompletion.user_id == user_id,
                UserTaskCompletion.task_id == task_id,
            )
            .first()
        )

    def count_recent_completions(
        self,
        user_id: int,
        event_id: int,
        window_seconds: int = 60,
    ) -> int:
        """Count completions by this user in the event within the last N seconds."""
        since = datetime.utcnow() - timedelta(seconds=window_seconds)
        return (
            self.db.query(UserTaskCompletion)
            .join(Task, Task.id == UserTaskCompletion.task_id)
            .filter(
                UserTaskCompletion.user_id == user_id,
                Task.event_id == event_id,
                UserTaskCompletion.completed_at >= since,
            )
            .count()
        )
