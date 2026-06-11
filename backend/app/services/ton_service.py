"""
app/services/ton_service.py
────────────────────────────
TON blockchain integration — deposit verification, balance queries,
distribution payload builder.
"""
import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_TON_API = {
    "testnet": "https://testnet.toncenter.com/api/v2",
    "mainnet": "https://toncenter.com/api/v2",
}
_NANOTON = Decimal("1_000_000_000")
_MIN_WALLET_BALANCE = Decimal("0.1")
_HTTP_TIMEOUT = 10


class TONService:

    def __init__(self) -> None:
        s = get_settings()
        self._base = _TON_API.get(s.ton_network, _TON_API["testnet"])
        self._api_key = s.ton_api_key
        self._contract = s.ton_contract_address

    # ── Internal ──────────────────────────────────────────────────────────

    async def _get(self, endpoint: str, params: Dict[str, Any]) -> Optional[Any]:
        params["api_key"] = self._api_key
        try:
            async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
                resp = await client.get(f"{self._base}/{endpoint}", params=params)
        except httpx.RequestError as exc:
            logger.error("TON API request error [%s]: %s", endpoint, exc)
            return None
        if resp.status_code != 200:
            logger.error("TON API [%s] HTTP %d", endpoint, resp.status_code)
            return None
        data = resp.json()
        if not data.get("ok"):
            logger.warning("TON API [%s] ok=false: %s", endpoint, data)
            return None
        return data.get("result")

    # ── Balance ───────────────────────────────────────────────────────────

    async def get_wallet_balance(self, address: str) -> Optional[Decimal]:
        result = await self._get("getAddressBalance", {"address": address})
        if result is None:
            return None
        try:
            return Decimal(int(result)) / _NANOTON
        except (TypeError, ValueError) as exc:
            logger.error("Balance parse error: %s", exc)
            return None

    # ── Wallet ownership ──────────────────────────────────────────────────

    async def verify_wallet_ownership(
        self, wallet_address: str, signature: str, message: str
    ) -> bool:
        """
        Verify the caller owns the wallet.

        Production: replace with toncrypto ed25519 TonConnect proof.
        Current guard: wallet must exist on-chain with ≥ 0.1 TON.
        """
        # TODO: implement verify_ton_proof(wallet_address, signature, message)
        balance = await self.get_wallet_balance(wallet_address)
        if balance is None or balance < _MIN_WALLET_BALANCE:
            logger.warning(
                "Wallet ownership check failed addr=%s balance=%s",
                wallet_address, balance,
            )
            return False
        return True

    # ── Deposit ───────────────────────────────────────────────────────────

    async def validate_deposit(
        self, tx_hash: str, expected_amount: Decimal
    ) -> bool:
        """
        Verify a deposit transaction:
         1. Exists in the contract's recent transaction history
         2. Destination is our contract address
         3. Value ≥ expected_amount
        """
        if not self._contract:
            logger.error("TON contract address not configured")
            return False

        result = await self._get(
            "getTransactions", {"address": self._contract, "limit": 50}
        )
        if not result:
            return False

        for tx in result:
            in_msg = tx.get("in_msg", {})
            tx_id = tx.get("transaction_id", {}).get("hash", "")
            if in_msg.get("hash") != tx_hash and tx_id != tx_hash:
                continue

            dest = in_msg.get("destination", "")
            if dest != self._contract:
                logger.warning(
                    "Deposit dest mismatch: expected=%s got=%s",
                    self._contract, dest,
                )
                return False

            received = Decimal(int(in_msg.get("value", 0))) / _NANOTON
            if received < expected_amount:
                logger.warning(
                    "Deposit amount insufficient: expected=%s received=%s",
                    expected_amount, received,
                )
                return False

            logger.info("Deposit validated tx=%s amount=%s TON", tx_hash, received)
            return True

        logger.warning("Deposit tx not found: %s", tx_hash)
        return False

    # ── Distribution payload ──────────────────────────────────────────────

    def build_distribution_payload(
        self,
        winners: List[Tuple[str, Decimal]],   # [(wallet_address, amount_ton)]
    ) -> Dict[str, Any]:
        """Build the payload for the smart-contract Distribute call."""
        distribution = []
        total = Decimal(0)
        for wallet, amount in winners:
            if not wallet:
                logger.warning("Skipping winner with no wallet")
                continue
            if amount < Decimal("0.01"):
                logger.warning("Skipping dust amount %s for %s", amount, wallet)
                continue
            distribution.append({
                "address": wallet,
                "amount": str(int(amount * _NANOTON)),
            })
            total += amount
        return {
            "type": "distribute",
            "winners": distribution,
            "total_nanoton": str(int(total * _NANOTON)),
        }


# ── Singleton ─────────────────────────────────────────────────────────────────

_instance: Optional[TONService] = None


def get_ton_service() -> TONService:
    global _instance
    if _instance is None:
        _instance = TONService()
    return _instance
