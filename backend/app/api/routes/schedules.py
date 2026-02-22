"""Schedules API Routes.

This module contains endpoints for report scheduling:
- CRUD operations for scheduled reports
- Manual trigger for immediate execution
- Schedule status and history
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

from backend.app.services.security import require_api_key
import backend.app.services.state_access as state_access
from backend.legacy.schemas.report_schema import ScheduleCreatePayload, ScheduleUpdatePayload
from backend.legacy.services.scheduler_service import (
    create_schedule,
    delete_schedule,
    get_schedule,
    list_schedules,
    update_schedule,
)

logger = logging.getLogger("neura.schedules")

router = APIRouter(dependencies=[Depends(require_api_key)])


def _correlation(request: Request) -> str | None:
    return getattr(request.state, "correlation_id", None)


_RUN_TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def _validate_run_time(run_time: str | None) -> None:
    """Raise 422 if run_time is provided but not valid HH:MM."""
    if run_time is None:
        return
    if not _RUN_TIME_RE.match(run_time.strip()):
        raise HTTPException(
            status_code=422,
            detail={
                "status": "error",
                "code": "invalid_run_time",
                "message": "run_time must be in HH:MM format (24-hour, e.g. '08:00' or '18:30').",
            },
        )


async def _refresh_scheduler() -> None:
    try:
        from backend.api import SCHEDULER
    except (ImportError, AttributeError):
        return
    if SCHEDULER is None:
        return
    try:
        await SCHEDULER.refresh()
    except Exception:
        logger.warning("Scheduler refresh failed", exc_info=True)


@router.get("")
def list_report_schedules(request: Request):
    """List all report schedules."""
    return {"schedules": list_schedules(), "correlation_id": _correlation(request)}


@router.post("")
async def create_report_schedule(payload: ScheduleCreatePayload, request: Request):
    """Create a new report schedule."""
    if payload.interval_minutes is not None and payload.interval_minutes < 1:
        raise HTTPException(
            status_code=422,
            detail={"status": "error", "code": "invalid_interval", "message": "interval_minutes must be a positive integer (>= 1), or omit to use frequency default."},
        )
    _validate_run_time(payload.run_time)
    schedule = create_schedule(payload)
    await _refresh_scheduler()
    return {"schedule": schedule, "correlation_id": _correlation(request)}


@router.get("/{schedule_id}")
def get_report_schedule(schedule_id: str, request: Request):
    """Get a specific schedule by ID."""
    schedule = get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "code": "schedule_not_found", "message": "Schedule not found."}
        )
    return {"schedule": schedule, "correlation_id": _correlation(request)}


@router.put("/{schedule_id}")
async def update_report_schedule(schedule_id: str, payload: ScheduleUpdatePayload, request: Request):
    """Update an existing report schedule."""
    _validate_run_time(payload.run_time)
    schedule = update_schedule(schedule_id, payload)
    await _refresh_scheduler()
    return {"schedule": schedule, "correlation_id": _correlation(request)}


@router.delete("/{schedule_id}")
async def delete_report_schedule(schedule_id: str, request: Request):
    """Delete a report schedule."""
    removed = delete_schedule(schedule_id)
    if not removed:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "code": "schedule_not_found", "message": "Schedule not found."}
        )
    await _refresh_scheduler()
    return {"status": "ok", "schedule_id": schedule_id, "correlation_id": _correlation(request)}


@router.post("/{schedule_id}/trigger")
async def trigger_schedule(schedule_id: str, background_tasks: BackgroundTasks, request: Request):
    """
    Manually trigger a scheduled report to run immediately.

    This creates a job and queues it for execution without waiting for the next scheduled run.
    The actual report generation happens asynchronously.
    """
    correlation_id = _correlation(request) or f"manual-trigger-{schedule_id}"

    # Find the schedule
    schedule = get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "code": "schedule_not_found", "message": "Schedule not found."}
        )

    # Import here to avoid circular imports
    from backend.app.schemas.generate.reports import RunPayload
    from backend.legacy.services.report_service import (
        JobRunTracker,
        _build_job_steps,
        _step_progress_from_steps,
        scheduler_runner,
    )

    # Dynamic date range based on frequency (daily=yesterday→today, weekly=7d, monthly=30d)
    from backend.app.services.jobs.report_scheduler import _compute_dynamic_dates
    frequency = str(schedule.get("frequency") or "daily").strip().lower()
    dyn_start, dyn_end = _compute_dynamic_dates(frequency)

    # Build the payload from schedule data
    payload = {
        "template_id": schedule.get("template_id"),
        "connection_id": schedule.get("connection_id"),
        "start_date": dyn_start,
        "end_date": dyn_end,
        "batch_ids": schedule.get("batch_ids") or None,
        "key_values": schedule.get("key_values") or None,
        "docx": bool(schedule.get("docx")),
        "xlsx": bool(schedule.get("xlsx")),
        "email_recipients": schedule.get("email_recipients") or None,
        "email_subject": schedule.get("email_subject") or f"[Manual Trigger] {schedule.get('name') or schedule.get('template_id')}",
        "email_message": schedule.get("email_message") or f"Manually triggered run for schedule '{schedule.get('name')}'.\nWindow: {dyn_start} - {dyn_end}.",
        "schedule_id": schedule_id,
        "schedule_name": schedule.get("name"),
    }
    kind = schedule.get("template_kind") or "pdf"

    # Create a RunPayload to validate the payload
    try:
        run_payload = RunPayload(**payload)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "code": "invalid_schedule_payload",
                "message": "Schedule has invalid configuration",
            }
        )

    # Create job record
    steps = _build_job_steps(run_payload, kind=kind)
    meta = {
        "start_date": payload.get("start_date"),
        "end_date": payload.get("end_date"),
        "schedule_id": schedule_id,
        "schedule_name": schedule.get("name"),
        "manual_trigger": True,
        "docx": bool(payload.get("docx")),
        "xlsx": bool(payload.get("xlsx")),
    }
    job_record = state_access.create_job(
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

    job_id = job_record.get("id")
    step_progress = _step_progress_from_steps(steps)
    job_tracker = JobRunTracker(job_id, correlation_id=correlation_id, step_progress=step_progress)

    def run_scheduled_report():
        """Background task to run the scheduled report."""
        started = datetime.now(timezone.utc)
        try:
            job_tracker.start()
            result = scheduler_runner(payload, kind, job_tracker=job_tracker)
            finished = datetime.now(timezone.utc)

            # Record the manual run in schedule history
            artifacts = {
                "html_url": result.get("html_url"),
                "pdf_url": result.get("pdf_url"),
                "docx_url": result.get("docx_url"),
                "xlsx_url": result.get("xlsx_url"),
            }
            state_access.record_schedule_run(
                schedule_id,
                started_at=started.isoformat(),
                finished_at=finished.isoformat(),
                status="success",
                next_run_at=None,  # Don't update next_run_at for manual triggers
                error=None,
                artifacts=artifacts,
            )
            job_tracker.succeed(result)
            logger.info(
                "manual_trigger_completed",
                extra={
                    "event": "manual_trigger_completed",
                    "schedule_id": schedule_id,
                    "job_id": job_id,
                    "correlation_id": correlation_id,
                }
            )
        except Exception as exc:
            finished = datetime.now(timezone.utc)
            state_access.record_schedule_run(
                schedule_id,
                started_at=started.isoformat(),
                finished_at=finished.isoformat(),
                status="failed",
                next_run_at=None,
                error="Schedule execution failed",
                artifacts=None,
            )
            job_tracker.fail("Scheduled job failed")
            logger.exception(
                "manual_trigger_failed",
                extra={
                    "event": "manual_trigger_failed",
                    "schedule_id": schedule_id,
                    "job_id": job_id,
                    "correlation_id": correlation_id,
                    "error": str(exc),
                }
            )

    # Queue the background task
    background_tasks.add_task(run_scheduled_report)

    logger.info(
        "manual_trigger_queued",
        extra={
            "event": "manual_trigger_queued",
            "schedule_id": schedule_id,
            "job_id": job_id,
            "correlation_id": correlation_id,
        }
    )

    return {
        "status": "triggered",
        "message": "Schedule triggered for immediate execution",
        "schedule_id": schedule_id,
        "job_id": job_id,
        "correlation_id": correlation_id,
    }


@router.post("/{schedule_id}/pause")
async def pause_schedule(schedule_id: str, request: Request):
    """Pause a schedule (set active to false)."""
    schedule = get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "code": "schedule_not_found", "message": "Schedule not found."}
        )

    updated = update_schedule(schedule_id, ScheduleUpdatePayload(active=False))
    await _refresh_scheduler()
    return {
        "status": "ok",
        "message": "Schedule paused",
        "schedule": updated,
        "correlation_id": _correlation(request),
    }


@router.post("/{schedule_id}/resume")
async def resume_schedule(schedule_id: str, request: Request):
    """Resume a paused schedule (set active to true)."""
    schedule = get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(
            status_code=404,
            detail={"status": "error", "code": "schedule_not_found", "message": "Schedule not found."}
        )

    updated = update_schedule(schedule_id, ScheduleUpdatePayload(active=True))
    await _refresh_scheduler()
    return {
        "status": "ok",
        "message": "Schedule resumed",
        "schedule": updated,
        "correlation_id": _correlation(request),
    }
