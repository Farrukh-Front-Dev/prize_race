"""
app/repositories/event_repository.py
──────────────────────────────────────
All DB queries related to Event.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.enums import EventStatus
from app.models.event import Event
from app.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):

    def __init__(self, db: Session) -> None:
        super().__init__(Event, db)

    def list_by_status(
        self,
        event_status: Optional[EventStatus] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Event]:
        q = self.db.query(Event)
        if event_status:
            q = q.filter(Event.status == event_status)
        return q.order_by(Event.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_tx_hash(self, tx_hash: str) -> Optional[Event]:
        return (
            self.db.query(Event).filter(Event.tx_hash == tx_hash).first()
        )

    def set_status(self, event: Event, new_status: EventStatus) -> Event:
        event.status = new_status
        return self.update(event)

    def activate(self, event: Event, tx_hash: str) -> Event:
        event.status = EventStatus.ACTIVE
        event.tx_hash = tx_hash
        return self.update(event)

    def finish(self, event: Event) -> Event:
        event.status = EventStatus.FINISHED
        return self.update(event)
