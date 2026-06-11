"""
app/api/v1/events.py
─────────────────────
Sprint lifecycle endpoints.

Status flow: DRAFT → PENDING_PAYMENT → ACTIVE → FINISHED
"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.enums import EventStatus
from app.models.event import Event
from app.models.participant import Participant
from app.models.user import User
from app.repositories.event_repository import EventRepository
from app.repositories.participant_repository import ParticipantRepository
from app.repositories.user_repository import UserRepository
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.schemas.participant import LeaderboardEntry, ParticipantResponse
from app.services.anti_fraud import AntiFraudService
from app.services.leaderboard_service import get_leaderboard_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["events"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _require_event(event_id: int, db: Session) -> Event:
    repo = EventRepository(db)
    event = repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")
    return event


def _require_organiser(event: Event, user_id: int) -> None:
    if event.organizer_id != user_id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Only the organiser can perform this action",
        )


# ── Create ────────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new sprint",
)
async def create_event(
    body: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = EventRepository(db)
    event = Event(organizer_id=current_user.id, **body.model_dump())
    created = repo.create(event)
    logger.info("Event created id=%d organiser=%d", created.id, current_user.id)
    return created


# ── List ──────────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=list[EventResponse],
    summary="List events with optional status filter",
)
async def list_events(
    event_status: EventStatus = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = EventRepository(db)
    return repo.list_by_status(event_status, skip=skip, limit=limit)


# ── Detail ────────────────────────────────────────────────────────────────────

@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Get event details",
)
async def get_event(
    event_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _require_event(event_id, db)


# ── Update ────────────────────────────────────────────────────────────────────

@router.put(
    "/{event_id}",
    response_model=EventResponse,
    summary="Update event (DRAFT status only)",
)
async def update_event(
    event_id: int,
    body: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = _require_event(event_id, db)
    _require_organiser(event, current_user.id)

    if event.status != EventStatus.DRAFT:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Event can only be updated in DRAFT status",
        )

    repo = EventRepository(db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    return repo.update(event)


# ── Lock (DRAFT → PENDING_PAYMENT) ───────────────────────────────────────────

@router.post(
    "/{event_id}/lock",
    response_model=EventResponse,
    summary="Lock event parameters and move to PENDING_PAYMENT",
)
async def lock_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = _require_event(event_id, db)
    _require_organiser(event, current_user.id)

    if event.status != EventStatus.DRAFT:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Cannot lock event with status {event.status}",
        )

    repo = EventRepository(db)
    updated = repo.set_status(event, EventStatus.PENDING_PAYMENT)
    logger.info("Event %d locked → PENDING_PAYMENT", event_id)
    return updated


# ── Join ──────────────────────────────────────────────────────────────────────

@router.post(
    "/{event_id}/join",
    response_model=ParticipantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Join an active event",
)
async def join_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = _require_event(event_id, db)

    if event.status != EventStatus.ACTIVE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Event is not active")

    valid, reason = AntiFraudService.validate_join(
        user=current_user,
        organiser_id=event.organizer_id,
        event_id=event_id,
        db=db,
    )
    if not valid:
        raise HTTPException(status.HTTP_403_FORBIDDEN, reason)

    try:
        p_repo = ParticipantRepository(db)
        participant = p_repo.create(
            Participant(user_id=current_user.id, event_id=event_id)
        )
        logger.info("User %d joined event %d", current_user.id, event_id)
        return participant
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Already joined this event"
        )


# ── Leaderboard ───────────────────────────────────────────────────────────────

@router.get(
    "/{event_id}/leaderboard",
    response_model=list[LeaderboardEntry],
    summary="Real-time leaderboard from Tarantool",
)
async def get_leaderboard(
    event_id: int,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_event(event_id, db)

    svc = get_leaderboard_service()
    raw = svc.get_leaderboard(event_id, limit=limit, offset=offset)
    if not raw:
        return []

    user_ids = [uid for uid, _, _ in raw]
    u_repo = UserRepository(db)
    user_map = {u.id: u for u in u_repo.get_many_by_ids(user_ids)}

    return [
        LeaderboardEntry(
            rank=rank,
            user_id=uid,
            username=user_map[uid].username if uid in user_map else None,
            total_xp=xp,
            wallet_address=user_map[uid].wallet_address if uid in user_map else None,
        )
        for uid, xp, rank in raw
    ]


# ── Finish (ACTIVE → FINISHED) ────────────────────────────────────────────────

@router.post(
    "/{event_id}/finish",
    response_model=EventResponse,
    summary="Manually finish an event (organiser) or auto-called when end_date passed",
)
async def finish_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Transitions event to FINISHED status.
    Only the organiser can call this, and only after end_date has passed.
    The Rust oracle should call this endpoint (or a background job) to
    trigger prize distribution.
    """
    event = _require_event(event_id, db)
    _require_organiser(event, current_user.id)

    if event.status != EventStatus.ACTIVE:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Cannot finish event with status {event.status}",
        )

    if datetime.utcnow() < event.end_date:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Event end date has not passed yet (ends {event.end_date.isoformat()})",
        )

    repo = EventRepository(db)
    finished = repo.finish(event)
    logger.info("Event %d finished → FINISHED", event_id)
    return finished


# ── Winners (top N after FINISHED) ───────────────────────────────────────────

@router.get(
    "/{event_id}/winners",
    response_model=list[LeaderboardEntry],
    summary="Get final top-N winners after event is FINISHED",
)
async def get_winners(
    event_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns the final sorted winners list.
    Only available when event status is FINISHED.
    Reads from Tarantool (in-memory) — still fast post-event.
    """
    event = _require_event(event_id, db)

    if event.status != EventStatus.FINISHED:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Winners are only available after the event is FINISHED",
        )

    svc = get_leaderboard_service()
    raw = svc.get_leaderboard(event_id, limit=event.top_n_winners)
    if not raw:
        return []

    user_ids = [uid for uid, _, _ in raw]
    u_repo = UserRepository(db)
    user_map = {u.id: u for u in u_repo.get_many_by_ids(user_ids)}

    return [
        LeaderboardEntry(
            rank=rank,
            user_id=uid,
            username=user_map[uid].username if uid in user_map else None,
            total_xp=xp,
            wallet_address=user_map[uid].wallet_address if uid in user_map else None,
        )
        for uid, xp, rank in raw
    ]
