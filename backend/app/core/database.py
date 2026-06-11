"""
app/core/database.py
─────────────────────
PostgreSQL (SQLAlchemy) + Tarantool connection management.

PostgreSQL:
  Standard SQLAlchemy engine + SessionLocal factory.
  get_db() is the FastAPI dependency that yields a session.

Tarantool:
  The official tarantool Python driver is *not* async-native.
  Strategy: per-thread connection via threading.local().
  Async route handlers offload blocking calls with asyncio.to_thread().
  TarantoolPool.get() returns a healthy connection with auto-reconnect.
"""
import logging
import threading
import time
from typing import Generator, Optional

import tarantool
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# ── PostgreSQL ────────────────────────────────────────────────────────────────

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_recycle=1800,          # recycle connections every 30 min
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Create all tables if they do not exist.

    DEV ONLY: In production, use Alembic migrations instead.
    This is only called when DEBUG=True to keep dev setup easy.
    In production (DEBUG=False), schema changes MUST go through
    `alembic upgrade head` in the Dockerfile CMD.
    """
    from app.models.base import Base  # local import avoids circular deps

    Base.metadata.create_all(bind=engine)
    logger.info("PostgreSQL tables created / verified (dev mode).")


# ── Tarantool ─────────────────────────────────────────────────────────────────

_MAX_RETRIES = 1           # only 1 attempt — fail fast, no log spam
_RETRY_DELAY = 0           # no sleep between attempts
_UNAVAILABLE_BACKOFF = 30  # seconds before retrying after total failure


class TarantoolPool:
    """
    Per-thread Tarantool connection with health-check and auto-reconnect.

    When Tarantool is unavailable the pool backs off for
    _UNAVAILABLE_BACKOFF seconds before retrying, so the sync worker
    does not spam the log with connection errors every 5 seconds.
    """

    _local: threading.local = threading.local()
    # Module-level "next retry" timestamp — shared across threads
    _next_retry_at: float = 0.0

    # ── private ──────────────────────────────────────────────────────────

    @classmethod
    def _create(cls) -> Optional[tarantool.Connection]:
        try:
            conn = tarantool.connect(
                settings.tarantool_host,
                settings.tarantool_port,
            )
            logger.info("Tarantool connected (thread=%s)", threading.current_thread().name)
            cls._next_retry_at = 0.0   # reset backoff on success
            return conn
        except Exception as exc:
            cls._next_retry_at = time.time() + _UNAVAILABLE_BACKOFF
            logger.warning(
                "Tarantool unavailable — will retry in %ds. (%s)",
                _UNAVAILABLE_BACKOFF, exc,
            )
            return None

    @classmethod
    def _current(cls) -> Optional[tarantool.Connection]:
        # Respect the back-off window — don't attempt a new connection yet
        if time.time() < cls._next_retry_at:
            return None

        conn: Optional[tarantool.Connection] = getattr(cls._local, "conn", None)
        if conn is None:
            conn = cls._create()
            cls._local.conn = conn
        return conn

    # ── public ───────────────────────────────────────────────────────────

    @classmethod
    def get(cls) -> Optional[tarantool.Connection]:
        """Return a healthy per-thread connection, or None if unavailable."""
        conn = cls._current()
        if conn is not None:
            try:
                conn.ping()
            except Exception:
                logger.warning("Tarantool connection stale — reconnecting.")
                cls._local.conn = None
                conn = cls._create()
                cls._local.conn = conn
        return conn


def get_tarantool() -> Optional[tarantool.Connection]:
    """Module-level shortcut used by services and middleware."""
    return TarantoolPool.get()
