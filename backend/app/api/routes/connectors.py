"""
Connector API Routes - Database and cloud storage connector endpoints.

All connector-connection CRUD is backed by the persistent StateStore
(``state["connectors"]`` / ``state["connector_credentials"]``).
No in-memory dicts — connections survive server restarts.
"""

from __future__ import annotations

import io
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Path, Query, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.app.services.security import require_api_key
from ...services.connectors import (
    get_connector,
    list_connectors as list_available_connectors,
    ConnectorBase,
    ConnectorType,
)
from backend.app.services.validation import is_read_only_sql, is_safe_external_url
from backend.app.services.state_access import state_store

logger = logging.getLogger("neura.api.connectors")

# Credential keys that must never appear in API responses
_SENSITIVE_KEYS = frozenset({
    "password", "secret", "token", "access_token", "refresh_token",
    "api_key", "private_key", "client_secret", "credentials",
})


def _redact_config(config: dict[str, Any] | None) -> dict[str, Any]:
    """Return a copy of config with sensitive values replaced by '***'."""
    if not config:
        return {}
    redacted = {}
    for k, v in config.items():
        if k.lower() in _SENSITIVE_KEYS:
            redacted[k] = "***"
        elif isinstance(v, dict):
            redacted[k] = _redact_config(v)
        else:
            redacted[k] = v
    return redacted

router = APIRouter(tags=["connectors"], dependencies=[Depends(require_api_key)])


# ============================================
# Schemas
# ============================================

class ConnectorInfo(BaseModel):
    """Connector type information."""

    id: str
    name: str
    type: str
    auth_types: list[str]
    capabilities: list[str]
    free_tier: bool
    config_schema: dict[str, Any]


class CreateConnectionRequest(BaseModel):
    """Create connection request."""

    name: str = Field(..., min_length=1, max_length=255)
    connector_type: str
    config: dict[str, Any]


class ConnectionResponse(BaseModel):
    """Connection response."""

    id: str
    name: str
    connector_type: str
    status: str
    created_at: str
    last_used: Optional[str]
    latency_ms: Optional[float]


class TestConnectionRequest(BaseModel):
    """Test connection request."""

    connector_type: str
    config: dict[str, Any]


class TestConnectionResponse(BaseModel):
    """Test connection response."""

    success: bool
    latency_ms: Optional[float]
    error: Optional[str]
    details: Optional[dict[str, Any]]


class QueryRequest(BaseModel):
    """Query request."""

    query: str
    parameters: Optional[dict[str, Any]] = None
    limit: int = Field(1000, ge=1, le=10000)


class QueryResponse(BaseModel):
    """Query response."""

    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    execution_time_ms: float
    truncated: bool
    error: Optional[str]


# ---------------------------------------------------------------------------
# Persistent connection helpers (StateStore-backed)
# ---------------------------------------------------------------------------

def _store_get_all() -> dict[str, dict]:
    """Return all connector connections from state."""
    with state_store.transaction() as state:
        return dict(state.get("connectors", {}))


def _store_get(connection_id: str) -> dict | None:
    """Return a single connector connection or *None*."""
    with state_store.transaction() as state:
        return state.get("connectors", {}).get(connection_id)


def _store_put(connection: dict) -> None:
    """Persist a connector connection (create or update).

    Raw config (which may contain credentials) is stored separately in
    ``connector_credentials`` and stripped from the main record to avoid
    accidental leakage through list/get endpoints.
    """
    with state_store.transaction() as state:
        # Store credentials separately
        if "config" in connection:
            state.setdefault("connector_credentials", {})[connection["id"]] = connection["config"]
        # Store connection metadata without raw config
        safe_record = {k: v for k, v in connection.items() if k != "config"}
        safe_record["has_credentials"] = "config" in connection
        state.setdefault("connectors", {})[connection["id"]] = safe_record


def _store_get_config(connection_id: str) -> dict[str, Any]:
    """Retrieve raw config (credentials) for a connection."""
    with state_store.transaction() as state:
        return state.get("connector_credentials", {}).get(connection_id, {})


def _store_delete(connection_id: str) -> bool:
    """Remove a connector connection. Return *True* if found."""
    with state_store.transaction() as state:
        removed = state.get("connectors", {}).pop(connection_id, None) is not None
        state.get("connector_credentials", {}).pop(connection_id, None)
        return removed


# ============================================
# Connector Discovery Endpoints
# ============================================

