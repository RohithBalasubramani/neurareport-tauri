from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request

from backend.app.schemas.generate.reports import RunPayload  # reuse existing schemas
from backend.legacy.services.report_service import (
    queue_report_job,
    run_report as run_report_service,
    list_report_runs as list_report_runs_service,
    get_report_run as get_report_run_service,
    generate_docx_for_run as generate_docx_for_run_service,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/reports/run")
def run_report(payload: RunPayload, request: Request):
    return run_report_service(payload, request, kind="pdf")


@router.post("/excel/reports/run")
def run_report_excel(payload: RunPayload, request: Request):
    return run_report_service(payload, request, kind="excel")


@router.post("/jobs/run-report")
async def enqueue_report_job(payload: RunPayload | list[RunPayload], request: Request):
    return await queue_report_job(payload, request, kind="pdf")


@router.post("/excel/jobs/run-report")
async def enqueue_report_job_excel(payload: RunPayload | list[RunPayload], request: Request):
    return await queue_report_job(payload, request, kind="excel")


@router.get("/reports/runs")
def list_report_runs_route(
    request: Request,
    template_id: str | None = None,
    connection_id: str | None = None,
    schedule_id: str | None = None,
    limit: int = 50,
):
    runs = list_report_runs_service(
        template_id=template_id,
        connection_id=connection_id,
        schedule_id=schedule_id,
        limit=limit,
    )
    return {"runs": runs, "correlation_id": getattr(request.state, "correlation_id", None)}


@router.get("/reports/runs/{run_id}")
def get_report_run_route(run_id: str, request: Request):
    run = get_report_run_service(run_id)
    if not run:
        raise HTTPException(status_code=404, detail={"status": "error", "code": "run_not_found", "message": "Run not found."})
    return {"run": run, "correlation_id": getattr(request.state, "correlation_id", None)}


@router.post("/reports/runs/{run_id}/generate-docx")
def generate_docx_route(run_id: str, request: Request):
    """Generate DOCX from an existing report run's PDF (on-demand, may take minutes)."""
    try:
        run = generate_docx_for_run_service(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail={"status": "error", "code": "generate_docx_failed", "message": str(exc)})
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail={"status": "error", "code": "generate_docx_failed", "message": str(exc)})
    return {"run": run, "correlation_id": getattr(request.state, "correlation_id", None)}
