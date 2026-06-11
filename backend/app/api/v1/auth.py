"""
app/api/v1/auth.py
───────────────────
User registration and profile endpoints.
/register is intentionally public — the Mini App calls it on first open.
"""
import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Register or update existing user (upsert by telegram_id)",
)
async def register(body: UserCreate, db: Session = Depends(get_db)):
    """
    Public endpoint — no X-Telegram-Init-Data required.
    Upserts the user: creates on first call, updates mutable fields on
    subsequent calls.
    """
    repo = UserRepository(db)
    user = repo.upsert(
        telegram_id=body.telegram_id,
        username=body.username,
        first_name=body.first_name,
        last_name=body.last_name,
    )
    logger.info("register telegram_id=%s", body.telegram_id)
    return user


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get authenticated user profile",
)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update username (wallet updated via /wallet/connect)",
)
async def update_me(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = UserRepository(db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    return repo.update(current_user)
