"""
app/repositories/base.py
─────────────────────────
Generic SQLAlchemy repository with common CRUD helpers.
Domain repositories inherit from this class.
"""
from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Thin wrapper around a SQLAlchemy session for one model type."""

    def __init__(self, model: Type[ModelT], db: Session) -> None:
        self.model = model
        self.db = db

    # ── Read ──────────────────────────────────────────────────────────────

    def get_by_id(self, obj_id: int) -> Optional[ModelT]:
        return self.db.query(self.model).filter(self.model.id == obj_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelT]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    # ── Write ─────────────────────────────────────────────────────────────

    def create(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelT) -> ModelT:
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelT) -> None:
        self.db.delete(obj)
        self.db.commit()
