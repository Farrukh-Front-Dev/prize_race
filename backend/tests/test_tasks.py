"""
tests/test_tasks.py
────────────────────
Unit tests for TaskRepository and TaskCompletionRepository.
"""
from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models.enums import EventStatus, VerificationType
from app.models.event import Event
from app.models.participant import Participant
from app.models.task import Task
from app.models.task_completion import UserTaskCompletion
from app.repositories.event_repository import EventRepository
from app.repositories.participant_repository import ParticipantRepository
from app.repositories.task_repository import TaskCompletionRepository, TaskRepository
from app.repositories.user_repository import UserRepository


# ── fixtures ─────────────────────────────────────────────────────────────────

def _user(db, tid):
    return UserRepository(db).upsert(telegram_id=tid)


def _event(db, organiser_id):
    return EventRepository(db).create(Event(
        organizer_id=organiser_id,
        title="Sprint",
        total_prize_pool=10,
        top_n_winners=3,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=7),
    ))


def _task(db, event_id, xp=50, vtype=VerificationType.MANUAL):
    return TaskRepository(db).create(Task(
        event_id=event_id,
        title="Do something",
        xp_reward=xp,
        verification_type=vtype,
    ))


def _participate(db, user_id, event_id):
    return ParticipantRepository(db).create(
        Participant(user_id=user_id, event_id=event_id)
    )


# ── TaskRepository ────────────────────────────────────────────────────────────

class TestTaskRepository:

    def test_create_task(self, db: Session):
        org = _user(db, "tsk_org1")
        event = _event(db, org.id)
        task = _task(db, event.id)
        assert task.id is not None
        assert task.xp_reward == 50

    def test_list_by_event(self, db: Session):
        org = _user(db, "tsk_org2")
        event = _event(db, org.id)
        t1 = _task(db, event.id, xp=10)
        t2 = _task(db, event.id, xp=20)
        repo = TaskRepository(db)
        tasks = repo.list_by_event(event.id)
        ids = [t.id for t in tasks]
        assert t1.id in ids
        assert t2.id in ids

    def test_get_by_id_not_found(self, db: Session):
        repo = TaskRepository(db)
        assert repo.get_by_id(999999) is None

    def test_channel_subscription_task(self, db: Session):
        org = _user(db, "tsk_org3")
        event = _event(db, org.id)
        task = TaskRepository(db).create(Task(
            event_id=event.id,
            title="Subscribe",
            xp_reward=30,
            verification_type=VerificationType.CHANNEL_SUBSCRIPTION,
            required_channel="@test_channel",
        ))
        assert task.required_channel == "@test_channel"
        assert task.verification_type == VerificationType.CHANNEL_SUBSCRIPTION


# ── TaskCompletionRepository ──────────────────────────────────────────────────

class TestTaskCompletionRepository:

    def test_create_completion(self, db: Session):
        org = _user(db, "cmp_org1")
        user = _user(db, "cmp_usr1")
        event = _event(db, org.id)
        task = _task(db, event.id)
        _participate(db, user.id, event.id)

        repo = TaskCompletionRepository(db)
        comp = repo.create(UserTaskCompletion(
            user_id=user.id,
            task_id=task.id,
            verified=True,
        ))
        assert comp.id is not None
        assert comp.verified is True

    def test_get_completion(self, db: Session):
        org = _user(db, "cmp_org2")
        user = _user(db, "cmp_usr2")
        event = _event(db, org.id)
        task = _task(db, event.id)
        _participate(db, user.id, event.id)

        repo = TaskCompletionRepository(db)
        repo.create(UserTaskCompletion(user_id=user.id, task_id=task.id, verified=True))
        found = repo.get_completion(user.id, task.id)
        assert found is not None
        assert found.user_id == user.id

    def test_get_completion_not_found(self, db: Session):
        repo = TaskCompletionRepository(db)
        assert repo.get_completion(99999, 99999) is None

    def test_count_recent_completions_zero(self, db: Session):
        org = _user(db, "cmp_org3")
        user = _user(db, "cmp_usr3")
        event = _event(db, org.id)
        repo = TaskCompletionRepository(db)
        count = repo.count_recent_completions(user.id, event.id)
        assert count == 0

    def test_count_recent_completions(self, db: Session):
        org = _user(db, "cmp_org4")
        user = _user(db, "cmp_usr4")
        event = _event(db, org.id)
        _participate(db, user.id, event.id)

        c_repo = TaskCompletionRepository(db)
        t_repo = TaskRepository(db)

        for i in range(3):
            task = t_repo.create(Task(
                event_id=event.id, title=f"T{i}", xp_reward=10,
                verification_type=VerificationType.MANUAL,
            ))
            c_repo.create(UserTaskCompletion(
                user_id=user.id, task_id=task.id, verified=True,
            ))

        count = c_repo.count_recent_completions(user.id, event.id, window_seconds=60)
        assert count == 3

    def test_duplicate_completion_raises(self, db: Session):
        from sqlalchemy.exc import IntegrityError
        org = _user(db, "cmp_org5")
        user = _user(db, "cmp_usr5")
        event = _event(db, org.id)
        task = _task(db, event.id)
        _participate(db, user.id, event.id)

        repo = TaskCompletionRepository(db)
        repo.create(UserTaskCompletion(user_id=user.id, task_id=task.id, verified=True))
        with pytest.raises(IntegrityError):
            repo.create(UserTaskCompletion(user_id=user.id, task_id=task.id, verified=True))
