# app/repositories/connections/db_connection.py
from __future__ import annotations

import argparse
import json
import os
import tempfile
import uuid
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

from ..dataframes import SQLiteDataFrameLoader, ensure_connection_loaded, dataframe_store
from backend.app.utils.sql_safety import get_write_operation, is_select_or_with
from ..dataframes import sqlite_shim
from ..state import state_store

STORAGE = os.path.join(tempfile.gettempdir(), "neura_connections.jsonl")


def _strip_quotes(s: str | None) -> str | None:
    if s is None:
        return None
    return s.strip().strip("'\"")


def _sqlite_path_from_url(db_url: str) -> str:
    u = urlparse(db_url)
    raw = (u.netloc + u.path) if u.netloc else (u.path or "")
    # /C:/Users/... -> C:/Users/...
    if raw.startswith("/") and len(raw) >= 3 and raw[2] == ":":
        raw = raw.lstrip("/")
    return raw.replace("/", os.sep)


def resolve_db_path(connection_id: str | None, db_url: str | None, db_path: str | None) -> Path:
    # a) connection_id -> lookup in STORAGE
    if connection_id:
        secrets = state_store.get_connection_secrets(connection_id)
        if secrets and secrets.get("database_path"):
            return Path(secrets["database_path"])
        record = state_store.get_connection_record(connection_id)
        if record and record.get("database_path"):
            return Path(record["database_path"])
        if os.path.exists(STORAGE):
            with open(STORAGE, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                        if rec.get("id") == connection_id:
                            cfg = rec.get("cfg") or {}
                            db = cfg.get("database")
                            if db:
                                # migrate legacy record into new store
                                state_store.upsert_connection(
                                    conn_id=connection_id,
                                    name=cfg.get("name") or f"{cfg.get('db_type') or 'sqlite'}@{Path(db).name}",
                                    db_type=cfg.get("db_type") or "sqlite",
                                    database_path=str(db),
                                    secret_payload={"database": str(db), "db_url": cfg.get("db_url")},
                                )
                                return Path(db)
                    except Exception:
                        continue
        # Fall through to db_url / db_path if the connection_id isn't stored yet
        # (e.g. creating a new connection where the ID is provided but not yet persisted).
        if not db_url and not db_path:
            raise RuntimeError(f"connection_id {connection_id!r} not found in storage")

    # b) db_url (preferred)
    db_url = _strip_quotes(db_url)
    if db_url:
        parsed = urlparse(db_url)
        if parsed.scheme:
            if parsed.scheme.lower() == "sqlite":
                return Path(_sqlite_path_from_url(db_url))
            if len(parsed.scheme) == 1 and db_url[1:3] in (":\\", ":/"):
                return Path(db_url)
            # Non-SQLite URL (PostgreSQL, etc.) — caller should use resolve_connection_ref() instead
            raise RuntimeError(f"resolve_db_path only handles SQLite. Use resolve_connection_ref() for {parsed.scheme} URLs.")
        return Path(db_url)

    # c) db_path (legacy)
    db_path = _strip_quotes(db_path)
    if db_path:
        return Path(db_path)

    # d) env fallback
    env_path = _strip_quotes(os.getenv("DB_PATH"))
    if env_path:
        return Path(env_path)

    raise RuntimeError("No DB specified. Provide --connection-id OR --db-url OR --db-path (or DB_PATH env).")


def resolve_connection_ref(connection_id: str) -> dict:
    """Resolve a connection_id to its type and access info.

    Returns dict with:
        db_type: "sqlite" | "postgresql"
        db_path: Path (for sqlite) or None
        connection_url: str (for postgresql) or None
    """
    secrets = state_store.get_connection_secrets(connection_id)
    if not secrets:
        # Fallback: try resolve_db_path for legacy sqlite connections
        db_path = resolve_db_path(connection_id=connection_id, db_url=None, db_path=None)
        return {"db_type": "sqlite", "db_path": db_path, "connection_url": None}

    db_type = secrets.get("db_type") or "sqlite"
    sp = secrets.get("secret_payload") or {}
    db_url = sp.get("db_url") or secrets.get("db_url")

    # Detect PostgreSQL from URL
    if db_url and db_url.startswith("postgresql"):
        db_type = "postgresql"

    if db_type in ("postgresql", "postgres"):
        return {"db_type": "postgresql", "db_path": None, "connection_url": db_url}
    else:
        database_path = secrets.get("database_path") or sp.get("database")
        if database_path:
            return {"db_type": "sqlite", "db_path": Path(database_path), "connection_url": None}
        # Last resort
        db_path = resolve_db_path(connection_id=connection_id, db_url=db_url, db_path=None)
        return {"db_type": "sqlite", "db_path": db_path, "connection_url": None}


def verify_sqlite(path) -> None:
    """Raise when the backing database cannot be materialized into DataFrames.

    Also accepts ConnectionRef objects — dispatches to PostgreSQL verification
    when the ref is a PostgreSQL connection.
    """
    # Support ConnectionRef objects from the updated pipeline
    if hasattr(path, 'is_postgresql') and path.is_postgresql:
        from backend.app.repositories.dataframes.postgres_loader import verify_postgres
        verify_postgres(path.connection_url)
        return

    db_file = Path(path)
    if not db_file.exists():
        raise FileNotFoundError(f"SQLite DB not found: {path}")
    try:
        loader = SQLiteDataFrameLoader(db_file)
        loader.table_names()
    except Exception as exc:  # pragma: no cover - surfaced to API caller
        raise RuntimeError(f"SQLite->DataFrame load error: {exc}") from exc


def execute_query(
    connection_id: str,
    sql: str,
    limit: int | None = None,
    offset: int = 0,
) -> dict:
    """Execute a SQL query on a connection and return results.

    Uses DataFrames instead of direct database access. The database is loaded
    into memory as DataFrames on first use and all queries run against the
    in-memory DataFrames via DuckDB.

    Args:
        connection_id: The connection ID to execute on
        sql: The SQL query to execute
        limit: Maximum number of rows to return
        offset: Number of rows to skip

    Returns:
        Dictionary with 'columns' (list of column names) and 'rows' (list of row data)
    """
    conn_ref = resolve_connection_ref(connection_id)
    db_type = conn_ref["db_type"]
    db_path = conn_ref["db_path"]
    connection_url = conn_ref["connection_url"]

    # Ensure DataFrames are loaded for this connection
    ensure_connection_loaded(
        connection_id,
        db_path=db_path,
        db_type=db_type,
        connection_url=connection_url,
    )

    # Basic safety check - only allow SELECT/WITH queries
    if not is_select_or_with(sql):
        raise ValueError("Only SELECT queries are allowed")

    write_op = get_write_operation(sql)
    if write_op:
        raise ValueError(f"Query contains prohibited operation: {write_op}")

    # Apply limit and offset if specified
    final_sql = sql
    if limit is not None:
        limit = int(limit)
        final_sql = f"{sql} LIMIT {limit}"
        if offset:
            offset = int(offset)
            final_sql += f" OFFSET {offset}"

    def coerce_value(val):
        """Convert values to JSON-serializable types."""
        if val is None:
            return None
        if isinstance(val, (date, datetime)):
            return val.isoformat()
        if isinstance(val, bytes):
            return val.decode("utf-8", errors="replace")
        return val

    # Execute using DataFrame store (works for both SQLite and PostgreSQL)
    store = dataframe_store
    result_df = store.execute_query(connection_id, final_sql)

    columns = list(result_df.columns) if not result_df.empty else []
    rows = []
    for _, row in result_df.iterrows():
        rows.append([coerce_value(row[col]) for col in columns])

    return {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
    }


def save_connection(cfg: dict) -> str:
    """Persist a minimal record and return a connection_id."""
    cid = cfg.get("id") or str(uuid.uuid4())
    db_type = cfg.get("db_type") or "sqlite"
    database = cfg.get("database")
    db_url = cfg.get("db_url")
    if db_url and not database:
        database = _sqlite_path_from_url(db_url)
    database_path = str(database) if database else ""
    name = cfg.get("name") or f"{db_type}@{Path(database_path).name if database_path else cid}"
    state_store.upsert_connection(
        conn_id=cid,
        name=name,
        db_type=db_type,
        database_path=database_path,
        secret_payload={"database": database_path, "db_url": db_url},
        status=cfg.get("status"),
        latency_ms=cfg.get("latency_ms"),
        tags=cfg.get("tags"),
    )
    return cid


# ---- CLI only (safe to import in API) ----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NeuraReport DB resolver")
    parser.add_argument("--connection-id")
    parser.add_argument("--db-url")  # e.g. sqlite:///C:/Users/you/file.db
    parser.add_argument("--db-path")  # legacy: direct path
    args = parser.parse_args()

    DB_PATH = resolve_db_path(
        connection_id=_strip_quotes(args.connection_id) or _strip_quotes(os.getenv("CONNECTION_ID")),
        db_url=_strip_quotes(args.db_url) or _strip_quotes(os.getenv("DB_URL")),
        db_path=_strip_quotes(args.db_path) or _strip_quotes(os.getenv("DB_PATH")),
    )
    verify_sqlite(DB_PATH)
    print(f"Resolved DB path: {DB_PATH}")
