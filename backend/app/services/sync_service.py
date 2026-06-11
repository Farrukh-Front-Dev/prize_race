"""
app/services/sync_service.py
──────────────────────────────
Background worker: drains Tarantool sync_queue → PostgreSQL.

Strategy:
  - Tarantool is the source of truth for XP during an active event
  - This worker persists XP deltas to Participant.total_xp in batches
  - Each record is committed independently to minimise rollback scope
  - Runs as an asyncio background task launched from app lifespan
"""
import asyncio
import logging

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.repositories.participant_repository import ParticipantRepository
from app.services.leaderboard_service import get_leaderboard_service

logger = logging.getLogger(__name__)
settings = get_settings()


def _process_batch() -> int:
    """Sync one batch synchronously (called via asyncio.to_thread)."""
    svc = get_leaderboard_service()
    pending = svc.get_pending_syncs(limit=settings.sync_batch_size)
    if not pending:
        return 0

    processed = 0
    db = SessionLocal()
    repo = ParticipantRepository(db)

    try:
        for record in pending:
            sync_id, event_id, user_id, xp_delta, _ = record
            try:
                participant = repo.get_participant(user_id, event_id)
                if participant:
                    repo.add_xp(participant, xp_delta)
                    svc.mark_sync_done(sync_id)
                    processed += 1
                else:
                    logger.warning(
                        "sync: participant not found user=%d event=%d",
                        user_id, event_id,
                    )
            except Exception as exc:
                db.rollback()
                logger.error("sync error on record %d: %s", sync_id, exc)
    finally:
        db.close()

    return processed


async def run_sync_worker() -> None:
    """Infinite async loop — launched as an asyncio.Task in app lifespan."""
    interval = settings.sync_interval_seconds
    logger.info("Sync worker started (interval=%ds, batch=%d)", interval, settings.sync_batch_size)

    while True:
        try:
            count = await asyncio.to_thread(_process_batch)
            if count:
                logger.debug("Synced %d XP records → PostgreSQL", count)
        except asyncio.CancelledError:
            logger.info("Sync worker cancelled.")
            raise
        except Exception as exc:
            logger.error("Sync worker unexpected error: %s", exc)
        await asyncio.sleep(interval)
