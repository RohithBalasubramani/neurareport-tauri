"""Job executor - runs jobs with tracking and observability."""

from __future__ import annotations

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from backend.engine.core.events import Event, publish_sync
from backend.engine.domain.jobs import Job, JobStatus, JobType

logger = logging.getLogger("neura.orchestration.executor")


@dataclass
class ExecutorConfig:
    """Configuration for job executor."""

    max_workers: int = 4
    default_timeout_seconds: float = 600.0
    enable_thread_injection_cancel: bool = False


@dataclass
class JobExecution:
    """Tracks a single job execution."""

    job: Job
    future: Optional[asyncio.Future] = None
    thread_id: Optional[int] = None
    started_at: Optional[datetime] = None
    child_pids: set = field(default_factory=set)


JobRunner = Callable[[Job, "JobExecutor"], Any]


class JobExecutor:
    """Executes jobs with tracking and cancellation support.

    Features:
    - Thread pool for parallel job execution
    - Job tracking and progress updates
    - Cancellation support
    - Event emission for observability
    """

    def __init__(self, config: Optional[ExecutorConfig] = None) -> None:
        self._config = config or ExecutorConfig()
        self._pool = ThreadPoolExecutor(
            max_workers=self._config.max_workers,
            thread_name_prefix="job-executor",
        )
        self._executions: Dict[str, JobExecution] = {}
        self._runners: Dict[JobType, JobRunner] = {}
        self._shutdown = False

    def register_runner(self, job_type: JobType, runner: JobRunner) -> None:
        """Register a runner function for a job type."""
        self._runners[job_type] = runner

    async def submit(self, job: Job) -> None:
        """Submit a job for execution."""
        if self._shutdown:
            raise RuntimeError("Executor is shutting down")

        if job.job_id in self._executions:
            raise ValueError(f"Job {job.job_id} is already running")

        runner = self._runners.get(job.job_type)
        if not runner:
            raise ValueError(f"No runner registered for job type: {job.job_type}")

        execution = JobExecution(job=job)
        self._executions[job.job_id] = execution

        # Emit job submitted event
        publish_sync(
            Event(
                name="job.submitted",
                payload={
                    "job_id": job.job_id,
                    "job_type": job.job_type.value,
                },
                correlation_id=job.correlation_id,
            )
        )

        # Run in thread pool
        loop = asyncio.get_running_loop()
        future = loop.run_in_executor(
            self._pool,
            self._run_job,
            job,
            runner,
            execution,
        )
        execution.future = future

    def _run_job(
        self,
        job: Job,
        runner: JobRunner,
        execution: JobExecution,
    ) -> Any:
        """Run a job in a worker thread."""
        import threading

        execution.thread_id = threading.get_ident()
        execution.started_at = datetime.now(timezone.utc)

        job.start()

        publish_sync(
            Event(
                name="job.started",
                payload={"job_id": job.job_id},
                correlation_id=job.correlation_id,
            )
        )

        logger.info(
            "job_started",
            extra={
                "job_id": job.job_id,
                "job_type": job.job_type.value,
                "correlation_id": job.correlation_id,
            },
        )

        start = time.perf_counter()

        try:
            result = runner(job, self)

            elapsed = (time.perf_counter() - start) * 1000
            job.succeed({"result": result} if result else None)

            publish_sync(
                Event(
                    name="job.completed",
                    payload={
                        "job_id": job.job_id,
                        "status": "succeeded",
                        "duration_ms": elapsed,
                    },
                    correlation_id=job.correlation_id,
                )
            )

            logger.info(
                "job_completed",
                extra={
                    "job_id": job.job_id,
                    "status": "succeeded",
                    "duration_ms": elapsed,
                    "correlation_id": job.correlation_id,
                },
            )

            return result

        except asyncio.CancelledError:
            job.cancel()
            publish_sync(
                Event(
                    name="job.cancelled",
                    payload={"job_id": job.job_id},
                    correlation_id=job.correlation_id,
                )
            )
            logger.info(
                "job_cancelled",
                extra={
                    "job_id": job.job_id,
                    "correlation_id": job.correlation_id,
                },
            )
            raise

        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            job.fail("Job execution failed")

            publish_sync(
                Event(
                    name="job.failed",
                    payload={
                        "job_id": job.job_id,
                        "error": "Job execution failed",
                        "duration_ms": elapsed,
                    },
                    correlation_id=job.correlation_id,
                )
            )

            logger.exception(
                "job_failed",
                extra={
                    "job_id": job.job_id,
                    "error": str(e),
                    "duration_ms": elapsed,
                    "correlation_id": job.correlation_id,
                },
            )

            raise

        finally:
            self._executions.pop(job.job_id, None)

    def cancel(self, job_id: str, *, force: bool = False) -> bool:
        """Cancel a running job."""
        execution = self._executions.get(job_id)
        if not execution:
            return False

        execution.job.cancel()

        if execution.future and not execution.future.done():
            cancelled = execution.future.cancel()
            if cancelled:
                return True

        if force and self._config.enable_thread_injection_cancel:
            return self._inject_cancel(execution)

        return False

    def _inject_cancel(self, execution: JobExecution) -> bool:
        """Attempt to cancel via thread exception injection."""
        if not execution.thread_id:
            return False

        try:
            import ctypes

            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(execution.thread_id),
                ctypes.py_object(asyncio.CancelledError),
            )
            return res == 1
        except Exception:
            return False

    def get_status(self, job_id: str) -> Optional[JobStatus]:
        """Get the status of a job."""
        execution = self._executions.get(job_id)
        if execution:
            return execution.job.status
        return None

    def get_active_jobs(self) -> list[str]:
        """Get IDs of all active jobs."""
        return list(self._executions.keys())

    async def shutdown(self, wait: bool = True) -> None:
        """Shutdown the executor."""
        self._shutdown = True

        if wait:
            # Wait for all jobs to complete
            futures = [
                e.future for e in self._executions.values()
                if e.future and not e.future.done()
            ]
            if futures:
                await asyncio.gather(*futures, return_exceptions=True)

        self._pool.shutdown(wait=wait)


# Global executor instance
_executor: Optional[JobExecutor] = None


def get_executor() -> JobExecutor:
    """Get or create the global job executor."""
    global _executor
    if _executor is None:
        _executor = JobExecutor()
    return _executor
