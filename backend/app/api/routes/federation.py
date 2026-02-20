"""API routes for Cross-Database Federation feature."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from backend.app.services.security import require_api_key
from backend.app.services.errors import AppError

logger = logging.getLogger("neura.api.federation")
from backend.app.schemas.federation import VirtualSchemaCreate, SuggestJoinsRequest, FederatedQueryRequest
from backend.app.services.federation.service import FederationService

router = APIRouter(dependencies=[Depends(require_api_key)])


def get_service() -> FederationService:
    return FederationService()


@router.post("/schemas")
async def create_virtual_schema(
    payload: VirtualSchemaCreate,
    request: Request,
    svc: FederationService = Depends(get_service),
):
    """Create a virtual schema spanning multiple databases."""
    correlation_id = getattr(request.state, "correlation_id", None)
    try:
        schema = svc.create_virtual_schema(payload, correlation_id)
    except (HTTPException, AppError):
        raise
    except Exception as exc:
        logger.exception("federation_create_schema_failed", extra={"event": "federation_create_schema_failed"})
        raise HTTPException(status_code=500, detail="Failed to create virtual schema")
    return {"status": "ok", "schema": schema.model_dump(), "correlation_id": correlation_id}


@router.get("/schemas")
async def list_virtual_schemas(
    request: Request,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    svc: FederationService = Depends(get_service),
):
    """List all virtual schemas."""
    correlation_id = getattr(request.state, "correlation_id", None)
    all_schemas = svc.list_virtual_schemas()
    page = all_schemas[offset:offset + limit]
    return {
        "status": "ok",
        "schemas": [s.model_dump() for s in page],
        "total": len(all_schemas),
        "correlation_id": correlation_id,
    }


@router.get("/schemas/{schema_id}")
async def get_virtual_schema(
    schema_id: str,
    request: Request,
    svc: FederationService = Depends(get_service),
):
    """Get a virtual schema by ID."""
    correlation_id = getattr(request.state, "correlation_id", None)
    schema = svc.get_virtual_schema(schema_id)
    if not schema:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": f"Schema {schema_id} not found"})
    return {"status": "ok", "schema": schema.model_dump(), "correlation_id": correlation_id}


@router.delete("/schemas/{schema_id}")
async def delete_virtual_schema(
    schema_id: str,
    request: Request,
    svc: FederationService = Depends(get_service),
):
    """Delete a virtual schema."""
    correlation_id = getattr(request.state, "correlation_id", None)
    deleted = svc.delete_virtual_schema(schema_id)
    if not deleted:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": f"Schema {schema_id} not found"})
    return {"status": "ok", "deleted": True, "correlation_id": correlation_id}


@router.post("/suggest-joins")
async def suggest_joins(
    payload: SuggestJoinsRequest,
    request: Request,
    svc: FederationService = Depends(get_service),
):
    """Get AI-suggested joins between tables in different connections."""
    correlation_id = getattr(request.state, "correlation_id", None)
    try:
        suggestions = svc.suggest_joins(payload.connection_ids, correlation_id)
    except (HTTPException, AppError):
        raise
    except Exception as exc:
        logger.exception("federation_suggest_joins_failed", extra={"event": "federation_suggest_joins_failed"})
        raise HTTPException(status_code=500, detail="Join suggestion failed")
    return {"status": "ok", "suggestions": [s.model_dump() for s in suggestions], "correlation_id": correlation_id}


@router.post("/query")
async def execute_federated_query(
    payload: FederatedQueryRequest,
    request: Request,
    svc: FederationService = Depends(get_service),
):
    """Execute a federated query across multiple databases."""
    correlation_id = getattr(request.state, "correlation_id", None)
    try:
        result = svc.execute_query(payload, correlation_id)
    except (HTTPException, AppError):
        raise
    except Exception as exc:
        logger.exception("federation_query_failed", extra={"event": "federation_query_failed"})
        raise HTTPException(status_code=500, detail="Federated query execution failed")
    return {"status": "ok", "result": result, "correlation_id": correlation_id}
