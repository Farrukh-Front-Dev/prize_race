"""
scripts/finish_expired_events.py
──────────────────────────────────
Finish all ACTIVE events whose end_date has passed.

Run via cron / systemd timer / APScheduler every minute:
    python scripts/finish_expired_events.py

In production this should be a proper background job or Celery task.
"""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, init_db
from app.models.enums import EventStatus
from app.models.event import Event
from app.repositories.event_repository import EventRepository


def main() -> None:
    init_db()
    db = SessionLocal()
    repo = EventRepository(db)

    try:
        now = datetime.utcnow()
        expired = (
            db.query(Event)
            .filter(
                Event.status == EventStatus.ACTIVE,
                Event.end_date <= now,
            )
            .all()
        )

        if not expired:
            print("No expired events found.")
            return

        for event in expired:
            repo.finish(event)
            print(f"✅ Event {event.id} '{event.title}' → FINISHED (ended {event.end_date})")

        print(f"\nFinished {len(expired)} event(s).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
