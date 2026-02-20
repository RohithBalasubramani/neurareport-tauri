"""
Agent Service - Production-grade orchestration of AI agents.

This service:
- Accepts agent requests and creates persistent tasks
- Executes agents with proper progress tracking
- Handles errors with categorization and retry logic
- Provides task management (list, get, cancel, retry)
- Background task queue via ThreadPoolExecutor (Trade-off 1)
- SSE progress streaming support (Trade-off 2)
- Worker isolation for horizontal scaling (Trade-off 3)

Design Principles:
- All task state is persisted to database
- Idempotency support for safe retries
- Progress updates stored and queryable
- Full audit trail via events
- Proper error categorization
- Background execution via ThreadPoolExecutor for durability
"""
from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from backend.app.repositories.agent_tasks import (
    AgentTaskModel,
    AgentTaskRepository,
    AgentTaskStatus,
    agent_task_repository,
)
from backend.app.repositories.agent_tasks.models import AgentType
from backend.app.services.agents.base_agent import (
    AgentError,
    ProgressUpdate,
    ValidationError,
)
from backend.app.services.agents.agent_registry import get_agent_registry


logger = logging.getLogger("neura.agents.service")

# ---------------------------------------------------------------------------
# Worker pool configuration (Trade-off 1 + 3)
# ---------------------------------------------------------------------------
_AGENT_WORKERS = max(int(os.getenv("NR_AGENT_WORKERS", "2") or "2"), 1)
_AGENT_EXECUTOR = ThreadPoolExecutor(
    max_workers=_AGENT_WORKERS,
    thread_name_prefix="agent-worker",
)


