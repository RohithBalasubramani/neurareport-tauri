from __future__ import annotations

import asyncio
import contextlib
import inspect
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.app.repositories.state import state_store
from backend.app.services.jobs.job_tracking import JobRunTracker, _build_job_steps, _step_progress_from_steps
from backend.app.schemas.generate.reports import RunPayload

logger = logging.getLogger("neura.scheduler")
_MISFIRE_GRACE_SECONDS_RAW = os.getenv("NEURA_SCHEDULER_MISFIRE_GRACE_SECONDS", "3600")
try:
    _MISFIRE_GRACE_SECONDS = int(_MISFIRE_GRACE_SECONDS_RAW)
except (TypeError, ValueError):
    _MISFIRE_GRACE_SECONDS = 3600
if _MISFIRE_GRACE_SECONDS <= 0:
    _MISFIRE_GRACE_SECONDS = None


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        value = datetime.fromisoformat(ts)
    except ValueError:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _next_run_datetime(schedule: dict, baseline: datetime) -> datetime:
    minutes = schedule.get("interval_minutes") or 0
    minutes = max(int(minutes), 1)
    return baseline + timedelta(minutes=minutes)


def _schedule_signature(schedule: dict) -> str:
    parts = [
        str(schedule.get("interval_minutes") or ""),
        str(schedule.get("start_date") or ""),
        str(schedule.get("end_date") or ""),
        "1" if schedule.get("active", True) else "0",
    ]
    return "|".join(parts)


def _scheduler_db_url() -> str:
    override = os.getenv("NEURA_SCHEDULER_DB_PATH")
    if override:
        path = Path(override).expanduser()
    else:
        state_db = os.getenv("NEURA_STATE_DB_PATH")
        if state_db:
            path = Path(state_db).expanduser()
        else:
            base_dir = getattr(state_store, "_base_dir", Path(__file__).resolve().parents[3] / "state")
            path = Path(base_dir) / "scheduler.sqlite3"
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path}"


