"""
Agent Task Models - SQLModel definitions for persistent agent task storage.

Design Principles:
- All task state is persisted to SQLite
- Tasks survive server restarts
- Progress is tracked and queryable
- Full audit trail via events table
- Idempotency via unique key constraint
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import field_validator
from sqlalchemy import Column, Index, text
from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel


def _utc_now() -> datetime:
    """Return current UTC time."""
    return datetime.now(timezone.utc)


def _generate_task_id() -> str:
    """Generate a time-sortable UUID v7-style ID.

    Format: timestamp_hex (8 chars) + random (8 chars) = 16 char ID
    This ensures tasks are naturally sorted by creation time.
    """
    import time
    import secrets

    # Milliseconds since epoch (fits in 48 bits = 12 hex chars, we use 8)
    ts_ms = int(time.time() * 1000)
    ts_hex = format(ts_ms, 'x')[-8:].zfill(8)  # Last 8 hex chars

    # Random component
    rand_hex = secrets.token_hex(4)  # 8 hex chars

    return f"{ts_hex}{rand_hex}"


class AgentTaskStatus(str, Enum):
    """Task execution status with clear semantics.

    State transitions:
    - PENDING → RUNNING (worker claims task)
    - RUNNING → COMPLETED (success)
    - RUNNING → FAILED (non-retryable error)
    - RUNNING → RETRYING (retryable error, will retry)
    - RETRYING → RUNNING (retry attempt starts)
    - RETRYING → FAILED (max retries exceeded)
    - PENDING/RUNNING → CANCELLED (user cancellation)
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

    @classmethod
    def terminal_statuses(cls) -> set["AgentTaskStatus"]:
        """Statuses that indicate task completion (no more work)."""
        return {cls.COMPLETED, cls.FAILED, cls.CANCELLED}

    @classmethod
    def active_statuses(cls) -> set["AgentTaskStatus"]:
        """Statuses that indicate task is in-flight."""
        return {cls.PENDING, cls.RUNNING, cls.RETRYING}


class AgentType(str, Enum):
    """Types of AI agents available."""
    RESEARCH = "research"
    DATA_ANALYST = "data_analyst"
    EMAIL_DRAFT = "email_draft"
    CONTENT_REPURPOSE = "content_repurpose"
    PROOFREADING = "proofreading"
    REPORT_ANALYST = "report_analyst"


