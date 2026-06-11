"""
tests/test_auth.py
───────────────────
Unit tests for /api/v1/auth endpoints.
"""
import pytest
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository


# ── UserRepository ────────────────────────────────────────────────────────────

class TestUserRepository:

    def test_upsert_creates_new_user(self, db: Session):
        repo = UserRepository(db)
        user = repo.upsert(
            telegram_id="111",
            username="alice",
            first_name="Alice",
        )
        assert user.id is not None
        assert user.telegram_id == "111"
        assert user.username == "alice"

    def test_upsert_returns_existing_user(self, db: Session):
        repo = UserRepository(db)
        u1 = repo.upsert(telegram_id="222", username="bob")
        u2 = repo.upsert(telegram_id="222", username="bob_updated")
        assert u1.id == u2.id
        assert u2.username == "bob_updated"

    def test_upsert_race_condition_safe(self, db: Session):
        """Second upsert with same telegram_id should not raise."""
        repo = UserRepository(db)
        repo.upsert(telegram_id="333")
        user = repo.upsert(telegram_id="333")
        assert user is not None

    def test_get_by_telegram_id(self, db: Session):
        repo = UserRepository(db)
        repo.upsert(telegram_id="444", first_name="Carol")
        found = repo.get_by_telegram_id("444")
        assert found is not None
        assert found.first_name == "Carol"

    def test_get_by_telegram_id_not_found(self, db: Session):
        repo = UserRepository(db)
        assert repo.get_by_telegram_id("nonexistent") is None

    def test_set_wallet(self, db: Session):
        repo = UserRepository(db)
        user = repo.upsert(telegram_id="555")
        updated = repo.set_wallet(user, "EQC_test_wallet_address_here_00000000000")
        assert updated.wallet_address == "EQC_test_wallet_address_here_00000000000"
