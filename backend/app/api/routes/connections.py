from __future__ import annotations

import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from backend.app.services.security import require_api_key
from backend.app.services.errors import AppError
from backend.app.schemas.connections import ConnectionTestRequest, ConnectionUpsertRequest
from backend.app.services.connections.service import ConnectionService

logger = logging.getLogger("neura.api.connections")

router = APIRouter(dependencies=[Depends(require_api_key)])

# SQL identifier pattern: alphanumeric + underscores, optionally schema-qualified
_SQL_IDENTIFIER_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$")


def get_service() -> ConnectionService:
    return ConnectionService()


def _corr(request: Request) -> str | None:
    return getattr(request.state, "correlation_id", None)


def _handle_connection_error(exc: Exception, operation: str):
    logger.exception(
        "connection_operation_failed",
        extra={"event": "connection_operation_failed", "operation": operation},
    )
    raise HTTPException(status_code=500, detail=f"Connection {operation} failed")


@router.post("/test")
async def test_connection(
    payload: ConnectionTestRequest,
    request: Request,
    svc: ConnectionService = Depends(get_service),
):
    try:
        return {"status": "ok", **svc.test(payload, _corr(request))}
    except (HTTPException, AppError):
        raise
    except Exception as exc:
        _handle_connection_error(exc, "test")


@router.get("")
async def list_connections(
    request: Request,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    svc: ConnectionService = Depends(get_service),
):
    try:
        connections = svc.list(_corr(request))
        total = len(connections)
        connections = connections[offset : offset + limit]
        return {"status": "ok", "connections": connections, "total": total, "correlation_id": _corr(request)}
    except (HTTPException, AppError):
        raise
    except Exception as exc:
        _handle_connection_error(exc, "list")


@router.post("")
async def upsert_connection(
    payload: ConnectionUpsertRequest,
    request: Request,
    svc: ConnectionService = Depends(get_service),
):
    try:
        connection = svc.upsert(payload, _corr(request))
        return {"status": "ok", "connection": connection.model_dump(), "correlation_id": _corr(request)}
    except (HTTPException, AppError):
        raise
    except Exception as exc:
        _handle_connection_error(exc, "upsert")


@router.delete("/{connection_id}")
async def delete_connection(
    connection_id: str,
    request: Request,
    svc: ConnectionService = Depends(get_service),
):
    try:
        # Verify existence before deleting
        existing = svc.repo.get(connection_id) if hasattr(svc.repo, "get") else None
        if existing is None and hasattr(svc.repo, "get"):
            raise HTTPException(status_code=404, detail="Connection not found")
        svc.delete(connection_id)
        return {"status": "ok", "connection_id": connection_id, "correlation_id": _corr(request)}
    except (HTTPException, AppError):
        raise
    except Exception as exc:
        _handle_connection_error(exc, "delete")


@router.post("/{connection_id}/health")
async def healthcheck_connection(
    connection_id: str,
    request: Request,
    svc: ConnectionService = Depends(get_service),
):
    """Verify a saved connection is still accessible."""
    try:
        result = svc.healthcheck(connection_id, _corr(request))
        return {
            "status": "ok",
            "connection_id": result.get("connection_id"),
            "latency_ms": result.get("latency_ms"),
            "correlation_id": _corr(request),
        }
    except (HTTPException, AppError):
        raise
    except Exception as exc:
        _handle_connection_error(exc, "healthcheck")


@router.get("/{connection_id}/schema")
async def connection_schema(
    connection_id: str,
    request: Request,
    include_row_counts: bool = Query(True),
    include_foreign_keys: bool = Query(True),
    sample_rows: int = Query(0, ge=0, le=25),
):
    from backend.legacy.services.connection_inspector import get_connection_schema

    try:
        result = get_connection_schema(
            connection_id,
            include_row_counts=include_row_counts,
            include_foreign_keys=include_foreign_keys,
            sample_rows=sample_rows,
        )
        result["correlation_id"] = _corr(request)
        return result
    except (HTTPException, AppError):
        raise
    except Exception as exc:
        _handle_connection_error(exc, "schema")


@router.get("/{connection_id}/preview")
async def connection_preview(
    connection_id: str,
    request: Request,
    table: str = Query(..., min_length=1, max_length=255),
    limit: int = Query(10, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    from backend.legacy.services.connection_inspector import get_connection_table_preview

    # Validate table name is a safe SQL identifier
    if not _SQL_IDENTIFIER_RE.match(table):
        raise HTTPException(
            status_code=400,
            detail="Invalid table name. Must be a valid SQL identifier (letters, digits, underscores).",
        )

    try:
        result = get_connection_table_preview(
            connection_id,
            table=table,
            limit=limit,
            offset=offset,
        )
        result["correlation_id"] = _corr(request)
        return result
    except (HTTPException, AppError):
        raise
    except Exception as exc:
        _handle_connection_error(exc, "preview")