class ReportScheduler:
    def __init__(
        self,
        runner: Callable[..., dict],
        *,
        poll_seconds: int = 60,
    ) -> None:
        """Initialize the report scheduler."""
        self._runner = runner
        self._poll_seconds = max(poll_seconds, 5)
        self._sync_job_id = "schedule-sync"
        # Backwards-compatible state expected by legacy tests.
        self._task: asyncio.Task | None = None
        self._inflight: set[str] = set()
        self._scheduler = AsyncIOScheduler(
            executors={"default": AsyncIOExecutor()},
            timezone=timezone.utc,
        )

    async def start(self) -> None:
        if self._task is not None and not self._task.done():
            return
        if not self._scheduler.running:
            self._scheduler.start()
        await self._sync_from_store()
        self._task = asyncio.create_task(self._sync_loop(), name="nr-schedule-sync")
        logger.info("scheduler_started", extra={"event": "scheduler_started"})

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
        logger.info("scheduler_stopped", extra={"event": "scheduler_stopped"})

    async def refresh(self) -> None:
        """Refresh scheduler jobs from persisted schedules."""
        await self._sync_from_store()

    async def _sync_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(self._poll_seconds)
                await self._sync_from_store()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("scheduler_sync_failed", extra={"event": "scheduler_sync_failed"})

    async def _dispatch_due_jobs(self) -> None:
        """
        Legacy dispatcher used by older tests and compatibility code.

        APScheduler handles scheduling in production, but tests expect a polling
        dispatcher that inspects `next_run_at` and `interval_minutes`.
        """
        now = _now_utc()
        schedules = state_store.list_schedules() or []
        for schedule in schedules:
            schedule_id = str(schedule.get("id") or "").strip()
            if not schedule_id:
                continue
            if not schedule.get("active", True):
                continue
            if schedule_id in self._inflight:
                continue

            start_date = _parse_iso(schedule.get("start_date"))
            if start_date and now < start_date:
                continue
            end_date = _parse_iso(schedule.get("end_date"))
            if end_date and now > end_date:
                continue

            next_run_at = _parse_iso(schedule.get("next_run_at"))
            if next_run_at and next_run_at > now:
                continue

            # Due now (no next_run_at => run immediately).
            self._inflight.add(schedule_id)

            async def _run_and_release(sched: dict = schedule, sid: str = schedule_id) -> None:
                try:
                    await self._run_schedule(sched)
                finally:
                    self._inflight.discard(sid)

            asyncio.create_task(_run_and_release())

    async def _sync_from_store(self) -> None:
        schedules = state_store.list_schedules()
        schedule_ids: set[str] = set()

        for schedule in schedules:
            schedule_id = schedule.get("id")
            if not schedule_id:
                continue
            schedule_ids.add(schedule_id)
            if not schedule.get("active", True):
                self._remove_job(schedule_id)
                continue

            interval_minutes = max(int(schedule.get("interval_minutes") or 0), 1)
            start_date = _parse_iso(schedule.get("start_date"))
            end_date = _parse_iso(schedule.get("end_date"))
            signature = _schedule_signature(schedule)

            job = self._scheduler.get_job(schedule_id)
            if job and job.kwargs.get("schedule_sig") == signature:
                continue
            if job:
                self._remove_job(schedule_id)

            trigger = IntervalTrigger(
                minutes=interval_minutes,
                start_date=start_date,
                end_date=end_date,
                timezone=timezone.utc,
            )
            job = self._scheduler.add_job(
                self._run_schedule,
                trigger=trigger,
                id=schedule_id,
                kwargs={"schedule_id": schedule_id, "schedule_sig": signature},
                replace_existing=True,
                max_instances=1,
                coalesce=True,
                misfire_grace_time=_MISFIRE_GRACE_SECONDS,
            )

            if job.next_run_time:
                state_store.update_schedule(
                    schedule_id,
                    next_run_at=job.next_run_time.astimezone(timezone.utc).isoformat(),
                )

        # Remove any orphaned jobs
        for job in self._scheduler.get_jobs():
            if job.id == self._sync_job_id:
                continue
            if job.id not in schedule_ids:
                self._remove_job(job.id)

    def _remove_job(self, job_id: str) -> None:
        try:
            self._scheduler.remove_job(job_id)
        except Exception:
            pass

    async def _run_schedule(self, schedule_id: str | dict, schedule_sig: str | None = None) -> None:
        schedule: dict | None
        if isinstance(schedule_id, dict):
            schedule = schedule_id
            schedule_id = str(schedule.get("id") or "")
        else:
            schedule = state_store.get_schedule(schedule_id)
        if not schedule or not schedule.get("active", True):
            return

        started = _now_utc()
        correlation_id = f"sched-{schedule_id or 'job'}-{started.timestamp():.0f}"
        job_tracker: JobRunTracker | None = None
        try:
            payload = {
                "template_id": schedule.get("template_id"),
                "connection_id": schedule.get("connection_id"),
                "start_date": schedule.get("start_date"),
                "end_date": schedule.get("end_date"),
                "batch_ids": schedule.get("batch_ids") or None,
                "key_values": schedule.get("key_values") or None,
                "docx": bool(schedule.get("docx")),
                "xlsx": bool(schedule.get("xlsx")),
                "email_recipients": schedule.get("email_recipients") or None,
                "email_subject": schedule.get("email_subject")
                or f"[Scheduled] {schedule.get('template_name') or schedule.get('template_id')}",
                "email_message": schedule.get("email_message")
                or (
                    f"Scheduled run '{schedule.get('name')}' completed.\n"
                    f"Window: {schedule.get('start_date')} - {schedule.get('end_date')}."
                ),
                "schedule_id": schedule_id,
                "schedule_name": schedule.get("name"),
            }
            kind = schedule.get("template_kind") or "pdf"
            try:
                run_payload = RunPayload(**payload)
            except Exception:
                run_payload = None
            if run_payload is not None:
                steps = _build_job_steps(run_payload, kind=kind)
                meta = {
                    "start_date": payload.get("start_date"),
                    "end_date": payload.get("end_date"),
                    "schedule_id": schedule_id,
                    "schedule_name": schedule.get("name"),
                    "docx": bool(payload.get("docx")),
                    "xlsx": bool(payload.get("xlsx")),
                    "payload": payload,
                }
                job_record = state_store.create_job(
                    job_type="run_report",
                    template_id=run_payload.template_id,
                    connection_id=run_payload.connection_id,
                    template_name=schedule.get("template_name") or run_payload.template_id,
                    template_kind=kind,
                    schedule_id=schedule_id,
                    correlation_id=correlation_id,
                    steps=steps,
                    meta=meta,
                )
                step_progress = _step_progress_from_steps(steps)
                job_tracker = JobRunTracker(
                    job_record.get("id"),
                    correlation_id=correlation_id,
                    step_progress=step_progress,
                )
                job_tracker.start()
            runner = self._runner
            if inspect.iscoroutinefunction(runner):
                result = await runner(payload, kind, job_tracker=job_tracker)
            else:
                result = await asyncio.to_thread(runner, payload, kind, job_tracker=job_tracker)
            if inspect.isawaitable(result):
                result = await result
        except Exception as exc:
            finished = _now_utc()
            next_run = _next_run_datetime(schedule, finished).isoformat()
            state_store.record_schedule_run(
                schedule_id,
                started_at=started.isoformat(),
                finished_at=finished.isoformat(),
                status="failed",
                next_run_at=next_run,
                error="Scheduled report generation failed",
                artifacts=None,
            )
            logger.exception(
                "schedule_run_failed",
                extra={
                    "event": "schedule_run_failed",
                    "schedule_id": schedule_id,
                },
            )
            if job_tracker:
                job_tracker.fail("Scheduled report generation failed")
        else:
            finished = _now_utc()
            next_run = _next_run_datetime(schedule, finished).isoformat()
            artifacts = {
                "html_url": result.get("html_url"),
                "pdf_url": result.get("pdf_url"),
                "docx_url": result.get("docx_url"),
                "xlsx_url": result.get("xlsx_url"),
            }
            state_store.record_schedule_run(
                schedule_id,
                started_at=started.isoformat(),
                finished_at=finished.isoformat(),
                status="success",
                next_run_at=next_run,
                error=None,
                artifacts=artifacts,
            )
            logger.info(
                "schedule_run_complete",
                extra={
                    "event": "schedule_run_complete",
                    "schedule_id": schedule_id,
                    "html": artifacts.get("html_url"),
                    "pdf": artifacts.get("pdf_url"),
                },
            )
            if job_tracker:
                job_tracker.succeed(result)
