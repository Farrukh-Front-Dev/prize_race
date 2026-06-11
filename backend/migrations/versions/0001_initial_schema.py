"""Initial schema — all tables

Revision ID: 0001
Revises:
Create Date: 2026-06-10
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ──────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.String(50), nullable=False),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("first_name", sa.String(255), nullable=True),
        sa.Column("last_name", sa.String(255), nullable=True),
        sa.Column("wallet_address", sa.String(255), nullable=True),
        sa.Column("telegram_created_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False,
                  server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)

    # ── events ─────────────────────────────────────────────────────────────
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organizer_id", sa.Integer(),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.Enum(
            "DRAFT", "PENDING_PAYMENT", "ACTIVE", "FINISHED",
            name="eventstatus"
        ), nullable=False, server_default="DRAFT"),
        sa.Column("top_n_winners", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("total_prize_pool", sa.Numeric(precision=18, scale=9), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=False),
        sa.Column("tx_hash", sa.String(255), nullable=True, unique=True),
        sa.Column("created_at", sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_events_id", "events", ["id"])
    op.create_index("ix_events_organizer_id", "events", ["organizer_id"])
    op.create_index("ix_events_status", "events", ["status"])

    # ── tasks ──────────────────────────────────────────────────────────────
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(),
                  sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("xp_reward", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("verification_type", sa.Enum(
            "manual", "channel_subscription",
            name="verificationtype"
        ), nullable=False, server_default="manual"),
        sa.Column("required_channel", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index("ix_tasks_id", "tasks", ["id"])
    op.create_index("ix_tasks_event_id", "tasks", ["event_id"])

    # ── participants ────────────────────────────────────────────────────────
    op.create_table(
        "participants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_id", sa.Integer(),
                  sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("total_xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("joined_at", sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "event_id", name="uq_participant_user_event"),
    )
    op.create_index("ix_participants_id", "participants", ["id"])
    op.create_index("idx_participant_event_user", "participants", ["event_id", "user_id"])

    # ── user_task_completions ───────────────────────────────────────────────
    op.create_table(
        "user_task_completions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("task_id", sa.Integer(),
                  sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.UniqueConstraint("user_id", "task_id", name="uq_completion_user_task"),
    )
    op.create_index("ix_user_task_completions_id", "user_task_completions", ["id"])
    op.create_index("idx_completion_task_user", "user_task_completions", ["task_id", "user_id"])


def downgrade() -> None:
    op.drop_table("user_task_completions")
    op.drop_table("participants")
    op.drop_table("tasks")
    op.drop_table("events")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS eventstatus")
    op.execute("DROP TYPE IF EXISTS verificationtype")
