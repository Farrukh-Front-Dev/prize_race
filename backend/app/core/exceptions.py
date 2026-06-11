"""
app/core/exceptions.py
───────────────────────
Domain-level exceptions + FastAPI exception handlers.

Using typed exceptions instead of raising HTTPException directly inside
services/repositories keeps business logic decoupled from the HTTP layer.
Handlers here convert them to appropriate JSON responses.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


# ── Domain exceptions ─────────────────────────────────────────────────────────

class PrizeRaceError(Exception):
    """Base exception for all domain errors."""


class NotFoundError(PrizeRaceError):
    """Requested resource does not exist."""
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found")
        self.resource = resource


class ForbiddenError(PrizeRaceError):
    """Caller is not allowed to perform the action."""
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(detail)
        self.detail = detail


class ConflictError(PrizeRaceError):
    """Action would violate a uniqueness / state constraint."""
    def __init__(self, detail: str = "Conflict"):
        super().__init__(detail)
        self.detail = detail


class ValidationError(PrizeRaceError):
    """Input data is semantically invalid."""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail)
        self.detail = detail


class UnauthorizedError(PrizeRaceError):
    """Authentication is missing or invalid."""
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(detail)
        self.detail = detail


class TooManyRequestsError(PrizeRaceError):
    """Rate limit or idempotency lock hit."""
    def __init__(self, detail: str = "Too many requests"):
        super().__init__(detail)
        self.detail = detail


class ExternalServiceError(PrizeRaceError):
    """Upstream service (TON, Telegram) returned an error."""
    def __init__(self, service: str, detail: str = ""):
        super().__init__(f"{service} error: {detail}")
        self.service = service
        self.detail = detail


# ── Handlers ──────────────────────────────────────────────────────────────────

def _json(code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=code, content={"detail": detail})


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all domain exception → HTTP response mappings to the app."""

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return _json(status.HTTP_404_NOT_FOUND, str(exc))

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(request: Request, exc: ForbiddenError):
        return _json(status.HTTP_403_FORBIDDEN, exc.detail)

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError):
        return _json(status.HTTP_409_CONFLICT, exc.detail)

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError):
        return _json(status.HTTP_422_UNPROCESSABLE_ENTITY, exc.detail)

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(request: Request, exc: UnauthorizedError):
        return _json(status.HTTP_401_UNAUTHORIZED, exc.detail)

    @app.exception_handler(TooManyRequestsError)
    async def too_many_handler(request: Request, exc: TooManyRequestsError):
        return _json(status.HTTP_429_TOO_MANY_REQUESTS, exc.detail)

    @app.exception_handler(ExternalServiceError)
    async def external_handler(request: Request, exc: ExternalServiceError):
        return _json(status.HTTP_502_BAD_GATEWAY, str(exc))
