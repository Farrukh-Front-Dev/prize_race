from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.enums import EventStatus


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    organizer_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        SQLEnum(EventStatus),
        default=EventStatus.DRAFT,
        nullable=False,
        index=True,
    )
    top_n_winners = Column(Integer, default=10, nullable=False)
    total_prize_pool = Column(Numeric(precision=18, scale=9), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    # Unique: one tx_hash per event, prevents deposit replay
    tx_hash = Column(String(255), nullable=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    organizer = relationship("User", foreign_keys=[organizer_id])
    participants = relationship(
        "Participant", back_populates="event", cascade="all, delete-orphan"
    )
    tasks = relationship(
        "Task", back_populates="event", cascade="all, delete-orphan"
    )
