"""Job scheduler - triggers scheduled jobs at the right time."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Callable, List, Optional, Protocol

from backend.engine.core.events import Event, publish_sync
from backend.engine.domain.jobs import Schedule, Job, JobType, JobStep

logger = logging.getLogger("neura.orchestration.scheduler")


class ScheduleRepository(Protocol):
    """Protocol for schedule storage."""

    def find_due(self, now: Optional[datetime] = None) -> List[Schedule]:
        ...

    def save(self, schedule: Schedule) -> Schedule:
        ...


class JobSubmitter(Protocol):
    """Protocol for job submission."""

    async def submit(self, job: Job) -> None:
        ...


class Scheduler:
    """Scheduler for recurring jobs.

    Polls for due schedules and submits jobs for execution.
    """

    def __init__(
        self,
        schedule_repo: ScheduleRepository,
        job_submitter: JobSubmitter,
        *,
        poll_interval_seconds: int = 60,
    ) -> None:
        self._repo = schedule_repo
        self._submitter = job_submitter
        self._poll_interval = max(poll_interval_seconds, 5)
        self._task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        self._inflight: set[str] = set()

    async def start(self) -> None:
        """Start the scheduler."""
        if self._task and not self._task.done():
            return

        self._stop_event.clear()
        self._task = asyncio.create_task(
            self._run_loop(),
            name="scheduler-loop",
        )

        logger.info("scheduler_started", extra={"event": "scheduler_started"})

        publish_sync(
            Event(
                name="scheduler.started",
                payload={"poll_interval": self._poll_interval},
            )
        )

    async def stop(self) -> None:
        """Stop the scheduler."""
        if not self._task:
            return

        self._stop_event.set()
        self._task.cancel()

        try:
            await self._task
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None

        logger.info("scheduler_stopped", extra={"event": "scheduler_stopped"})

        publish_sync(Event(name="scheduler.stopped", payload={}))

    async def _run_loop(self) -> None:
        """Main scheduler loop."""
        try:
            while not self._stop_event.is_set():
                try:
                    await self._check_and_dispatch()
                except Exception:
                    logger.exception(
                        "scheduler_tick_failed",
                        extra={"event": "scheduler_tick_failed"},
                    )

                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=self._poll_interval,
                    )
                except asyncio.TimeoutError:
                    continue
        except asyncio.CancelledError:
            raise

    async def _check_and_dispatch(self) -> None:
        """Check for due schedules and dispatch jobs."""
        now = datetime.now(timezone.utc)
        due_schedules = self._repo.find_due(now)

        for schedule in due_schedules:
            if not schedule.active:
                continue

            if schedule.schedule_id in self._inflight:
                continue

            self._inflight.add(schedule.schedule_id)

            try:
                await self._dispatch_schedule(schedule)
            except Exception:
                logger.exception(
                    "schedule_dispatch_failed",
                    extra={
                        "schedule_id": schedule.schedule_id,
                        "event": "schedule_dispatch_failed",
                    },
                )
            finally:
                self._inflight.discard(schedule.schedule_id)

    async def _dispatch_schedule(self, schedule: Schedule) -> None:
        """Create and submit a job for a schedule."""
        correlation_id = f"sched-{schedule.schedule_id}-{int(datetime.now(timezone.utc).timestamp())}"

        # Create job
        job = Job.create(
            job_type=JobType.REPORT_GENERATION,
            template_id=schedule.template_id,
            template_name=schedule.template_name,
            template_kind=schedule.template_kind,
            connection_id=schedule.connection_id,
            schedule_id=schedule.schedule_id,
            correlation_id=correlation_id,
            steps=[
                JobStep(name="dataLoad", label="Load database"),
                JobStep(name="contractCheck", label="Prepare contract"),
                JobStep(name="renderPdf", label="Render PDF"),
                JobStep(name="finalize", label="Finalize"),
            ],
            meta={
                "start_date": schedule.start_date,
                "end_date": schedule.end_date,
                "schedule_name": schedule.name,
                "docx": schedule.docx,
                "xlsx": schedule.xlsx,
            },
        )

        logger.info(
            "schedule_job_created",
            extra={
                "schedule_id": schedule.schedule_id,
                "job_id": job.job_id,
                "correlation_id": correlation_id,
                "event": "schedule_job_created",
            },
        )

        publish_sync(
            Event(
                name="schedule.triggered",
                payload={
                    "schedule_id": schedule.schedule_id,
                    "job_id": job.job_id,
                },
                correlation_id=correlation_id,
            )
        )

        # Submit job
        try:
            await self._submitter.submit(job)

            # Record successful trigger (next_run_at will be updated on completion)
            schedule.record_run("triggered")
            self._repo.save(schedule)

        except Exception as e:
            # Record failed trigger
            logger.exception("Schedule trigger failed for %s", schedule.id)
            schedule.record_run("failed", error="Schedule trigger failed")
            self._repo.save(schedule)
            raise

    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._task is not None and not self._task.done()