class AgentService:
    """
    Central service for managing AI agent tasks.

    This service is the main entry point for:
    - Creating and executing agent tasks
    - Tracking task progress
    - Managing task lifecycle (cancel, retry)
    - Querying task history

    Example usage:
        service = AgentService()

        # Create and execute a research task
        task = await service.run_research(
            topic="AI in healthcare",
            depth="comprehensive",
            idempotency_key="user123-research-001"
        )

        # Check task status
        task = service.get_task(task.task_id)
        print(f"Status: {task.status}, Progress: {task.progress_percent}%")

        # Cancel a pending task
        service.cancel_task(task.task_id)
    """

    # Map AgentType enum values to registry names
    _AGENT_TYPE_TO_REGISTRY: Dict[str, str] = {
        "research": "research",
        "data_analyst": "data_analyst",
        "email_draft": "email_draft",
        "content_repurpose": "content_repurpose",
        "proofreading": "proofreading",
        "report_analyst": "report_analyst",
    }

    def __init__(self, repository: Optional[AgentTaskRepository] = None):
        """Initialize the agent service.

        Args:
            repository: Optional repository instance. Uses singleton if not provided.
        """
        self._repo = repository or agent_task_repository
        # Use the agent registry for dynamic agent discovery
        self._registry = get_agent_registry()
        # Trigger auto-discovery so @register_agent decorators are loaded
        self._registry.auto_discover()
        # Backwards-compat: some tests and legacy code expect a mapping of
        # AgentType -> agent instance.
        self._agents: Dict[AgentType, Any] = {}
        for atype in AgentType:
            registry_name = self._AGENT_TYPE_TO_REGISTRY.get(atype.value)
            if not registry_name:
                continue
            agent = self._registry.get(registry_name)
            if agent is not None:
                self._agents[atype] = agent
        # Track running task locks to prevent duplicate execution
        self._running_tasks: set[str] = set()
        self._running_tasks_lock = threading.Lock()

    # =========================================================================
    # TASK CREATION AND EXECUTION
    # =========================================================================

    async def run_research(
        self,
        topic: str,
        depth: str = "comprehensive",
        focus_areas: Optional[List[str]] = None,
        max_sections: int = 5,
        *,
        idempotency_key: Optional[str] = None,
        user_id: Optional[str] = None,
        priority: int = 0,
        webhook_url: Optional[str] = None,
        sync: bool = True,
    ) -> AgentTaskModel:
        """
        Run the research agent.

        Args:
            topic: Topic to research
            depth: Research depth (quick, moderate, comprehensive)
            focus_areas: Optional areas to focus on
            max_sections: Maximum number of sections
            idempotency_key: Optional key for deduplication
            user_id: Optional user identifier
            priority: Task priority (0-10)
            webhook_url: Optional webhook for completion notification
            sync: If True, wait for completion. If False, return immediately.

        Returns:
            AgentTaskModel with task info (and result if sync=True)

        Raises:
            ValidationError: If input validation fails
        """
        input_params = {
            "topic": topic,
            "depth": depth,
            "focus_areas": focus_areas or [],
            "max_sections": max_sections,
        }

        # Check idempotency
        if idempotency_key:
            task, created = self._repo.create_or_get_by_idempotency_key(
                agent_type=AgentType.RESEARCH,
                input_params=input_params,
                idempotency_key=idempotency_key,
                user_id=user_id,
                priority=priority,
                webhook_url=webhook_url,
            )
            if not created:
                logger.info(f"Returning existing task {task.task_id} for idempotency key")
                return task
        else:
            task = self._repo.create_task(
                agent_type=AgentType.RESEARCH,
                input_params=input_params,
                user_id=user_id,
                priority=priority,
                webhook_url=webhook_url,
            )

        if sync:
            # Execute synchronously and return result
            return await self._execute_task(task.task_id)
        else:
            # Enqueue onto ThreadPoolExecutor for durable background execution.
            # The executor survives individual request contexts and the task state
            # is persisted in SQLite, so even if the worker crashes mid-flight the
            # AgentTaskWorker will recover it on the next poll cycle.
            self._enqueue_background(task.task_id)
            return task

    async def run_data_analyst(
        self,
        question: str,
        data: List[Dict[str, Any]],
        data_description: Optional[str] = None,
        generate_charts: bool = True,
        *,
        idempotency_key: Optional[str] = None,
        user_id: Optional[str] = None,
        priority: int = 0,
        webhook_url: Optional[str] = None,
        sync: bool = True,
    ) -> AgentTaskModel:
        """Run the data analyst agent."""
        input_params = {
            "question": question,
            "data": data,
            "data_description": data_description,
            "generate_charts": generate_charts,
        }
        return await self._create_and_run(
            agent_type=AgentType.DATA_ANALYST,
            input_params=input_params,
            idempotency_key=idempotency_key,
            user_id=user_id,
            priority=priority,
            webhook_url=webhook_url,
            sync=sync,
        )

    async def run_email_draft(
        self,
        context: str,
        purpose: str,
        tone: str = "professional",
        recipient_info: Optional[str] = None,
        previous_emails: Optional[List[str]] = None,
        include_subject: bool = True,
        *,
        idempotency_key: Optional[str] = None,
        user_id: Optional[str] = None,
        priority: int = 0,
        webhook_url: Optional[str] = None,
        sync: bool = True,
    ) -> AgentTaskModel:
        """Run the email draft agent."""
        input_params = {
            "context": context,
            "purpose": purpose,
            "tone": tone,
            "recipient_info": recipient_info,
            "previous_emails": previous_emails,
            "include_subject": include_subject,
        }
        return await self._create_and_run(
            agent_type=AgentType.EMAIL_DRAFT,
            input_params=input_params,
            idempotency_key=idempotency_key,
            user_id=user_id,
            priority=priority,
            webhook_url=webhook_url,
            sync=sync,
        )

    async def run_content_repurpose(
        self,
        content: str,
        source_format: str,
        target_formats: List[str],
        preserve_key_points: bool = True,
        adapt_length: bool = True,
        *,
        idempotency_key: Optional[str] = None,
        user_id: Optional[str] = None,
        priority: int = 0,
        webhook_url: Optional[str] = None,
        sync: bool = True,
    ) -> AgentTaskModel:
        """Run the content repurposing agent."""
        input_params = {
            "content": content,
            "source_format": source_format,
            "target_formats": target_formats,
            "preserve_key_points": preserve_key_points,
            "adapt_length": adapt_length,
        }
        return await self._create_and_run(
            agent_type=AgentType.CONTENT_REPURPOSE,
            input_params=input_params,
            idempotency_key=idempotency_key,
            user_id=user_id,
            priority=priority,
            webhook_url=webhook_url,
            sync=sync,
        )

    async def run_proofreading(
        self,
        text: str,
        style_guide: Optional[str] = None,
        focus_areas: Optional[List[str]] = None,
        preserve_voice: bool = True,
        *,
        idempotency_key: Optional[str] = None,
        user_id: Optional[str] = None,
        priority: int = 0,
        webhook_url: Optional[str] = None,
        sync: bool = True,
    ) -> AgentTaskModel:
        """Run the proofreading agent."""
        input_params = {
            "text": text,
            "style_guide": style_guide,
            "focus_areas": focus_areas,
            "preserve_voice": preserve_voice,
        }
        return await self._create_and_run(
            agent_type=AgentType.PROOFREADING,
            input_params=input_params,
            idempotency_key=idempotency_key,
            user_id=user_id,
            priority=priority,
            webhook_url=webhook_url,
            sync=sync,
        )

    async def run_report_analyst(
        self,
        run_id: str,
        analysis_type: str = "summarize",
        question: Optional[str] = None,
        compare_run_id: Optional[str] = None,
        focus_areas: Optional[List[str]] = None,
        *,
        idempotency_key: Optional[str] = None,
        user_id: Optional[str] = None,
        priority: int = 0,
        webhook_url: Optional[str] = None,
        sync: bool = True,
    ) -> AgentTaskModel:
        """Run the report analyst agent."""
        input_params = {
            "run_id": run_id,
            "analysis_type": analysis_type,
            "question": question,
            "compare_run_id": compare_run_id,
            "focus_areas": focus_areas,
        }
        return await self._create_and_run(
            agent_type=AgentType.REPORT_ANALYST,
            input_params=input_params,
            idempotency_key=idempotency_key,
            user_id=user_id,
            priority=priority,
            webhook_url=webhook_url,
            sync=sync,
        )

    # =========================================================================
    # SHARED CREATE-AND-RUN LOGIC
    # =========================================================================

    async def _create_and_run(
        self,
        agent_type: AgentType,
        input_params: Dict[str, Any],
        *,
        idempotency_key: Optional[str] = None,
        user_id: Optional[str] = None,
        priority: int = 0,
        webhook_url: Optional[str] = None,
        sync: bool = True,
    ) -> AgentTaskModel:
        """Shared task creation and execution for all agent types."""
        if idempotency_key:
            task, created = self._repo.create_or_get_by_idempotency_key(
                agent_type=agent_type,
                input_params=input_params,
                idempotency_key=idempotency_key,
                user_id=user_id,
                priority=priority,
                webhook_url=webhook_url,
            )
            if not created:
                logger.info(f"Returning existing task {task.task_id} for idempotency key")
                return task
        else:
            task = self._repo.create_task(
                agent_type=agent_type,
                input_params=input_params,
                user_id=user_id,
                priority=priority,
                webhook_url=webhook_url,
            )

        if sync:
            return await self._execute_task(task.task_id)
        else:
            self._enqueue_background(task.task_id)
            return task

    async def _execute_task(self, task_id: str) -> AgentTaskModel:
        """Execute a task with proper state management.

        Args:
            task_id: Task to execute

        Returns:
            Updated AgentTaskModel
        """
        from backend.app.repositories.agent_tasks.repository import TaskConflictError

        # For the sync path (run_task with sync=True), track the task here.
        # The background path (_enqueue_background) already adds it.
        with self._running_tasks_lock:
            self._running_tasks.add(task_id)

        try:

            # Claim the task — transition PENDING → RUNNING atomically.
            # A TaskConflictError means another worker legitimately claimed
            # the task first; this is an expected race, not a real error.
            try:
                task = self._repo.claim_task(task_id)
            except TaskConflictError:
                logger.debug(f"Task {task_id} already claimed by another worker, skipping")
                return self._repo.get_task_or_raise(task_id)
            except Exception as e:
                logger.error(f"Failed to claim task {task_id}: {e}")
                raise

            # Get the agent implementation.
            # Prefer the explicit AgentType -> agent mapping so tests/legacy code
            # can override implementations without touching the registry.
            agent = None
            try:
                atype = task.agent_type
                if isinstance(atype, str):
                    atype = AgentType(atype)
                agent = self._agents.get(atype)
            except Exception:
                agent = None

            if agent is None:
                agent_type_str = task.agent_type.value if hasattr(task.agent_type, "value") else str(task.agent_type)
                registry_name = self._AGENT_TYPE_TO_REGISTRY.get(agent_type_str, agent_type_str)
                agent = self._registry.get(registry_name)
                if not agent:
                    raise AgentError(
                        f"Unknown agent type: {task.agent_type} (registry key: {registry_name})",
                        code="UNKNOWN_AGENT_TYPE",
                        retryable=False,
                    )

            # Create progress callback
            def on_progress(update: ProgressUpdate):
                try:
                    self._repo.update_progress(
                        task_id,
                        percent=update.percent,
                        message=update.message,
                        current_step=update.current_step,
                        total_steps=update.total_steps,
                        current_step_num=update.current_step_num,
                    )
                except Exception as e:
                    logger.warning(f"Failed to update progress for {task_id}: {e}")

            # Execute the agent — extract params based on type
            agent_kwargs = self._build_agent_kwargs(task)
            result, metadata = await agent.execute(
                **agent_kwargs,
                progress_callback=on_progress,
            )

            # Complete the task
            result_dict = result.model_dump() if hasattr(result, "model_dump") else result
            task = self._repo.complete_task(
                task_id,
                result=result_dict,
                tokens_input=metadata.get("tokens_input", 0),
                tokens_output=metadata.get("tokens_output", 0),
                estimated_cost_cents=metadata.get("estimated_cost_cents", 0),
            )

            # Trigger webhook if configured
            if task.webhook_url:
                await self._notify_webhook(task)

            return task

        except AgentError as e:
            # Fail with proper categorization
            task = self._repo.fail_task(
                task_id,
                error_message=e.message,
                error_code=e.code,
                is_retryable=e.retryable,
            )
            if task.webhook_url and task.is_terminal():
                await self._notify_webhook(task)
            return task

        except Exception as e:
            # Unexpected error - mark as retryable
            logger.exception(f"Unexpected error executing task {task_id}")
            error_message = str(e) or "Task execution failed due to an unexpected error"
            task = self._repo.fail_task(
                task_id,
                error_message=error_message,
                error_code="UNEXPECTED_ERROR",
                is_retryable=True,
            )
            if task.webhook_url and task.is_terminal():
                await self._notify_webhook(task)
            return task

        finally:
            with self._running_tasks_lock:
                self._running_tasks.discard(task_id)

    @staticmethod
    def _build_agent_kwargs(task: AgentTaskModel) -> Dict[str, Any]:
        """Extract the correct keyword arguments for an agent's execute() method.

        Each agent type has a distinct set of parameters.  This routing table
        maps ``AgentType`` → ``dict`` of keyword arguments drawn from
        ``task.input_params``.  Adding a new agent type requires only a new
        elif branch here plus the corresponding ``run_*`` method.
        """
        p = task.input_params
        atype = task.agent_type
        if isinstance(atype, str):
            atype = AgentType(atype)

        if atype == AgentType.RESEARCH:
            return {
                "topic": p.get("topic", ""),
                "depth": p.get("depth", "comprehensive"),
                "focus_areas": p.get("focus_areas"),
                "max_sections": p.get("max_sections", 5),
            }
        elif atype == AgentType.DATA_ANALYST:
            return {
                "question": p.get("question", ""),
                "data": p.get("data", []),
                "data_description": p.get("data_description"),
                "generate_charts": p.get("generate_charts", True),
            }
        elif atype == AgentType.EMAIL_DRAFT:
            return {
                "context": p.get("context", ""),
                "purpose": p.get("purpose", ""),
                "tone": p.get("tone", "professional"),
                "recipient_info": p.get("recipient_info"),
                "previous_emails": p.get("previous_emails"),
                "include_subject": p.get("include_subject", True),
            }
        elif atype == AgentType.CONTENT_REPURPOSE:
            return {
                "content": p.get("content", ""),
                "source_format": p.get("source_format", ""),
                "target_formats": p.get("target_formats", []),
                "preserve_key_points": p.get("preserve_key_points", True),
                "adapt_length": p.get("adapt_length", True),
            }
        elif atype == AgentType.PROOFREADING:
            return {
                "text": p.get("text", ""),
                "style_guide": p.get("style_guide"),
                "focus_areas": p.get("focus_areas"),
                "preserve_voice": p.get("preserve_voice", True),
            }
        elif atype == AgentType.REPORT_ANALYST:
            return {
                "run_id": p.get("run_id", ""),
                "analysis_type": p.get("analysis_type", "summarize"),
                "question": p.get("question"),
                "compare_run_id": p.get("compare_run_id"),
                "focus_areas": p.get("focus_areas"),
            }
        else:
            raise AgentError(
                f"Unknown agent type: {atype}",
                code="UNKNOWN_AGENT_TYPE",
                retryable=False,
            )

    async def _notify_webhook(self, task: AgentTaskModel) -> None:
        """Send webhook notification for task completion."""
        if not task.webhook_url:
            return

        try:
            import httpx

            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(
                    task.webhook_url,
                    json={
                        "event": "task_completed" if task.status == AgentTaskStatus.COMPLETED else "task_failed",
                        "task_id": task.task_id,
                        "status": task.status.value if isinstance(task.status, AgentTaskStatus) else task.status,
                        "result": task.result if task.status == AgentTaskStatus.COMPLETED else None,
                        "error": {
                            "code": task.error_code,
                            "message": task.error_message,
                        } if task.error_message else None,
                    },
                )
                logger.info(f"Webhook notification sent for task {task.task_id}")
        except Exception as e:
            logger.warning(f"Failed to send webhook for task {task.task_id}: {e}")

    # =========================================================================
    # TASK MANAGEMENT
    # =========================================================================

    def get_task(self, task_id: str) -> Optional[AgentTaskModel]:
        """Get a task by ID.

        Args:
            task_id: Task identifier

        Returns:
            AgentTaskModel or None if not found
        """
        return self._repo.get_task(task_id)

    def list_tasks(
        self,
        *,
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[AgentTaskModel]:
        """List tasks with optional filtering.

        Args:
            agent_type: Filter by agent type
            status: Filter by status
            user_id: Filter by user
            limit: Maximum number of tasks
            offset: Number to skip

        Returns:
            List of AgentTaskModel
        """
        # Convert string filters to enums
        agent_type_enum = None
        if agent_type:
            try:
                agent_type_enum = AgentType(agent_type)
            except ValueError:
                pass

        status_enum = None
        if status:
            try:
                status_enum = AgentTaskStatus(status)
            except ValueError:
                pass

        return self._repo.list_tasks(
            agent_type=agent_type_enum,
            status=status_enum,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )

    def count_tasks(
        self,
        *,
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> int:
        """Count tasks matching filters (for pagination total).

        Args:
            agent_type: Filter by agent type
            status: Filter by status
            user_id: Filter by user

        Returns:
            Total count of matching tasks
        """
        agent_type_enum = None
        if agent_type:
            try:
                agent_type_enum = AgentType(agent_type)
            except ValueError:
                pass

        status_enum = None
        if status:
            try:
                status_enum = AgentTaskStatus(status)
            except ValueError:
                pass

        return self._repo.count_tasks(
            agent_type=agent_type_enum,
            status=status_enum,
            user_id=user_id,
        )

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
        return self._repo.cancel_task(task_id, reason)

    async def retry_task(self, task_id: str) -> AgentTaskModel:
        """Manually retry a failed task.

        Args:
            task_id: Task identifier

        Returns:
            Updated AgentTaskModel

        Raises:
            TaskNotFoundError: If task doesn't exist
            TaskConflictError: If task cannot be retried
        """
        task = self._repo.get_task_or_raise(task_id)

        if not task.can_retry():
            from backend.app.repositories.agent_tasks.repository import TaskConflictError
            raise TaskConflictError(
                f"Cannot retry task {task_id}: status={task.status}, "
                f"retryable={task.is_retryable}, attempts={task.attempt_count}/{task.max_attempts}"
            )

        # Reset to pending for re-execution
        # This is a simplified approach - in production, use the retry scheduling
        task = self._repo.claim_retry_task(task_id)
        return await self._execute_task(task_id)

    def get_task_events(self, task_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit events for a task.

        Args:
            task_id: Task identifier
            limit: Maximum number of events

        Returns:
            List of event dictionaries
        """
        events = self._repo.get_task_events(task_id, limit=limit)
        return [
            {
                "id": e.id,
                "event_type": e.event_type,
                "previous_status": e.previous_status,
                "new_status": e.new_status,
                "event_data": e.event_data,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in events
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics.

        Returns:
            Dictionary with task counts by status
        """
        return self._repo.get_stats()

    # =========================================================================
    # BACKGROUND WORKER (for task queue integration)
    # =========================================================================

    async def process_pending_tasks(self, limit: int = 5) -> int:
        """Process pending tasks (for worker mode).

        Uses ``_enqueue_background`` so tasks run in parallel within the
        ThreadPoolExecutor rather than blocking the worker loop sequentially.

        Args:
            limit: Maximum number of tasks to process

        Returns:
            Number of tasks enqueued
        """
        from backend.app.repositories.agent_tasks.repository import TaskConflictError

        pending = self._repo.list_pending_tasks(limit=limit)
        enqueued = 0

        for task in pending:
            with self._running_tasks_lock:
                if task.task_id in self._running_tasks:
                    continue

            try:
                self._enqueue_background(task.task_id)
                enqueued += 1
            except TaskConflictError:
                # Another worker already claimed it — expected race condition
                logger.debug(f"Task {task.task_id} already claimed by another worker")
            except Exception as e:
                logger.error(f"Failed to enqueue pending task {task.task_id}: {e}")

        return enqueued

    async def process_retry_tasks(self, limit: int = 5) -> int:
        """Process tasks ready for retry (for worker mode).

        Args:
            limit: Maximum number of tasks to process

        Returns:
            Number of tasks enqueued for retry
        """
        from backend.app.repositories.agent_tasks.repository import TaskConflictError

        ready = self._repo.list_retrying_tasks(limit=limit)
        enqueued = 0

        for task in ready:
            with self._running_tasks_lock:
                if task.task_id in self._running_tasks:
                    continue

            try:
                self._repo.claim_retry_task(task.task_id)
                self._enqueue_background(task.task_id)
                enqueued += 1
            except TaskConflictError:
                logger.debug(f"Retry task {task.task_id} already claimed by another worker")
            except Exception as e:
                logger.error(f"Failed to enqueue retry task {task.task_id}: {e}")

        return enqueued

    # =========================================================================
    # BACKGROUND EXECUTION (Trade-off 1)
    # =========================================================================

    def execute_task_sync(self, task_id: str, agent_type: str, params: dict) -> None:
        """Synchronous entry point for Dramatiq worker execution.

        Creates an event loop and runs ``_execute_task`` to completion.
        Called from ``backend.app.services.worker.tasks.agent_tasks``.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._execute_task(task_id))
        finally:
            loop.close()

    # =========================================================================
    # BACKGROUND EXECUTION (Trade-off 1)
    # =========================================================================

    def _enqueue_background(self, task_id: str) -> None:
        """Submit a task to the ThreadPoolExecutor for background execution.

        The executor runs in a daemon thread and persists across request
        lifecycles. Task state is tracked in SQLite so recovery is possible
        if the worker dies.

        If the executor has been shut down (server shutting down), the task
        remains in PENDING state and will be picked up by the AgentTaskWorker
        on next startup via ``recover_stale_tasks()``.

        Args:
            task_id: Task to execute
        """
        # Mark the task as tracked BEFORE submitting to the executor so that
        # concurrent poll cycles do not enqueue the same task twice.
        with self._running_tasks_lock:
            if task_id in self._running_tasks:
                logger.debug(f"Task {task_id} already enqueued, skipping duplicate")
                return
            self._running_tasks.add(task_id)

        def _worker() -> None:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self._execute_task(task_id))
                finally:
                    loop.close()
            except Exception:
                logger.exception(f"Background worker failed for task {task_id}")

        try:
            _AGENT_EXECUTOR.submit(_worker)
            logger.info(f"Task {task_id} enqueued for background execution")
        except RuntimeError:
            # Executor shut down — task stays PENDING in DB for recovery
            with self._running_tasks_lock:
                self._running_tasks.discard(task_id)
            logger.warning(
                f"Executor shut down, task {task_id} remains PENDING for recovery"
            )

    def recover_stale_tasks(self) -> int:
        """Recover tasks stuck in RUNNING state (server restart recovery).

        Should be called during application startup.

        Returns:
            Number of tasks recovered
        """
        recovered = self._repo.recover_stale_tasks()
        count = len(recovered)

        # Re-enqueue any tasks that were moved to RETRYING
        for task in recovered:
            if task.status == AgentTaskStatus.RETRYING:
                try:
                    self._repo.claim_retry_task(task.task_id)
                    self._enqueue_background(task.task_id)
                except Exception as e:
                    logger.error(f"Failed to re-enqueue recovered task {task.task_id}: {e}")

        if count:
            logger.info(f"Recovered {count} stale agent tasks on startup")
        return count

    # =========================================================================
    # PROGRESS SUBSCRIPTION (Trade-off 2 - SSE support)
    # =========================================================================

    async def stream_task_progress(
        self,
        task_id: str,
        *,
        poll_interval: float = 0.5,
        timeout: float = 300.0,
        heartbeat_interval: float = 15.0,
    ):
        """Async generator that yields progress events for SSE streaming.

        Polls the task at ``poll_interval`` seconds and yields NDJSON events
        whenever progress changes.  Emits periodic ``heartbeat`` events when
        no progress change is detected for ``heartbeat_interval`` seconds so
        proxies and browsers keep the connection alive.

        Terminates when the task reaches a terminal state or the timeout
        expires.

        Args:
            task_id: Task to stream
            poll_interval: Seconds between polls
            timeout: Maximum streaming duration in seconds
            heartbeat_interval: Seconds between heartbeat events when idle
        """
        start = time.monotonic()
        last_version = -1
        last_percent = -1
        last_emit_time = time.monotonic()

        while (time.monotonic() - start) < timeout:
            try:
                task = self._repo.get_task(task_id)
            except Exception as exc:
                logger.warning(f"DB error while streaming task {task_id}: {exc}")
                yield {
                    "event": "error",
                    "data": {"code": "DB_ERROR", "message": "Temporary database error, retrying..."},
                }
                await asyncio.sleep(poll_interval * 2)
                continue

            if task is None:
                yield {"event": "error", "data": {"code": "TASK_NOT_FOUND", "message": f"Task {task_id} not found"}}
                return

            # Only emit when something changed
            changed = task.version != last_version or task.progress_percent != last_percent

            if changed:
                last_version = task.version
                last_percent = task.progress_percent
                last_emit_time = time.monotonic()

                yield {
                    "event": "progress",
                    "data": {
                        "task_id": task.task_id,
                        "status": task.status.value if hasattr(task.status, "value") else task.status,
                        "progress": {
                            "percent": task.progress_percent,
                            "message": task.progress_message,
                            "current_step": task.current_step,
                            "total_steps": task.total_steps,
                            "current_step_num": task.current_step_num,
                        },
                    },
                }

                # Terminal state — send final event and stop
                if task.is_terminal():
                    final_data = {
                        "task_id": task.task_id,
                        "status": task.status.value if hasattr(task.status, "value") else task.status,
                    }
                    if task.status == AgentTaskStatus.COMPLETED:
                        final_data["result"] = task.result
                    elif task.error_message:
                        final_data["error"] = {
                            "code": task.error_code,
                            "message": task.error_message,
                        }
                    yield {"event": "complete", "data": final_data}
                    return

            elif (time.monotonic() - last_emit_time) >= heartbeat_interval:
                # Keep connection alive with heartbeat
                last_emit_time = time.monotonic()
                yield {
                    "event": "heartbeat",
                    "data": {"task_id": task_id, "timestamp": datetime.now(timezone.utc).isoformat()},
                }

            await asyncio.sleep(poll_interval)

        # Timeout
        yield {"event": "error", "data": {"code": "STREAM_TIMEOUT", "message": "Progress stream timed out"}}


class AgentTaskWorker:
    """
    Background worker that polls for pending and retryable agent tasks.

    This worker bridges the gap between the persistent task queue (SQLite)
    and the actual execution. It runs as a daemon thread and processes
    tasks from the repository.

    For horizontal scaling (Trade-off 3), multiple workers can run in
    separate processes. The ``claim_task`` / ``claim_retry_task`` methods
    use optimistic locking to prevent double-execution.

    Usage:
        worker = AgentTaskWorker(agent_service)
        worker.start()   # begins polling in background thread
        # ... on shutdown ...
        worker.stop()
    """

    DEFAULT_POLL_INTERVAL = int(os.getenv("NR_AGENT_POLL_INTERVAL", "5"))
    DEFAULT_BATCH_SIZE = int(os.getenv("NR_AGENT_BATCH_SIZE", "3"))

    def __init__(
        self,
        service: AgentService,
        *,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ):
        self._service = service
        self._poll_interval = poll_interval
        self._batch_size = batch_size
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._stats = {
            "pending_processed": 0,
            "retries_processed": 0,
            "errors": 0,
            "cycles": 0,
        }

    @property
    def is_running(self) -> bool:
        return self._running and self._thread is not None and self._thread.is_alive()

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    def start(self) -> bool:
        """Start the worker polling loop in a daemon thread."""
        if self.is_running:
            logger.warning("Agent task worker already running")
            return False

        self._stop_event.clear()
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop,
            name="AgentTaskWorker",
            daemon=True,
        )
        self._thread.start()
        logger.info(
            f"Agent task worker started (poll={self._poll_interval}s, batch={self._batch_size})"
        )
        return True

    def stop(self, timeout: float = 10) -> bool:
        """Stop the worker."""
        if not self._running:
            return True
        self._running = False
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                logger.warning("Agent task worker stop timed out")
                return False
        logger.info(f"Agent task worker stopped. Stats: {self._stats}")
        return True

    def _run_loop(self) -> None:
        """Main polling loop - runs in background thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            while self._running and not self._stop_event.is_set():
                try:
                    self._stats["cycles"] += 1

                    # Process pending tasks
                    pending = loop.run_until_complete(
                        self._service.process_pending_tasks(limit=self._batch_size)
                    )
                    self._stats["pending_processed"] += pending

                    # Process retryable tasks
                    retried = loop.run_until_complete(
                        self._service.process_retry_tasks(limit=self._batch_size)
                    )
                    self._stats["retries_processed"] += retried

                except Exception:
                    self._stats["errors"] += 1
                    logger.exception("Agent task worker cycle error")

                self._stop_event.wait(timeout=self._poll_interval)
        finally:
            loop.close()


# Singleton instances
agent_service = AgentService()
agent_task_worker = AgentTaskWorker(agent_service)
