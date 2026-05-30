"""
PostgreSQL Sync Service
Batch sync from Tarantool to PostgreSQL for persistence
"""

import asyncio
import logging
from sqlalchemy.orm import Session
from app.models import Participant
from app.services.tarantool_service import get_leaderboard_service

logger = logging.getLogger(__name__)


class PostgresSyncService:
    """
    Batch sync service for persisting Tarantool data to PostgreSQL.
    
    Strategy:
    - Tarantool handles real-time updates (fast)
    - PostgreSQL gets batch updates (efficient)
    - Reduces database load by 90%+
    """

    def __init__(self, db: Session):
        self.db = db
        self.tarantool = get_leaderboard_service()

    async def sync_pending_xp(self, batch_size: int = 100):
        """
        Sync pending XP changes from Tarantool to PostgreSQL
        
        Args:
            batch_size: Number of records to sync per batch
        """
        try:
            pending = self.tarantool.get_pending_syncs(limit=batch_size)

            if not pending:
                logger.debug("No pending syncs")
                return

            logger.info(f"Syncing {len(pending)} records to PostgreSQL")

            for sync_record in pending:
                sync_id, event_id, user_id, xp_delta, status = sync_record

                try:
                    # Find participant
                    participant = (
                        self.db.query(Participant)
                        .filter(
                            Participant.user_id == user_id,
                            Participant.event_id == event_id,
                        )
                        .first()
                    )

                    if participant:
                        # Update XP
                        participant.total_xp += xp_delta
                        self.db.commit()

                        # Mark as synced
                        self.tarantool.mark_sync_done(sync_id)
                        logger.debug(
                            f"Synced XP for user {user_id} in event {event_id}"
                        )
                    else:
                        logger.warning(
                            f"Participant not found: user {user_id}, event {event_id}"
                        )

                except Exception as e:
                    logger.error(f"Error syncing record {sync_id}: {e}")
                    self.db.rollback()

        except Exception as e:
            logger.error(f"Error in sync_pending_xp: {e}")

    async def start_sync_worker(self, interval_seconds: int = 5):
        """
        Start background worker for continuous sync
        
        Args:
            interval_seconds: Sync interval
        """
        logger.info(f"Starting PostgreSQL sync worker (interval: {interval_seconds}s)")

        while True:
            try:
                await self.sync_pending_xp()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in sync worker: {e}")
                await asyncio.sleep(interval_seconds)
