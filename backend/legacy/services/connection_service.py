from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Optional

from fastapi import HTTPException

from backend.app.repositories.connections.db_connection import resolve_db_path, save_connection, verify_sqlite
from backend.app.repositories.state import store as state_store_module
from backend.legacy.schemas.connection_schema import ConnectionUpsertPayload, TestPayload
from backend.legacy.utils.connection_utils import display_name_for_path

logger = logging.getLogger(__name__)


def _http_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"status": "error", "code": code, "message": message})


def _state_store():
    return state_store_module.state_store


def test_connection(payload: TestPayload) -> dict[str, Any]:
    t0 = time.time()
    try:
        db_path: Path = resolve_db_path(
            connection_id=None,
            db_url=payload.db_url,
            db_path=payload.database if (payload.db_type or "").lower() == "sqlite" else None,
        )
        verify_sqlite(db_path)
    except Exception as exc:
        logger.exception("test_connection_failed")
        raise _http_error(400, "connection_invalid", "Connection test failed")

    latency_ms = int((time.time() - t0) * 1000)
    resolved = Path(db_path).resolve()
    display_name = display_name_for_path(resolved, "sqlite")
    cfg = {
        "db_type": "sqlite",
        "database": str(resolved),
        "db_url": payload.db_url,
        "name": display_name,
        "status": "connected",
        "latency_ms": latency_ms,
    }
    cid = save_connection(cfg)
    _state_store().record_connection_ping(
        cid,
        status="connected",
        detail=f"Connected ({display_name})",
        latency_ms=latency_ms,
    )

    return {
        "ok": True,
        "details": f"Connected ({display_name})",
        "latency_ms": latency_ms,
        "connection_id": cid,
        "normalized": {
            "db_type": "sqlite",
            "database": str(resolved),
        },
    }


def list_connections() -> list[dict]:
    return _state_store().list_connections()


def upsert_connection(payload: ConnectionUpsertPayload) -> dict[str, Any]:
    if not payload.db_url and not payload.database and not payload.id:
        raise _http_error(400, "invalid_payload", "Provide db_url or database when creating a connection.")

    existing = _state_store().get_connection_record(payload.id) if payload.id else None
    try:
        if payload.db_url:
            db_path = resolve_db_path(connection_id=None, db_url=payload.db_url, db_path=None)
        elif payload.database:
            db_path = Path(payload.database)
            ALLOWED_EXTENSIONS = {".db", ".sqlite", ".sqlite3", ".duckdb"}
            if db_path.suffix.lower() not in ALLOWED_EXTENSIONS:
                raise _http_error(400, "invalid_database_extension", "invalid_database_extension")
        elif existing and existing.get("database_path"):
            db_path = Path(existing["database_path"])
        else:
            raise RuntimeError("No database information supplied.")
    except Exception as exc:
        logger.exception("upsert_connection_invalid_database")
        raise _http_error(400, "invalid_database", "Invalid database reference")

    db_type = (payload.db_type or (existing or {}).get("db_type") or "sqlite").lower()
    if db_type != "sqlite":
        raise _http_error(400, "unsupported_db", "Only sqlite connections are supported in this build.")

    secret_payload: Optional[dict[str, Any]] = None
    if payload.db_url or payload.database:
        secret_payload = {
            "db_url": payload.db_url,
            "database": str(db_path),
        }

    record = _state_store().upsert_connection(
        conn_id=payload.id,
        name=payload.name or display_name_for_path(Path(db_path), db_type),
        db_type=db_type,
        database_path=str(db_path),
        secret_payload=secret_payload,
        status=payload.status,
        latency_ms=payload.latency_ms,
        tags=payload.tags,
    )

    if payload.status:
        _state_store().record_connection_ping(
            record["id"],
            status=payload.status,
            detail=None,
            latency_ms=payload.latency_ms,
        )
    return record


def delete_connection(connection_id: str) -> bool:
    return _state_store().delete_connection(connection_id)


def healthcheck_connection(connection_id: str) -> dict[str, Any]:
    t0 = time.time()
    try:
        db_path = resolve_db_path(connection_id=connection_id, db_url=None, db_path=None)
        verify_sqlite(db_path)
    except Exception as exc:
        logger.exception("healthcheck_connection_failed")
        _state_store().record_connection_ping(
            connection_id,
            status="failed",
            detail="Healthcheck failed",
            latency_ms=None,
        )
        raise _http_error(400, "connection_unhealthy", "Connection healthcheck failed")

    latency_ms = int((time.time() - t0) * 1000)
    _state_store().record_connection_ping(
        connection_id,
        status="connected",
        detail="Healthcheck succeeded",
        latency_ms=latency_ms,
    )
    return {
        "status": "ok",
        "connection_id": connection_id,
        "latency_ms": latency_ms,
    }
