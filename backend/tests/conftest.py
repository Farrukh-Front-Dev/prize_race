"""
tests/conftest.py
──────────────────
Shared pytest fixtures.

Design decisions:
  - SQLite :memory: — fast, isolated per test session, no cleanup needed.
  - Tarantool mocked globally — tests never need a running Tarantool.
  - TelegramAuthMiddleware bypassed — a test-only header is checked so
    HTTP integration tests can set telegram_id without real InitData.
  - Each `db` fixture rolls back after the test — full isolation.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from app.core.database import get_db
from app.models.base import Base
from app.main import create_app

# ── In-memory SQLite ──────────────────────────────────────────────────────────

_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_ENGINE)


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    Base.metadata.create_all(bind=_ENGINE)
    yield
    Base.metadata.drop_all(bind=_ENGINE)


@pytest.fixture()
def db():
    """Each test gets its own transaction that is rolled back on teardown."""
    connection = _ENGINE.connect()
    transaction = connection.begin()
    session = _Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


# ── Test app with all external deps mocked ────────────────────────────────────

@pytest.fixture()
def client(db):
    """
    HTTP test client with:
      - DB overridden to the test session
      - Tarantool mocked (returns None everywhere)
      - TelegramAuthMiddleware bypassed via X-Test-Telegram-Id header
    """
    app = create_app()

    def _override_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_db

    # Patch Tarantool connection pool globally
    with patch("app.core.database.TarantoolPool.get", return_value=None):
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c


# ── Auth helper ───────────────────────────────────────────────────────────────

def auth_headers(telegram_id: str = "123456789") -> dict:
    """
    Inject a test-only auth header.
    TelegramAuthMiddleware must honour X-Test-Telegram-Id in DEBUG mode
    (see middleware.py _PUBLIC_PREFIXES / test bypass logic).
    For repository-level tests no HTTP header is needed.
    """
    return {"X-Test-Telegram-Id": telegram_id}
