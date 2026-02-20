from __future__ import annotations

import os
import threading
import time
from pathlib import Path
from typing import Any

from fastapi import HTTPException

import logging

from backend.app.repositories.connections.db_connection import resolve_db_path, verify_sqlite
from backend.app.repositories.dataframes.sqlite_loader import get_loader
from backend.app.repositories.dataframes.postgres_loader import get_postgres_loader, verify_postgres
from backend.app.repositories.dataframes import sqlite_shim
from backend.app.repositories.state import store as state_store_module

logger = logging.getLogger(__name__)

_SCHEMA_CACHE: dict[tuple[str, bool, bool, int], dict] = {}
_SCHEMA_CACHE_LOCK = threading.Lock()
_SCHEMA_CACHE_TTL_SECONDS = max(int(os.getenv("NR_SCHEMA_CACHE_TTL_SECONDS", "30") or "30"), 0)
_SCHEMA_CACHE_MAX_ENTRIES = max(int(os.getenv("NR_SCHEMA_CACHE_MAX_ENTRIES", "32") or "32"), 5)


def _http_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"status": "error", "code": code, "message": message})


def _state_store():
    return state_store_module.state_store


def _quote_identifier(name: str) -> str:
    return name.replace('"', '""')


def _coerce_value(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value).hex()
    return value


def _resolve_connection_info(connection_id: str) -> dict:
    """Resolve connection info from state store. Returns dict with db_type, loader, db_identifier."""
    store = _state_store()
    secrets = store.get_connection_secrets(connection_id) if store else None
    db_type = "sqlite"
    db_url = None

    if secrets:
        sp = secrets.get("secret_payload") or {}
        db_url = sp.get("db_url") or secrets.get("db_url")
        db_type = secrets.get("db_type") or "sqlite"
        # Detect from URL
        if db_url and db_url.startswith("postgresql"):
            db_type = "postgresql"

    if db_type in ("postgresql", "postgres"):
        if not db_url:
            raise _http_error(400, "connection_invalid", "No database URL for PostgreSQL connection")
        verify_postgres(db_url)
        loader = get_postgres_loader(db_url)
        return {"db_type": "postgresql", "loader": loader, "db_identifier": db_url}
    else:
        db_path = resolve_db_path(connection_id=connection_id, db_url=None, db_path=None)
        verify_sqlite(db_path)
        loader = get_loader(db_path)
        return {"db_type": "sqlite", "loader": loader, "db_identifier": str(db_path), "db_path": db_path}


def _count_rows_from_loader(loader, table: str) -> int:
    """Get row count from loader's DataFrame."""
    try:
        frame = loader.frame(table)
        return len(frame)
    except Exception:
        return 0


def _sample_rows_from_loader(loader, table: str, limit: int, offset: int = 0) -> list[dict]:
    """Get sample rows from loader's DataFrame."""
    try:
        frame = loader.frame(table)
        sample = frame.iloc[offset:offset + limit]
        rows = []
        for _, row in sample.iterrows():
            rows.append({key: _coerce_value(value) for key, value in row.to_dict().items()})
        return rows
    except Exception:
        return []


def get_connection_schema(
    connection_id: str,
    *,
    include_row_counts: bool = True,
    include_foreign_keys: bool = True,
    sample_rows: int = 0,
) -> dict[str, Any]:
    if not connection_id:
        raise _http_error(400, "connection_missing", "connection_id is required")
    try:
        conn_info = _resolve_connection_info(connection_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Connection validation failed for %s", connection_id)
        raise _http_error(400, "connection_invalid", "Connection validation failed")

    loader = conn_info["loader"]
    db_identifier = conn_info["db_identifier"]

    cache_key = (connection_id, include_row_counts, include_foreign_keys, int(sample_rows or 0))
    cache_enabled = _SCHEMA_CACHE_TTL_SECONDS > 0

    # For SQLite, use file mtime for cache invalidation. For PG, use time-based only.
    cache_mtime = 0.0
    if cache_enabled and conn_info["db_type"] == "sqlite":
        try:
            cache_mtime = conn_info["db_path"].stat().st_mtime
        except OSError:
            cache_mtime = 0.0

    if cache_enabled:
        now = time.time()
        with _SCHEMA_CACHE_LOCK:
            entry = _SCHEMA_CACHE.get(cache_key)
        if entry:
            cached_age = now - float(entry.get("ts") or 0.0)
            if entry.get("mtime") == cache_mtime and cached_age <= _SCHEMA_CACHE_TTL_SECONDS:
                return entry.get("data") or {}

    tables = []
    for table_name in loader.table_names():
        columns = [
            {
                "name": col.get("name"),
                "type": col.get("type"),
                "notnull": bool(col.get("notnull")),
                "pk": bool(col.get("pk")),
                "default": col.get("dflt_value"),
            }
            for col in loader.pragma_table_info(table_name)
        ]
        table_record = {
            "name": table_name,
            "columns": columns,
        }
        if include_foreign_keys:
            table_record["foreign_keys"] = loader.foreign_keys(table_name)
        if include_row_counts:
            table_record["row_count"] = _count_rows_from_loader(loader, table_name)
        if sample_rows and sample_rows > 0:
            table_record["sample_rows"] = _sample_rows_from_loader(loader, table_name, min(sample_rows, 25))
        tables.append(table_record)

    connection_record = _state_store().get_connection_record(connection_id) or {}
    result = {
        "connection_id": connection_id,
        "connection_name": connection_record.get("name"),
        "database": db_identifier,
        "table_count": len(tables),
        "tables": tables,
    }
    if cache_enabled:
        with _SCHEMA_CACHE_LOCK:
            _SCHEMA_CACHE[cache_key] = {"mtime": cache_mtime, "ts": time.time(), "data": result}
            if len(_SCHEMA_CACHE) > _SCHEMA_CACHE_MAX_ENTRIES:
                oldest = sorted(_SCHEMA_CACHE.items(), key=lambda item: item[1].get("ts") or 0.0)
                for key, _ in oldest[: max(len(_SCHEMA_CACHE) - _SCHEMA_CACHE_MAX_ENTRIES, 0)]:
                    _SCHEMA_CACHE.pop(key, None)
    return result


def get_connection_table_preview(
    connection_id: str,
    *,
    table: str,
    limit: int = 10,
    offset: int = 0,
) -> dict[str, Any]:
    if not connection_id:
        raise _http_error(400, "connection_missing", "connection_id is required")
    if not table:
        raise _http_error(400, "table_missing", "table name is required")
    try:
        conn_info = _resolve_connection_info(connection_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Connection validation failed for %s", connection_id)
        raise _http_error(400, "connection_invalid", "Connection validation failed")

    loader = conn_info["loader"]
    tables = loader.table_names()
    if table not in tables:
        raise _http_error(404, "table_not_found", f"Table '{table}' not found")

    safe_limit = max(1, min(int(limit or 10), 200))
    safe_offset = max(0, int(offset or 0))
    columns = [col.get("name") for col in loader.pragma_table_info(table)]
    rows = _sample_rows_from_loader(loader, table, safe_limit, safe_offset)
    return {
        "connection_id": connection_id,
        "table": table,
        "columns": columns,
        "rows": rows,
        "row_count": _count_rows_from_loader(loader, table),
        "limit": safe_limit,
        "offset": safe_offset,
    }
