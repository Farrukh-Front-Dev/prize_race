"""
scripts/seed_dev_data.py
─────────────────────────
Populate the database with minimal development/demo data.
Safe to run multiple times (idempotent).

Usage:
    python scripts/seed_dev_data.py
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, init_db
from app.models.enums import EventStatus
from app.models.event import Event
from app.models.task import Task
from app.repositories.user_repository import UserRepository
from app.repositories.event_repository import EventRepository
from app.repositories.task_repository import TaskRepository


def main() -> None:
    init_db()
    db = SessionLocal()

    try:
        u_repo = UserRepository(db)
        e_repo = EventRepository(db)
        t_repo = TaskRepository(db)

        # Organiser
        org = u_repo.upsert(
            telegram_id="100000001",
            username="organiser_dev",
            first_name="Dev Organiser",
        )
        print(f"Organiser: id={org.id} telegram_id={org.telegram_id}")

        # Participant
        p1 = u_repo.upsert(
            telegram_id="100000002",
            username="participant_dev",
            first_name="Dev Participant",
        )
        print(f"Participant: id={p1.id} telegram_id={p1.telegram_id}")

        # Event in DRAFT
        existing = e_repo.list_by_status(EventStatus.DRAFT, limit=1)
        if not existing:
            event = e_repo.create(Event(
                organizer_id=org.id,
                title="Dev Sprint #1",
                description="Seeded development sprint",
                total_prize_pool=100.0,
                top_n_winners=3,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=7),
            ))
            print(f"Event: id={event.id} title={event.title} status={event.status}")

            # Tasks
            for i, (title, xp, vtype) in enumerate([
                ("Follow @channel", 50, "channel_subscription"),
                ("Share post", 30, "manual"),
                ("Invite a friend", 100, "manual"),
            ], 1):
                task = t_repo.create(Task(
                    event_id=event.id,
                    title=title,
                    xp_reward=xp,
                    verification_type=vtype,
                    required_channel="@dev_channel" if vtype == "channel_subscription" else None,
                ))
                print(f"  Task {i}: id={task.id} title={task.title} xp={task.xp_reward}")
        else:
            print("DRAFT event already exists — skipping event seed")

        print("\n✅ Dev data seeded successfully")
    finally:
        db.close()


if __name__ == "__main__":
    main()
