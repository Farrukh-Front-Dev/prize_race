from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app.database import get_db
from app.models import Event, User, Participant, EventStatus
from app.schemas import EventResponse, EventCreate, EventUpdate, ParticipantResponse, LeaderboardEntry
from app.services.tarantool_service import get_leaderboard_service

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("/", response_model=EventResponse)
async def create_event(
    event_data: EventCreate,
    organizer_id: int,
    db: Session = Depends(get_db),
):
    """Create new sprint (event)"""
    organizer = db.query(User).filter(User.id == organizer_id).first()
    if not organizer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizer not found",
        )

    new_event = Event(
        organizer_id=organizer_id,
        **event_data.dict(),
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


@router.get("/", response_model=list[EventResponse])
async def list_events(
    status_filter: EventStatus = Query(None),
    db: Session = Depends(get_db),
):
    """List all events with optional status filter"""
    query = db.query(Event)
    if status_filter:
        query = query.filter(Event.status == status_filter)
    return query.all()


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get event details"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return event


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_update: EventUpdate,
    organizer_id: int,
    db: Session = Depends(get_db),
):
    """Update event (only in DRAFT status)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if event.organizer_id != organizer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizer can update event",
        )

    if event.status != EventStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update events in DRAFT status",
        )

    update_data = event_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return event


@router.post("/{event_id}/join", response_model=ParticipantResponse)
async def join_event(
    event_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Join event (with idempotency and conflict handling)
    
    SECURITY:
    - Anti-fraud checks
    - Account age verification
    - Duplicate prevention
    """
    from app.services.anti_fraud_service import AntiFraudService

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if event.status != EventStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is not active",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if organizer
    if event.organizer_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organizer cannot participate in their own event",
        )

    # Anti-fraud validation
    is_valid, reason = AntiFraudService.validate_user_for_event(
        user, event_id, db
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=reason,
        )

    try:
        participant = Participant(user_id=user_id, event_id=event_id)
        db.add(participant)
        db.commit()
        db.refresh(participant)
        return participant
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already joined this event",
        )


@router.get("/{event_id}/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard(
    event_id: int,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """
    Get event leaderboard (top participants by XP)
    
    PERFORMANCE NOTE:
    - Reads from Tarantool (in-memory) for O(log N) speed
    - Fetches user details from PostgreSQL
    - Supports up to 10,000+ participants without lag
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # Get leaderboard from Tarantool (fast)
    tarantool_service = get_leaderboard_service()
    tarantool_leaderboard = tarantool_service.get_leaderboard(
        event_id, limit=limit
    )

    if not tarantool_leaderboard:
        return []

    # Get user details from PostgreSQL
    user_ids = [uid for uid, _, _ in tarantool_leaderboard]
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    user_map = {u.id: u for u in users}

    # Build response
    leaderboard = [
        LeaderboardEntry(
            rank=rank,
            user_id=uid,
            username=user_map.get(uid).username if uid in user_map else None,
            total_xp=xp,
            wallet_address=user_map.get(uid).wallet_address
            if uid in user_map
            else None,
        )
        for uid, xp, rank in tarantool_leaderboard
    ]

    return leaderboard
