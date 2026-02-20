from __future__ import annotations

import os
import threading
import time
from pathlib import Path
from typing import Any

from backend.app.repositories.connections.db_connection import resolve_db_path, verify_sqlite
from backend.app.repositories.dataframes.sqlite_loader import get_loader
from backend.app.repositories.state import store as state_store_module

_SCHEMA_CACHE: dict[tuple[str, bool, bool, int], dict] = {}
_SCHEMA_CACHE_LOCK = threading.Lock()
_SCHEMA_CACHE_TTL_SECONDS = max(int(os.getenv("NR_SCHEMA_CACHE_TTL_SECONDS", "30") or "30"), 0)
_SCHEMA_CACHE_MAX_ENTRIES = max(int(os.getenv("NR_SCHEMA_CACHE_MAX_ENTRIES", "32") or "32"), 5)


def _state_store():
    return state_store_module.state_store


def _coerce_value(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value).hex()
    return value


def _count_rows(db_path: Path, table: str) -> int:
    loader = get_loader(db_path)
    try:
        frame = loader.frame(table)
        return len(frame)
    except Exception:
        return 0


def _sample_rows(db_path: Path, table: str, limit: int, offset: int = 0) -> list[dict[str, Any]]:
    loader = get_loader(db_path)
    try:
        frame = loader.frame(table)
        sample = frame.iloc[offset : offset + limit]
        rows: list[dict[str, Any]] = []
        for _, row in sample.iterrows():
            rows.append({key: _coerce_value(value) for key, value in row.to_dict().items()})
        return rows
    except Exception:
        return []


def _cache_get(
    cache_key: tuple[str, bool, bool, int],
    *,
    db_path: Path,
) -> dict | None:
    if _SCHEMA_CACHE_TTL_SECONDS <= 0:
        return None
    try:
        cache_mtime = db_path.stat().st_mtime
    except OSError:
        cache_mtime = 0.0
    now = time.time()
    with _SCHEMA_CACHE_LOCK:
        entry = _SCHEMA_CACHE.get(cache_key)
    if not entry:
        return None
    cached_age = now - float(entry.get("ts") or 0.0)
    if entry.get("mtime") == cache_mtime and cached_age <= _SCHEMA_CACHE_TTL_SECONDS:
        return entry.get("data") or {}
    return None


def _cache_set(cache_key: tuple[str, bool, bool, int], *, db_path: Path, data: dict) -> None:
    if _SCHEMA_CACHE_TTL_SECONDS <= 0:
        return
    try:
        cache_mtime = db_path.stat().st_mtime
    except OSError:
        cache_mtime = 0.0
    with _SCHEMA_CACHE_LOCK:
        _SCHEMA_CACHE[cache_key] = {"mtime": cache_mtime, "ts": time.time(), "data": data}
        if len(_SCHEMA_CACHE) > _SCHEMA_CACHE_MAX_ENTRIES:
            oldest = sorted(_SCHEMA_CACHE.items(), key=lambda item: item[1].get("ts") or 0.0)
            for key, _ in oldest[: max(len(_SCHEMA_CACHE) - _SCHEMA_CACHE_MAX_ENTRIES, 0)]:
                _SCHEMA_CACHE.pop(key, None)


def get_connection_schema(
    connection_id: str,
    *,
    include_row_counts: bool = True,
    include_foreign_keys: bool = True,
    sample_rows: int = 0,
) -> dict[str, Any]:
    if not connection_id:
        raise ValueError("connection_id is required")

    db_path = resolve_db_path(connection_id=connection_id, db_url=None, db_path=None)
    verify_sqlite(db_path)

    cache_key = (connection_id, include_row_counts, include_foreign_keys, int(sample_rows or 0))
    cached = _cache_get(cache_key, db_path=db_path)
    if cached is not None:
        return cached

    loader = get_loader(db_path)
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
        table_record: dict[str, Any] = {
            "name": table_name,
            "columns": columns,
        }
        if include_foreign_keys:
            table_record["foreign_keys"] = loader.foreign_keys(table_name)
        if include_row_counts:
            table_record["row_count"] = _count_rows(db_path, table_name)
        if sample_rows and sample_rows > 0:
            table_record["sample_rows"] = _sample_rows(db_path, table_name, min(sample_rows, 25))
        tables.append(table_record)

    connection_record = _state_store().get_connection_record(connection_id) or {}
    result = {
        "connection_id": connection_id,
        "connection_name": connection_record.get("name"),
        "database": str(db_path),
        "table_count": len(tables),
        "tables": tables,
    }
    _cache_set(cache_key, db_path=db_path, data=result)
    return result


def get_connection_table_preview(
    connection_id: str,
    *,
    table: str,
    limit: int = 10,
    offset: int = 0,
) -> dict[str, Any]:
    if not connection_id:
        raise ValueError("connection_id is required")
    if not table:
        raise ValueError("table is required")

    db_path = resolve_db_path(connection_id=connection_id, db_url=None, db_path=None)
    verify_sqlite(db_path)

    loader = get_loader(db_path)
    tables = loader.table_names()
    if table not in tables:
        raise ValueError(f"Table '{table}' not found")

    safe_limit = max(1, min(int(limit or 10), 200))
    safe_offset = max(0, int(offset or 0))
    columns = [col.get("name") for col in loader.pragma_table_info(table)]
    rows = _sample_rows(db_path, table, safe_limit, safe_offset)
    return {
        "connection_id": connection_id,
        "table": table,
        "columns": columns,
        "rows": rows,
        "row_count": _count_rows(db_path, table),
        "limit": safe_limit,
        "offset": safe_offset,
    }
