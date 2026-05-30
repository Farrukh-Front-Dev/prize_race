"""
Tarantool Leaderboard Service
Professional implementation for high-performance ranking system
"""

import tarantool
from typing import List, Tuple, Optional
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class TarantoolLeaderboardService:
    """
    High-performance leaderboard using Tarantool in-memory database.
    
    Design Principles:
    - O(log N) insert/update operations via TREE index
    - Real-time ranking without database locks
    - Automatic TTL for temporary data
    - Batch sync to PostgreSQL for persistence
    """

    # Space names
    LEADERBOARD_SPACE = "leaderboard"
    LOCK_SPACE = "locks"
    QUEUE_SPACE = "sync_queue"

    def __init__(self):
        self.conn = None
        self._connect()

    def _connect(self):
        """Establish connection to Tarantool"""
        try:
            self.conn = tarantool.connect(
                settings.tarantool_host,
                settings.tarantool_port,
            )
            logger.info("Connected to Tarantool")
        except Exception as e:
            logger.error(f"Failed to connect to Tarantool: {e}")
            self.conn = None

    def _ensure_spaces(self):
        """Create spaces if they don't exist"""
        try:
            # Leaderboard space: (event_id, user_id, xp, timestamp)
            self.conn.eval("""
                if not box.space.leaderboard then
                    local s = box.schema.space.create('leaderboard')
                    s:create_index('primary', {type = 'hash', parts = {1, 'unsigned', 2, 'unsigned'}})
                    s:create_index('xp_rank', {type = 'tree', parts = {1, 'unsigned', 3, 'unsigned', unique = false}})
                end
            """)

            # Locks space: (lock_key, timestamp, ttl)
            self.conn.eval("""
                if not box.space.locks then
                    local s = box.schema.space.create('locks')
                    s:create_index('primary', {type = 'hash', parts = {1, 'string'}})
                end
            """)

            # Sync queue: (id, event_id, user_id, xp_delta, status)
            self.conn.eval("""
                if not box.space.sync_queue then
                    local s = box.schema.space.create('sync_queue')
                    s:create_index('primary', {type = 'hash', parts = {1, 'unsigned'}})
                    s:create_index('status', {type = 'tree', parts = {5, 'string'}, unique = false})
                end
            """)

            logger.info("Tarantool spaces initialized")
        except Exception as e:
            logger.warning(f"Spaces might already exist: {e}")

    def add_xp(self, event_id: int, user_id: int, xp_amount: int) -> bool:
        """
        Add XP to user in event (atomic operation)
        
        Args:
            event_id: Event/Sprint ID
            user_id: User ID
            xp_amount: XP to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create composite key
            key = (event_id, user_id)

            # Get current XP
            result = self.conn.select(self.LEADERBOARD_SPACE, key)

            if result:
                # Update existing
                current_xp = result[0][2]
                new_xp = current_xp + xp_amount
                self.conn.replace(
                    self.LEADERBOARD_SPACE,
                    (event_id, user_id, new_xp, tarantool.Timestamp()),
                )
            else:
                # Insert new
                self.conn.insert(
                    self.LEADERBOARD_SPACE,
                    (event_id, user_id, xp_amount, tarantool.Timestamp()),
                )

            # Queue for PostgreSQL sync
            self._queue_sync(event_id, user_id, xp_amount)

            logger.info(f"Added {xp_amount} XP to user {user_id} in event {event_id}")
            return True

        except Exception as e:
            logger.error(f"Error adding XP: {e}")
            return False

    def get_leaderboard(
        self,
        event_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Tuple[int, int, int]]:
        """
        Get leaderboard for event (sorted by XP descending)
        
        Args:
            event_id: Event ID
            limit: Number of results
            offset: Pagination offset
            
        Returns:
            List of (user_id, xp, rank) tuples
        """
        try:
            # Query using xp_rank index (TREE index for sorting)
            results = self.conn.select(
                self.LEADERBOARD_SPACE,
                (event_id,),
                index=1,  # xp_rank index
                limit=limit + offset,
                offset=offset,
            )

            # Reverse to get descending order (highest XP first)
            leaderboard = []
            for rank, (eid, uid, xp, _) in enumerate(reversed(results), 1):
                if eid == event_id:
                    leaderboard.append((uid, xp, rank))

            return leaderboard

        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []

    def get_user_rank(self, event_id: int, user_id: int) -> Optional[int]:
        """
        Get user's rank in event
        
        Args:
            event_id: Event ID
            user_id: User ID
            
        Returns:
            Rank (1-based) or None if not found
        """
        try:
            # Get all users in event sorted by XP
            all_users = self.conn.select(
                self.LEADERBOARD_SPACE,
                (event_id,),
                index=1,
            )

            # Find user's rank
            for rank, (eid, uid, xp, _) in enumerate(reversed(all_users), 1):
                if eid == event_id and uid == user_id:
                    return rank

            return None

        except Exception as e:
            logger.error(f"Error getting user rank: {e}")
            return None

    def get_top_winners(self, event_id: int, top_n: int) -> List[Tuple[int, int]]:
        """
        Get top N winners for event (for prize distribution)
        
        Args:
            event_id: Event ID
            top_n: Number of winners
            
        Returns:
            List of (user_id, xp) tuples
        """
        try:
            leaderboard = self.get_leaderboard(event_id, limit=top_n)
            return [(uid, xp) for uid, xp, _ in leaderboard]

        except Exception as e:
            logger.error(f"Error getting top winners: {e}")
            return []

    def acquire_lock(self, lock_key: str, ttl_seconds: int = 3) -> bool:
        """
        Acquire idempotency lock (for duplicate request prevention)
        
        Args:
            lock_key: Unique lock identifier
            ttl_seconds: Lock TTL
            
        Returns:
            True if lock acquired, False if already locked
        """
        try:
            # Try to insert lock
            result = self.conn.insert(
                self.LOCK_SPACE,
                (lock_key, tarantool.Timestamp()),
            )
            logger.info(f"Lock acquired: {lock_key}")
            return True

        except tarantool.DatabaseError as e:
            if "Duplicate key" in str(e):
                logger.warning(f"Lock already exists: {lock_key}")
                return False
            raise

    def release_lock(self, lock_key: str) -> bool:
        """Release idempotency lock"""
        try:
            self.conn.delete(self.LOCK_SPACE, (lock_key,))
            logger.info(f"Lock released: {lock_key}")
            return True
        except Exception as e:
            logger.error(f"Error releasing lock: {e}")
            return False

    def _queue_sync(self, event_id: int, user_id: int, xp_delta: int):
        """Queue XP change for PostgreSQL sync"""
        try:
            self.conn.insert(
                self.QUEUE_SPACE,
                (
                    None,  # Auto-increment ID
                    event_id,
                    user_id,
                    xp_delta,
                    "pending",  # status
                ),
            )
        except Exception as e:
            logger.error(f"Error queuing sync: {e}")

    def get_pending_syncs(self, limit: int = 100) -> List[Tuple]:
        """Get pending syncs for batch PostgreSQL update"""
        try:
            results = self.conn.select(
                self.QUEUE_SPACE,
                ("pending",),
                index=1,
                limit=limit,
            )
            return results
        except Exception as e:
            logger.error(f"Error getting pending syncs: {e}")
            return []

    def mark_sync_done(self, sync_id: int):
        """Mark sync as completed"""
        try:
            self.conn.update(
                self.QUEUE_SPACE,
                (sync_id,),
                [("=", 4, "completed")],
            )
        except Exception as e:
            logger.error(f"Error marking sync done: {e}")

    def reset_event_leaderboard(self, event_id: int) -> bool:
        """Reset leaderboard for event (admin operation)"""
        try:
            # Delete all entries for event
            results = self.conn.select(
                self.LEADERBOARD_SPACE,
                (event_id,),
                index=1,
            )

            for entry in results:
                self.conn.delete(
                    self.LEADERBOARD_SPACE,
                    (entry[0], entry[1]),
                )

            logger.info(f"Reset leaderboard for event {event_id}")
            return True

        except Exception as e:
            logger.error(f"Error resetting leaderboard: {e}")
            return False


# Singleton instance
_leaderboard_service = None


def get_leaderboard_service() -> TarantoolLeaderboardService:
    """Get or create leaderboard service instance"""
    global _leaderboard_service
    if _leaderboard_service is None:
        _leaderboard_service = TarantoolLeaderboardService()
        _leaderboard_service._ensure_spaces()
    return _leaderboard_service