@router.get("/types")
async def list_connector_types() -> list[ConnectorInfo]:
    """List all available connector types."""
    return [ConnectorInfo(**c) for c in list_available_connectors()]


@router.get("/types/{connector_type}")
async def get_connector_type(connector_type: str) -> ConnectorInfo:
    """Get information about a specific connector type."""
    connectors = list_available_connectors()
    for c in connectors:
        if c["id"] == connector_type:
            return ConnectorInfo(**c)
    raise HTTPException(status_code=404, detail="Connector type not found")


@router.get("/types/by-category/{category}")
async def list_connectors_by_category(
    category: str = Path(..., pattern="^(database|cloud_storage|productivity|api)$"),
) -> list[ConnectorInfo]:
    """List connectors by category."""
    connectors = list_available_connectors()
    return [ConnectorInfo(**c) for c in connectors if c["type"] == category]


# ============================================
# Connection Test Endpoints
# ============================================

@router.post("/{connector_type}/test", response_model=TestConnectionResponse)
async def test_connection(
    connector_type: str,
    request: TestConnectionRequest,
):
    """Test a connection configuration."""
    try:
        connector = get_connector(connector_type, request.config)
        result = await connector.test_connection()
        return TestConnectionResponse(
            success=result.success,
            latency_ms=result.latency_ms,
            error=result.error,
            details=result.details,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e) or "Invalid connector configuration")
    except Exception as e:
        logger.exception("connector_test_failed", extra={"connector_type": connector_type})
        return TestConnectionResponse(
            success=False,
            latency_ms=None,
            error=f"{type(e).__name__}: Connection test failed",
            details=None,
        )


# ============================================
# Connection CRUD Endpoints
# ============================================

@router.post("/{connector_type}/connect", response_model=ConnectionResponse)
async def create_connection(
    connector_type: str,
    request: CreateConnectionRequest,
):
    """Create and save a new connection."""
    try:
        # Test connection first
        connector = get_connector(connector_type, request.config)
        test_result = await connector.test_connection()

        if not test_result.success:
            detail = "Connection failed"
            if getattr(test_result, "error", None):
                detail = f"{detail}: {test_result.error}"
            raise HTTPException(
                status_code=400,
                detail=detail,
            )

        now = datetime.now(timezone.utc).isoformat()
        connection = {
            "id": str(uuid.uuid4()),
            "name": request.name,
            "connector_type": connector_type,
            "config": request.config,
            "status": "connected",
            "created_at": now,
            "last_used": now,
            "latency_ms": test_result.latency_ms,
        }
        _store_put(connection)

        return ConnectionResponse(
            id=connection["id"],
            name=connection["name"],
            connector_type=connection["connector_type"],
            status=connection["status"],
            created_at=connection["created_at"],
            last_used=connection["last_used"],
            latency_ms=connection["latency_ms"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e) or "Invalid connection configuration")


