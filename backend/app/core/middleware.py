"""
app/core/middleware.py
───────────────────────
1. TelegramAuthMiddleware  — validates X-Telegram-Init-Data on every request
2. IdempotencyLockMiddleware — atomic Tarantool lock for mutation endpoints
"""
import logging
import time

from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.database import get_tarantool
from app.core.security import validate_telegram_init_data

logger = logging.getLogger(__name__)

_LOCK_TTL = 5  # seconds

# Endpoints that skip auth
_PUBLIC_PREFIXES = (
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/api/v1/auth/register",
)

# Only POST/PUT on these prefixes get an idempotency lock
_LOCKED_PREFIXES = (
    "/api/v1/events",
    "/api/v1/tasks",
    "/api/v1/wallet",
)


def _json(code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=code, content={"detail": detail})


# ── Auth ──────────────────────────────────────────────────────────────────────

class TelegramAuthMiddleware(BaseHTTPMiddleware):
    """
    Validate Telegram Mini App InitData on every non-public request.

    On success  → sets request.state.telegram_id and .telegram_user
    On failure  → returns 401 immediately
    """

    async def dispatch(self, request: Request, call_next):
        if any(request.url.path.startswith(p) for p in _PUBLIC_PREFIXES):
            return await call_next(request)

        # ── Test bypass (DEBUG mode only) ─────────────────────────────────
        # Integration tests inject X-Test-Telegram-Id to skip HMAC validation.
        from app.core.config import get_settings as _gs
        if _gs().debug:
            test_id = request.headers.get("X-Test-Telegram-Id", "").strip()
            if test_id:
                request.state.telegram_user = {"id": test_id}
                request.state.telegram_id = test_id
                return await call_next(request)
        # ─────────────────────────────────────────────────────────────────

        init_data = request.headers.get("X-Telegram-Init-Data", "").strip()
        if not init_data:
            return _json(
                status.HTTP_401_UNAUTHORIZED,
                "Missing X-Telegram-Init-Data header",
            )

        user_data = validate_telegram_init_data(init_data)
        if not user_data:
            return _json(
                status.HTTP_401_UNAUTHORIZED,
                "Invalid or expired Telegram InitData",
            )

        request.state.telegram_user = user_data
        request.state.telegram_id = str(user_data["id"])
        return await call_next(request)


# ── Idempotency lock ──────────────────────────────────────────────────────────

class IdempotencyLockMiddleware(BaseHTTPMiddleware):
    """
    Prevent duplicate mutations via an atomic Tarantool lock.

    Flow:
      1. lock_key = "lock:<telegram_id>:<METHOD>:<path>"
      2. INSERT into Tarantool locks space (atomic)
         → success   : proceed, release lock after response
         → duplicate : 429 immediately (another request in flight)
         → Tarantool down : log warning, allow request through
    """

    async def dispatch(self, request: Request, call_next):
        if request.method not in ("POST", "PUT"):
            return await call_next(request)

        if not any(request.url.path.startswith(p) for p in _LOCKED_PREFIXES):
            return await call_next(request)

        telegram_id: str = getattr(request.state, "telegram_id", "")
        if not telegram_id:
            return await call_next(request)

        lock_key = f"lock:{telegram_id}:{request.method}:{request.url.path}"
        conn = get_tarantool()
        acquired = False

        if conn is not None:
            try:
                conn.insert("locks", (lock_key, int(time.time()) + _LOCK_TTL))
                acquired = True
            except Exception as exc:
                if "Duplicate key" in str(exc) or "already exists" in str(exc):
                    return _json(
                        status.HTTP_429_TOO_MANY_REQUESTS,
                        "Request is already being processed, please wait",
                    )
                logger.warning("Idempotency lock unavailable: %s", exc)

        try:
            return await call_next(request)
        finally:
            if acquired and conn is not None:
                try:
                    conn.delete("locks", (lock_key,))
                except Exception as exc:
                    logger.warning("Failed to release lock %s: %s", lock_key, exc)
