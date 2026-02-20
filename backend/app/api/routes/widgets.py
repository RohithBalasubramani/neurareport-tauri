"""
Widget Intelligence API Routes — widget catalog, selection, grid packing, data.

Endpoints:
    GET  /widgets/catalog              Full widget catalog (24 scenarios)
    POST /widgets/recommend            Claude-powered widget recommendations for a DB connection
    POST /widgets/select               AI-powered widget selection
    POST /widgets/pack-grid            Pack widgets into CSS grid layout
    POST /widgets/{scenario}/validate  Validate data shape
    POST /widgets/{scenario}/format    Format raw data
    POST /widgets/data                 Live data from active DB connection
    POST /widgets/data/report          Data from a report run (RAG)
    POST /widgets/feedback             Thompson Sampling reward signal
"""
from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.security import require_api_key

logger = logging.getLogger("neura.api.widgets")

router = APIRouter(tags=["widgets"], dependencies=[Depends(require_api_key)])

# Lazy-init service singleton
_svc = None


def _get_svc():
    global _svc
    if _svc is None:
        from backend.app.services.widget_intelligence.service import WidgetIntelligenceService
        _svc = WidgetIntelligenceService()
    return _svc


# ── Schemas ──────────────────────────────────────────────────────────────


class WidgetSelectRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    query_type: str = Field(default="overview")
    data_profile: Optional[dict[str, Any]] = None
    max_widgets: int = Field(default=10, ge=1, le=20)


class GridPackRequest(BaseModel):
    widgets: list[dict[str, Any]] = Field(...)


class ValidateRequest(BaseModel):
    data: dict[str, Any] = Field(...)


class FormatRequest(BaseModel):
    data: dict[str, Any] = Field(...)


class FeedbackRequest(BaseModel):
    scenario: str = Field(..., min_length=1)
    reward: float = Field(..., ge=-1.0, le=1.0)


class WidgetDataRequest(BaseModel):
    connection_id: str = Field(..., min_length=1)
    scenario: str = Field(..., min_length=1)
    variant: Optional[str] = None
    filters: Optional[dict[str, Any]] = None
    limit: int = Field(default=100, ge=1, le=1000)


class RecommendRequest(BaseModel):
    connection_id: str = Field(..., min_length=1)
    query: str = Field(default="overview", max_length=2000)
    max_widgets: int = Field(default=8, ge=1, le=20)


class WidgetReportDataRequest(BaseModel):
    run_id: str = Field(..., min_length=1)
    scenario: str = Field(..., min_length=1)
    variant: Optional[str] = None


# Lazy-init data resolver
_resolver = None


def _get_resolver():
    global _resolver
    if _resolver is None:
        from backend.app.services.widget_intelligence.data_resolver import WidgetDataResolver
        _resolver = WidgetDataResolver()
    return _resolver


# ── Endpoints ────────────────────────────────────────────────────────────


@router.get("/catalog")
async def get_widget_catalog():
    """Return the full widget catalog with all registered scenarios."""
    svc = _get_svc()
    catalog = svc.get_catalog()
    return {"widgets": catalog, "count": len(catalog)}


