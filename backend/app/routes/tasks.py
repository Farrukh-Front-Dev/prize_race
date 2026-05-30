from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models import Task, Event, User, UserTaskCompletion, Participant
from app.schemas import TaskResponse, TaskCreate, TaskCompletionResponse
from app.services.tarantool_service import get_leaderboard_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    event_id: int,
    organizer_id: int,
    db: Session = Depends(get_db),
):
    """Create task for event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if event.organizer_id != organizer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizer can create tasks",
        )

    new_task = Task(event_id=event_id, **task_data.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get task details"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.post("/{task_id}/verify", response_model=TaskCompletionResponse)
async def verify_task(
    task_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Verify task completion
    
    FLOW:
    1. Validate task and user
    2. Create completion record in PostgreSQL
    3. Add XP to Tarantool (real-time)
    4. Queue for PostgreSQL sync (batch)
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if user is participant in event
    participant = (
        db.query(Participant)
        .filter(
            Participant.user_id == user_id,
            Participant.event_id == task.event_id,
        )
        .first()
    )
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not participant in this event",
        )

    try:
        # Check if task already completed
        existing = (
            db.query(UserTaskCompletion)
            .filter(
                UserTaskCompletion.user_id == user_id,
                UserTaskCompletion.task_id == task_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task already completed by user",
            )

        # Create completion record
        completion = UserTaskCompletion(
            user_id=user_id,
            task_id=task_id,
            verified=True,
        )
        db.add(completion)
        db.commit()

        # Add XP to Tarantool (real-time, non-blocking)
        tarantool_service = get_leaderboard_service()
        tarantool_service.add_xp(
            task.event_id,
            user_id,
            task.xp_reward,
        )

        db.refresh(completion)
        return completion

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already completed",
        )
