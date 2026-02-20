"""API routes for Natural Language to SQL feature."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from backend.app.services.security import require_api_key
from backend.app.schemas.nl2sql import (
    NL2SQLGenerateRequest,
    NL2SQLExecuteRequest,
    NL2SQLSaveRequest,
)
from backend.app.services.nl2sql.service import NL2SQLService

router = APIRouter(dependencies=[Depends(require_api_key)])


def get_service() -> NL2SQLService:
    return NL2SQLService()


@router.post("/generate")
async def generate_sql(
    payload: NL2SQLGenerateRequest,
    request: Request,
    svc: NL2SQLService = Depends(get_service),
):
    """Generate SQL from a natural language question."""
    correlation_id = getattr(request.state, "correlation_id", None)
    result = svc.generate_sql(payload, correlation_id)
    return {
        "status": "ok",
        "sql": result.sql,
        "explanation": result.explanation,
        "confidence": result.confidence,
        "warnings": result.warnings,
        "original_question": result.original_question,
        "correlation_id": correlation_id,
    }


@router.post("/execute")
async def execute_query(
    payload: NL2SQLExecuteRequest,
    request: Request,
    svc: NL2SQLService = Depends(get_service),
):
    """Execute a SQL query and return results."""
    correlation_id = getattr(request.state, "correlation_id", None)
    result = svc.execute_query(payload, correlation_id)
    return {
        "status": "ok",
        "columns": result.columns,
        "rows": result.rows,
        "row_count": result.row_count,
        "total_count": result.total_count,
        "execution_time_ms": result.execution_time_ms,
        "truncated": result.truncated,
        "correlation_id": correlation_id,
    }


@router.post("/explain")
async def explain_query(
    request: Request,
    sql: str = Query(..., min_length=1, max_length=10000),
    svc: NL2SQLService = Depends(get_service),
):
    """Get a natural language explanation of a SQL query."""
    correlation_id = getattr(request.state, "correlation_id", None)
    explanation = svc.explain_query(sql, correlation_id)
    return {
        "status": "ok",
        "explanation": explanation,
        "correlation_id": correlation_id,
    }


@router.post("/save")
async def save_query(
    payload: NL2SQLSaveRequest,
    request: Request,
    svc: NL2SQLService = Depends(get_service),
):
    """Save a query as a reusable data source."""
    correlation_id = getattr(request.state, "correlation_id", None)
    saved = svc.save_query(payload, correlation_id)
    return {
        "status": "ok",
        "query": saved.model_dump(mode="json"),
        "correlation_id": correlation_id,
    }


@router.get("/saved")
async def list_saved_queries(
    request: Request,
    connection_id: Optional[str] = Query(None, max_length=64),
    tags: Optional[List[str]] = Query(None),
    svc: NL2SQLService = Depends(get_service),
):
    """List saved queries."""
    correlation_id = getattr(request.state, "correlation_id", None)
    queries = svc.list_saved_queries(connection_id=connection_id, tags=tags)
    return {
        "status": "ok",
        "queries": [q.model_dump(mode="json") for q in queries],
        "correlation_id": correlation_id,
    }


@router.get("/saved/{query_id}")
async def get_saved_query(
    query_id: str,
    request: Request,
    svc: NL2SQLService = Depends(get_service),
):
    """Get a saved query by ID."""
    correlation_id = getattr(request.state, "correlation_id", None)
    query = svc.get_saved_query(query_id)
    if not query:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "code": "not_found",
                "message": "Query not found",
            },
        )
    return {
        "status": "ok",
        "query": query.model_dump(mode="json"),
        "correlation_id": correlation_id,
    }


@router.delete("/saved/{query_id}")
async def delete_saved_query(
    query_id: str,
    request: Request,
    svc: NL2SQLService = Depends(get_service),
):
    """Delete a saved query."""
    correlation_id = getattr(request.state, "correlation_id", None)
    deleted = svc.delete_saved_query(query_id)
    return {
        "status": "ok" if deleted else "error",
        "deleted": deleted,
        "query_id": query_id,
        "correlation_id": correlation_id,
    }


@router.get("/history")
async def get_query_history(
    request: Request,
    connection_id: Optional[str] = Query(None, max_length=64),
    limit: int = Query(50, ge=1, le=200),
    svc: NL2SQLService = Depends(get_service),
):
    """Get query history."""
    correlation_id = getattr(request.state, "correlation_id", None)
    history = svc.get_query_history(connection_id=connection_id, limit=limit)
    return {
        "status": "ok",
        "history": [h.model_dump(mode="json") for h in history],
        "correlation_id": correlation_id,
    }


@router.delete("/history/{entry_id}")
async def delete_query_history_entry(
    entry_id: str,
    request: Request,
    svc: NL2SQLService = Depends(get_service),
):
    """Delete a query history entry."""
    correlation_id = getattr(request.state, "correlation_id", None)
    deleted = svc.delete_query_history_entry(entry_id)
    return {
        "status": "ok" if deleted else "error",
        "deleted": deleted,
        "entry_id": entry_id,
        "correlation_id": correlation_id,
    }
