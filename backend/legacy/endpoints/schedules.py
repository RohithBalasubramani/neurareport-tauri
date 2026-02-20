from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from backend.legacy.schemas.report_schema import ScheduleCreatePayload, ScheduleUpdatePayload
from backend.legacy.services.scheduler_service import create_schedule, delete_schedule, list_schedules, update_schedule

router = APIRouter()


def _correlation(request: Request) -> str | None:
    return getattr(request.state, "correlation_id", None)


@router.get("/reports/schedules")
def list_report_schedules(request: Request):
    return {"schedules": list_schedules(), "correlation_id": _correlation(request)}


@router.post("/reports/schedules")
def create_report_schedule(payload: ScheduleCreatePayload, request: Request):
    schedule = create_schedule(payload)
    return {"schedule": schedule, "correlation_id": _correlation(request)}


@router.put("/reports/schedules/{schedule_id}")
def update_report_schedule(schedule_id: str, payload: ScheduleUpdatePayload, request: Request):
    schedule = update_schedule(schedule_id, payload)
    return {"schedule": schedule, "correlation_id": _correlation(request)}


@router.delete("/reports/schedules/{schedule_id}")
def delete_report_schedule(schedule_id: str, request: Request):
    removed = delete_schedule(schedule_id)
    if not removed:
        raise HTTPException(status_code=404, detail={"status": "error", "code": "schedule_not_found", "message": "Schedule not found."})
    return {"status": "ok", "schedule_id": schedule_id, "correlation_id": _correlation(request)}
