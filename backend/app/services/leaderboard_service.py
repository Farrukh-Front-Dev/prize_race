"""
app/services/leaderboard_service.py
─────────────────────────────────────
High-performance in-memory leaderboard backed by Tarantool.

Space layout (created once via box.once in bootstrap_tarantool_spaces):
  leaderboard : [event_id uint, user_id uint, xp uint, updated_at uint]
    primary   : HASH  (event_id, user_id)
    xp_rank   : TREE  (event_id, xp) non-unique  ← sorted scans

  locks       : [lock_key str, expires_at uint]
    primary   : HASH  (lock_key)

  sync_queue  : [id uint/auto, event_id uint, user_id uint,
                 xp_delta uint, status str]
    primary   : HASH  (id)
    by_status : TREE  (status) non-unique
"""
import logging
import time
from typing import List, Optional, Tuple

import tarantool

from app.core.database import get_tarantool

logger = logging.getLogger(__name__)

_LB = "leaderboard"
_LK = "locks"
_SQ = "sync_queue"

# ── Tarantool space bootstrap (idempotent via box.once) ───────────────────────

_BOOTSTRAP_LUA = """
box.once('prize_race_v1', function()
    local lb = box.schema.space.create('leaderboard', {if_not_exists=true})
    lb:format({
        {name='event_id',   type='unsigned'},
        {name='user_id',    type='unsigned'},
        {name='xp',         type='unsigned'},
        {name='updated_at', type='unsigned'},
    })
    lb:create_index('primary', {type='hash',
        parts={'event_id','user_id'}, if_not_exists=true})
    lb:create_index('xp_rank', {type='tree',
        parts={'event_id','xp'}, unique=false, if_not_exists=true})

    local lk = box.schema.space.create('locks', {if_not_exists=true})
    lk:format({
        {name='lock_key',   type='string'},
        {name='expires_at', type='unsigned'},
    })
    lk:create_index('primary', {type='hash',
        parts={'lock_key'}, if_not_exists=true})

    local sq = box.schema.space.create('sync_queue', {if_not_exists=true})
    sq:format({
        {name='id',       type='unsigned'},
        {name='event_id', type='unsigned'},
        {name='user_id',  type='unsigned'},
        {name='xp_delta', type='unsigned'},
        {name='status',   type='string'},
    })
    sq:create_index('primary', {type='hash',
        parts={'id'}, sequence=true, if_not_exists=true})
    sq:create_index('by_status', {type='tree',
        parts={'status'}, unique=false, if_not_exists=true})
end)
"""


def bootstrap_tarantool_spaces() -> None:
    """Create Tarantool spaces once (safe to call on every startup)."""
    conn = get_tarantool()
    if conn is None:
        logger.error("bootstrap_tarantool_spaces: no connection available.")
        return
    try:
        conn.eval(_BOOTSTRAP_LUA)
        logger.info("Tarantool spaces bootstrapped.")
    except Exception as exc:
        logger.error("Tarantool bootstrap error: %s", exc)


# ── Service ───────────────────────────────────────────────────────────────────

