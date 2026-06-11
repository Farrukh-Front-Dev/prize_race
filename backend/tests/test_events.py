"""
tests/test_events.py
─────────────────────
Unit tests for EventRepository and EventService logic.
"""
from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models.enums import EventStatus
from app.models.event import Event
from app.models.user import User
from app.repositories.event_repository import EventRepository
from app.repositories.user_repository import UserRepository


def _create_organiser(db: Session, telegram_id: str = "org1") -> User:
    repo = UserRepository(db)
    return repo.upsert(telegram_id=telegram_id, username="organiser")


def _create_event(db: Session, organiser: User) -> Event:
    repo = EventRepository(db)
    return repo.create(Event(
        organizer_id=organiser.id,
        title="Test Sprint",
        total_prize_pool=10.0,
        top_n_winners=3,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=7),
    ))


class TestEventRepository:

    def test_create_event(self, db: Session):
        org = _create_organiser(db, "ev_org1")
        event = _create_event(db, org)
        assert event.id is not None
        assert event.status == EventStatus.DRAFT

    def test_list_by_status(self, db: Session):
        org = _create_organiser(db, "ev_org2")
        event = _create_event(db, org)
        repo = EventRepository(db)

        drafts = repo.list_by_status(EventStatus.DRAFT)
        assert any(e.id == event.id for e in drafts)

        actives = repo.list_by_status(EventStatus.ACTIVE)
        assert not any(e.id == event.id for e in actives)

    def test_set_status(self, db: Session):
        org = _create_organiser(db, "ev_org3")
        event = _create_event(db, org)
        repo = EventRepository(db)

        updated = repo.set_status(event, EventStatus.PENDING_PAYMENT)
        assert updated.status == EventStatus.PENDING_PAYMENT

    def test_activate(self, db: Session):
        org = _create_organiser(db, "ev_org4")
        event = _create_event(db, org)
        repo = EventRepository(db)
        repo.set_status(event, EventStatus.PENDING_PAYMENT)

        activated = repo.activate(event, tx_hash="abc123" * 11)
        assert activated.status == EventStatus.ACTIVE
        assert activated.tx_hash is not None

    def test_get_by_tx_hash(self, db: Session):
        org = _create_organiser(db, "ev_org5")
        event = _create_event(db, org)
        repo = EventRepository(db)
        repo.set_status(event, EventStatus.PENDING_PAYMENT)
        tx = "x" * 64
        repo.activate(event, tx_hash=tx)

        found = repo.get_by_tx_hash(tx)
        assert found is not None
        assert found.id == event.id

    def test_finish(self, db: Session):
        org = _create_organiser(db, "ev_org6")
        event = _create_event(db, org)
        repo = EventRepository(db)
        finished = repo.finish(event)
        assert finished.status == EventStatus.FINISHED
