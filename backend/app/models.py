from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, UniqueConstraint, Index, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    wallet_address = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    participants = relationship("Participant", back_populates="user")
    task_completions = relationship("UserTaskCompletion", back_populates="user")


class EventStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_PAYMENT = "PENDING_PAYMENT"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(EventStatus), default=EventStatus.DRAFT)
    top_n_winners = Column(Integer, default=10)
    total_prize_pool = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    tx_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    participants = relationship("Participant", back_populates="event")
    tasks = relationship("Task", back_populates="event")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    xp_reward = Column(Integer, default=10)
    verification_type = Column(String(50), default="manual")
    required_channel = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="tasks")
    completions = relationship("UserTaskCompletion", back_populates="task")


class Participant(Base):
    __tablename__ = "participants"
    __table_args__ = (
        UniqueConstraint("user_id", "event_id", name="uq_user_event"),
        Index("idx_event_user", "event_id", "user_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    total_xp = Column(Integer, default=0)
    joined_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="participants")
    event = relationship("Event", back_populates="participants")


class UserTaskCompletion(Base):
    __tablename__ = "user_task_completions"
    __table_args__ = (
        UniqueConstraint("user_id", "task_id", name="uq_user_task"),
        Index("idx_task_user", "task_id", "user_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    verified = Column(Boolean, default=False)

    user = relationship("User", back_populates="task_completions")
    task = relationship("Task", back_populates="completions")
