"""
app/repositories/participant_repository.py
───────────────────────────────────────────
All DB queries related to Participant.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.participant import Participant
from app.repositories.base import BaseRepository


class ParticipantRepository(BaseRepository[Participant]):

    def __init__(self, db: Session) -> None:
        super().__init__(Participant, db)

    def get_participant(
        self, user_id: int, event_id: int
    ) -> Optional[Participant]:
        return (
            self.db.query(Participant)
            .filter(
                Participant.user_id == user_id,
                Participant.event_id == event_id,
            )
            .first()
        )

    def is_participant(self, user_id: int, event_id: int) -> bool:
        return self.get_participant(user_id, event_id) is not None

    def add_xp(self, participant: Participant, xp: int) -> Participant:
        """
        Atomically increment persisted XP using a SQL-level UPDATE.
        Avoids lost-update race when multiple sync workers run in parallel.
        """
        from sqlalchemy import update as sa_update
        self.db.execute(
            sa_update(Participant)
            .where(
                Participant.user_id == participant.user_id,
                Participant.event_id == participant.event_id,
            )
            .values(total_xp=Participant.total_xp + xp)
        )
        self.db.commit()
        self.db.refresh(participant)
        return participant
