from __future__ import annotations

from fastapi import APIRouter, Request

from backend.app.schemas.generate.reports import RunPayload


def build_run_router(
    *,
    reports_run_fn,
    enqueue_job_fn,
) -> APIRouter:
    """
    Build router for run endpoints while delegating to existing handlers.
    """
    router = APIRouter()

    @router.post("/reports/run")
    def start_run(payload: RunPayload, request: Request):
        return reports_run_fn(payload, request, kind="pdf")

    @router.post("/excel/reports/run")
    def start_run_excel(payload: RunPayload, request: Request):
        return reports_run_fn(payload, request, kind="excel")

    @router.post("/jobs/run-report")
    async def enqueue_report_job(payload: RunPayload | list[RunPayload], request: Request):
        return await enqueue_job_fn(payload, request, kind="pdf")

    @router.post("/excel/jobs/run-report")
    async def enqueue_report_job_excel(payload: RunPayload | list[RunPayload], request: Request):
        return await enqueue_job_fn(payload, request, kind="excel")

    return router
