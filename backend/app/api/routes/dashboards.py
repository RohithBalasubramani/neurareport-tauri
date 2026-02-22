"""
Dashboard API Routes - Dashboard building and analytics endpoints.

All CRUD is delegated to persistent service classes backed by the
StateStore.  No in-memory dicts — dashboards survive server restarts.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from backend.app.services.dashboards.service import DashboardService
from backend.app.services.dashboards.widget_service import WidgetService
from backend.app.services.dashboards.snapshot_service import SnapshotService
from backend.app.services.dashboards.embed_service import EmbedService
from backend.app.services.security import require_api_key
from backend.app.services.analytics import (
    insight_service,
    trend_service,
    anomaly_service,
    correlation_service,
)
from backend.app.schemas.analytics import (
    DataSeries,
    InsightsRequest,
    TrendRequest,
    AnomaliesRequest,
    CorrelationsRequest,
    ForecastMethod,
)
from backend.app.services.nl2sql.service import NL2SQLService
from backend.app.schemas.nl2sql import NL2SQLExecuteRequest
from backend.app.services.validation import is_read_only_sql

logger = logging.getLogger("neura.api.dashboards")

router = APIRouter(tags=["dashboards"], dependencies=[Depends(require_api_key)])

# Maximum rows accepted by inline analytics endpoints
MAX_ANALYTICS_ROWS = 10_000

# Service singletons
_dashboard_svc = DashboardService()
_widget_svc = WidgetService()
_snapshot_svc = SnapshotService()
_embed_svc = EmbedService()
_nl2sql_svc = NL2SQLService()


# ============================================
# Schemas
# ============================================

# All valid widget types: legacy types + intelligent widget scenarios
_LEGACY_WIDGET_TYPES = {"chart", "metric", "table", "text", "filter", "map"}
_SCENARIO_WIDGET_TYPES = {
    "kpi", "alerts", "trend", "trend-multi-line", "trends-cumulative",
    "comparison", "distribution", "composition", "category-bar",
    "flow-sankey", "matrix-heatmap", "timeline", "eventlogstream",
    "narrative", "peopleview", "peoplehexgrid", "peoplenetwork",
    "supplychainglobe", "edgedevicepanel", "chatstream",
    "diagnosticpanel", "uncertaintypanel", "agentsview", "vaultview",
}


class WidgetConfig(BaseModel):
    """Widget configuration — supports both legacy types and intelligent widget scenarios."""

    type: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=255)
    data_source: Optional[str] = None
    query: Optional[str] = Field(None, max_length=10_000)
    chart_type: Optional[str] = None
    variant: Optional[str] = None
    scenario: Optional[str] = None
    options: dict[str, Any] = {}

    @field_validator("type")
    @classmethod
    def validate_widget_type(cls, v: str) -> str:
        base_type = v.split(":")[0]
        if base_type not in _LEGACY_WIDGET_TYPES and v not in _SCENARIO_WIDGET_TYPES:
            raise ValueError(
                f"Invalid widget type: {v}. Must be a legacy type "
                f"(chart, metric, table, text, filter, map) or a scenario type."
            )
        return v

    @field_validator("query")
    @classmethod
    def validate_query_is_read_only(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        ok, reason = is_read_only_sql(v)
        if not ok:
            raise ValueError(f"Widget query must be read-only: {reason}")
        return v


class DashboardWidget(BaseModel):
    """Dashboard widget with position."""

    id: str
    config: WidgetConfig
    x: int = 0
    y: int = 0
    w: int = 4
    h: int = 3


class CreateDashboardRequest(BaseModel):
    """Create dashboard request."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    widgets: list[DashboardWidget] = []
    filters: list[dict[str, Any]] = []
    theme: Optional[str] = None


