"""
app/services/anti_fraud.py
───────────────────────────
Anti-fraud checks before joining events or completing tasks.

All public methods return (is_valid: bool, reason: str) so the
API layer gets a human-readable rejection message.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Tuple

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.user import User
from app.repositories.participant_repository import ParticipantRepository
from app.repositories.task_repository import TaskCompletionRepository

logger = logging.getLogger(__name__)
settings = get_settings()

# Completion rate-limit: max N tasks within this many seconds
_RATE_WINDOW_SECONDS = 60
_RATE_MAX_COMPLETIONS = 50


class AntiFraudService:

    # ── Account age ───────────────────────────────────────────────────────

    @staticmethod
    def check_account_age(user: User) -> Tuple[bool, str]:
        """
        Account must be at least MIN_ACCOUNT_AGE_DAYS old.
        ``telegram_created_at`` takes precedence over ``created_at``.
        """
        reference = user.telegram_created_at or user.created_at
        if reference is None:
            return False, "Account creation date unknown"

        # Make both sides naive-UTC for comparison
        if reference.tzinfo is not None:
            reference = reference.replace(tzinfo=None)

        age = datetime.utcnow() - reference
        min_age = timedelta(days=settings.min_account_age_days)

        if age < min_age:
            days_left = (min_age - age).days + 1
            return (
                False,
                f"Account too young — {days_left} day(s) until eligible",
            )
        return True, "ok"

    # ── Organiser conflict ────────────────────────────────────────────────

    @staticmethod
    def check_not_organiser(user_id: int, organiser_id: int) -> Tuple[bool, str]:
        if user_id == organiser_id:
            return False, "Organiser cannot participate in their own event"
        return True, "ok"

    # ── Duplicate participation ───────────────────────────────────────────

    @staticmethod
    def check_not_already_joined(
        user_id: int, event_id: int, db: Session
    ) -> Tuple[bool, str]:
        repo = ParticipantRepository(db)
        if repo.is_participant(user_id, event_id):
            return False, "Already joined this event"
        return True, "ok"

    # ── Task completion rate ──────────────────────────────────────────────

    @staticmethod
    def check_completion_rate(
        user_id: int, event_id: int, db: Session
    ) -> Tuple[bool, str]:
        repo = TaskCompletionRepository(db)
        count = repo.count_recent_completions(
            user_id, event_id, _RATE_WINDOW_SECONDS
        )
        if count >= _RATE_MAX_COMPLETIONS:
            return (
                False,
                f"Too many task completions in {_RATE_WINDOW_SECONDS}s — slow down",
            )
        return True, "ok"

    # ── Composite checks ──────────────────────────────────────────────────

    @classmethod
    def validate_join(
        cls,
        user: User,
        organiser_id: int,
        event_id: int,
        db: Session,
    ) -> Tuple[bool, str]:
        for fn, args in [
            (cls.check_account_age, (user,)),
            (cls.check_not_organiser, (user.id, organiser_id)),
            (cls.check_not_already_joined, (user.id, event_id, db)),
        ]:
            ok, reason = fn(*args)
            if not ok:
                return False, reason
        return True, "ok"

    @classmethod
    def validate_task_completion(
        cls, user: User, event_id: int, db: Session
    ) -> Tuple[bool, str]:
        return cls.check_completion_rate(user.id, event_id, db)
