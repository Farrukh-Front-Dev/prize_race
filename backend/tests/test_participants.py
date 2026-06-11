"""
tests/test_participants.py
───────────────────────────
Unit tests for ParticipantRepository and anti-fraud join validation.
"""
from datetime import datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.enums import EventStatus
from app.models.event import Event
from app.models.participant import Participant
from app.models.user import User
from app.repositories.event_repository import EventRepository
from app.repositories.participant_repository import ParticipantRepository
from app.repositories.user_repository import UserRepository
from app.services.anti_fraud import AntiFraudService


# ── Helpers ───────────────────────────────────────────────────────────────────

def _user(db, tid, days_old=40):
    u = UserRepository(db).upsert(telegram_id=tid)
    u.created_at = datetime.utcnow() - timedelta(days=days_old)
    db.commit()
    db.refresh(u)
    return u


def _active_event(db, organiser_id):
    e = EventRepository(db).create(Event(
        organizer_id=organiser_id,
        title="Active Sprint",
        total_prize_pool=10,
        top_n_winners=3,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=7),
    ))
    EventRepository(db).set_status(e, EventStatus.PENDING_PAYMENT)
    return EventRepository(db).activate(e, tx_hash="x" * 64)


# ── ParticipantRepository ─────────────────────────────────────────────────────

class TestParticipantRepository:

    def test_create_participant(self, db: Session):
        org = _user(db, "par_org1")
        event = _active_event(db, org.id)
        usr = _user(db, "par_usr1")

        repo = ParticipantRepository(db)
        p = repo.create(Participant(user_id=usr.id, event_id=event.id))
        assert p.id is not None
        assert p.total_xp == 0

    def test_is_participant_true(self, db: Session):
        org = _user(db, "par_org2")
        event = _active_event(db, org.id)
        usr = _user(db, "par_usr2")
        ParticipantRepository(db).create(Participant(user_id=usr.id, event_id=event.id))

        repo = ParticipantRepository(db)
        assert repo.is_participant(usr.id, event.id) is True

    def test_is_participant_false(self, db: Session):
        org = _user(db, "par_org3")
        event = _active_event(db, org.id)
        usr = _user(db, "par_usr3")

        repo = ParticipantRepository(db)
        assert repo.is_participant(usr.id, event.id) is False

    def test_duplicate_join_raises(self, db: Session):
        org = _user(db, "par_org4")
        event = _active_event(db, org.id)
        usr = _user(db, "par_usr4")

        repo = ParticipantRepository(db)
        repo.create(Participant(user_id=usr.id, event_id=event.id))
        with pytest.raises(IntegrityError):
            repo.create(Participant(user_id=usr.id, event_id=event.id))

    def test_add_xp_atomic(self, db: Session):
        org = _user(db, "par_org5")
        event = _active_event(db, org.id)
        usr = _user(db, "par_usr5")

        repo = ParticipantRepository(db)
        p = repo.create(Participant(user_id=usr.id, event_id=event.id))
        assert p.total_xp == 0

        repo.add_xp(p, 100)
        db.refresh(p)
        assert p.total_xp == 100

        repo.add_xp(p, 50)
        db.refresh(p)
        assert p.total_xp == 150


# ── AntiFraud composite join validation ──────────────────────────────────────

class TestAntiFraudJoin:

    def test_valid_join_passes(self, db: Session):
        org = _user(db, "afj_org1")
        event = _active_event(db, org.id)
        usr = _user(db, "afj_usr1", days_old=40)

        ok, reason = AntiFraudService.validate_join(
            user=usr,
            organiser_id=event.organizer_id,
            event_id=event.id,
            db=db,
        )
        assert ok is True

    def test_young_account_blocked(self, db: Session):
        org = _user(db, "afj_org2")
        event = _active_event(db, org.id)
        usr = _user(db, "afj_usr2", days_old=5)

        ok, reason = AntiFraudService.validate_join(
            user=usr,
            organiser_id=event.organizer_id,
            event_id=event.id,
            db=db,
        )
        assert ok is False
        assert "young" in reason.lower()

    def test_organiser_blocked(self, db: Session):
        org = _user(db, "afj_org3", days_old=40)
        event = _active_event(db, org.id)

        ok, reason = AntiFraudService.validate_join(
            user=org,
            organiser_id=event.organizer_id,
            event_id=event.id,
            db=db,
        )
        assert ok is False
        assert "organiser" in reason.lower()

    def test_already_joined_blocked(self, db: Session):
        org = _user(db, "afj_org4")
        event = _active_event(db, org.id)
        usr = _user(db, "afj_usr4", days_old=40)
        ParticipantRepository(db).create(Participant(user_id=usr.id, event_id=event.id))

        ok, reason = AntiFraudService.validate_join(
            user=usr,
            organiser_id=event.organizer_id,
            event_id=event.id,
            db=db,
        )
        assert ok is False
        assert "joined" in reason.lower()