@router.get("")
async def list_connections(
    connector_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List saved connections."""
    connections = list(_store_get_all().values())
    if connector_type:
        connections = [c for c in connections if c["connector_type"] == connector_type]
    connections.sort(key=lambda c: c["created_at"], reverse=True)
    return {
        "connections": [
            ConnectionResponse(
                id=c["id"],
                name=c["name"],
                connector_type=c["connector_type"],
                status=c["status"],
                created_at=c["created_at"],
                last_used=c.get("last_used"),
                latency_ms=c.get("latency_ms"),
            )
            for c in connections[offset:offset + limit]
        ],
        "total": len(connections),
        "offset": offset,
        "limit": limit,
    }


@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(
    connection_id: str = Path(..., min_length=36, max_length=36, pattern="^[0-9a-f-]{36}$"),
):
    """Get a connection by ID.

    Note: connection_id is restricted to UUID format to disambiguate from
    /{connector_type}/... routes which use short alphanumeric names.
    """
    c = _store_get(connection_id)
    if c is None:
        raise HTTPException(status_code=404, detail="Connection not found")
    return ConnectionResponse(
        id=c["id"],
        name=c["name"],
        connector_type=c["connector_type"],
        status=c["status"],
        created_at=c["created_at"],
        last_used=c.get("last_used"),
        latency_ms=c.get("latency_ms"),
    )


@router.delete("/{connection_id}")
async def delete_connection(
    connection_id: str = Path(..., min_length=36, max_length=36, pattern="^[0-9a-f-]{36}$"),
):
    """Delete a connection."""
    if not _store_delete(connection_id):
        raise HTTPException(status_code=404, detail="Connection not found")
    return {"status": "ok", "message": "Connection deleted"}


# ============================================
# Connection Health & Schema Endpoints
# ============================================

@router.post("/{connection_id}/health", response_model=TestConnectionResponse)
async def check_connection_health(
    connection_id: str = Path(..., min_length=36, max_length=36, pattern="^[0-9a-f-]{36}$"),
):
    """Check if a connection is healthy."""
    conn = _store_get(connection_id)
    if conn is None:
        raise HTTPException(status_code=404, detail="Connection not found")

    config = _store_get_config(connection_id)
    try:
        connector = get_connector(conn["connector_type"], config)
        result = await connector.test_connection()

        # Persist updated health status
        conn["status"] = "connected" if result.success else "error"
        conn["latency_ms"] = result.latency_ms
        conn["config"] = config  # include config so _store_put can re-persist credentials
        _store_put(conn)

        return TestConnectionResponse(
            success=result.success,
            latency_ms=result.latency_ms,
            error=result.error,
            details=result.details,
        )
    except Exception as e:
        logger.exception("connector_health_failed", extra={"connection_id": connection_id})
        conn["status"] = "error"
        _store_put(conn)
        return TestConnectionResponse(
            success=False,
            latency_ms=None,
            error=f"{type(e).__name__}: Health check failed",
            details=None,
        )


@router.get("/{connection_id}/schema")
async def get_connection_schema(
    connection_id: str = Path(..., min_length=36, max_length=36, pattern="^[0-9a-f-]{36}$"),
):
    """Get schema information for a connection."""
    conn = _store_get(connection_id)
    if conn is None:
        raise HTTPException(status_code=404, detail="Connection not found")
    config = _store_get_config(connection_id)
    connector = None
    try:
        connector = get_connector(conn["connector_type"], config)
        await connector.connect()
        schema = await connector.discover_schema()
        return {
            "tables": [t.model_dump() for t in schema.tables],
            "views": [v.model_dump() for v in schema.views],
            "schemas": schema.schemas,
        }
    except Exception as e:
        logger.exception("connector_schema_failed", extra={"connection_id": connection_id})
        raise HTTPException(status_code=500, detail="Failed to retrieve schema")
    finally:
        if connector is not None:
            try:
                await connector.disconnect()
            except Exception:
                pass


# ============================================
# Query Execution Endpoints
# ============================================

@router.post("/{connection_id}/query", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    connection_id: str = Path(..., min_length=36, max_length=36, pattern="^[0-9a-f-]{36}$"),
):
    """Execute a query on a connection."""
    # Validate query is read-only before execution
    is_safe, sql_error = is_read_only_sql(request.query)
    if not is_safe:
        raise HTTPException(status_code=400, detail=sql_error)

    conn = _store_get(connection_id)
    if conn is None:
        raise HTTPException(status_code=404, detail="Connection not found")

    config = _store_get_config(connection_id)
    connector = None
    try:
        connector = get_connector(conn["connector_type"], config)
        await connector.connect()
        result = await connector.execute_query(
            request.query,
            request.parameters,
            request.limit,
        )

        # Persist last-used timestamp
        conn["last_used"] = datetime.now(timezone.utc).isoformat()
        conn["config"] = config  # include config so _store_put can re-persist credentials
        _store_put(conn)

        return QueryResponse(
            columns=result.columns,
            rows=result.rows,
            row_count=result.row_count,
            execution_time_ms=result.execution_time_ms,
            truncated=result.truncated,
            error=result.error,
        )
    except Exception as e:
        logger.exception("connector_query_failed", extra={"connection_id": connection_id})
        return QueryResponse(
            columns=[],
            rows=[],
            row_count=0,
            execution_time_ms=0.0,
            truncated=False,
            error=f"{type(e).__name__}: Query execution failed",
        )
    finally:
        if connector is not None:
            try:
                await connector.disconnect()
            except Exception:
                pass


# ============================================
# OAuth Endpoints
# ============================================

def _validate_redirect_uri(redirect_uri: str) -> None:
    """Validate redirect_uri is a safe external URL (not internal/private)."""
    is_safe, reason = is_safe_external_url(redirect_uri)
    if not is_safe:
        raise HTTPException(
            status_code=400,
            detail="Invalid redirect_uri",
        )


def _redact_tokens(tokens: dict[str, Any] | None) -> dict[str, Any]:
    """Redact sensitive fields from OAuth tokens, keeping only metadata."""
    if not tokens:
        return {}
    redacted = {}
    for k, v in tokens.items():
        if k.lower() in _SENSITIVE_KEYS or "token" in k.lower():
            redacted[k] = "***"
        else:
            redacted[k] = v
    # Indicate tokens were received but redacted
    redacted["_redacted"] = True
    return redacted


@router.get("/{connector_type}/oauth/authorize")
async def get_oauth_url(
    connector_type: str,
    redirect_uri: str = Query(..., max_length=2000),
    state: Optional[str] = None,
):
    """Get OAuth authorization URL for a connector."""
    _validate_redirect_uri(redirect_uri)
    try:
        connector = get_connector(connector_type, {})
        if state is None:
            state = str(uuid.uuid4())
        auth_url = connector.get_oauth_url(redirect_uri, state)
        if not auth_url:
            raise HTTPException(
                status_code=400,
                detail="This connector does not support OAuth",
            )
        return {
            "authorization_url": auth_url,
            "state": state,
        }
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning("Invalid connector request: %s", e)
        raise HTTPException(status_code=400, detail="Invalid connector configuration")


@router.post("/{connector_type}/oauth/callback")
async def handle_oauth_callback(
    connector_type: str,
    code: str = Query(..., max_length=2000),
    redirect_uri: str = Query(..., max_length=2000),
    state: Optional[str] = None,
):
    """Handle OAuth callback and exchange code for tokens."""
    _validate_redirect_uri(redirect_uri)
    try:
        connector = get_connector(connector_type, {})
        tokens = connector.handle_oauth_callback(code, redirect_uri)
        return {
            "status": "ok",
            "tokens": _redact_tokens(tokens) if isinstance(tokens, dict) else {"_redacted": True},
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("oauth_callback_failed", extra={"connector_type": connector_type})
        raise HTTPException(status_code=400, detail="OAuth callback failed")


# ============================================
# File Operations Endpoints
# ============================================


class FileInfoResponse(BaseModel):
    """File information response."""

    id: str
    name: str
    path: str
    size_bytes: int
    mime_type: Optional[str]
    created_at: Optional[str]
    modified_at: Optional[str]
    is_folder: bool
    download_url: Optional[str]


class FileUploadResponse(BaseModel):
    """File upload response."""

    status: str
    file: FileInfoResponse


class SyncStatusResponse(BaseModel):
    """Sync status response."""

    connection_id: str
    status: str
    started_at: Optional[str]
    completed_at: Optional[str]
    files_synced: int
    errors: list[str]


class SyncScheduleRequest(BaseModel):
    """Sync schedule request."""

    interval_minutes: int = Field(..., ge=5, le=1440)
    enabled: bool = True


class SyncScheduleResponse(BaseModel):
    """Sync schedule response."""

    connection_id: str
    interval_minutes: int
    enabled: bool
    next_run: Optional[str]


@router.get("/{connection_id}/files")
async def list_connection_files(
    connection_id: str = Path(..., min_length=36, max_length=36, pattern="^[0-9a-f-]{36}$"),
    path: str = Query("/", max_length=2000),
    recursive: bool = Query(False),
) -> dict[str, Any]:
    """List files for a cloud storage connection.

    Returns files and folders at the given *path* within the connected
    cloud storage provider.
    """
    conn = _store_get(connection_id)
    if conn is None:
        raise HTTPException(status_code=404, detail="Connection not found")

    config = _store_get_config(connection_id)
    connector = None
    try:
        connector = get_connector(conn["connector_type"], config)
        await connector.connect()
        files = await connector.list_files(path=path, recursive=recursive)

        # Update last-used timestamp
        conn["last_used"] = datetime.now(timezone.utc).isoformat()
        conn["config"] = config
        _store_put(conn)

        return {
            "connection_id": connection_id,
            "path": path,
            "files": [
                FileInfoResponse(
                    id=f.id,
                    name=f.name,
                    path=f.path,
                    size_bytes=f.size_bytes,
                    mime_type=f.mime_type,
                    created_at=f.created_at,
                    modified_at=f.modified_at,
                    is_folder=f.is_folder,
                    download_url=f.download_url,
                ).model_dump()
                for f in files
            ],
            "total": len(files),
        }
    except NotImplementedError:
        raise HTTPException(
            status_code=400,
            detail="This connector does not support file listing",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("connector_list_files_failed", extra={"connection_id": connection_id})
        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: Failed to list files",
        )
    finally:
        if connector is not None:
            try:
                await connector.disconnect()
            except Exception:
                pass


@router.get("/{connection_id}/files/download")
async def download_connection_file(
    connection_id: str = Path(..., min_length=36, max_length=36, pattern="^[0-9a-f-]{36}$"),
    path: str = Query(..., min_length=1, max_length=2000),
):
    """Download a file from a cloud storage connection.

    The *path* query parameter identifies the file to download.  The
    response streams the raw file bytes with an appropriate content type.
    """
    conn = _store_get(connection_id)
    if conn is None:
        raise HTTPException(status_code=404, detail="Connection not found")

    config = _store_get_config(connection_id)
    connector = None
    try:
        connector = get_connector(conn["connector_type"], config)
        await connector.connect()
        content = await connector.download_file(file_id=path)

        # Update last-used timestamp
        conn["last_used"] = datetime.now(timezone.utc).isoformat()
        conn["config"] = config
        _store_put(conn)

        # Derive a filename from the path for the Content-Disposition header
        filename = path.rsplit("/", 1)[-1] or "download"

        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(content)),
            },
        )
    except NotImplementedError:
        raise HTTPException(
            status_code=400,
            detail="This connector does not support file download",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("connector_download_file_failed", extra={"connection_id": connection_id, "path": path})
        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: Failed to download file",
        )
    finally:
        if connector is not None:
            try:
                await connector.disconnect()
            except Exception:
                pass


@router.post("/{connection_id}/files/upload", response_model=FileUploadResponse)
async def upload_connection_file(
    connection_id: str = Path(..., min_length=36, max_length=36, pattern="^[0-9a-f-]{36}$"),
    path: str = Query("/", max_length=2000),
    file: UploadFile = File(...),
):
    """Upload a file to a cloud storage connection.

    Accepts a multipart file upload and stores it at the given *path*
    within the connected cloud storage provider.
    """
    conn = _store_get(connection_id)
    if conn is None:
        raise HTTPException(status_code=404, detail="Connection not found")

    config = _store_get_config(connection_id)
    connector = None
    try:
        connector = get_connector(conn["connector_type"], config)
        await connector.connect()

        content = await file.read()
        file_info = await connector.upload_file(
            content=content,
            path=path,
            filename=file.filename or "upload",
            mime_type=file.content_type,
        )

        # Update last-used timestamp
        conn["last_used"] = datetime.now(timezone.utc).isoformat()
        conn["config"] = config
        _store_put(conn)

        return FileUploadResponse(
            status="ok",
            file=FileInfoResponse(
                id=file_info.id,
                name=file_info.name,
                path=file_info.path,
                size_bytes=file_info.size_bytes,
                mime_type=file_info.mime_type,
                created_at=file_info.created_at,
                modified_at=file_info.modified_at,
                is_folder=file_info.is_folder,
                download_url=file_info.download_url,
            ),
        )
    except NotImplementedError:
        raise HTTPException(
            status_code=400,
            detail="This connector does not support file upload",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("connector_upload_file_failed", extra={"connection_id": connection_id})
        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: Failed to upload file",
        )
    finally:
        if connector is not None:
            try:
                await connector.disconnect()
            except Exception:
                pass


# ============================================
# Sync Endpoints
# ============================================

@router.post("/{connection_id}/sync")
async def start_connection_sync(
    connection_id: str = Path(..., min_length=36, max_length=36, pattern="^[0-9a-f-]{36}$"),
) -> dict[str, Any]:
    """Start syncing a connection.

    Initiates a sync operation for the connection and records the sync
    status in the persistent state store under ``connector_sync_status``.
    """
    conn = _store_get(connection_id)
    if conn is None:
        raise HTTPException(status_code=404, detail="Connection not found")

    config = _store_get_config(connection_id)
    connector = None
    try:
        connector = get_connector(conn["connector_type"], config)
        await connector.connect()

        now = datetime.now(timezone.utc).isoformat()
        sync_status = {
            "connection_id": connection_id,
            "status": "in_progress",
            "started_at": now,
            "completed_at": None,
            "files_synced": 0,
            "errors": [],
        }

        # Persist initial sync status
        with state_store.transaction() as state:
            state.setdefault("connector_sync_status", {})[connection_id] = sync_status

        # Attempt sync by listing all files (implementation-dependent)
        files_synced = 0
        errors: list[str] = []
        try:
            files = await connector.list_files(path="/", recursive=True)
            files_synced = len(files)
        except NotImplementedError:
            errors.append("Connector does not support file listing for sync")
        except Exception as e:
            errors.append(f"{type(e).__name__}: {e}")

        # Update sync status with results
        completed_at = datetime.now(timezone.utc).isoformat()
        final_status = "completed" if not errors else "completed_with_errors"
        sync_status.update({
            "status": final_status,
            "completed_at": completed_at,
            "files_synced": files_synced,
            "errors": errors,
        })

        with state_store.transaction() as state:
            state.setdefault("connector_sync_status", {})[connection_id] = sync_status

        # Update last-used timestamp on the connection
        conn["last_used"] = completed_at
        conn["config"] = config
        _store_put(conn)

        return sync_status
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("connector_sync_failed", extra={"connection_id": connection_id})
        # Record failure in sync status
        error_status = {
            "connection_id": connection_id,
            "status": "failed",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "files_synced": 0,
            "errors": [f"{type(e).__name__}: {e}"],
        }
        with state_store.transaction() as state:
            state.setdefault("connector_sync_status", {})[connection_id] = error_status
        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: Sync failed",
        )
    finally:
        if connector is not None:
            try:
                await connector.disconnect()
            except Exception:
                pass


@router.get("/{connection_id}/sync/status", response_model=SyncStatusResponse)
async def get_sync_status(
    connection_id: str = Path(..., min_length=36, max_length=36, pattern="^[0-9a-f-]{36}$"),
):
    """Get the sync status for a connection.

    Returns the most recent sync status from the state store.  If no
    sync has been run yet, a ``never_synced`` status is returned.
    """
    conn = _store_get(connection_id)
    if conn is None:
        raise HTTPException(status_code=404, detail="Connection not found")

    with state_store.transaction() as state:
        sync_statuses = state.get("connector_sync_status", {})
        sync_status = sync_statuses.get(connection_id)

    if sync_status is None:
        return SyncStatusResponse(
            connection_id=connection_id,
            status="never_synced",
            started_at=None,
            completed_at=None,
            files_synced=0,
            errors=[],
        )

    return SyncStatusResponse(
        connection_id=sync_status["connection_id"],
        status=sync_status["status"],
        started_at=sync_status.get("started_at"),
        completed_at=sync_status.get("completed_at"),
        files_synced=sync_status.get("files_synced", 0),
        errors=sync_status.get("errors", []),
    )


@router.post("/{connection_id}/sync/schedule", response_model=SyncScheduleResponse)
async def schedule_connection_sync(
    request: SyncScheduleRequest,
    connection_id: str = Path(..., min_length=36, max_length=36, pattern="^[0-9a-f-]{36}$"),
):
    """Schedule periodic sync for a connection.

    Stores the schedule configuration in the state store under
    ``connector_sync_status`` so that a background worker can pick it
    up.  The *interval_minutes* field must be between 5 and 1440 (24h).
    """
    conn = _store_get(connection_id)
    if conn is None:
        raise HTTPException(status_code=404, detail="Connection not found")

    now = datetime.now(timezone.utc)

    # Calculate next run time based on interval
    next_run = (now + timedelta(minutes=request.interval_minutes)).isoformat()

    schedule = {
        "connection_id": connection_id,
        "interval_minutes": request.interval_minutes,
        "enabled": request.enabled,
        "next_run": next_run if request.enabled else None,
        "created_at": now.isoformat(),
    }

    with state_store.transaction() as state:
        sync_status = state.setdefault("connector_sync_status", {}).get(connection_id, {})
        sync_status["schedule"] = schedule
        state.setdefault("connector_sync_status", {})[connection_id] = sync_status

    logger.info(
        "connector_sync_scheduled",
        extra={
            "connection_id": connection_id,
            "interval_minutes": request.interval_minutes,
            "enabled": request.enabled,
        },
    )

    return SyncScheduleResponse(
        connection_id=connection_id,
        interval_minutes=request.interval_minutes,
        enabled=request.enabled,
        next_run=next_run if request.enabled else None,
    )
