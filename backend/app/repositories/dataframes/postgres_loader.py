"""
PostgreSQL DataFrame Loader — mirrors SQLiteDataFrameLoader interface.

Loads PostgreSQL tables into cached pandas DataFrames for DuckDB query execution.
Uses SQLAlchemy + psycopg2 for synchronous access (required by pandas.read_sql_query).
"""

from __future__ import annotations

import logging
import threading
from typing import Any

import pandas as pd
from sqlalchemy import create_engine, text, inspect

logger = logging.getLogger("neura.dataframes.postgres")

# Maximum rows to load per table to avoid OOM on large industrial datasets
DEFAULT_ROW_LIMIT = 500_000


class PostgresDataFrameLoader:
    """Load PostgreSQL tables into cached pandas DataFrames."""

    def __init__(self, connection_url: str, row_limit: int = DEFAULT_ROW_LIMIT):
        self.connection_url = connection_url
        self.row_limit = row_limit
        self._engine = create_engine(
            connection_url,
            connect_args={"connect_timeout": 10},
            pool_pre_ping=True,
            pool_size=2,
            max_overflow=3,
        )
        self._table_names: list[str] | None = None
        self._frames: dict[str, pd.DataFrame] = {}
        self._lock = threading.Lock()
        self._table_info_cache: dict[str, list[dict[str, Any]]] = {}
        self._foreign_keys_cache: dict[str, list[dict[str, Any]]] = {}
        # Track mtime as a version marker (incremented on invalidation)
        self._mtime: float = 0.0

    def table_names(self) -> list[str]:
        """Return a cached list of user tables in the database."""
        with self._lock:
            if self._table_names is not None:
                return list(self._table_names)

        with self._engine.connect() as conn:
            result = conn.execute(text(
                "SELECT table_schema, table_name "
                "FROM information_schema.tables "
                "WHERE table_type = 'BASE TABLE' "
                "AND table_schema NOT IN ('pg_catalog', 'information_schema') "
                "ORDER BY table_schema, table_name"
            ))
            tables = []
            for row in result:
                schema, name = row[0], row[1]
                if schema == "public":
                    tables.append(name)
                else:
                    tables.append(f"{schema}.{name}")

        with self._lock:
            self._table_names = tables
        return list(tables)

    def _assert_table(self, table_name: str) -> str:
        clean = str(table_name or "").strip()
        if not clean:
            raise ValueError("table_name must be a non-empty string")
        if clean not in self.table_names():
            raise RuntimeError(f"Table {clean!r} not found in PostgreSQL database")
        return clean

    def _parse_table_ref(self, table_name: str) -> tuple[str, str]:
        """Parse 'schema.table' into (schema, table). Default schema is 'public'."""
        if "." in table_name:
            parts = table_name.split(".", 1)
            return parts[0], parts[1]
        return "public", table_name

    def frame(self, table_name: str) -> pd.DataFrame:
        """
        Return the cached DataFrame for `table_name`, loading it from the
        database on first access.
        """
        clean = self._assert_table(table_name)
        with self._lock:
            cached = self._frames.get(clean)
            if cached is not None:
                return cached
        df = self._read_table(clean)
        with self._lock:
            self._frames[clean] = df
        return df

    def frames(self) -> dict[str, pd.DataFrame]:
        """Eagerly load and return all user tables as DataFrames."""
        for name in self.table_names():
            self.frame(name)
        with self._lock:
            return dict(self._frames)

    def _read_table(self, table_name: str) -> pd.DataFrame:
        schema, table = self._parse_table_ref(table_name)
        # Quote identifiers to prevent SQL injection
        quoted_schema = schema.replace('"', '""')
        quoted_table = table.replace('"', '""')
        sql = f'SELECT * FROM "{quoted_schema}"."{quoted_table}"'
        if self.row_limit:
            sql += f" LIMIT {int(self.row_limit)}"

        try:
            with self._engine.connect() as conn:
                df = pd.read_sql_query(text(sql), conn)
        except Exception as exc:
            raise RuntimeError(f"Failed loading table {table_name!r} into DataFrame: {exc}") from exc

        row_count = len(df)
        if self.row_limit and row_count >= self.row_limit:
            logger.warning(
                f"Table {table_name!r} hit row limit ({self.row_limit}). "
                f"Data is truncated — increase row_limit for full access."
            )

        # DuckDB fails to register DataFrames with string dtypes; coerce to object.
        for col in df.columns:
            if pd.api.types.is_string_dtype(df[col].dtype):
                df[col] = df[col].astype("object")
        return df

    def column_type(self, table_name: str, column_name: str) -> str:
        table = self.frame(table_name)
        if column_name not in table.columns:
            return ""
        series = table[column_name]
        if pd.api.types.is_datetime64_any_dtype(series):
            return "TIMESTAMP"
        if pd.api.types.is_integer_dtype(series):
            return "INTEGER"
        if pd.api.types.is_float_dtype(series):
            return "REAL"
        if pd.api.types.is_bool_dtype(series):
            return "BOOLEAN"
        return "TEXT"

    def table_info(self, table_name: str) -> list[tuple[str, str]]:
        table = self.frame(table_name)
        return [(col, str(table[col].dtype)) for col in table.columns]

    def pragma_table_info(self, table_name: str) -> list[dict[str, Any]]:
        """Return column metadata in the same format as SQLite PRAGMA table_info."""
        info, _ = self._load_table_metadata(table_name)
        return list(info)

    def foreign_keys(self, table_name: str) -> list[dict[str, Any]]:
        """Return foreign keys in the same format as SQLite PRAGMA foreign_key_list."""
        _, fks = self._load_table_metadata(table_name)
        return list(fks)

    def _load_table_metadata(
        self, table_name: str,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        clean = self._assert_table(table_name)
        with self._lock:
            cached_info = self._table_info_cache.get(clean)
            cached_fks = self._foreign_keys_cache.get(clean)
            if cached_info is not None and cached_fks is not None:
                return cached_info, cached_fks

        schema, table = self._parse_table_ref(clean)
        info_rows: list[dict[str, Any]] = []
        fk_rows: list[dict[str, Any]] = []

        try:
            with self._engine.connect() as conn:
                # Column info from information_schema
                result = conn.execute(text(
                    "SELECT ordinal_position, column_name, data_type, "
                    "is_nullable, column_default "
                    "FROM information_schema.columns "
                    "WHERE table_schema = :schema AND table_name = :table "
                    "ORDER BY ordinal_position"
                ), {"schema": schema, "table": table})

                # Get primary key columns
                pk_result = conn.execute(text(
                    "SELECT kcu.column_name "
                    "FROM information_schema.table_constraints tc "
                    "JOIN information_schema.key_column_usage kcu "
                    "  ON tc.constraint_name = kcu.constraint_name "
                    "  AND tc.table_schema = kcu.table_schema "
                    "WHERE tc.constraint_type = 'PRIMARY KEY' "
                    "  AND tc.table_schema = :schema "
                    "  AND tc.table_name = :table"
                ), {"schema": schema, "table": table})
                pk_columns = {r[0] for r in pk_result}

                for row in result:
                    info_rows.append({
                        "cid": int(row[0]) - 1,  # 0-indexed like SQLite
                        "name": str(row[1]),
                        "type": str(row[2] or "").upper(),
                        "notnull": 1 if row[3] == "NO" else 0,
                        "dflt_value": row[4],
                        "pk": 1 if row[1] in pk_columns else 0,
                    })

                # Foreign keys
                fk_result = conn.execute(text(
                    "SELECT tc.constraint_name, kcu.column_name, "
                    "ccu.table_name AS ref_table, ccu.column_name AS ref_column, "
                    "rc.update_rule, rc.delete_rule "
                    "FROM information_schema.table_constraints tc "
                    "JOIN information_schema.key_column_usage kcu "
                    "  ON tc.constraint_name = kcu.constraint_name "
                    "  AND tc.table_schema = kcu.table_schema "
                    "JOIN information_schema.constraint_column_usage ccu "
                    "  ON tc.constraint_name = ccu.constraint_name "
                    "JOIN information_schema.referential_constraints rc "
                    "  ON tc.constraint_name = rc.constraint_name "
                    "WHERE tc.constraint_type = 'FOREIGN KEY' "
                    "  AND tc.table_schema = :schema "
                    "  AND tc.table_name = :table"
                ), {"schema": schema, "table": table})

                for i, row in enumerate(fk_result):
                    fk_rows.append({
                        "id": i,
                        "seq": 0,
                        "table": str(row[2] or ""),
                        "from": str(row[1] or ""),
                        "to": str(row[3] or ""),
                        "on_update": str(row[4] or ""),
                        "on_delete": str(row[5] or ""),
                        "match": "",
                    })

        except Exception as exc:
            raise RuntimeError(f"Failed loading metadata for table {clean!r}: {exc}") from exc

        with self._lock:
            self._table_info_cache[clean] = info_rows
            self._foreign_keys_cache[clean] = fk_rows
        return info_rows, fk_rows

    def dispose(self) -> None:
        """Dispose the SQLAlchemy engine and release connections."""
        try:
            self._engine.dispose()
        except Exception:
            pass


def verify_postgres(connection_url: str) -> None:
    """Verify a PostgreSQL database is accessible by running SELECT 1."""
    engine = create_engine(connection_url, connect_args={"connect_timeout": 5})
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        raise RuntimeError(f"PostgreSQL connection failed: {exc}") from exc
    finally:
        engine.dispose()


# Loader cache (keyed by connection URL)
_PG_LOADER_CACHE: dict[str, PostgresDataFrameLoader] = {}
_PG_LOADER_CACHE_LOCK = threading.Lock()


def get_postgres_loader(connection_url: str) -> PostgresDataFrameLoader:
    """Get or create a cached PostgresDataFrameLoader for a connection URL."""
    with _PG_LOADER_CACHE_LOCK:
        loader = _PG_LOADER_CACHE.get(connection_url)
        if loader is None:
            loader = PostgresDataFrameLoader(connection_url)
            _PG_LOADER_CACHE[connection_url] = loader
    return loader
