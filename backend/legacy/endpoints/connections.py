from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.legacy.core.config import get_settings
from backend.legacy.schemas.connection_schema import ConnectionUpsertPayload, TestPayload
from backend.legacy.services.connection_service import (
    delete_connection,
    healthcheck_connection,
    list_connections,
    test_connection,
    upsert_connection,
)
from backend.legacy.services.connection_inspector import get_connection_schema, get_connection_table_preview

router = APIRouter()


def _correlation(request: Request) -> str | None:
    return getattr(request.state, "correlation_id", None)


@router.post("/connections/test")
def test_connection_route(payload: TestPayload, request: Request, settings=Depends(get_settings)):
    result = test_connection(payload)
    result["correlation_id"] = _correlation(request)
    return result


@router.get("/connections")
def list_connections_route(request: Request):
    return {"status": "ok", "connections": list_connections(), "correlation_id": _correlation(request)}


@router.post("/connections")
def upsert_connection_route(payload: ConnectionUpsertPayload, request: Request):
    record = upsert_connection(payload)
    return {"status": "ok", "connection": record, "correlation_id": _correlation(request)}


@router.delete("/connections/{connection_id}")
def delete_connection_route(connection_id: str, request: Request):
    removed = delete_connection(connection_id)
    if not removed:
        raise HTTPException(status_code=404, detail={"status": "error", "code": "connection_not_found", "message": "Connection not found."})
    return {"status": "ok", "connection_id": connection_id, "correlation_id": _correlation(request)}


@router.post("/connections/{connection_id}/health")
def healthcheck_connection_route(connection_id: str, request: Request):
    result = healthcheck_connection(connection_id)
    result["correlation_id"] = _correlation(request)
    return result


@router.get("/connections/{connection_id}/schema")
def connection_schema_route(
    connection_id: str,
    request: Request,
    include_row_counts: bool = True,
    include_foreign_keys: bool = True,
    sample_rows: int = 0,
):
    result = get_connection_schema(
        connection_id,
        include_row_counts=include_row_counts,
        include_foreign_keys=include_foreign_keys,
        sample_rows=sample_rows,
    )
    result["correlation_id"] = _correlation(request)
    return result


@router.get("/connections/{connection_id}/preview")
def connection_preview_route(
    connection_id: str,
    request: Request,
    table: str,
    limit: int = 10,
    offset: int = 0,
):
    result = get_connection_table_preview(
        connection_id,
        table=table,
        limit=limit,
        offset=offset,
    )
    result["correlation_id"] = _correlation(request)
    return result
