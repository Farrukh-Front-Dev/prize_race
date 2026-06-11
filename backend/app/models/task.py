from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.enums import VerificationType


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(
        Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    xp_reward = Column(Integer, default=10, nullable=False)
    verification_type = Column(
        SQLEnum(VerificationType),
        default=VerificationType.MANUAL,
        nullable=False,
    )
    # Required only for CHANNEL_SUBSCRIPTION tasks (e.g. "@mychannel")
    required_channel = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    event = relationship("Event", back_populates="tasks")
    completions = relationship(
        "UserTaskCompletion", back_populates="task", cascade="all, delete-orphan"
    )