class LeaderboardService:
    """All leaderboard operations against Tarantool."""

    @staticmethod
    def _conn() -> Optional[tarantool.Connection]:
        return get_tarantool()

    # ── XP ────────────────────────────────────────────────────────────────

    def add_xp(self, event_id: int, user_id: int, xp: int) -> bool:
        """
        Atomically upsert XP for (event_id, user_id).
        Uses Tarantool UPSERT: insert-or-increment.
        """
        conn = self._conn()
        if conn is None:
            logger.error("add_xp: no Tarantool connection")
            return False
        try:
            now = int(time.time())
            conn.upsert(
                _LB,
                (event_id, user_id, xp, now),
                [("+", 2, xp), ("=", 3, now)],   # field indices 0-based
            )
            self._enqueue(event_id, user_id, xp)
            return True
        except Exception as exc:
            logger.error("add_xp error: %s", exc)
            return False

    def get_user_xp(self, event_id: int, user_id: int) -> int:
        conn = self._conn()
        if conn is None:
            return 0
        try:
            rows = conn.select(_LB, (event_id, user_id))
            return int(rows[0][2]) if rows else 0
        except Exception as exc:
            logger.error("get_user_xp error: %s", exc)
            return 0

    # ── Leaderboard ───────────────────────────────────────────────────────

    def get_leaderboard(
        self,
        event_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Tuple[int, int, int]]:
        """
        Return [(user_id, xp, rank), ...] sorted by XP descending.
        Fetches all rows for the event from Tarantool (in-memory →
        fast even at 10k+ participants) then sorts in Python.
        """
        conn = self._conn()
        if conn is None:
            return []
        try:
            rows = conn.select(
                _LB,
                (event_id, 0),
                index="xp_rank",
                limit=65535,
                iterator=tarantool.IteratorType.GE,
            )
            event_rows = sorted(
                [r for r in rows if r[0] == event_id],
                key=lambda r: r[2],
                reverse=True,
            )
            page = event_rows[offset: offset + limit]
            return [
                (int(r[1]), int(r[2]), offset + i + 1)
                for i, r in enumerate(page)
            ]
        except Exception as exc:
            logger.error("get_leaderboard error: %s", exc)
            return []

    def get_user_rank(self, event_id: int, user_id: int) -> Optional[int]:
        conn = self._conn()
        if conn is None:
            return None
        try:
            rows = conn.select(
                _LB, (event_id, 0),
                index="xp_rank", limit=65535,
                iterator=tarantool.IteratorType.GE,
            )
            sorted_rows = sorted(
                [r for r in rows if r[0] == event_id],
                key=lambda r: r[2], reverse=True,
            )
            for rank, r in enumerate(sorted_rows, 1):
                if r[1] == user_id:
                    return rank
            return None
        except Exception as exc:
            logger.error("get_user_rank error: %s", exc)
            return None

    def get_top_winners(
        self, event_id: int, top_n: int
    ) -> List[Tuple[int, int]]:
        """Return [(user_id, xp), ...] for top N — used by oracle."""
        lb = self.get_leaderboard(event_id, limit=top_n)
        return [(uid, xp) for uid, xp, _ in lb]

    def reset(self, event_id: int) -> bool:
        """Delete all leaderboard entries for an event (admin)."""
        conn = self._conn()
        if conn is None:
            return False
        try:
            rows = conn.select(
                _LB, (event_id, 0),
                index="xp_rank", limit=65535,
                iterator=tarantool.IteratorType.GE,
            )
            for r in rows:
                if r[0] == event_id:
                    conn.delete(_LB, (r[0], r[1]))
            return True
        except Exception as exc:
            logger.error("reset error: %s", exc)
            return False

    # ── Sync queue ────────────────────────────────────────────────────────

    def _enqueue(self, event_id: int, user_id: int, xp_delta: int) -> None:
        conn = self._conn()
        if conn is None:
            return
        try:
            conn.insert(_SQ, (0, event_id, user_id, xp_delta, "pending"))
        except Exception as exc:
            logger.error("_enqueue error: %s", exc)

    def get_pending_syncs(self, limit: int = 100) -> list:
        conn = self._conn()
        if conn is None:
            return []
        try:
            return list(
                conn.select(_SQ, ("pending",), index="by_status", limit=limit)
            )
        except Exception as exc:
            logger.error("get_pending_syncs error: %s", exc)
            return []

    def mark_sync_done(self, sync_id: int) -> None:
        conn = self._conn()
        if conn is None:
            return
        try:
            conn.update(_SQ, (sync_id,), [("=", 4, "completed")])
        except Exception as exc:
            logger.error("mark_sync_done error: %s", exc)


# ── Singleton ─────────────────────────────────────────────────────────────────

_instance: Optional[LeaderboardService] = None


def get_leaderboard_service() -> LeaderboardService:
    global _instance
    if _instance is None:
        _instance = LeaderboardService()
    return _instance
