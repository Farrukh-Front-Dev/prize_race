"""
app/core/security.py
─────────────────────
Telegram Mini App InitData validation (HMAC-SHA256).

Official spec:
  https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app

Key derivation:
  secret_key = HMAC-SHA256(key=b"WebAppData", msg=bot_token)
  NOT sha256(bot_token) — that was the old, incorrect approach.
"""
import hashlib
import hmac
import json
import logging
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Reject InitData older than 5 minutes (prevents replay attacks)
_MAX_AGE_SECONDS = 300


def _build_secret_key(bot_token: str) -> bytes:
    return hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode(),
        digestmod=hashlib.sha256,
    ).digest()


def validate_telegram_init_data(init_data: str) -> Optional[Dict[str, Any]]:
    """
    Validate a Telegram WebApp InitData string.

    Returns the parsed ``user`` dict on success, None on any failure.

    DEV MODE (DEBUG=True):
      Accepts ``hash=mock_hash_for_development`` without HMAC check.
      This allows testing in a regular browser without a real Telegram session.
      The auth_date freshness check is also skipped for mock data.
    """
    settings = get_settings()
    try:
        # unquote_plus handles both %XX encoding AND + → space
        decoded = urllib.parse.unquote_plus(init_data)

        data: Dict[str, str] = {}
        for pair in decoded.split("&"):
            if "=" not in pair:
                continue
            key, _, value = pair.partition("=")
            data[key] = value

        received_hash = data.pop("hash", None)
        if not received_hash:
            logger.warning("InitData: missing hash field")
            return None

        # ── Dev mock bypass ───────────────────────────────────────────────
        # Only active when DEBUG=True — never reaches production
        if settings.debug and received_hash == "mock_hash_for_development":
            user_str = data.get("user")
            if not user_str:
                logger.warning("InitData (mock): missing user field")
                return None
            user_data: Dict[str, Any] = json.loads(urllib.parse.unquote(user_str))
            logger.info("InitData: mock user accepted (DEBUG mode) id=%s", user_data.get("id"))
            return user_data
        # ─────────────────────────────────────────────────────────────────

        check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))

        secret_key = _build_secret_key(settings.telegram_bot_token)
        expected_hash = hmac.new(
            key=secret_key,
            msg=check_string.encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(received_hash, expected_hash):
            logger.warning("InitData: signature mismatch")
            return None

        auth_date = int(data.get("auth_date", 0))
        age = int(datetime.now(timezone.utc).timestamp()) - auth_date
        if age > _MAX_AGE_SECONDS:
            logger.warning("InitData: stale (%ds old, max %ds)", age, _MAX_AGE_SECONDS)
            return None

        user_str = data.get("user")
        if not user_str:
            logger.warning("InitData: missing user field")
            return None

        user_data = json.loads(user_str)
        logger.debug("InitData valid for telegram_id=%s", user_data.get("id"))
        return user_data

    except Exception as exc:
        logger.error("InitData validation error: %s", exc)
        return None
