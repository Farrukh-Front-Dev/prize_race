from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app.middleware import TelegramAuthMiddleware, IdempotencyLockMiddleware
from app.routes import auth, events, tasks, wallet
from app.services.tarantool_service import get_leaderboard_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting PrizeRace API...")
    init_db()
    tarantool_service = get_leaderboard_service()
    logger.info("✅ Tarantool Leaderboard Service initialized")
    logger.info("✅ Telegram Validation Service ready")
    logger.info("✅ TON Integration Service ready")

    yield

    # Shutdown
    logger.info("🛑 Shutting down PrizeRace API...")


# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="PrizeRace API",
    description="Web3 Sprint Platform with Telegram Mini App",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(IdempotencyLockMiddleware)
app.add_middleware(TelegramAuthMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(tasks.router)
app.include_router(wallet.router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "PrizeRace API",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