class AgentTaskModel(SQLModel, table=True):
    """
    Persistent model for agent tasks.

    Invariants:
    - task_id is unique and immutable
    - idempotency_key is unique when not null
    - progress_percent is in range [0, 100]
    - attempt_count <= max_attempts
    - completed_at is set IFF status is terminal
    - result is set IFF status is COMPLETED
    - error_message is set IFF status is FAILED
    """
    __tablename__ = "agent_tasks"

    # Primary key - time-sortable ID
    task_id: str = Field(
        default_factory=_generate_task_id,
        primary_key=True,
        max_length=32,
        description="Unique task identifier"
    )

    # Task type and status
    agent_type: AgentType = Field(
        ...,
        index=True,
        description="Type of agent executing this task"
    )
    status: AgentTaskStatus = Field(
        default=AgentTaskStatus.PENDING,
        index=True,
        description="Current execution status"
    )

    # Input/Output - stored as JSON
    input_params: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
        description="Input parameters for the agent"
    )
    result: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
        description="Task result (only when COMPLETED)"
    )

    # Error handling
    error_message: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Error message (only when FAILED)"
    )
    error_code: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Machine-readable error code"
    )
    is_retryable: bool = Field(
        default=True,
        description="Whether this error is retryable"
    )

    # Idempotency support
    idempotency_key: Optional[str] = Field(
        default=None,
        max_length=64,
        index=True,
        description="Client-provided idempotency key"
    )

    # User tracking (optional - for multi-tenant scenarios)
    user_id: Optional[str] = Field(
        default=None,
        max_length=64,
        index=True,
        description="User who created the task"
    )

    # Progress tracking
    progress_percent: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Completion percentage (0-100)"
    )
    progress_message: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Human-readable progress message"
    )
    current_step: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Current processing step name"
    )
    total_steps: Optional[int] = Field(
        default=None,
        ge=0,
        description="Total number of steps"
    )
    current_step_num: Optional[int] = Field(
        default=None,
        ge=0,
        description="Current step number"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=_utc_now,
        index=True,
        description="Task creation time"
    )
    started_at: Optional[datetime] = Field(
        default=None,
        description="Time when task started running"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Time when task completed (success or failure)"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Time after which task results may be deleted"
    )

    # Retry tracking
    attempt_count: int = Field(
        default=0,
        ge=0,
        description="Number of execution attempts"
    )
    max_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts"
    )
    next_retry_at: Optional[datetime] = Field(
        default=None,
        description="Scheduled time for next retry"
    )
    last_error: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Error from last failed attempt (for retrying tasks)"
    )

    # Cost tracking (for LLM usage)
    tokens_input: int = Field(
        default=0,
        ge=0,
        description="Input tokens consumed"
    )
    tokens_output: int = Field(
        default=0,
        ge=0,
        description="Output tokens generated"
    )
    estimated_cost_cents: int = Field(
        default=0,
        ge=0,
        description="Estimated cost in cents (USD)"
    )

    # Priority for queue ordering
    priority: int = Field(
        default=0,
        ge=0,
        le=10,
        index=True,
        description="Task priority (higher = more urgent)"
    )

    # Webhook notification
    webhook_url: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="URL to notify on completion"
    )

    # Version for optimistic locking
    version: int = Field(
        default=1,
        ge=1,
        description="Version for optimistic concurrency control"
    )

    class Config:
        # Allow enum values in serialization
        use_enum_values = True

    @field_validator('progress_percent')
    @classmethod
    def validate_progress(cls, v: int) -> int:
        """Ensure progress is within valid range."""
        return max(0, min(100, v))

    def is_terminal(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in AgentTaskStatus.terminal_statuses()

    def is_active(self) -> bool:
        """Check if task is still in progress."""
        return self.status in AgentTaskStatus.active_statuses()

    def can_cancel(self) -> bool:
        """Check if task can be cancelled."""
        return self.status in {AgentTaskStatus.PENDING, AgentTaskStatus.RUNNING}

    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return (
            self.status == AgentTaskStatus.FAILED and
            self.is_retryable and
            self.attempt_count < self.max_attempts
        )

    def to_response_dict(self) -> Dict[str, Any]:
        """Convert to API response format."""
        return {
            "task_id": self.task_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "progress": {
                "percent": self.progress_percent,
                "message": self.progress_message,
                "current_step": self.current_step,
                "total_steps": self.total_steps,
                "current_step_num": self.current_step_num,
            },
            "result": self.result,
            "error": {
                "code": self.error_code,
                "message": self.error_message,
                "retryable": self.is_retryable,
            } if self.error_message else None,
            "timestamps": {
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "started_at": self.started_at.isoformat() if self.started_at else None,
                "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            },
            "cost": {
                "tokens_input": self.tokens_input,
                "tokens_output": self.tokens_output,
                "estimated_cost_cents": self.estimated_cost_cents,
            },
            "attempts": {
                "count": self.attempt_count,
                "max": self.max_attempts,
            },
            "links": {
                "self": f"/agents/tasks/{self.task_id}",
                "cancel": f"/agents/tasks/{self.task_id}/cancel" if self.can_cancel() else None,
                "retry": f"/agents/tasks/{self.task_id}/retry" if self.can_retry() else None,
                "events": f"/agents/tasks/{self.task_id}/events",
                "stream": f"/agents/tasks/{self.task_id}/stream" if self.is_active() else None,
            }
        }


class AgentTaskEvent(SQLModel, table=True):
    """
    Audit log for agent task state changes.

    Every state transition and significant event is logged here.
    This provides:
    - Full audit trail for debugging
    - Timeline of task execution
    - Metrics data for monitoring
    """
    __tablename__ = "agent_task_events"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Auto-incrementing event ID"
    )
    task_id: str = Field(
        ...,
        foreign_key="agent_tasks.task_id",
        index=True,
        max_length=32,
        description="Task this event belongs to"
    )
    event_type: str = Field(
        ...,
        max_length=50,
        index=True,
        description="Type of event (created, started, progress, completed, failed, cancelled, retrying)"
    )
    event_data: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
        description="Event-specific data"
    )
    previous_status: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Status before this event"
    )
    new_status: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Status after this event"
    )
    created_at: datetime = Field(
        default_factory=_utc_now,
        index=True,
        description="Event timestamp"
    )

    class Config:
        use_enum_values = True


# Define indexes for common queries
# Note: SQLModel handles basic indexes via Field(index=True)
# For composite indexes, we define them here for documentation
# Actual creation happens via Alembic migrations in production

INDEX_DEFINITIONS = [
    # For listing pending tasks ordered by priority
    "CREATE INDEX IF NOT EXISTS idx_tasks_pending_priority ON agent_tasks(status, priority DESC, created_at) WHERE status = 'pending'",

    # For finding tasks by idempotency key
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_tasks_idempotency ON agent_tasks(idempotency_key) WHERE idempotency_key IS NOT NULL",

    # For cleanup of expired tasks
    "CREATE INDEX IF NOT EXISTS idx_tasks_expires ON agent_tasks(expires_at) WHERE expires_at IS NOT NULL",

    # For user task listing
    "CREATE INDEX IF NOT EXISTS idx_tasks_user_created ON agent_tasks(user_id, created_at DESC) WHERE user_id IS NOT NULL",

    # For events timeline
    "CREATE INDEX IF NOT EXISTS idx_events_task_time ON agent_task_events(task_id, created_at DESC)",
]