class UpdateDashboardRequest(BaseModel):
    """Update dashboard request."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    widgets: Optional[list[DashboardWidget]] = None
    filters: Optional[list[dict[str, Any]]] = None
    theme: Optional[str] = None
    refresh_interval: Optional[int] = Field(None, ge=5, le=86400)
    metadata: Optional[dict[str, Any]] = None


class AddWidgetRequest(BaseModel):
    """Add widget request."""

    config: WidgetConfig
    x: int = Field(0, ge=0, le=11)
    y: int = Field(0, ge=0, le=99)
    w: int = Field(4, ge=1, le=12)
    h: int = Field(3, ge=1, le=20)


class UpdateWidgetRequest(BaseModel):
    """Update widget request — all fields optional."""

    config: Optional[WidgetConfig] = None
    x: Optional[int] = Field(None, ge=0, le=11)
    y: Optional[int] = Field(None, ge=0, le=99)
    w: Optional[int] = Field(None, ge=1, le=12)
    h: Optional[int] = Field(None, ge=1, le=20)


class WidgetLayoutItem(BaseModel):
    """Single widget layout position update."""

    widget_id: str
    x: int
    y: int
    w: int = Field(..., ge=1)
    h: int = Field(..., ge=1)


class UpdateLayoutRequest(BaseModel):
    """Update layout positions for all widgets."""

    items: list[WidgetLayoutItem]


class DashboardFilterRequest(BaseModel):
    """Add or update a dashboard filter."""

    field: str = Field(..., min_length=1, max_length=255)
    operator: str = Field(..., pattern="^(eq|neq|gt|gte|lt|lte|in|not_in|contains|between)$")
    value: Any
    label: Optional[str] = None


class DashboardVariableRequest(BaseModel):
    """Set a dashboard variable value."""

    value: Any


class WhatIfRequest(BaseModel):
    """Run a what-if simulation."""

    variable_changes: dict[str, Any]
    metrics_to_evaluate: list[str] = Field(..., min_length=1)


class ShareDashboardRequest(BaseModel):
    """Share a dashboard with users."""

    users: list[str] = Field(..., min_length=1)
    permission: str = Field("view", pattern="^(view|edit|admin)$")


class DashboardResponse(BaseModel):
    """Dashboard response."""

    id: str
    name: str
    description: Optional[str]
    widgets: list[DashboardWidget]
    filters: list[dict[str, Any]]
    theme: Optional[str]
    refresh_interval: Optional[int]
    metadata: Optional[dict[str, Any]] = None
    created_at: str
    updated_at: str


# ============================================
# Dashboard CRUD Endpoints
# ============================================

@router.post("", response_model=DashboardResponse)
async def create_dashboard(request: CreateDashboardRequest):
    """Create a new dashboard."""
    dashboard = _dashboard_svc.create_dashboard(
        name=request.name,
        description=request.description,
        widgets=[w.model_dump() for w in request.widgets],
        filters=request.filters,
        theme=request.theme,
    )
    return DashboardResponse(**dashboard)


@router.get("")
async def list_dashboards(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List all dashboards."""
    return _dashboard_svc.list_dashboards(limit=limit, offset=offset)


# ============================================
# Static-path routes (must precede /{dashboard_id})
# ============================================

@router.get("/stats")
async def get_dashboard_stats():
    """Get dashboard statistics."""
    return _dashboard_svc.get_stats()


