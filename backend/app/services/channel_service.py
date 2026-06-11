"""
app/services/channel_service.py
─────────────────────────────────
Telegram channel membership check via getChatMember Bot API.
"""
import logging
from typing import Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_BOT_API_URL = "https://api.telegram.org/bot{token}/getChatMember"
_HTTP_TIMEOUT = 5
_ACTIVE_STATUSES = frozenset({"member", "administrator", "creator"})


class ChannelService:

    def __init__(self) -> None:
        settings = get_settings()
        self._url = _BOT_API_URL.format(token=settings.telegram_bot_token)

    async def is_subscribed(self, telegram_user_id: int, channel: str) -> bool:
        """
        Return True if the user is an active member of ``channel``.
        channel: "@username" or numeric "-100…" chat_id.

        Fails open on network errors — we prefer not to block users
        due to upstream outages.
        """
        try:
            async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
                resp = await client.get(
                    self._url,
                    params={"chat_id": channel, "user_id": telegram_user_id},
                )
        except httpx.RequestError as exc:
            logger.error("getChatMember network error: %s", exc)
            return True  # fail open

        if resp.status_code != 200:
            logger.warning(
                "getChatMember HTTP %d user=%d channel=%s",
                resp.status_code, telegram_user_id, channel,
            )
            return True  # fail open

        data = resp.json()
        if not data.get("ok"):
            if data.get("error_code") == 400:
                return False  # user definitely not in chat
            logger.warning("getChatMember error: %s", data)
            return True  # fail open for other API errors

        member_status: str = data.get("result", {}).get("status", "")
        subscribed = member_status in _ACTIVE_STATUSES
        logger.debug(
            "channel_check user=%d channel=%s status=%s → %s",
            telegram_user_id, channel, member_status, subscribed,
        )
        return subscribed


# ── Singleton ─────────────────────────────────────────────────────────────────

_instance: Optional[ChannelService] = None


def get_channel_service() -> ChannelService:
    global _instance
    if _instance is None:
        _instance = ChannelService()
    return _instance
