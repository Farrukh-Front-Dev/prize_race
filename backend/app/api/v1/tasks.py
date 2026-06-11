"""
app/api/v1/tasks.py
────────────────────
Task CRUD and verification endpoints.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.enums import EventStatus, VerificationType
from app.models.task import Task
from app.models.task_completion import UserTaskCompletion
from app.models.user import User
from app.repositories.event_repository import EventRepository
from app.repositories.participant_repository import ParticipantRepository
from app.repositories.task_repository import TaskCompletionRepository, TaskRepository
from app.schemas.task import TaskCreate, TaskResponse
from app.schemas.task_completion import TaskCompletionResponse
from app.services.anti_fraud import AntiFraudService
from app.services.channel_service import get_channel_service
from app.services.leaderboard_service import get_leaderboard_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _require_task(task_id: int, db: Session) -> Task:
    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    return task


def _require_event(event_id: int, db: Session):
    repo = EventRepository(db)
    event = repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")
    return event


# ── Create ────────────────────────────────────────────────────────────────────

@router.post(
    "/event/{event_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create task for an event (organiser only, DRAFT)",
)
async def create_task(
    body: TaskCreate,
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = _require_event(event_id, db)

    if event.organizer_id != current_user.id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Only the organiser can create tasks",
        )
    if event.status != EventStatus.DRAFT:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Tasks can only be added while event is in DRAFT status",
        )

    repo = TaskRepository(db)
    task = repo.create(Task(event_id=event_id, **body.model_dump()))
    logger.info("Task %d created for event %d", task.id, event_id)
    return task


# ── List ──────────────────────────────────────────────────────────────────────

@router.get(
    "/event/{event_id}",
    response_model=list[TaskResponse],
    summary="List all tasks for an event",
)
async def list_event_tasks(
    event_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_event(event_id, db)
    repo = TaskRepository(db)
    return repo.list_by_event(event_id)


# ── Detail ────────────────────────────────────────────────────────────────────

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task details",
)
async def get_task(
    task_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _require_task(task_id, db)


# ── Verify ────────────────────────────────────────────────────────────────────

@router.post(
    "/{task_id}/verify",
    response_model=TaskCompletionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Verify task completion — award XP",
)
async def verify_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verification flow:
      1. Task and event exist, event is ACTIVE
      2. User is a confirmed participant
      3. Anti-fraud rate check
      4. Channel subscription check (if required)
      5. Insert completion — DB UNIQUE constraint is the final guard
      6. Award XP in Tarantool (non-blocking)
    """
    task = _require_task(task_id, db)
    event = _require_event(task.event_id, db)

    if event.status != EventStatus.ACTIVE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Event is not active")

    # ── Participant check ─────────────────────────────────────────────────
    p_repo = ParticipantRepository(db)
    if not p_repo.is_participant(current_user.id, task.event_id):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "You are not a participant in this event",
        )

    # ── Anti-fraud ────────────────────────────────────────────────────────
    ok, reason = AntiFraudService.validate_task_completion(
        user=current_user, event_id=task.event_id, db=db
    )
    if not ok:
        raise HTTPException(status.HTTP_403_FORBIDDEN, reason)

    # ── Channel subscription ──────────────────────────────────────────────
    if task.verification_type == VerificationType.CHANNEL_SUBSCRIPTION:
        if not task.required_channel:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Task misconfiguration: missing required_channel",
            )
        try:
            tg_user_id = int(current_user.telegram_id)
        except (ValueError, TypeError):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Invalid Telegram user ID format",
            )
        svc = get_channel_service()
        if not await svc.is_subscribed(tg_user_id, task.required_channel):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Subscribe to {task.required_channel} to complete this task",
            )

    # ── Persist completion ────────────────────────────────────────────────
    c_repo = TaskCompletionRepository(db)
    try:
        completion = c_repo.create(
            UserTaskCompletion(
                user_id=current_user.id,
                task_id=task_id,
                verified=True,
            )
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Task already completed")

    # ── Award XP (Tarantool, non-blocking) ───────────────────────────────
    lb = get_leaderboard_service()
    if not lb.add_xp(task.event_id, current_user.id, task.xp_reward):
        logger.warning(
            "Tarantool XP award failed user=%d task=%d — sync will retry",
            current_user.id, task_id,
        )

    logger.info(
        "Task %d verified user=%d +%d XP", task_id, current_user.id, task.xp_reward
    )
    return completion
