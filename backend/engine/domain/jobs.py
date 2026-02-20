"""Job domain entities.

Jobs represent long-running operations that need tracking.
Schedules define recurring job executions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class JobStatus(str, Enum):
    """Status of a job."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @property
    def is_terminal(self) -> bool:
        return self in (JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED)

    @property
    def is_active(self) -> bool:
        return self in (JobStatus.PENDING, JobStatus.QUEUED, JobStatus.RUNNING)


class StepStatus(str, Enum):
    """Status of a job step."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class JobStep:
    """A step within a job."""

    name: str
    label: str
    status: StepStatus = StepStatus.PENDING
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_weight: float = 0.0

    def start(self) -> None:
        self.status = StepStatus.RUNNING
        self.started_at = datetime.now(timezone.utc)

    def succeed(self) -> None:
        self.status = StepStatus.SUCCEEDED
        self.completed_at = datetime.now(timezone.utc)

    def fail(self, error: str) -> None:
        self.status = StepStatus.FAILED
        self.error = error
        self.completed_at = datetime.now(timezone.utc)

    def skip(self) -> None:
        self.status = StepStatus.SKIPPED
        self.completed_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "label": self.label,
            "status": self.status.value,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class JobType(str, Enum):
    """Types of jobs."""

    REPORT_GENERATION = "run_report"
    TEMPLATE_IMPORT = "import_template"
    TEMPLATE_ANALYSIS = "analyze_template"
    CONTRACT_BUILD = "build_contract"
    SCHEMA_DISCOVERY = "discover_schema"


@dataclass
class Job:
    """A tracked job/operation.

    Jobs have:
    - Unique ID and correlation ID
    - Status with state machine
    - Steps with individual tracking
    - Progress percentage
    - Result or error
    """

    job_id: str
    job_type: JobType
    status: JobStatus
    steps: List[JobStep] = field(default_factory=list)
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    template_id: Optional[str] = None
    template_name: Optional[str] = None
    template_kind: Optional[str] = None
    connection_id: Optional[str] = None
    schedule_id: Optional[str] = None
    correlation_id: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        job_type: JobType,
        steps: Optional[List[JobStep]] = None,
        **kwargs: Any,
    ) -> Job:
        return cls(
            job_id=str(uuid.uuid4()),
            job_type=job_type,
            status=JobStatus.PENDING,
            steps=steps or [],
            **kwargs,
        )

    def can_transition_to(self, new_status: JobStatus) -> bool:
        """Check if transition to new status is valid."""
        valid_transitions = {
            JobStatus.PENDING: {JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.CANCELLED},
            JobStatus.QUEUED: {JobStatus.RUNNING, JobStatus.CANCELLED},
            JobStatus.RUNNING: {JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED},
            JobStatus.SUCCEEDED: set(),
            JobStatus.FAILED: set(),
            JobStatus.CANCELLED: set(),
        }
        return new_status in valid_transitions.get(self.status, set())

    def start(self) -> None:
        if not self.can_transition_to(JobStatus.RUNNING):
            return
        self.status = JobStatus.RUNNING
        self.started_at = datetime.now(timezone.utc)

    def succeed(self, result: Optional[Dict[str, Any]] = None) -> None:
        if not self.can_transition_to(JobStatus.SUCCEEDED):
            return
        self.status = JobStatus.SUCCEEDED
        self.progress = 100.0
        self.result = result
        self.completed_at = datetime.now(timezone.utc)

    def fail(self, error: str) -> None:
        if not self.can_transition_to(JobStatus.FAILED):
            return
        self.status = JobStatus.FAILED
        self.error = error
        self.completed_at = datetime.now(timezone.utc)

    def cancel(self) -> None:
        if not self.can_transition_to(JobStatus.CANCELLED):
            return
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.now(timezone.utc)

    def update_progress(self, progress: float) -> None:
        self.progress = max(0.0, min(100.0, progress))

    def get_step(self, name: str) -> Optional[JobStep]:
        for step in self.steps:
            if step.name == name:
                return step
        return None

    def step_running(self, name: str) -> None:
        step = self.get_step(name)
        if step:
            step.start()

    def step_succeeded(self, name: str, progress: Optional[float] = None) -> None:
        step = self.get_step(name)
        if step:
            step.succeed()
            if progress is not None:
                self.update_progress(progress)

    def step_failed(self, name: str, error: str) -> None:
        step = self.get_step(name)
        if step:
            step.fail(error)

    @property
    def duration_seconds(self) -> Optional[float]:
        if not self.started_at:
            return None
        end = self.completed_at or datetime.now(timezone.utc)
        return (end - self.started_at).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "job_type": self.job_type.value,
            "status": self.status.value,
            "steps": [s.to_dict() for s in self.steps],
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "template_id": self.template_id,
            "template_name": self.template_name,
            "template_kind": self.template_kind,
            "connection_id": self.connection_id,
            "schedule_id": self.schedule_id,
            "correlation_id": self.correlation_id,
            "meta": self.meta,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class Schedule:
    """A recurring job schedule.

    Schedules define when jobs should run automatically.
    """

    schedule_id: str
    name: str
    template_id: str
    connection_id: str
    interval_minutes: int
    active: bool = True
    template_name: Optional[str] = None
    template_kind: str = "pdf"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    batch_ids: Optional[List[str]] = None
    key_values: Optional[Dict[str, str]] = None
    docx: bool = False
    xlsx: bool = False
    email_recipients: Optional[List[str]] = None
    email_subject: Optional[str] = None
    email_message: Optional[str] = None
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    last_run_status: Optional[str] = None
    last_run_error: Optional[str] = None
    run_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        name: str,
        template_id: str,
        connection_id: str,
        interval_minutes: int,
        **kwargs: Any,
    ) -> Schedule:
        now = datetime.now(timezone.utc)
        return cls(
            schedule_id=str(uuid.uuid4()),
            name=name,
            template_id=template_id,
            connection_id=connection_id,
            interval_minutes=max(1, interval_minutes),
            next_run_at=now + timedelta(minutes=max(1, interval_minutes)),
            **kwargs,
        )

    def is_due(self, now: Optional[datetime] = None) -> bool:
        if not self.active or not self.next_run_at:
            return False
        now = now or datetime.now(timezone.utc)
        return self.next_run_at <= now

    def record_run(
        self,
        status: str,
        error: Optional[str] = None,
        finished_at: Optional[datetime] = None,
    ) -> None:
        finished = finished_at or datetime.now(timezone.utc)
        self.last_run_at = finished
        self.last_run_status = status
        self.last_run_error = error
        self.run_count += 1
        self.next_run_at = finished + timedelta(minutes=self.interval_minutes)
        self.updated_at = datetime.now(timezone.utc)

    def pause(self) -> None:
        self.active = False
        self.updated_at = datetime.now(timezone.utc)

    def resume(self) -> None:
        self.active = True
        if not self.next_run_at or self.next_run_at < datetime.now(timezone.utc):
            self.next_run_at = datetime.now(timezone.utc) + timedelta(
                minutes=self.interval_minutes
            )
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schedule_id": self.schedule_id,
            "id": self.schedule_id,  # Compatibility
            "name": self.name,
            "template_id": self.template_id,
            "connection_id": self.connection_id,
            "interval_minutes": self.interval_minutes,
            "active": self.active,
            "template_name": self.template_name,
            "template_kind": self.template_kind,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "batch_ids": self.batch_ids,
            "key_values": self.key_values,
            "docx": self.docx,
            "xlsx": self.xlsx,
            "email_recipients": self.email_recipients,
            "email_subject": self.email_subject,
            "email_message": self.email_message,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "last_run_status": self.last_run_status,
            "last_run_error": self.last_run_error,
            "run_count": self.run_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Schedule:
        def parse_dt(val: Any) -> Optional[datetime]:
            if val is None:
                return None
            if isinstance(val, datetime):
                return val
            if isinstance(val, str):
                return datetime.fromisoformat(val)
            return None

        return cls(
            schedule_id=data.get("schedule_id") or data.get("id", str(uuid.uuid4())),
            name=data["name"],
            template_id=data["template_id"],
            connection_id=data["connection_id"],
            interval_minutes=int(data.get("interval_minutes", 60)),
            active=bool(data.get("active", True)),
            template_name=data.get("template_name"),
            template_kind=data.get("template_kind", "pdf"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            batch_ids=data.get("batch_ids"),
            key_values=data.get("key_values"),
            docx=bool(data.get("docx")),
            xlsx=bool(data.get("xlsx")),
            email_recipients=data.get("email_recipients"),
            email_subject=data.get("email_subject"),
            email_message=data.get("email_message"),
            next_run_at=parse_dt(data.get("next_run_at")),
            last_run_at=parse_dt(data.get("last_run_at")),
            last_run_status=data.get("last_run_status"),
            last_run_error=data.get("last_run_error"),
            run_count=int(data.get("run_count", 0)),
            created_at=parse_dt(data.get("created_at")) or datetime.now(timezone.utc),
            updated_at=parse_dt(data.get("updated_at")) or datetime.now(timezone.utc),
        )
