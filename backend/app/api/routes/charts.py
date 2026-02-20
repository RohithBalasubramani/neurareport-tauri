"""API routes for Auto-Chart Generation."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from backend.app.services.security import require_api_key
from backend.app.services.charts.auto_chart_service import AutoChartService
from backend.app.services.background_tasks import enqueue_background_job
import backend.app.services.state_access as state_access

logger = logging.getLogger("neura.api.charts")

VALID_CHART_TYPES = {"bar", "line", "scatter", "pie", "area", "heatmap", "histogram", "box", "radar", "treemap"}

router = APIRouter(dependencies=[Depends(require_api_key)])


class ChartAnalyzeRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., min_length=1, max_length=100)
    column_descriptions: Optional[Dict[str, str]] = None
    max_suggestions: int = Field(default=3, ge=1, le=10)


class ChartGenerateRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., min_length=1, max_length=1000)
    chart_type: str
    x_field: str
    y_fields: List[str] = Field(..., min_length=1, max_length=20)
    title: Optional[str] = Field(None, max_length=255)

    @field_validator("chart_type")
    @classmethod
    def validate_chart_type(cls, v: str) -> str:
        if v not in VALID_CHART_TYPES:
            raise ValueError(f"Invalid chart_type '{v}'. Must be one of: {', '.join(sorted(VALID_CHART_TYPES))}")
        return v

    @model_validator(mode="after")
    def validate_fields_exist_in_data(self):
        if not self.data:
            return self
        sample_keys = set(self.data[0].keys())
        if self.x_field not in sample_keys:
            raise ValueError(f"x_field '{self.x_field}' not found in data keys: {sorted(sample_keys)}")
        missing = [f for f in self.y_fields if f not in sample_keys]
        if missing:
            raise ValueError(f"y_fields {missing} not found in data keys: {sorted(sample_keys)}")
        return self


def get_service() -> AutoChartService:
    return AutoChartService()


@router.post("/analyze")
async def analyze_for_charts(
    payload: ChartAnalyzeRequest,
    request: Request,
    svc: AutoChartService = Depends(get_service),
    background: bool = Query(False),
):
    """Analyze data and suggest appropriate chart visualizations."""
    correlation_id = getattr(request.state, "correlation_id", None)
    if not background:
        suggestions = svc.analyze_data_for_charts(
            data=payload.data,
            column_descriptions=payload.column_descriptions,
            max_suggestions=payload.max_suggestions,
            correlation_id=correlation_id,
        )
        return {"status": "ok", "suggestions": suggestions, "correlation_id": correlation_id}

    async def runner(job_id: str) -> None:
        state_access.record_job_start(job_id)
        state_access.record_job_step(job_id, "analyze", status="running", label="Analyze chart data")
        try:
            suggestions = svc.analyze_data_for_charts(
                data=payload.data,
                column_descriptions=payload.column_descriptions,
                max_suggestions=payload.max_suggestions,
                correlation_id=correlation_id,
            )
            state_access.record_job_step(job_id, "analyze", status="succeeded", progress=100.0)
            state_access.record_job_completion(
                job_id,
                status="succeeded",
                result={"suggestions": suggestions},
            )
        except Exception as exc:
            logger.exception("chart_analyze_failed", extra={"job_id": job_id})
            safe_msg = "Chart analysis failed"
            state_access.record_job_step(job_id, "analyze", status="failed", error=safe_msg)
            state_access.record_job_completion(job_id, status="failed", error=safe_msg)

    job = await enqueue_background_job(
        job_type="chart_analyze",
        steps=[{"name": "analyze", "label": "Analyze chart data"}],
        meta={"background": True, "row_count": len(payload.data)},
        runner=runner,
    )
    return {"status": "queued", "job_id": job["id"], "correlation_id": correlation_id}


@router.post("/generate")
async def generate_chart_config(
    payload: ChartGenerateRequest,
    request: Request,
    svc: AutoChartService = Depends(get_service),
    background: bool = Query(False),
):
    """Generate a chart configuration."""
    correlation_id = getattr(request.state, "correlation_id", None)
    if not background:
        config = svc.generate_chart_config(
            data=payload.data,
            chart_type=payload.chart_type,
            x_field=payload.x_field,
            y_fields=payload.y_fields,
            title=payload.title,
        )
        return {"status": "ok", "chart": config, "correlation_id": correlation_id}

    async def runner(job_id: str) -> None:
        state_access.record_job_start(job_id)
        state_access.record_job_step(job_id, "generate", status="running", label="Generate chart config")
        try:
            config = svc.generate_chart_config(
                data=payload.data,
                chart_type=payload.chart_type,
                x_field=payload.x_field,
                y_fields=payload.y_fields,
                title=payload.title,
            )
            state_access.record_job_step(job_id, "generate", status="succeeded", progress=100.0)
            state_access.record_job_completion(
                job_id,
                status="succeeded",
                result={"chart": config},
            )
        except Exception as exc:
            logger.exception("chart_generate_failed", extra={"job_id": job_id})
            safe_msg = "Chart generation failed"
            state_access.record_job_step(job_id, "generate", status="failed", error=safe_msg)
            state_access.record_job_completion(job_id, status="failed", error=safe_msg)

    job = await enqueue_background_job(
        job_type="chart_generate",
        steps=[{"name": "generate", "label": "Generate chart config"}],
        meta={"background": True, "row_count": len(payload.data)},
        runner=runner,
    )
    return {"status": "queued", "job_id": job["id"], "correlation_id": correlation_id}
