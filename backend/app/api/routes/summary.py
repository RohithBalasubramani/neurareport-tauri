"""API routes for Executive Summary Generation."""
from __future__ import annotations

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, Query, Request

from backend.app.services.security import require_api_key
from backend.app.services.summary.service import SummaryService
from backend.app.services.background_tasks import enqueue_background_job
import backend.app.services.state_access as state_access

router = APIRouter(dependencies=[Depends(require_api_key)])


class SummaryRequest(BaseModel):
    content: str = Field(..., min_length=10, max_length=50000)
    tone: str = Field(default="formal", pattern="^(formal|conversational|technical)$")
    max_sentences: int = Field(default=5, ge=2, le=15)
    focus_areas: Optional[List[str]] = Field(None, max_length=5)


def get_service() -> SummaryService:
    return SummaryService()


def _is_cancelled(job_id: str) -> bool:
    job = state_access.get_job(job_id) or {}
    return str(job.get("status") or "").strip().lower() == "cancelled"


@router.post("/generate")
async def generate_summary(
    payload: SummaryRequest,
    request: Request,
    svc: SummaryService = Depends(get_service),
    background: bool = Query(False),
):
    """Generate an executive summary from content."""
    correlation_id = getattr(request.state, "correlation_id", None)
    if not background:
        summary = svc.generate_summary(
            content=payload.content,
            tone=payload.tone,
            max_sentences=payload.max_sentences,
            focus_areas=payload.focus_areas,
            correlation_id=correlation_id,
        )
        return {"status": "ok", "summary": summary, "correlation_id": correlation_id}

    async def runner(job_id: str) -> None:
        if _is_cancelled(job_id):
            return
        state_access.record_job_start(job_id)
        state_access.record_job_step(job_id, "generate", status="running", label="Generate summary")
        try:
            summary = svc.generate_summary(
                content=payload.content,
                tone=payload.tone,
                max_sentences=payload.max_sentences,
                focus_areas=payload.focus_areas,
                correlation_id=correlation_id,
            )
            if _is_cancelled(job_id):
                state_access.record_job_step(job_id, "generate", status="cancelled", error="Cancelled by user")
                return
            state_access.record_job_step(job_id, "generate", status="succeeded", progress=100.0)
            state_access.record_job_completion(
                job_id,
                status="succeeded",
                result={"summary": summary},
            )
        except Exception as exc:
            if _is_cancelled(job_id):
                state_access.record_job_step(job_id, "generate", status="cancelled", error="Cancelled by user")
                return
            logger.exception("summary_job_failed", extra={"job_id": job_id})
            state_access.record_job_step(job_id, "generate", status="failed", error="Summary generation failed")
            state_access.record_job_completion(job_id, status="failed", error="Summary generation failed")

    job = await enqueue_background_job(
        job_type="summary_generate",
        steps=[{"name": "generate", "label": "Generate summary"}],
        meta={"background": True, "content_length": len(payload.content)},
        runner=runner,
    )
    return {"status": "queued", "job_id": job["id"], "correlation_id": correlation_id}


@router.get("/reports/{report_id}")
async def get_report_summary(
    report_id: str,
    request: Request,
    svc: SummaryService = Depends(get_service),
    background: bool = Query(False),
):
    """Generate summary for a specific report."""
    correlation_id = getattr(request.state, "correlation_id", None)
    if not background:
        summary = svc.generate_report_summary(report_id, correlation_id)
        return {"status": "ok", "summary": summary, "correlation_id": correlation_id}

    async def runner(job_id: str) -> None:
        if _is_cancelled(job_id):
            return
        state_access.record_job_start(job_id)
        state_access.record_job_step(job_id, "generate", status="running", label="Generate report summary")
        try:
            summary = svc.generate_report_summary(report_id, correlation_id)
            if _is_cancelled(job_id):
                state_access.record_job_step(job_id, "generate", status="cancelled", error="Cancelled by user")
                return
            state_access.record_job_step(job_id, "generate", status="succeeded", progress=100.0)
            state_access.record_job_completion(
                job_id,
                status="succeeded",
                result={"summary": summary, "report_id": report_id},
            )
        except Exception as exc:
            if _is_cancelled(job_id):
                state_access.record_job_step(job_id, "generate", status="cancelled", error="Cancelled by user")
                return
            logger.exception("summary_job_failed", extra={"job_id": job_id})
            state_access.record_job_step(job_id, "generate", status="failed", error="Summary generation failed")
            state_access.record_job_completion(job_id, status="failed", error="Summary generation failed")

    job = await enqueue_background_job(
        job_type="summary_report",
        steps=[{"name": "generate", "label": "Generate report summary"}],
        meta={"background": True, "report_id": report_id},
        runner=runner,
    )
    return {"status": "queued", "job_id": job["id"], "correlation_id": correlation_id}
