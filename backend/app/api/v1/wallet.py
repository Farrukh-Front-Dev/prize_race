"""
app/api/v1/wallet.py
─────────────────────
TON wallet connect and deposit validation.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.enums import EventStatus
from app.models.user import User
from app.repositories.event_repository import EventRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse
from app.schemas.wallet import DepositRequest, WalletConnectRequest
from app.services.ton_service import get_ton_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wallet", tags=["wallet"])


# ── Connect wallet ────────────────────────────────────────────────────────────

@router.post(
    "/connect",
    response_model=UserResponse,
    summary="Connect TON wallet to user account",
)
async def connect_wallet(
    body: WalletConnectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Security:
      1. Verify wallet ownership (signature / balance proof)
      2. Confirm wallet has ≥ 0.1 TON
      3. Store address on user record
    """
    ton = get_ton_service()

    # verify_wallet_ownership internally checks balance ≥ 0.1 TON.
    # This is documented as a placeholder until real ed25519 proof is wired.
    if not await ton.verify_wallet_ownership(
        body.wallet_address, body.signature, body.message
    ):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Wallet ownership verification failed",
        )

    repo = UserRepository(db)
    updated = repo.set_wallet(current_user, body.wallet_address)
    logger.info("Wallet %s connected for user %d", body.wallet_address, current_user.id)
    return updated


# ── Validate deposit ──────────────────────────────────────────────────────────

@router.post(
    "/deposit",
    summary="Validate prize pool deposit — activates the event",
)
async def validate_deposit(
    body: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Organiser calls this after depositing TON to the smart contract.

    Flow:
      1. Wallet must be connected
      2. Caller must be the event organiser
      3. Event must be in PENDING_PAYMENT status
      4. tx_hash must not be reused
      5. Verify transaction on-chain
      6. Transition event → ACTIVE
    """
    if not current_user.wallet_address:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Wallet not connected — call /wallet/connect first",
        )

    e_repo = EventRepository(db)

    event = e_repo.get_by_id(body.event_id)
    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

    if event.organizer_id != current_user.id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Only the event organiser can validate a deposit",
        )

    if event.status != EventStatus.PENDING_PAYMENT:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Event must be in PENDING_PAYMENT status (current: {event.status})",
        )

    # Guard against tx_hash reuse across events
    if e_repo.get_by_tx_hash(body.tx_hash):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Transaction hash already used for another event",
        )

    ton = get_ton_service()
    if not await ton.validate_deposit(
        tx_hash=body.tx_hash,
        expected_amount=Decimal(str(body.amount)),
    ):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Deposit transaction could not be verified on-chain",
        )

    activated = e_repo.activate(event, body.tx_hash)
    logger.info("Event %d activated via tx=%s", activated.id, body.tx_hash)

    return {
        "status": "success",
        "event_id": activated.id,
        "event_status": activated.status,
        "tx_hash": activated.tx_hash,
    }


# ── Balance ───────────────────────────────────────────────────────────────────

@router.get(
    "/balance",
    summary="Get connected wallet's TON balance",
)
async def get_balance(current_user: User = Depends(get_current_user)):
    if not current_user.wallet_address:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Wallet not connected")

    ton = get_ton_service()
    balance = await ton.get_wallet_balance(current_user.wallet_address)
    if balance is None:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            "Unable to retrieve balance from TON network",
        )

    return {
        "wallet_address": current_user.wallet_address,
        "balance_ton": float(balance),
        "currency": "TON",
    }
