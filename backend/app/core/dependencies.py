"""
app/core/dependencies.py
─────────────────────────
Shared FastAPI dependencies:
  - get_db      → SQLAlchemy Session
  - get_current_user → authenticated User ORM object
"""
import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    Resolve the authenticated Telegram user from request state.

    TelegramAuthMiddleware stores telegram_id on request.state after
    validating the X-Telegram-Init-Data header.

    If the user does not exist yet in the DB they are auto-created
    (upsert on first visit) — this is safe because telegram_id has a
    UNIQUE constraint and the /register endpoint handles explicit
    registration with richer data.
    """
    telegram_id: Optional[str] = getattr(request.state, "telegram_id", None)
    if not telegram_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        tg = getattr(request.state, "telegram_user", {})
        user = User(
            telegram_id=telegram_id,
            username=tg.get("username"),
            first_name=tg.get("first_name"),
            last_name=tg.get("last_name"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Auto-registered user telegram_id=%s", telegram_id)

    return user
