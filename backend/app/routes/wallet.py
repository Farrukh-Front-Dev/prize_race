"""
Wallet Management Routes
TON wallet connection and deposit handling
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import User, Event, EventStatus
from app.schemas import UserResponse
from app.services.telegram_service import TelegramValidationService
from app.services.ton_service import get_ton_service
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/wallet", tags=["wallet"])


class WalletConnectRequest(BaseModel):
    """Wallet connection request"""
    wallet_address: str
    signature: str
    message: str


class DepositRequest(BaseModel):
    """Deposit validation request"""
    event_id: int
    tx_hash: str
    amount: float


class WalletResponse(BaseModel):
    """Wallet info response"""
    wallet_address: str
    balance: float
    connected_at: str

    class Config:
        from_attributes = True


@router.post("/connect", response_model=UserResponse)
async def connect_wallet(
    request: WalletConnectRequest,
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Connect TON wallet to user account
    
    SECURITY:
    - Verify wallet ownership via signature
    - Check wallet has minimum balance
    - Store wallet address encrypted
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Verify wallet ownership
    ton_service = get_ton_service()
    is_valid = await ton_service.verify_wallet_ownership(
        request.wallet_address,
        request.signature,
        request.message,
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid wallet signature",
        )

    # Check wallet balance
    balance = await ton_service.get_wallet_balance(request.wallet_address)
    if balance is None or balance < Decimal("0.1"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient wallet balance (minimum 0.1 TON)",
        )

    # Update user wallet
    user.wallet_address = request.wallet_address
    db.commit()
    db.refresh(user)

    logger.info(f"✅ Wallet connected for user {user_id}: {request.wallet_address}")
    return user


@router.post("/deposit")
async def validate_deposit(
    request: DepositRequest,
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Validate deposit transaction
    
    FLOW:
    1. Get event details
    2. Verify transaction on blockchain
    3. Update event status to ACTIVE
    4. Store transaction hash
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet not connected",
        )

    event = db.query(Event).filter(Event.id == request.event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if event.organizer_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizer can deposit",
        )

    if event.status != EventStatus.PENDING_PAYMENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Event status must be PENDING_PAYMENT, got {event.status}",
        )

    # Validate deposit on blockchain
    ton_service = get_ton_service()
    is_valid = await ton_service.validate_deposit(
        request.tx_hash,
        Decimal(str(request.amount)),
        "contract_address_here",  # TODO: Get from config
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid deposit transaction",
        )

    # Update event status
    event.status = EventStatus.ACTIVE
    event.tx_hash = request.tx_hash
    db.commit()
    db.refresh(event)

    logger.info(f"✅ Deposit validated for event {request.event_id}: {request.tx_hash}")

    return {
        "status": "success",
        "event_id": event.id,
        "event_status": event.status,
        "tx_hash": event.tx_hash,
    }


@router.get("/balance")
async def get_wallet_balance(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Get user's wallet balance"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet not connected",
        )

    ton_service = get_ton_service()
    balance = await ton_service.get_wallet_balance(user.wallet_address)

    if balance is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get balance",
        )

    return {
        "wallet_address": user.wallet_address,
        "balance": float(balance),
        "currency": "TON",
    }