@router.get("/snapshots/{snapshot_id}")
async def get_snapshot(snapshot_id: str):
    """Get a snapshot by ID and return its URL and content hash."""
    snapshot = _snapshot_svc.get_snapshot(snapshot_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return {
        "snapshot_id": snapshot["id"],
        "url": snapshot.get("url"),
        "content_hash": snapshot.get("content_hash"),
        "format": snapshot.get("format"),
        "status": snapshot.get("status", "completed"),
        "created_at": snapshot.get("created_at"),
    }


@router.get("/templates")
async def list_dashboard_templates():
    """List available dashboard templates."""
    templates = _dashboard_svc.list_templates()
    return {"templates": templates}


@router.post("/templates/{template_id}/create", response_model=DashboardResponse)
async def create_dashboard_from_template(
    template_id: str,
    name: Optional[str] = Query(None, min_length=1, max_length=255),
):
    """Create a new dashboard from an existing template."""
    template = _dashboard_svc.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")

    dashboard_name = name or f"{template.get('name', 'Dashboard')} (copy)"
    dashboard = _dashboard_svc.create_dashboard(
        name=dashboard_name,
        description=template.get("description"),
        widgets=template.get("widgets", []),
        filters=template.get("filters", []),
        theme=template.get("theme"),
    )
    logger.info(
        "dashboard_created_from_template",
        extra={
            "event": "dashboard_created_from_template",
            "template_id": template_id,
            "dashboard_id": dashboard["id"],
        },
    )
    return DashboardResponse(**dashboard)


@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(dashboard_id: str):
    """Get a dashboard by ID."""
    dashboard = _dashboard_svc.get_dashboard(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return DashboardResponse(**dashboard)


@router.put("/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(dashboard_id: str, request: UpdateDashboardRequest):
    """Update a dashboard."""
    widgets = [w.model_dump() for w in request.widgets] if request.widgets is not None else None
    # Merge user-supplied metadata with existing (preserve sharing etc.)
    merged_metadata = request.metadata
    if merged_metadata is not None:
        existing = _dashboard_svc.get_dashboard(dashboard_id)
        if existing and existing.get("metadata"):
            merged_metadata = {**existing["metadata"], **merged_metadata}

    dashboard = _dashboard_svc.update_dashboard(
        dashboard_id,
        name=request.name,
        description=request.description,
        widgets=widgets,
        filters=request.filters,
        theme=request.theme,
        refresh_interval=request.refresh_interval,
        metadata=merged_metadata,
    )
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return DashboardResponse(**dashboard)


@router.delete("/{dashboard_id}")
async def delete_dashboard(dashboard_id: str):
    """Delete a dashboard."""
    if not _dashboard_svc.delete_dashboard(dashboard_id):
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return {"status": "ok", "message": "Dashboard deleted"}


# ============================================
# Widget Endpoints
# ============================================

@router.post("/{dashboard_id}/widgets")
async def add_widget(dashboard_id: str, request: AddWidgetRequest):
    """Add a widget to a dashboard."""
    try:
        widget = _widget_svc.add_widget(
            dashboard_id,
            config=request.config.model_dump(),
            x=request.x,
            y=request.y,
            w=request.w,
            h=request.h,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return widget


@router.put("/{dashboard_id}/widgets/{widget_id}")
async def update_widget(
    dashboard_id: str,
    widget_id: str,
    request: UpdateWidgetRequest,
):
    """Update a widget."""
    widget = _widget_svc.update_widget(
        dashboard_id,
        widget_id,
        config=request.config.model_dump() if request.config else None,
        x=request.x,
        y=request.y,
        w=request.w,
        h=request.h,
    )
    if widget is None:
        raise HTTPException(status_code=404, detail="Widget not found")
    return widget


@router.delete("/{dashboard_id}/widgets/{widget_id}")
async def delete_widget(dashboard_id: str, widget_id: str):
    """Delete a widget from a dashboard."""
    if not _widget_svc.delete_widget(dashboard_id, widget_id):
        raise HTTPException(status_code=404, detail="Widget not found")
    return {"status": "ok", "message": "Widget deleted"}


# ============================================
# Snapshot & Embed Endpoints
# ============================================

@router.post("/{dashboard_id}/snapshot")
async def create_snapshot(
    dashboard_id: str,
    format: str = Query("png", pattern="^(png|pdf)$"),
):
    """Create a snapshot of the dashboard and trigger rendering."""
    try:
        snapshot = _snapshot_svc.create_snapshot(dashboard_id, format=format)
    except ValueError:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Render in a thread so the sync Playwright call doesn't block the
    # ASGI event loop.
    loop = asyncio.get_running_loop()
    rendered = await loop.run_in_executor(
        None, _snapshot_svc.render_snapshot, snapshot["id"]
    )

    return {
        "status": "ok",
        "snapshot_id": rendered["id"],
        "format": rendered["format"],
        "render_status": rendered.get("status", "pending"),
        "content_hash": rendered["content_hash"],
        "created_at": rendered["created_at"],
    }


@router.post("/{dashboard_id}/embed")
async def generate_embed_token(
    dashboard_id: str,
    expires_hours: int = Query(24, ge=1, le=720),
):
    """Generate an embed token for the dashboard."""
    try:
        result = _embed_svc.generate_embed_token(
            dashboard_id,
            expires_hours=expires_hours,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return {
        "status": "ok",
        "embed_token": result["embed_token"],
        "embed_url": result["embed_url"],
        "expires_hours": result["expires_hours"],
        "expires_at": result["expires_at"],
    }


# ============================================
# Analytics Endpoints
# ============================================

@router.post("/{dashboard_id}/query")
async def execute_widget_query(
    dashboard_id: str,
    widget_id: str = Query(...),
    filters: Optional[dict[str, Any]] = None,
):
    """Execute a widget's query with optional filters."""
    dashboard = _dashboard_svc.get_dashboard(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    widget = _widget_svc.get_widget(dashboard_id, widget_id)
    if widget is None:
        raise HTTPException(status_code=404, detail="Widget not found")

    config = widget.get("config", {})
    sql_query = config.get("query")
    connection_id = config.get("data_source")

    if not sql_query or not connection_id:
        return {
            "widget_id": widget_id,
            "data": [],
            "metadata": {"reason": "Widget has no query or data_source configured"},
        }

    try:
        result = _nl2sql_svc.execute_query(
            NL2SQLExecuteRequest(
                sql=sql_query,
                connection_id=connection_id,
            ),
        )
        return {
            "widget_id": widget_id,
            "data": result.rows,
            "metadata": {
                "columns": result.columns,
                "row_count": result.row_count,
                "execution_time_ms": result.execution_time_ms,
                "truncated": result.truncated,
            },
        }
    except Exception as exc:
        logger.warning(
            "widget_query_failed",
            extra={
                "event": "widget_query_failed",
                "dashboard_id": dashboard_id,
                "widget_id": widget_id,
                "error": str(exc),
            },
        )
        logger.exception("Widget query execution failed: %s", exc)
        raise HTTPException(status_code=422, detail="Query execution failed")


@router.post("/analytics/insights")
async def generate_insights(
    data: list[dict[str, Any]],
    context: Optional[str] = None,
):
    """Generate AI insights from data.

    Converts raw data dicts into DataSeries and delegates to the
    analytics InsightService.
    """
    if len(data) > MAX_ANALYTICS_ROWS:
        raise HTTPException(status_code=422, detail=f"Data exceeds maximum of {MAX_ANALYTICS_ROWS} rows")
    series = _dicts_to_series(data)
    if not series:
        raise HTTPException(status_code=422, detail="No numeric data series found in input")

    request = InsightsRequest(data=series, context=context)
    result = await insight_service.generate_insights(request)
    return result.model_dump()


@router.post("/analytics/trends")
async def predict_trends(
    data: list[dict[str, Any]],
    date_column: str,
    value_column: str,
    periods: int = Query(12, ge=1, le=100),
):
    """Predict future trends from time series data.

    Extracts the named value column from the data dicts and delegates
    to the analytics TrendService.
    """
    if len(data) > MAX_ANALYTICS_ROWS:
        raise HTTPException(status_code=422, detail=f"Data exceeds maximum of {MAX_ANALYTICS_ROWS} rows")
    values = [
        float(row[value_column])
        for row in data
        if value_column in row and _is_numeric(row[value_column])
    ]
    if len(values) < 2:
        raise HTTPException(status_code=422, detail=f"Need at least 2 numeric values in '{value_column}'")

    request = TrendRequest(
        data=DataSeries(name=value_column, values=values),
        forecast_periods=periods,
        method=ForecastMethod.AUTO,
    )
    result = await trend_service.analyze_trend(request)
    return result.model_dump()


@router.post("/analytics/anomalies")
async def detect_anomalies(
    data: list[dict[str, Any]],
    columns: list[str],
    method: str = Query("zscore", pattern="^(zscore|iqr|isolation_forest)$"),
):
    """Detect anomalies in data.

    Runs anomaly detection on each requested column via the
    analytics AnomalyService.  Results are aggregated across columns.

    Note: only ``zscore`` method is currently implemented in the
    analytics engine.  ``iqr`` and ``isolation_forest`` are accepted
    for forward compatibility but fall back to z-score with a warning.
    """
    if len(data) > MAX_ANALYTICS_ROWS:
        raise HTTPException(status_code=422, detail=f"Data exceeds maximum of {MAX_ANALYTICS_ROWS} rows")
    if method != "zscore":
        logger.warning(
            "anomaly_method_unsupported",
            extra={
                "event": "anomaly_method_unsupported",
                "requested": method,
                "fallback": "zscore",
            },
        )

    all_anomalies: list[dict[str, Any]] = []
    all_stats: dict[str, Any] = {}

    for col in columns:
        values = [
            float(row[col])
            for row in data
            if col in row and _is_numeric(row[col])
        ]
        if len(values) < 3:
            continue
        request = AnomaliesRequest(data=DataSeries(name=col, values=values))
        result = await anomaly_service.detect_anomalies(request)
        all_anomalies.extend([a.model_dump() for a in result.anomalies])
        all_stats[col] = result.baseline_stats

    return {
        "anomalies": all_anomalies,
        "statistics": all_stats,
        "method_used": "zscore",
        "narrative": (
            f"Detected {len(all_anomalies)} anomalies across {len(columns)} columns."
            if all_anomalies
            else "No anomalies detected."
        ),
    }


@router.post("/analytics/correlations")
async def find_correlations(
    data: list[dict[str, Any]],
    columns: Optional[list[str]] = None,
):
    """Find correlations between columns.

    Extracts numeric columns from the data dicts and delegates to the
    analytics CorrelationService.
    """
    if len(data) > MAX_ANALYTICS_ROWS:
        raise HTTPException(status_code=422, detail=f"Data exceeds maximum of {MAX_ANALYTICS_ROWS} rows")
    target_cols = columns
    if not target_cols and data:
        target_cols = _detect_numeric_columns(data)

    if not target_cols or len(target_cols) < 2:
        raise HTTPException(status_code=422, detail="Need at least 2 numeric columns for correlation analysis")

    series = []
    for col in target_cols:
        values = [
            float(row.get(col, float("nan")))
            if _is_numeric(row.get(col))
            else float("nan")
            for row in data
        ]
        series.append(DataSeries(name=col, values=values))

    request = CorrelationsRequest(data=series)
    result = await correlation_service.analyze_correlations(request)
    return result.model_dump()


# ── Helpers ──────────────────────────────────────────────────────────

def _is_numeric(value: Any) -> bool:
    """Return True if value can be cast to float."""
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    return False


def _detect_numeric_columns(data: list[dict[str, Any]]) -> list[str]:
    """Return column names that contain at least one numeric value across all rows."""
    if not data:
        return []
    all_keys: dict[str, bool] = {}
    for row in data:
        for k, v in row.items():
            if k not in all_keys and _is_numeric(v):
                all_keys[k] = True
    return list(all_keys)


def _dicts_to_series(data: list[dict[str, Any]]) -> list[DataSeries]:
    """Convert a list of row-dicts to DataSeries (one per numeric column)."""
    cols = _detect_numeric_columns(data)
    series = []
    for col in cols:
        values = [
            float(row[col]) if col in row and _is_numeric(row[col]) else float("nan")
            for row in data
        ]
        series.append(DataSeries(name=col, values=values))
    return series


# ============================================
# Layout, Refresh, Filters, Variables, What-If,
# Templates, Sharing, and Export Endpoints
# ============================================

@router.put("/{dashboard_id}/layout")
async def update_widget_layout(dashboard_id: str, request: UpdateLayoutRequest):
    """Update widget layout positions for all widgets in a dashboard."""
    dashboard = _dashboard_svc.get_dashboard(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    updated: list[dict[str, Any]] = []
    for item in request.items:
        widget = _widget_svc.update_widget(
            dashboard_id,
            item.widget_id,
            x=item.x,
            y=item.y,
            w=item.w,
            h=item.h,
        )
        if widget is None:
            raise HTTPException(
                status_code=404,
                detail=f"Widget {item.widget_id} not found",
            )
        updated.append(widget)

    logger.info(
        "layout_updated",
        extra={
            "event": "layout_updated",
            "dashboard_id": dashboard_id,
            "widget_count": len(updated),
        },
    )
    return {"status": "ok", "updated_widgets": len(updated), "layout": updated}


@router.post("/{dashboard_id}/refresh")
async def refresh_dashboard(dashboard_id: str):
    """Refresh all widgets in a dashboard.

    Retrieves the dashboard, iterates over its widgets, and returns
    a per-widget refresh status.
    """
    dashboard = _dashboard_svc.get_dashboard(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    widgets = dashboard.get("widgets", [])
    results: list[dict[str, Any]] = []

    for widget in widgets:
        widget_id = widget.get("id", "unknown")
        try:
            config = widget.get("config", {})
            sql_query = config.get("query")
            connection_id = config.get("data_source")

            if sql_query and connection_id:
                _nl2sql_svc.execute_query(
                    NL2SQLExecuteRequest(
                        sql=sql_query,
                        connection_id=connection_id,
                    ),
                )
                results.append({"widget_id": widget_id, "status": "refreshed"})
            else:
                results.append({"widget_id": widget_id, "status": "skipped", "reason": "no query configured"})
        except Exception as exc:
            logger.warning(
                "widget_refresh_failed",
                extra={
                    "event": "widget_refresh_failed",
                    "dashboard_id": dashboard_id,
                    "widget_id": widget_id,
                    "error": str(exc),
                },
            )
            results.append({"widget_id": widget_id, "status": "error", "error": str(exc)})

    logger.info(
        "dashboard_refreshed",
        extra={
            "event": "dashboard_refreshed",
            "dashboard_id": dashboard_id,
            "total_widgets": len(widgets),
        },
    )
    return {
        "status": "ok",
        "dashboard_id": dashboard_id,
        "total_widgets": len(widgets),
        "results": results,
    }


@router.post("/{dashboard_id}/filters")
async def add_dashboard_filter(dashboard_id: str, request: DashboardFilterRequest):
    """Add a filter to a dashboard."""
    dashboard = _dashboard_svc.get_dashboard(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    new_filter: dict[str, Any] = {
        "id": str(uuid.uuid4()),
        "field": request.field,
        "operator": request.operator,
        "value": request.value,
        "label": request.label or request.field,
    }

    filters = dashboard.get("filters", [])
    filters.append(new_filter)

    updated = _dashboard_svc.update_dashboard(dashboard_id, filters=filters)
    if updated is None:
        raise HTTPException(status_code=500, detail="Failed to update dashboard filters")

    logger.info(
        "filter_added",
        extra={
            "event": "filter_added",
            "dashboard_id": dashboard_id,
            "filter_id": new_filter["id"],
        },
    )
    return {"status": "ok", "filter": new_filter}


@router.put("/{dashboard_id}/filters/{filter_id}")
async def update_dashboard_filter(
    dashboard_id: str,
    filter_id: str,
    request: DashboardFilterRequest,
):
    """Update an existing filter on a dashboard."""
    dashboard = _dashboard_svc.get_dashboard(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    filters = dashboard.get("filters", [])
    found = False
    for i, f in enumerate(filters):
        if f.get("id") == filter_id:
            filters[i] = {
                "id": filter_id,
                "field": request.field,
                "operator": request.operator,
                "value": request.value,
                "label": request.label or request.field,
            }
            found = True
            break

    if not found:
        raise HTTPException(status_code=404, detail="Filter not found")

    updated = _dashboard_svc.update_dashboard(dashboard_id, filters=filters)
    if updated is None:
        raise HTTPException(status_code=500, detail="Failed to update dashboard filters")

    logger.info(
        "filter_updated",
        extra={
            "event": "filter_updated",
            "dashboard_id": dashboard_id,
            "filter_id": filter_id,
        },
    )
    return {"status": "ok", "filter": filters[i]}


@router.delete("/{dashboard_id}/filters/{filter_id}")
async def delete_dashboard_filter(dashboard_id: str, filter_id: str):
    """Delete a filter from a dashboard."""
    dashboard = _dashboard_svc.get_dashboard(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    filters = dashboard.get("filters", [])
    original_len = len(filters)
    filters = [f for f in filters if f.get("id") != filter_id]

    if len(filters) == original_len:
        raise HTTPException(status_code=404, detail="Filter not found")

    updated = _dashboard_svc.update_dashboard(dashboard_id, filters=filters)
    if updated is None:
        raise HTTPException(status_code=500, detail="Failed to update dashboard filters")

    logger.info(
        "filter_deleted",
        extra={
            "event": "filter_deleted",
            "dashboard_id": dashboard_id,
            "filter_id": filter_id,
        },
    )
    return {"status": "ok", "message": "Filter deleted"}


@router.put("/{dashboard_id}/variables/{variable_name}")
async def set_dashboard_variable(
    dashboard_id: str,
    variable_name: str,
    request: DashboardVariableRequest,
):
    """Set a dashboard variable value.

    Stores the variable in the dashboard's metadata dict so it can be
    referenced by widget queries and filters.
    """
    dashboard = _dashboard_svc.get_dashboard(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    metadata = dashboard.get("metadata", {})
    variables = metadata.get("variables", {})
    variables[variable_name] = request.value
    metadata["variables"] = variables

    updated = _dashboard_svc.update_dashboard(dashboard_id, metadata=metadata)
    if updated is None:
        raise HTTPException(status_code=500, detail="Failed to update dashboard variable")

    logger.info(
        "variable_set",
        extra={
            "event": "variable_set",
            "dashboard_id": dashboard_id,
            "variable_name": variable_name,
        },
    )
    return {
        "status": "ok",
        "variable_name": variable_name,
        "value": request.value,
    }


@router.post("/{dashboard_id}/what-if")
async def run_what_if_simulation(dashboard_id: str, request: WhatIfRequest):
    """Run a what-if simulation on dashboard data.

    Applies hypothetical variable changes and evaluates the requested
    metrics using the analytics services.
    """
    dashboard = _dashboard_svc.get_dashboard(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    simulation_results: dict[str, Any] = {}

    for metric in request.metrics_to_evaluate:
        try:
            # Collect baseline data from dashboard widgets for this metric
            baseline_values: list[float] = []
            for widget in dashboard.get("widgets", []):
                config = widget.get("config", {})
                if config.get("data_source") and config.get("query"):
                    result = _nl2sql_svc.execute_query(
                        NL2SQLExecuteRequest(
                            sql=config["query"],
                            connection_id=config["data_source"],
                        ),
                    )
                    for row in result.rows:
                        if metric in row and _is_numeric(row[metric]):
                            baseline_values.append(float(row[metric]))

            if len(baseline_values) < 2:
                simulation_results[metric] = {
                    "status": "insufficient_data",
                    "message": f"Not enough data points for metric '{metric}'",
                }
                continue

            # Apply variable changes as scaling factors
            adjusted_values = list(baseline_values)
            for var_name, change in request.variable_changes.items():
                if _is_numeric(change):
                    factor = float(change)
                    adjusted_values = [v * factor for v in adjusted_values]

            baseline_series = DataSeries(name=f"{metric}_baseline", values=baseline_values)
            adjusted_series = DataSeries(name=f"{metric}_adjusted", values=adjusted_values)

            baseline_request = InsightsRequest(data=[baseline_series], context="what-if baseline")
            adjusted_request = InsightsRequest(data=[adjusted_series], context="what-if adjusted")

            baseline_insights = await insight_service.generate_insights(baseline_request)
            adjusted_insights = await insight_service.generate_insights(adjusted_request)

            simulation_results[metric] = {
                "status": "ok",
                "baseline": baseline_insights.model_dump(),
                "adjusted": adjusted_insights.model_dump(),
                "variable_changes": request.variable_changes,
            }
        except Exception as exc:
            logger.warning(
                "what_if_metric_failed",
                extra={
                    "event": "what_if_metric_failed",
                    "dashboard_id": dashboard_id,
                    "metric": metric,
                    "error": str(exc),
                },
            )
            simulation_results[metric] = {
                "status": "error",
                "error": str(exc),
            }

    logger.info(
        "what_if_completed",
        extra={
            "event": "what_if_completed",
            "dashboard_id": dashboard_id,
            "metrics_evaluated": len(request.metrics_to_evaluate),
        },
    )
    return {
        "status": "ok",
        "dashboard_id": dashboard_id,
        "variable_changes": request.variable_changes,
        "results": simulation_results,
    }


@router.post("/{dashboard_id}/save-as-template")
async def save_dashboard_as_template(
    dashboard_id: str,
    name: Optional[str] = Query(None, min_length=1, max_length=255),
):
    """Save an existing dashboard as a reusable template."""
    dashboard = _dashboard_svc.get_dashboard(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    template_id = str(uuid.uuid4())
    template: dict[str, Any] = {
        "id": template_id,
        "name": name or f"{dashboard.get('name', 'Dashboard')} Template",
        "description": dashboard.get("description"),
        "widgets": dashboard.get("widgets", []),
        "filters": dashboard.get("filters", []),
        "theme": dashboard.get("theme"),
        "source_dashboard_id": dashboard_id,
    }

    _dashboard_svc.save_template(template)

    logger.info(
        "template_saved",
        extra={
            "event": "template_saved",
            "dashboard_id": dashboard_id,
            "template_id": template_id,
        },
    )
    return {"status": "ok", "template_id": template_id, "template": template}


@router.post("/{dashboard_id}/share")
async def share_dashboard(dashboard_id: str, request: ShareDashboardRequest):
    """Share a dashboard with other users."""
    dashboard = _dashboard_svc.get_dashboard(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    metadata = dashboard.get("metadata", {})
    sharing = metadata.get("sharing", [])

    for user in request.users:
        # Update existing entry or add new one
        existing = next((s for s in sharing if s.get("user") == user), None)
        if existing:
            existing["permission"] = request.permission
        else:
            sharing.append({
                "id": str(uuid.uuid4()),
                "user": user,
                "permission": request.permission,
            })

    metadata["sharing"] = sharing
    updated = _dashboard_svc.update_dashboard(dashboard_id, metadata=metadata)
    if updated is None:
        raise HTTPException(status_code=500, detail="Failed to share dashboard")

    logger.info(
        "dashboard_shared",
        extra={
            "event": "dashboard_shared",
            "dashboard_id": dashboard_id,
            "shared_with": request.users,
            "permission": request.permission,
        },
    )
    return {
        "status": "ok",
        "dashboard_id": dashboard_id,
        "shared_with": request.users,
        "permission": request.permission,
    }


@router.get("/{dashboard_id}/export")
async def export_dashboard(dashboard_id: str):
    """Export a complete dashboard and all its data as JSON."""
    dashboard = _dashboard_svc.get_dashboard(dashboard_id)
    if dashboard is None:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    widget_data: list[dict[str, Any]] = []
    for widget in dashboard.get("widgets", []):
        widget_id = widget.get("id", "unknown")
        config = widget.get("config", {})
        sql_query = config.get("query")
        connection_id = config.get("data_source")

        entry: dict[str, Any] = {
            "widget_id": widget_id,
            "config": config,
            "x": widget.get("x"),
            "y": widget.get("y"),
            "w": widget.get("w"),
            "h": widget.get("h"),
        }

        if sql_query and connection_id:
            try:
                result = _nl2sql_svc.execute_query(
                    NL2SQLExecuteRequest(
                        sql=sql_query,
                        connection_id=connection_id,
                    ),
                )
                entry["data"] = {
                    "rows": result.rows,
                    "columns": result.columns,
                    "row_count": result.row_count,
                }
            except Exception as exc:
                logger.warning(
                    "export_widget_query_failed",
                    extra={
                        "event": "export_widget_query_failed",
                        "dashboard_id": dashboard_id,
                        "widget_id": widget_id,
                        "error": str(exc),
                    },
                )
                entry["data"] = {"error": str(exc)}
        else:
            entry["data"] = None

        widget_data.append(entry)

    logger.info(
        "dashboard_exported",
        extra={
            "event": "dashboard_exported",
            "dashboard_id": dashboard_id,
            "widget_count": len(widget_data),
        },
    )
    return {
        "dashboard_id": dashboard_id,
        "name": dashboard.get("name"),
        "description": dashboard.get("description"),
        "theme": dashboard.get("theme"),
        "filters": dashboard.get("filters", []),
        "refresh_interval": dashboard.get("refresh_interval"),
        "metadata": dashboard.get("metadata", {}),
        "widgets": widget_data,
        "created_at": dashboard.get("created_at"),
        "updated_at": dashboard.get("updated_at"),
    }


# ============================================
# Auto-Compose (Widget Intelligence)
# ============================================

class AutoComposeRequest(BaseModel):
    """Auto-compose widgets for a dashboard using AI selection."""

    query: str = Field(..., min_length=1, max_length=2000)
    query_type: str = Field(default="overview")
    max_widgets: int = Field(default=8, ge=1, le=20)


@router.post("/{dashboard_id}/auto-compose")
async def auto_compose_dashboard(dashboard_id: str, req: AutoComposeRequest):
    """Use AI to auto-compose widgets for an existing dashboard."""
    dashboard = _dashboard_svc.get_dashboard(dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    from backend.app.services.widget_intelligence.service import WidgetIntelligenceService
    intelligence_svc = WidgetIntelligenceService()

    widgets = intelligence_svc.select_widgets(
        query=req.query,
        query_type=req.query_type,
        max_widgets=req.max_widgets,
    )
    layout = intelligence_svc.pack_grid(widgets)

    new_widgets = []
    for w, cell in zip(widgets, layout.get("cells", [])):
        demo_data = intelligence_svc.get_demo_data(w["scenario"])
        new_widgets.append({
            "id": w["id"],
            "config": {
                "type": w["scenario"],
                "title": w.get("question", w["scenario"]),
                "variant": w["variant"],
                "scenario": w["scenario"],
            },
            "x": cell["col_start"] - 1,
            "y": cell["row_start"] - 1,
            "w": cell["col_end"] - cell["col_start"],
            "h": cell["row_end"] - cell["row_start"],
            "data": demo_data,
        })

    existing_widgets = dashboard.get("widgets", [])
    updated = _dashboard_svc.update_dashboard(
        dashboard_id,
        widgets=existing_widgets + new_widgets,
    )
    return {"dashboard": updated, "added_widgets": len(new_widgets)}
