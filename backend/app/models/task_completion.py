from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base


class UserTaskCompletion(Base):
    __tablename__ = "user_task_completions"
    __table_args__ = (
        UniqueConstraint("user_id", "task_id", name="uq_completion_user_task"),
        Index("idx_completion_task_user", "task_id", "user_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    task_id = Column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    verified = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="task_completions")
    task = relationship("Task", back_populates="completions")