@router.post("/recommend")
async def recommend_widgets(req: RecommendRequest):
    """Analyze a connected DB using Claude LLM and recommend optimal widgets."""
    try:
        from backend.app.repositories.connections.db_connection import resolve_db_path
        from backend.legacy.services.mapping.helpers import build_rich_catalog_from_db, format_catalog_rich
        from backend.resolvers.grid_packer import pack_grid as dynamic_pack
        from backend.app.services.widget_intelligence.models.design import (
            VALID_SCENARIOS, VARIANT_TO_SCENARIO, WidgetSlot,
        )
        from backend.app.services.widget_intelligence.models.intent import WidgetSize
        from backend.app.services.llm.client import get_llm_client

        # 1. Resolve DB path from connection_id
        db_path = resolve_db_path(req.connection_id, None, None)

        # 2. Build rich catalog from DB schema
        rich_catalog = build_rich_catalog_from_db(db_path)
        table_count = len(rich_catalog)
        total_columns = sum(len(cols) for cols in rich_catalog.values())
        numeric_cols = sum(
            1 for cols in rich_catalog.values()
            for c in cols if c.get("type", "").upper() in ("INTEGER", "REAL", "FLOAT", "NUMERIC", "DECIMAL", "DOUBLE")
        )
        has_ts = any(
            c.get("type", "").upper() in ("DATE", "DATETIME", "TIMESTAMP")
            or any(kw in c.get("column", "").lower() for kw in ("date", "time", "timestamp"))
            for cols in rich_catalog.values() for c in cols
        )

        # 3. Format schema as text for Claude
        schema_text = format_catalog_rich(rich_catalog)

        # 4. Build variant reference for the prompt
        variant_list = "\n".join(
            f"  - {variant} (scenario: {scenario})"
            for variant, scenario in sorted(VARIANT_TO_SCENARIO.items())
        )

        # 5. Call Claude LLM to recommend widgets
        system_prompt = f"""You are a data visualization expert. Given a database schema and a user query, recommend the best dashboard widgets.

Available scenarios: {', '.join(VALID_SCENARIOS)}

Available variants (variant → scenario):
{variant_list}

Widget sizes: compact, normal, expanded, hero

Rules:
- Analyze the database tables and columns to understand what data is available
- Match the user's intent to the most relevant widget scenarios
- Pick the best variant for each scenario based on the data shape
- Assign a relevance score (0.0–1.0) for how well each widget fits
- Generate a short question each widget answers (e.g. "What is the total billing amount?")
- Pick appropriate sizes: use "hero" for the most important widget, "expanded" for secondary insights, "normal" for standard widgets, "compact" for supporting metrics
- Return at most {req.max_widgets} widgets, ordered by relevance (highest first)
- Only recommend scenarios that make sense for the available data
- If the DB has numeric columns, include KPI and trend widgets
- If the DB has date/time columns, include timeline or trend widgets
- If the DB has categorical columns, include distribution or category-bar widgets

DATABASE SCHEMA:
{schema_text}

Respond with ONLY a JSON array (no markdown, no explanation):
[
  {{"scenario": "kpi", "variant": "kpi-live", "size": "hero", "relevance": 0.95, "question": "What is the current total?"}},
  ...
]"""

        user_message = req.query or "overview"

        client = get_llm_client()
        response = client.complete(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            description="widget_recommend",
            use_cache=True,
            cache_ttl=300.0,
        )

        # 6. Extract JSON from LLM response
        raw_text = (
            response.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        from backend.app.services.utils.llm import extract_json_array_from_llm_response
        recommended = extract_json_array_from_llm_response(raw_text, default=[])
        if not recommended:
            logger.error("LLM response has no JSON array: %s", raw_text[:500])
            raise ValueError("Claude did not return a valid JSON array")

        # 7. Validate and build WidgetSlot objects
        slots: list[WidgetSlot] = []
        for i, rec in enumerate(recommended[:req.max_widgets]):
            scenario = rec.get("scenario", "")
            variant = rec.get("variant", scenario)
            size_str = rec.get("size", "normal")
            relevance = float(rec.get("relevance", 0.5))
            question = rec.get("question", "")

            # Validate scenario
            if scenario not in VALID_SCENARIOS:
                logger.warning("LLM recommended invalid scenario %s, skipping", scenario)
                continue

            # Validate variant belongs to scenario
            if variant in VARIANT_TO_SCENARIO and VARIANT_TO_SCENARIO[variant] != scenario:
                variant = scenario  # Fall back to base scenario name

            # Validate size
            try:
                size = WidgetSize(size_str)
            except ValueError:
                size = WidgetSize.normal

            slots.append(WidgetSlot(
                id=f"w-{uuid.uuid4().hex[:8]}",
                scenario=scenario,
                variant=variant,
                size=size,
                relevance=min(max(relevance, 0.0), 1.0),
                question=question,
            ))

        if not slots:
            logger.warning("LLM returned no valid widgets, raw: %s", raw_text[:500])

        # 8. Pack into grid layout
        grid = dynamic_pack(slots)

        # 9. Build response
        widgets = [
            {
                "id": s.id,
                "scenario": s.scenario,
                "variant": s.variant,
                "size": s.size.value if hasattr(s.size, "value") else str(s.size),
                "question": s.question,
                "relevance": s.relevance,
            }
            for s in slots
        ]

        return {
            "widgets": widgets,
            "count": len(widgets),
            "grid": {
                "cells": [
                    {
                        "widget_id": c.widget_id,
                        "col_start": c.col_start,
                        "col_end": c.col_end,
                        "row_start": c.row_start,
                        "row_end": c.row_end,
                    }
                    for c in grid.cells
                ],
                "total_cols": grid.total_cols,
                "total_rows": grid.total_rows,
                "utilization_pct": grid.utilization_pct,
            },
            "profile": {
                "table_count": table_count,
                "column_count": total_columns,
                "numeric_columns": numeric_cols,
                "has_timeseries": has_ts,
                "tables": list(rich_catalog.keys()),
            },
        }

    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Widget recommendation failed")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {e}")


