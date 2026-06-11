"""
tests/test_anti_fraud.py
─────────────────────────
Unit tests for AntiFraudService.
"""
from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.anti_fraud import AntiFraudService


def _make_user(days_old: int = 40, telegram_id: str = "999") -> User:
    return User(
        telegram_id=telegram_id,
        created_at=datetime.utcnow() - timedelta(days=days_old),
    )


class TestAccountAge:

    def test_old_account_passes(self):
        user = _make_user(days_old=40)
        ok, _ = AntiFraudService.check_account_age(user)
        assert ok is True

    def test_young_account_blocked(self):
        user = _make_user(days_old=5)
        ok, reason = AntiFraudService.check_account_age(user)
        assert ok is False
        assert "young" in reason.lower()

    def test_exactly_min_age_passes(self):
        from app.core.config import get_settings
        min_days = get_settings().min_account_age_days
        user = _make_user(days_old=min_days)
        ok, _ = AntiFraudService.check_account_age(user)
        assert ok is True

    def test_no_created_at_blocked(self):
        user = User(telegram_id="x", created_at=None)
        ok, reason = AntiFraudService.check_account_age(user)
        assert ok is False
        assert "unknown" in reason.lower()


class TestOrganiserConflict:

    def test_organiser_blocked(self):
        ok, reason = AntiFraudService.check_not_organiser(7, 7)
        assert ok is False
        assert "organiser" in reason.lower()

    def test_non_organiser_passes(self):
        ok, _ = AntiFraudService.check_not_organiser(7, 8)
        assert ok is True


class TestSecurity:

    def test_validate_init_data_missing_hash(self):
        from app.core.security import validate_telegram_init_data
        result = validate_telegram_init_data("user=%7B%22id%22%3A1%7D&auth_date=0")
        assert result is None

    def test_validate_init_data_empty(self):
        from app.core.security import validate_telegram_init_data
        result = validate_telegram_init_data("")
        assert result is None
