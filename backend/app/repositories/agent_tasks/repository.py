"""
Agent Task Repository - Database operations for agent tasks.

Design Principles:
- All operations are atomic
- Optimistic locking prevents race conditions
- Events are logged for all state changes
- Idempotency is enforced at the database level
- Cleanup of old tasks is automatic
"""
from __future__ import annotations

import logging
import os
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

from sqlalchemy import event, text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, create_engine, select

from backend.app.repositories.agent_tasks.models import (
    AgentTaskEvent,
    AgentTaskModel,
    AgentTaskStatus,
    AgentType,
    INDEX_DEFINITIONS,
    _utc_now,
)

logger = logging.getLogger("neura.agent_tasks.repository")


def _serialize_for_json(obj: Any) -> Any:
    """Recursively serialize objects to JSON-safe format.

    Converts:
    - datetime → ISO 8601 string
    - Enum → value
    - dict → recursively serialize values
    - list/tuple → recursively serialize elements
    - other → pass through
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, dict):
        return {k: _serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return type(obj)(_serialize_for_json(item) for item in obj)
    else:
        return obj


class TaskNotFoundError(Exception):
    """Raised when a task is not found."""
    pass


class TaskConflictError(Exception):
    """Raised when a task operation conflicts with current state."""
    pass


class IdempotencyConflictError(Exception):
    """Raised when an idempotency key is already used."""

    def __init__(self, existing_task_id: str):
        self.existing_task_id = existing_task_id
        super().__init__(f"Idempotency key already used by task {existing_task_id}")


class OptimisticLockError(Exception):
    """Raised when optimistic locking detects a concurrent modification."""
    pass


class AgentTaskRepository:
    """
    Repository for agent task persistence.

    Features:
    - SQLite-backed persistent storage
    - Thread-safe operations with connection pooling
    - Automatic cleanup of old tasks
    - Event logging for audit trail
    - Idempotency key support
    - Optimistic locking for concurrent updates

    Usage:
        repo = AgentTaskRepository()

        # Create a task
        task = repo.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "AI trends"},
            idempotency_key="user123-research-ai-trends"
        )

        # Update progress
        repo.update_progress(task.task_id, percent=50, message="Analyzing sources...")

        # Complete task
        repo.complete_task(task.task_id, result={"summary": "..."})
    """

    # Configuration
    DEFAULT_DB_FILENAME = "agent_tasks.db"
    MAX_TASK_AGE_DAYS = 7  # Tasks older than this can be cleaned up
    CLEANUP_BATCH_SIZE = 100
    IDEMPOTENCY_WINDOW_HOURS = 24

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the repository.

        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            state_dir = Path(
                os.getenv("NEURA_STATE_DIR")
                or Path(__file__).resolve().parents[4] / "state"
            )
            state_dir.mkdir(parents=True, exist_ok=True)
            db_path = state_dir / self.DEFAULT_DB_FILENAME

        self._db_path = db_path
        self._engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,
            connect_args={
                "check_same_thread": False,
                "timeout": 30,
            },
            pool_pre_ping=True,
        )

        # Enable WAL mode for better concurrency
        @event.listens_for(self._engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA busy_timeout=30000")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        self._lock = threading.RLock()
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Initialize database schema if not already done."""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            # Create tables
            SQLModel.metadata.create_all(self._engine)

            # Create additional indexes
            with Session(self._engine) as session:
                for index_sql in INDEX_DEFINITIONS:
                    try:
                        session.execute(text(index_sql))
                    except Exception as e:
                        # Index might already exist, which is fine
                        logger.debug(f"Index creation skipped: {e}")
                session.commit()

            self._initialized = True
            logger.info(f"Agent tasks database initialized at {self._db_path}")

    @contextmanager
    def _session(self) -> Generator[Session, None, None]:
        """Get a database session with automatic cleanup."""
        self._ensure_initialized()
        with Session(self._engine, expire_on_commit=False) as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    # =========================================================================
    # CREATE operations
    # =========================================================================

    def create_task(
        self,
        agent_type: AgentType,
        input_params: Dict[str, Any],
        *,
        idempotency_key: Optional[str] = None,
        user_id: Optional[str] = None,
        priority: int = 0,
        max_attempts: int = 3,
        webhook_url: Optional[str] = None,
        expires_in_hours: int = 24 * 7,  # 1 week default
    ) -> AgentTaskModel:
        """Create a new agent task.

        Args:
            agent_type: Type of agent to run
            input_params: Parameters for the agent
            idempotency_key: Optional key for deduplication
            user_id: Optional user identifier
            priority: Task priority (0-10, higher = more urgent)
            max_attempts: Maximum retry attempts
            webhook_url: URL to notify on completion
            expires_in_hours: Hours until task results expire

        Returns:
            Created AgentTaskModel

        Raises:
            IdempotencyConflictError: If idempotency_key already exists
        """
        now = _utc_now()
        expires_at = now + timedelta(hours=expires_in_hours) if expires_in_hours > 0 else None

        with self._session() as session:
            # Check idempotency key
            if idempotency_key:
                existing = self._find_by_idempotency_key(session, idempotency_key)
                if existing:
                    raise IdempotencyConflictError(existing.task_id)

            # Create task
            task = AgentTaskModel(
                agent_type=agent_type,
                input_params=input_params,
                status=AgentTaskStatus.PENDING,
                idempotency_key=idempotency_key,
                user_id=user_id,
                priority=priority,
                max_attempts=max_attempts,
                webhook_url=webhook_url,
                expires_at=expires_at,
                created_at=now,
            )

            session.add(task)
            try:
                session.flush()  # Get the task_id
            except IntegrityError:
                # Idempotency is enforced at the DB level; concurrent writers can
                # race between the existence check and INSERT. Convert the
                # resulting unique constraint violation into a domain error.
                if not idempotency_key:
                    raise
                session.rollback()
                existing = self._find_by_idempotency_key(session, idempotency_key)
                if existing:
                    raise IdempotencyConflictError(existing.task_id)
                raise

            # Log creation event
            self._log_event(
                session,
                task.task_id,
                "created",
                new_status=AgentTaskStatus.PENDING.value,
                data={"input_params": input_params}
            )

            logger.info(f"Created task {task.task_id} of type {agent_type}")
            return task

    def create_or_get_by_idempotency_key(
        self,
        agent_type: AgentType,
        input_params: Dict[str, Any],
        idempotency_key: str,
        _depth: int = 0,
        **kwargs,
    ) -> Tuple[AgentTaskModel, bool]:
        """Create a task or return existing one if idempotency key matches.

        Args:
            agent_type: Type of agent to run
            input_params: Parameters for the agent
            idempotency_key: Key for deduplication (required)
            _depth: Internal recursion depth counter (do not set manually)
            **kwargs: Additional arguments for create_task

        Returns:
            Tuple of (task, created) where created is True if new task was created
        """
        if _depth > 3:
            raise RuntimeError("Failed to create or retrieve task after multiple retries")
        try:
            task = self.create_task(
                agent_type=agent_type,
                input_params=input_params,
                idempotency_key=idempotency_key,
                **kwargs,
            )
            return task, True
        except IdempotencyConflictError as e:
            task = self.get_task(e.existing_task_id)
            if task is None:
                # Race condition - task was deleted after we found it
                # Retry creation
                return self.create_or_get_by_idempotency_key(
                    agent_type, input_params, idempotency_key, _depth=_depth + 1, **kwargs
                )
            return task, False

    # =========================================================================
    # READ operations
    # =========================================================================

    def get_task(self, task_id: str) -> Optional[AgentTaskModel]:
        """Get a task by ID.

        Args:
            task_id: Task identifier

        Returns:
            AgentTaskModel or None if not found
        """
        with self._session() as session:
            return session.get(AgentTaskModel, task_id)

    def get_task_or_raise(self, task_id: str) -> AgentTaskModel:
        """Get a task by ID, raising if not found.

        Args:
            task_id: Task identifier

        Returns:
            AgentTaskModel

        Raises:
            TaskNotFoundError: If task doesn't exist
        """
        task = self.get_task(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return task

    def list_tasks(
        self,
        *,
        agent_type: Optional[AgentType] = None,
        status: Optional[AgentTaskStatus] = None,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        include_expired: bool = False,
    ) -> List[AgentTaskModel]:
        """List tasks with optional filtering.

        Args:
            agent_type: Filter by agent type
            status: Filter by status
            user_id: Filter by user
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip
            include_expired: Include expired tasks

        Returns:
            List of AgentTaskModel ordered by created_at DESC
        """
        with self._session() as session:
            query = select(AgentTaskModel)

            if agent_type:
                query = query.where(AgentTaskModel.agent_type == agent_type)
            if status:
                query = query.where(AgentTaskModel.status == status)
            if user_id:
                query = query.where(AgentTaskModel.user_id == user_id)
            if not include_expired:
                now = _utc_now()
                query = query.where(
                    (AgentTaskModel.expires_at.is_(None)) |
                    (AgentTaskModel.expires_at > now)
                )

            query = query.order_by(AgentTaskModel.created_at.desc())
            query = query.offset(offset).limit(limit)

            return list(session.exec(query).all())

    def count_tasks(
        self,
        *,
        agent_type: Optional[AgentType] = None,
        status: Optional[AgentTaskStatus] = None,
        user_id: Optional[str] = None,
        include_expired: bool = False,
    ) -> int:
        """Count tasks matching filters (for pagination total).

        Args:
            agent_type: Filter by agent type
            status: Filter by status
            user_id: Filter by user
            include_expired: Include expired tasks

        Returns:
            Total count of matching tasks
        """
        from sqlalchemy import func

        with self._session() as session:
            query = select(func.count()).select_from(AgentTaskModel)

            if agent_type:
                query = query.where(AgentTaskModel.agent_type == agent_type)
            if status:
                query = query.where(AgentTaskModel.status == status)
            if user_id:
                query = query.where(AgentTaskModel.user_id == user_id)
            if not include_expired:
                now = _utc_now()
                query = query.where(
                    (AgentTaskModel.expires_at.is_(None)) |
                    (AgentTaskModel.expires_at > now)
                )

            return session.exec(query).one()

    def list_pending_tasks(
        self,
        *,
        agent_type: Optional[AgentType] = None,
        limit: int = 10,
    ) -> List[AgentTaskModel]:
        """List pending tasks ordered by priority and creation time.

        Used by workers to claim tasks.

        Args:
            agent_type: Filter by agent type
            limit: Maximum number of tasks to return

        Returns:
            List of pending tasks, highest priority first
        """
        with self._session() as session:
            query = select(AgentTaskModel).where(
                AgentTaskModel.status == AgentTaskStatus.PENDING
            )

            if agent_type:
                query = query.where(AgentTaskModel.agent_type == agent_type)

            query = query.order_by(
                AgentTaskModel.priority.desc(),
                AgentTaskModel.created_at.asc()
            )
            query = query.limit(limit)

            return list(session.exec(query).all())

    def list_retrying_tasks(
        self,
        *,
        before: Optional[datetime] = None,
        limit: int = 10,
    ) -> List[AgentTaskModel]:
        """List tasks that are ready for retry.

        Args:
            before: Only include tasks with next_retry_at before this time
            limit: Maximum number of tasks to return

        Returns:
            List of tasks ready for retry
        """
        now = before or _utc_now()

        with self._session() as session:
            query = select(AgentTaskModel).where(
                AgentTaskModel.status == AgentTaskStatus.RETRYING,
                AgentTaskModel.next_retry_at <= now,
            ).order_by(
                AgentTaskModel.next_retry_at.asc()
            ).limit(limit)

            return list(session.exec(query).all())

    def get_task_events(
        self,
        task_id: str,
        *,
        limit: int = 100,
    ) -> List[AgentTaskEvent]:
        """Get events for a task.

        Args:
            task_id: Task identifier
            limit: Maximum number of events to return

        Returns:
            List of events ordered by created_at DESC
        """
        with self._session() as session:
            query = select(AgentTaskEvent).where(
                AgentTaskEvent.task_id == task_id
            ).order_by(
                AgentTaskEvent.created_at.desc()
            ).limit(limit)

            return list(session.exec(query).all())

    def _find_by_idempotency_key(
        self,
        session: Session,
        idempotency_key: str,
    ) -> Optional[AgentTaskModel]:
        """Find a task by idempotency key within the validity window."""
        cutoff = _utc_now() - timedelta(hours=self.IDEMPOTENCY_WINDOW_HOURS)

        query = select(AgentTaskModel).where(
            AgentTaskModel.idempotency_key == idempotency_key,
            AgentTaskModel.created_at > cutoff,
        )

        return session.exec(query).first()

    # =========================================================================
    # UPDATE operations
    # =========================================================================

    def claim_task(self, task_id: str) -> AgentTaskModel:
        """Claim a pending task for execution.

        Atomically transitions task from PENDING to RUNNING.

        Args:
            task_id: Task identifier

        Returns:
            Updated AgentTaskModel

        Raises:
            TaskNotFoundError: If task doesn't exist
            TaskConflictError: If task is not in PENDING state
        """
        with self._session() as session:
            started_at = _utc_now()
            result = session.execute(
                text(
                    "UPDATE agent_tasks "
                    "SET status = :running, started_at = :started_at, "
                    "attempt_count = attempt_count + 1, version = version + 1 "
                    "WHERE task_id = :task_id AND status = :pending"
                ),
                {
                    "running": AgentTaskStatus.RUNNING.name,
                    "started_at": started_at,
                    "task_id": task_id,
                    "pending": AgentTaskStatus.PENDING.name,
                },
            )

            if result.rowcount != 1:
                task = session.get(AgentTaskModel, task_id)
                if task is None:
                    raise TaskNotFoundError(f"Task {task_id} not found")
                raise TaskConflictError(
                    f"Cannot claim task {task_id}: status is {task.status}, expected PENDING"
                )

            task = session.get(AgentTaskModel, task_id)
            assert task is not None  # row exists if UPDATE succeeded

            self._log_event(
                session,
                task_id,
                "started",
                previous_status=AgentTaskStatus.PENDING.value,
                new_status=AgentTaskStatus.RUNNING.value,
                data={"attempt": task.attempt_count},
            )

            logger.info(f"Claimed task {task_id} (attempt {task.attempt_count})")
            return task

    def claim_retry_task(self, task_id: str) -> AgentTaskModel:
        """Claim a retrying task for re-execution.

        Atomically transitions task from RETRYING to RUNNING.

        Args:
            task_id: Task identifier

        Returns:
            Updated AgentTaskModel

        Raises:
            TaskNotFoundError: If task doesn't exist
            TaskConflictError: If task is not in RETRYING state
        """
        with self._session() as session:
            started_at = _utc_now()
            result = session.execute(
                text(
                    "UPDATE agent_tasks "
                    "SET status = :running, started_at = :started_at, "
                    "attempt_count = attempt_count + 1, next_retry_at = NULL, "
                    "version = version + 1 "
                    "WHERE task_id = :task_id AND status = :retrying"
                ),
                {
                    "running": AgentTaskStatus.RUNNING.name,
                    "started_at": started_at,
                    "task_id": task_id,
                    "retrying": AgentTaskStatus.RETRYING.name,
                },
            )

            if result.rowcount != 1:
                task = session.get(AgentTaskModel, task_id)
                if task is None:
                    raise TaskNotFoundError(f"Task {task_id} not found")
                raise TaskConflictError(
                    f"Cannot claim retry for task {task_id}: status is {task.status}, expected RETRYING"
                )

            task = session.get(AgentTaskModel, task_id)
            assert task is not None

            self._log_event(
                session,
                task_id,
                "retry_started",
                previous_status=AgentTaskStatus.RETRYING.value,
                new_status=AgentTaskStatus.RUNNING.value,
                data={"attempt": task.attempt_count},
            )

            logger.info(f"Claimed retry for task {task_id} (attempt {task.attempt_count})")
            return task

    def claim_batch(
        self,
        *,
        limit: int = 5,
        exclude_task_ids: Optional[set] = None,
    ) -> List[AgentTaskModel]:
        """Atomically claim up to ``limit`` PENDING tasks.

        Eliminates the TOCTOU race between list_pending_tasks() and
        claim_task() by selecting and claiming within one session.

        Args:
            limit: Maximum number of tasks to claim
            exclude_task_ids: Task IDs to skip (already running in-process)

        Returns:
            List of successfully claimed AgentTaskModel instances
        """
        started_at = _utc_now()
        exclude = exclude_task_ids or set()

        with self._session() as session:
            candidates = list(
                session.exec(
                    select(AgentTaskModel)
                    .where(AgentTaskModel.status == AgentTaskStatus.PENDING)
                    .order_by(
                        AgentTaskModel.priority.desc(),
                        AgentTaskModel.created_at.asc(),
                    )
                    .limit(limit + len(exclude))
                ).all()
            )

            claimed: List[AgentTaskModel] = []
            for task in candidates:
                if task.task_id in exclude:
                    continue
                if len(claimed) >= limit:
                    break

                result = session.execute(
                    text(
                        "UPDATE agent_tasks "
                        "SET status = :running, started_at = :started_at, "
                        "attempt_count = attempt_count + 1, version = version + 1 "
                        "WHERE task_id = :task_id AND status = :pending"
                    ),
                    {
                        "running": AgentTaskStatus.RUNNING.name,
                        "started_at": started_at,
                        "task_id": task.task_id,
                        "pending": AgentTaskStatus.PENDING.name,
                    },
                )

                if result.rowcount == 1:
                    session.expire(task)
                    refreshed = session.get(AgentTaskModel, task.task_id)
                    if refreshed:
                        self._log_event(
                            session,
                            task.task_id,
                            "started",
                            previous_status=AgentTaskStatus.PENDING.value,
                            new_status=AgentTaskStatus.RUNNING.value,
                            data={"attempt": refreshed.attempt_count, "batch_claim": True},
                        )
                        claimed.append(refreshed)

            if claimed:
                logger.info(f"Batch-claimed {len(claimed)} task(s)")
            return claimed

    def update_progress(
        self,
        task_id: str,
        *,
        percent: Optional[int] = None,
        message: Optional[str] = None,
        current_step: Optional[str] = None,
        total_steps: Optional[int] = None,
        current_step_num: Optional[int] = None,
    ) -> AgentTaskModel:
        """Update task progress.

        Args:
            task_id: Task identifier
            percent: Completion percentage (0-100)
            message: Human-readable progress message
            current_step: Current step name
            total_steps: Total number of steps
            current_step_num: Current step number

        Returns:
            Updated AgentTaskModel

        Raises:
            TaskNotFoundError: If task doesn't exist
            TaskConflictError: If task is not in RUNNING state
        """
        with self._session() as session:
            task = session.get(AgentTaskModel, task_id)
            if task is None:
                raise TaskNotFoundError(f"Task {task_id} not found")

            if task.status != AgentTaskStatus.RUNNING:
                raise TaskConflictError(
                    f"Cannot update progress for task {task_id}: status is {task.status}, expected RUNNING"
                )

            if percent is not None:
                # Progress should be monotonically increasing
                task.progress_percent = max(task.progress_percent, min(100, max(0, percent)))
            if message is not None:
                task.progress_message = message[:500]  # Truncate if too long
            if current_step is not None:
                task.current_step = current_step[:100]
            if total_steps is not None:
                task.total_steps = total_steps
            if current_step_num is not None:
                task.current_step_num = current_step_num

            task.version += 1

            self._log_event(
                session,
                task_id,
                "progress",
                data={
                    "percent": task.progress_percent,
                    "message": task.progress_message,
                    "step": task.current_step,
                }
            )

            session.add(task)
            return task

    def complete_task(
        self,
        task_id: str,
        result: Dict[str, Any],
        *,
        tokens_input: int = 0,
        tokens_output: int = 0,
        estimated_cost_cents: int = 0,
    ) -> AgentTaskModel:
        """Mark a task as completed with results.

        Args:
            task_id: Task identifier
            result: Task result data
            tokens_input: Input tokens consumed
            tokens_output: Output tokens generated
            estimated_cost_cents: Estimated cost in cents

        Returns:
            Updated AgentTaskModel

        Raises:
            TaskNotFoundError: If task doesn't exist
            TaskConflictError: If task is not in RUNNING state
        """
        with self._session() as session:
            task = session.get(AgentTaskModel, task_id)
            if task is None:
                raise TaskNotFoundError(f"Task {task_id} not found")

            if task.status != AgentTaskStatus.RUNNING:
                raise TaskConflictError(
                    f"Cannot complete task {task_id}: status is {task.status}, expected RUNNING"
                )

            old_status = task.status
            task.status = AgentTaskStatus.COMPLETED
            task.result = _serialize_for_json(result)
            task.progress_percent = 100
            task.progress_message = "Completed"
            task.completed_at = _utc_now()
            task.tokens_input = tokens_input
            task.tokens_output = tokens_output
            task.estimated_cost_cents = estimated_cost_cents
            task.version += 1

            self._log_event(
                session,
                task_id,
                "completed",
                previous_status=old_status.value,
                new_status=AgentTaskStatus.COMPLETED.value,
                data={
                    "tokens_input": tokens_input,
                    "tokens_output": tokens_output,
                }
            )

            session.add(task)
            logger.info(f"Completed task {task_id}")
            return task

    def fail_task(
        self,
        task_id: str,
        error_message: str,
        *,
        error_code: Optional[str] = None,
        is_retryable: bool = True,
        tokens_input: int = 0,
        tokens_output: int = 0,
    ) -> AgentTaskModel:
        """Mark a task as failed.

        If the error is retryable and attempts remain, schedules a retry.
        Otherwise, marks as permanently failed.

        Args:
            task_id: Task identifier
            error_message: Error description
            error_code: Machine-readable error code
            is_retryable: Whether this error can be retried
            tokens_input: Input tokens consumed before failure
            tokens_output: Output tokens generated before failure

        Returns:
            Updated AgentTaskModel

        Raises:
            TaskNotFoundError: If task doesn't exist
            TaskConflictError: If task is not in RUNNING state
        """
        with self._session() as session:
            task = session.get(AgentTaskModel, task_id)
            if task is None:
                raise TaskNotFoundError(f"Task {task_id} not found")

            if task.status != AgentTaskStatus.RUNNING:
                raise TaskConflictError(
                    f"Cannot fail task {task_id}: status is {task.status}, expected RUNNING"
                )

            old_status = task.status
            task.last_error = error_message[:2000]
            task.tokens_input += tokens_input
            task.tokens_output += tokens_output
            task.is_retryable = is_retryable

            # Check if we can retry
            can_retry = is_retryable and task.attempt_count < task.max_attempts

            if can_retry:
                # Schedule retry with exponential backoff
                delay_seconds = self._compute_retry_delay(task.attempt_count)
                task.status = AgentTaskStatus.RETRYING
                task.next_retry_at = _utc_now() + timedelta(seconds=delay_seconds)
                task.progress_message = f"Retry scheduled in {delay_seconds}s"

                self._log_event(
                    session,
                    task_id,
                    "retry_scheduled",
                    previous_status=old_status.value,
                    new_status=AgentTaskStatus.RETRYING.value,
                    data={
                        "error": error_message[:500],
                        "error_code": error_code,
                        "attempt": task.attempt_count,
                        "next_retry_at": task.next_retry_at,
                    }
                )
                logger.warning(
                    f"Task {task_id} failed (attempt {task.attempt_count}), "
                    f"retry scheduled for {task.next_retry_at}"
                )
            else:
                # Permanent failure
                task.status = AgentTaskStatus.FAILED
                task.error_message = error_message[:2000]
                task.error_code = error_code
                task.completed_at = _utc_now()

                self._log_event(
                    session,
                    task_id,
                    "failed",
                    previous_status=old_status.value,
                    new_status=AgentTaskStatus.FAILED.value,
                    data={
                        "error": error_message[:500],
                        "error_code": error_code,
                        "final": True,
                    }
                )
                logger.error(f"Task {task_id} failed permanently: {error_message[:200]}")

            task.version += 1
            session.add(task)
            return task

    def cancel_task(self, task_id: str, reason: Optional[str] = None) -> AgentTaskModel:
        """Cancel a pending or running task.

        Args:
            task_id: Task identifier
            reason: Optional cancellation reason

        Returns:
            Updated AgentTaskModel

        Raises:
            TaskNotFoundError: If task doesn't exist
            TaskConflictError: If task cannot be cancelled
        """
        with self._session() as session:
            task = session.get(AgentTaskModel, task_id)
            if task is None:
                raise TaskNotFoundError(f"Task {task_id} not found")

            if not task.can_cancel():
                raise TaskConflictError(
                    f"Cannot cancel task {task_id}: status is {task.status}"
                )

            old_status = task.status
            task.status = AgentTaskStatus.CANCELLED
            task.completed_at = _utc_now()
            task.error_message = reason or "Cancelled by user"
            task.version += 1

            self._log_event(
                session,
                task_id,
                "cancelled",
                previous_status=old_status.value,
                new_status=AgentTaskStatus.CANCELLED.value,
                data={"reason": reason}
            )

            session.add(task)
            logger.info(f"Cancelled task {task_id}")
            return task

    # =========================================================================
    # DELETE operations
    # =========================================================================

    def delete_task(self, task_id: str) -> bool:
        """Delete a task and its events.

        Only terminal tasks can be deleted.

        Args:
            task_id: Task identifier

        Returns:
            True if deleted, False if not found

        Raises:
            TaskConflictError: If task is still active
        """
        with self._session() as session:
            task = session.get(AgentTaskModel, task_id)
            if task is None:
                return False

            if task.is_active():
                raise TaskConflictError(
                    f"Cannot delete active task {task_id}: status is {task.status}"
                )

            # Delete events first (foreign key constraint)
            session.execute(
                text("DELETE FROM agent_task_events WHERE task_id = :task_id").bindparams(task_id=task_id)
            )

            session.delete(task)
            logger.info(f"Deleted task {task_id}")
            return True

    def cleanup_expired_tasks(self, batch_size: Optional[int] = None) -> int:
        """Delete expired tasks and their events.

        Args:
            batch_size: Maximum number of tasks to delete

        Returns:
            Number of tasks deleted
        """
        batch_size = batch_size or self.CLEANUP_BATCH_SIZE
        now = _utc_now()

        with self._session() as session:
            # Find expired terminal tasks
            query = select(AgentTaskModel).where(
                AgentTaskModel.expires_at <= now,
                AgentTaskModel.status.in_([s.value for s in AgentTaskStatus.terminal_statuses()])
            ).limit(batch_size)

            tasks = list(session.exec(query).all())

            for task in tasks:
                # Delete events first
                session.execute(
                    text("DELETE FROM agent_task_events WHERE task_id = :task_id").bindparams(task_id=task.task_id)
                )
                session.delete(task)

            if tasks:
                logger.info(f"Cleaned up {len(tasks)} expired tasks")

            return len(tasks)

    # =========================================================================
    # Helper methods
    # =========================================================================

    def _log_event(
        self,
        session: Session,
        task_id: str,
        event_type: str,
        *,
        previous_status: Optional[str] = None,
        new_status: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> AgentTaskEvent:
        """Log a task event for audit trail."""
        event = AgentTaskEvent(
            task_id=task_id,
            event_type=event_type,
            previous_status=previous_status,
            new_status=new_status,
            event_data=_serialize_for_json(data) if data else None,
        )
        session.add(event)
        return event

    def _compute_retry_delay(self, attempt: int) -> int:
        """Compute retry delay with exponential backoff and jitter.

        Uses: base_delay * 2^attempt + random_jitter

        Args:
            attempt: Current attempt number (1-based)

        Returns:
            Delay in seconds
        """
        import random

        base_delay = 5  # 5 seconds base
        max_delay = 300  # 5 minutes max

        # Exponential backoff: 5, 10, 20, 40, 80, ...
        delay = base_delay * (2 ** (attempt - 1))

        # Add jitter (±25%)
        jitter = delay * 0.25 * (random.random() * 2 - 1)
        delay = delay + jitter

        return min(int(delay), max_delay)

    def get_stats(self) -> Dict[str, Any]:
        """Get repository statistics.

        Returns:
            Dictionary with task counts by status
        """
        with self._session() as session:
            stats = {}
            for status in AgentTaskStatus:
                count_query = select(AgentTaskModel).where(
                    AgentTaskModel.status == status
                )
                count = len(list(session.exec(count_query).all()))
                stats[status.value] = count

            stats["total"] = sum(stats.values())
            return stats

    def recover_stale_tasks(
        self,
        stale_threshold_seconds: int = 600,  # 10 minutes
    ) -> List[AgentTaskModel]:
        """
        Recover tasks that are stuck in RUNNING state.

        This is used on server startup to handle tasks that were
        in-flight when the server crashed.

        Args:
            stale_threshold_seconds: Tasks running longer than this are considered stale

        Returns:
            List of recovered tasks
        """
        cutoff = _utc_now() - timedelta(seconds=stale_threshold_seconds)
        recovered = []

        with self._session() as session:
            # Find stale RUNNING tasks
            stale_query = select(AgentTaskModel).where(
                AgentTaskModel.status == AgentTaskStatus.RUNNING,
                AgentTaskModel.started_at < cutoff,
            )
            stale_tasks = list(session.exec(stale_query).all())

            for task in stale_tasks:
                old_status = task.status

                # If retryable and attempts remain, schedule retry
                if task.is_retryable and task.attempt_count < task.max_attempts:
                    task.status = AgentTaskStatus.RETRYING
                    task.next_retry_at = _utc_now() + timedelta(seconds=30)
                    task.last_error = "Task was interrupted (server restart)"
                else:
                    # Otherwise, mark as failed
                    task.status = AgentTaskStatus.FAILED
                    task.error_message = "Task was interrupted (server restart)"
                    task.error_code = "SERVER_RESTART"
                    task.completed_at = _utc_now()

                task.version += 1

                self._log_event(
                    session,
                    task.task_id,
                    "recovered",
                    previous_status=old_status.value,
                    new_status=task.status.value,
                    data={"reason": "server_restart", "stale_seconds": stale_threshold_seconds}
                )

                session.add(task)
                recovered.append(task)

            if recovered:
                logger.info(f"Recovered {len(recovered)} stale tasks on startup")

        return recovered


# Singleton instance
agent_task_repository = AgentTaskRepository()