@router.post("/select")
async def select_widgets(req: WidgetSelectRequest):
    """AI-powered widget selection for a dashboard query."""
    svc = _get_svc()
    widgets = svc.select_widgets(
        query=req.query,
        query_type=req.query_type,
        data_profile=req.data_profile,
        max_widgets=req.max_widgets,
    )
    return {"widgets": widgets, "count": len(widgets)}


@router.post("/pack-grid")
async def pack_grid(req: GridPackRequest):
    """Pack selected widgets into a CSS grid layout."""
    svc = _get_svc()
    if not req.widgets:
        raise HTTPException(status_code=400, detail="At least one widget required")
    layout = svc.pack_grid(req.widgets)
    return layout


@router.post("/{scenario}/validate")
async def validate_widget_data(scenario: str, req: ValidateRequest):
    """Validate data shape for a widget scenario."""
    svc = _get_svc()
    errors = svc.validate_data(scenario, req.data)
    return {"scenario": scenario, "valid": len(errors) == 0, "errors": errors}


@router.post("/{scenario}/format")
async def format_widget_data(scenario: str, req: FormatRequest):
    """Format raw data into frontend-ready shape."""
    svc = _get_svc()
    formatted = svc.format_data(scenario, req.data)
    return {"scenario": scenario, "data": formatted}


@router.post("/data")
async def get_widget_data(req: WidgetDataRequest):
    """Fetch live data from an active DB connection using the widget's RAG strategy."""
    resolver = _get_resolver()
    result = resolver.resolve(
        connection_id=req.connection_id,
        scenario=req.scenario,
        variant=req.variant,
        filters=req.filters,
        limit=req.limit,
    )
    # Always return the result — error field signals issues to the frontend
    return result


@router.post("/data/report")
async def get_widget_report_data(req: WidgetReportDataRequest):
    """Fetch widget data from a report run's extracted tables and content."""
    from backend.app.services.reports.report_context import ReportContextProvider

    provider = ReportContextProvider()
    ctx = provider.get_report_context(req.run_id)
    if not ctx:
        raise HTTPException(status_code=404, detail=f"Report run {req.run_id} not found")

    svc = _get_svc()
    plugin_meta = None
    catalog = svc.get_catalog()
    for w in catalog:
        if w["scenario"] == req.scenario:
            plugin_meta = w
            break

    # Build data from report context based on RAG strategy
    rag_strategy = plugin_meta["rag_strategy"] if plugin_meta else "single_metric"

    data = {}
    if rag_strategy in ("single_metric", "multi_metric") and ctx.tables:
        # Use first table from report
        table = ctx.tables[0]
        data = {
            "labels": [row[0] if row else "" for row in table.get("rows", [])],
            "datasets": [],
        }
        headers = table.get("headers", [])
        for i, hdr in enumerate(headers[1:], 1):
            data["datasets"].append({
                "label": hdr,
                "data": [row[i] if i < len(row) else 0 for row in table.get("rows", [])],
            })

    elif rag_strategy == "narrative":
        data = {
            "title": f"Report: {ctx.template_name}",
            "text": ctx.text_content[:2000] if ctx.text_content else "No content available.",
            "highlights": [
                f"Template: {ctx.template_name}",
                f"Status: {ctx.status}",
                f"Records: {len(ctx.tables)} tables",
            ],
        }

    elif rag_strategy in ("alert_query", "events_in_range"):
        # Treat report tables as event data
        events = []
        for t in ctx.tables:
            for row in t.get("rows", [])[:20]:
                events.append({
                    "message": row[0] if row else "",
                    "timestamp": row[1] if len(row) > 1 else "",
                    "severity": "info",
                })
        data = {"events": events, "alerts": events}

    else:
        data = {
            "title": ctx.template_name,
            "text": ctx.text_content[:500] if ctx.text_content else "",
        }

    # Format through plugin if available
    formatted = svc.format_data(req.scenario, data) if data else data

    return {
        "scenario": req.scenario,
        "data": formatted,
        "source": f"report:{req.run_id}",
        "strategy": rag_strategy,
    }


@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    """Submit reward signal for Thompson Sampling learning."""
    svc = _get_svc()
    svc.update_feedback(req.scenario, req.reward)
    return {"status": "ok", "scenario": req.scenario}
