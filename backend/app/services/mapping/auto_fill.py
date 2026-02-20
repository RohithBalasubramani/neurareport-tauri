from __future__ import annotations

import hashlib
import json
import logging
from backend.app.repositories.dataframes.sqlite_loader import get_loader
from pathlib import Path
from typing import Optional

logger = logging.getLogger("neura.auto_fill")


def _compute_db_signature(db_path) -> Optional[str]:
    """
    Build a stable fingerprint of the database schema (user tables only).
    Captures table columns and foreign keys to detect schema drift.
    """
    # Handle PostgreSQL connections
    if hasattr(db_path, 'is_postgresql') and db_path.is_postgresql:
        return hashlib.md5((db_path.connection_url or "").encode()).hexdigest()[:16]

    schema: dict[str, dict[str, list[dict[str, object]]]] = {}
    try:
        loader = get_loader(db_path)
    except Exception as exc:
        logger.warning(
            "db_signature_connect_failed",
            extra={
                "event": "db_signature_connect_failed",
                "db_path": str(db_path),
            },
            exc_info=exc,
        )
        return None

    try:
        tables = loader.table_names()
        for table in tables:
            table_entry: dict[str, list[dict[str, object]]] = {"columns": [], "foreign_keys": []}
            try:
                columns = loader.pragma_table_info(table)
                table_entry["columns"] = [
                    {
                        "name": str(col.get("name") or ""),
                        "type": str(col.get("type") or ""),
                        "notnull": int(col.get("notnull") or 0),
                        "pk": int(col.get("pk") or 0),
                    }
                    for col in columns
                ]
            except Exception:
                table_entry["columns"] = []

            try:
                fks = loader.foreign_keys(table)
                table_entry["foreign_keys"] = [
                    {
                        "id": int(fk.get("id", 0)),
                        "seq": int(fk.get("seq", 0)),
                        "table": str(fk.get("table") or ""),
                        "from": str(fk.get("from") or ""),
                        "to": str(fk.get("to") or ""),
                    }
                    for fk in fks
                ]
            except Exception:
                table_entry["foreign_keys"] = []

            schema[table] = table_entry
    except Exception as exc:
        logger.warning(
            "db_signature_pragmas_failed",
            extra={
                "event": "db_signature_pragmas_failed",
                "db_path": str(db_path),
            },
            exc_info=exc,
        )
        return None

    payload = json.dumps(schema, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
