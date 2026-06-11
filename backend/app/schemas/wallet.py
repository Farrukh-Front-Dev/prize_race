from decimal import Decimal

from pydantic import BaseModel, Field


class WalletConnectRequest(BaseModel):
    wallet_address: str = Field(..., min_length=48, max_length=64)
    signature: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)


class DepositRequest(BaseModel):
    event_id: int
    tx_hash: str = Field(..., min_length=64, max_length=128)
    # Decimal for monetary precision
    amount: Decimal = Field(..., gt=0, decimal_places=9)
