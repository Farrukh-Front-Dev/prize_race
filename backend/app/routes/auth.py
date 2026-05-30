from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserCreate, UserUpdate

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register or get existing user (Upsert logic)"""
    try:
        # Try to find existing user
        existing_user = db.query(User).filter(
            User.telegram_id == user_data.telegram_id
        ).first()

        if existing_user:
            return existing_user

        # Create new user
        new_user = User(**user_data.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    telegram_id: str, db: Session = Depends(get_db)
):
    """Get current user profile"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/me", response_model=UserResponse)
async def update_user(
    telegram_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
):
    """Update user profile"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user
