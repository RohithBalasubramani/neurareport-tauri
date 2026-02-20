"""API routes for Template Recommendations."""
from __future__ import annotations

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, Query, Request

from backend.app.services.security import require_api_key
from backend.app.services.recommendations.service import RecommendationService
from backend.app.services.background_tasks import enqueue_background_job
import backend.app.services.state_access as state_access

router = APIRouter(dependencies=[Depends(require_api_key)])


class TemplateRecommendRequest(BaseModel):
    """Request payload for template recommendations (frontend format)."""
    data_description: Optional[str] = Field(None, max_length=1000)
    data_columns: Optional[List[str]] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    output_format: Optional[str] = Field(None, max_length=50)


def get_service() -> RecommendationService:
    return RecommendationService()



@router.post("/templates")
async def recommend_templates_post(
    payload: TemplateRecommendRequest,
    request: Request,
    svc: RecommendationService = Depends(get_service),
    background: bool = Query(False),
):
    """Get template recommendations based on data description and columns."""
    correlation_id = getattr(request.state, "correlation_id", None)

    # Build context from frontend payload
    context_parts = []
    if payload.data_description:
        context_parts.append(f"Data description: {payload.data_description}")
    if payload.data_columns:
        context_parts.append(f"Data columns: {', '.join(payload.data_columns)}")
    if payload.industry:
        context_parts.append(f"Industry: {payload.industry}")
    if payload.output_format:
        context_parts.append(f"Output format: {payload.output_format}")

    context = " | ".join(context_parts) if context_parts else None

    if not background:
        recommendations = svc.recommend_templates(
            context=context,
            limit=5,
            correlation_id=correlation_id,
        )
        return {"status": "ok", "recommendations": recommendations, "correlation_id": correlation_id}

    async def runner(job_id: str) -> None:
        state_access.record_job_start(job_id)
        state_access.record_job_step(job_id, "recommend", status="running", label="Generate recommendations")
        try:
            recommendations = svc.recommend_templates(
                context=context,
                limit=5,
                correlation_id=correlation_id,
            )
            state_access.record_job_step(job_id, "recommend", status="succeeded", progress=100.0)
            state_access.record_job_completion(
                job_id,
                status="succeeded",
                result={"recommendations": recommendations},
            )
        except Exception as exc:
            logger.exception("recommend_job_failed", extra={"job_id": job_id})
            state_access.record_job_step(job_id, "recommend", status="failed", error="Recommendation generation failed")
            state_access.record_job_completion(job_id, status="failed", error="Recommendation generation failed")

    job = await enqueue_background_job(
        job_type="recommend_templates",
        steps=[{"name": "recommend", "label": "Generate recommendations"}],
        meta={"background": True, "context": context},
        runner=runner,
    )
    return {"status": "queued", "job_id": job["id"], "correlation_id": correlation_id}


@router.get("/templates")
async def recommend_templates_get(
    request: Request,
    connection_id: Optional[str] = Query(None),
    context: Optional[str] = Query(None, max_length=500),
    limit: int = Query(5, ge=1, le=20),
    svc: RecommendationService = Depends(get_service),
    background: bool = Query(False),
):
    """Get template recommendations based on context (query params)."""
    correlation_id = getattr(request.state, "correlation_id", None)
    if not background:
        recommendations = svc.recommend_templates(
            connection_id=connection_id,
            context=context,
            limit=limit,
            correlation_id=correlation_id,
        )
        return {"status": "ok", "recommendations": recommendations, "correlation_id": correlation_id}

    async def runner(job_id: str) -> None:
        state_access.record_job_start(job_id)
        state_access.record_job_step(job_id, "recommend", status="running", label="Generate recommendations")
        try:
            recommendations = svc.recommend_templates(
                connection_id=connection_id,
                context=context,
                limit=limit,
                correlation_id=correlation_id,
            )
            state_access.record_job_step(job_id, "recommend", status="succeeded", progress=100.0)
            state_access.record_job_completion(
                job_id,
                status="succeeded",
                result={"recommendations": recommendations},
            )
        except Exception as exc:
            logger.exception("recommend_job_failed", extra={"job_id": job_id})
            state_access.record_job_step(job_id, "recommend", status="failed", error="Recommendation generation failed")
            state_access.record_job_completion(job_id, status="failed", error="Recommendation generation failed")

    job = await enqueue_background_job(
        job_type="recommend_templates",
        steps=[{"name": "recommend", "label": "Generate recommendations"}],
        meta={"background": True, "context": context, "connection_id": connection_id},
        runner=runner,
    )
    return {"status": "queued", "job_id": job["id"], "correlation_id": correlation_id}


@router.get("/catalog")
async def get_template_catalog(
    request: Request,
):
    """Get template catalog for browsing."""
    correlation_id = getattr(request.state, "correlation_id", None)

    templates = state_access.list_templates()

    # Build catalog with summary info
    catalog = []
    for t in templates:
        if t.get("status") == "approved":
            catalog.append({
                "id": t.get("id"),
                "name": t.get("name"),
                "kind": t.get("kind"),
                "description": t.get("description", ""),
                "tags": t.get("tags", []),
                "created_at": t.get("created_at"),
            })

    # Sort by name
    catalog.sort(key=lambda x: x.get("name", "").lower())

    return {"status": "ok", "catalog": catalog, "total": len(catalog), "correlation_id": correlation_id}


@router.get("/templates/{template_id}/similar")
async def get_similar_templates(
    template_id: str,
    request: Request,
    limit: int = Query(3, ge=1, le=10),
    svc: RecommendationService = Depends(get_service),
):
    """Get templates similar to a given template."""
    correlation_id = getattr(request.state, "correlation_id", None)
    similar = svc.get_similar_templates(template_id, limit)
    return {"status": "ok", "similar": similar, "correlation_id": correlation_id}
