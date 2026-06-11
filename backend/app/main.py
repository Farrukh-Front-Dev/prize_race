"""
app/main.py
────────────
FastAPI application factory and lifespan manager.
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import v1_router
from app.core.config import get_settings
from app.core.database import init_db
from app.core.exceptions import register_exception_handlers
from app.core.middleware import IdempotencyLockMiddleware, TelegramAuthMiddleware
from app.services.leaderboard_service import bootstrap_tarantool_spaces
from app.services.sync_service import run_sync_worker

settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting PrizeRace API…")

    init_db()   # DEV: creates tables; PROD: Alembic runs in Dockerfile CMD
    logger.info("PostgreSQL ready.")

    bootstrap_tarantool_spaces()
    logger.info("Tarantool ready.")

    sync_task = asyncio.create_task(run_sync_worker())
    logger.info("Sync worker started.")

    yield  # ── application runs ────────────────────────────────────────────

    logger.info("Shutting down…")
    sync_task.cancel()
    try:
        await sync_task
    except asyncio.CancelledError:
        pass
    logger.info("Done.")


# ── App factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title="PrizeRace API",
        description="Web3 Sprint Platform — Telegram Mini App + TON blockchain",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    # ── CORS ──────────────────────────────────────────────────────────────
    # credentials=True requires explicit origins — wildcard is only for dev
    cors_origins = ["*"] if settings.debug else ["https://web.telegram.org"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Custom middleware (starlette applies bottom-up) ───────────────────
    # 2nd: idempotency lock (needs telegram_id already on request.state)
    app.add_middleware(IdempotencyLockMiddleware)
    # 1st: auth (populates request.state.telegram_id)
    app.add_middleware(TelegramAuthMiddleware)

    # ── Domain exception handlers ─────────────────────────────────────────
    register_exception_handlers(app)

    # ── Routes ────────────────────────────────────────────────────────────
    app.include_router(v1_router, prefix=settings.api_v1_prefix)

    # ── Utility ───────────────────────────────────────────────────────────
    @app.get("/health", include_in_schema=False)
    async def health():
        return {"status": "ok"}

    @app.get("/", include_in_schema=False)
    async def root():
        return {"name": "PrizeRace API", "version": "1.0.0"}

    return app


app = create_app()

# ── Dev entrypoint ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
