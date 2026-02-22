from __future__ import annotations

import os
import re
import sqlite3
import threading
from pathlib import Path
from typing import Any, Mapping, Sequence

import duckdb
import pandas as pd


class SQLiteDataFrameLoader:
    """Load SQLite tables into cached pandas DataFrames."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self._table_names: list[str] | None = None
        self._frames: dict[str, pd.DataFrame] = {}
        self._lock = threading.Lock()
        self._mtime = os.path.getmtime(self.db_path) if self.db_path.exists() else 0.0
        self._table_info_cache: dict[str, list[dict[str, Any]]] = {}
        self._foreign_keys_cache: dict[str, list[dict[str, Any]]] = {}

    def table_names(self) -> list[str]:
        """Return a cached list of user tables in the database."""
        with self._lock:
            if self._table_names is not None:
                return list(self._table_names)

            with sqlite3.connect(str(self.db_path)) as con:
                cur = con.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
                )
                tables = [str(row[0]) for row in cur.fetchall() if row and row[0]]
            self._table_names = tables
            return list(self._table_names)

    def _assert_table(self, table_name: str) -> str:
        clean = str(table_name or "").strip()
        if not clean:
            raise ValueError("table_name must be a non-empty string")
        if clean not in self.table_names():
            raise RuntimeError(f"Table {clean!r} not found in {self.db_path}")
        return clean

    def frame(self, table_name: str) -> pd.DataFrame:
        """
        Return the cached DataFrame for `table_name`, loading it from disk
        on first access. Callers should treat the returned DataFrame as
        read-only because it is shared across consumers.
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
        quoted = table_name.replace('"', '""')
        try:
            with sqlite3.connect(str(self.db_path)) as con:
                df = pd.read_sql_query(f'SELECT rowid AS "__rowid__", * FROM "{quoted}"', con)
        except Exception as exc:  # pragma: no cover - surfaced to caller
            raise RuntimeError(f"Failed loading table {table_name!r} into DataFrame: {exc}") from exc
        # DuckDB fails to register DataFrames with string dtypes; coerce to object.
        for col in df.columns:
            if pd.api.types.is_string_dtype(df[col].dtype):
                df[col] = df[col].astype("object")
        if "__rowid__" in df.columns:
            rowid_series = df["__rowid__"].copy()
            if "rowid" not in df.columns:
                df.insert(0, "rowid", rowid_series)
        return df

    def column_type(self, table_name: str, column_name: str) -> str:
        table = self.frame(table_name)
        if column_name not in table.columns:
            return ""
        series = table[column_name]
        if pd.api.types.is_datetime64_any_dtype(series):
            return "DATETIME"
        if pd.api.types.is_integer_dtype(series):
            return "INTEGER"
        if pd.api.types.is_float_dtype(series):
            return "REAL"
        if pd.api.types.is_bool_dtype(series):
            return "INTEGER"
        return "TEXT"

    def table_info(self, table_name: str) -> list[tuple[str, str]]:
        table = self.frame(table_name)
        return [(col, str(table[col].dtype)) for col in table.columns]

    def _load_table_metadata(
        self, table_name: str
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        clean = self._assert_table(table_name)
        with self._lock:
            cached_info = self._table_info_cache.get(clean)
            cached_fks = self._foreign_keys_cache.get(clean)
            if cached_info is not None and cached_fks is not None:
                return cached_info, cached_fks

        quoted = clean.replace("'", "''")
        info_rows: list[dict[str, Any]] = []
        fk_rows: list[dict[str, Any]] = []
        try:
            with sqlite3.connect(str(self.db_path)) as con:
                cur = con.execute(f"PRAGMA table_info('{quoted}')")
                info_rows = [
                    {
                        "cid": int(row[0]),
                        "name": str(row[1]),
                        "type": str(row[2] or ""),
                        "notnull": int(row[3] or 0),
                        "dflt_value": row[4],
                        "pk": int(row[5] or 0),
                    }
                    for row in cur.fetchall()
                ]
                cur = con.execute(f"PRAGMA foreign_key_list('{quoted}')")
                fk_rows = [
                    {
                        "id": int(row[0]),
                        "seq": int(row[1]),
                        "table": str(row[2] or ""),
                        "from": str(row[3] or ""),
                        "to": str(row[4] or ""),
                        "on_update": str(row[5] or ""),
                        "on_delete": str(row[6] or ""),
                        "match": str(row[7] or ""),
                    }
                    for row in cur.fetchall()
                ]
        except Exception as exc:  # pragma: no cover - surfaced to caller
            raise RuntimeError(f"Failed loading metadata for table {clean!r}: {exc}") from exc

        with self._lock:
            self._table_info_cache[clean] = info_rows
            self._foreign_keys_cache[clean] = fk_rows
        return info_rows, fk_rows

    def pragma_table_info(self, table_name: str) -> list[dict[str, Any]]:
        info, _ = self._load_table_metadata(table_name)
        return list(info)

    def foreign_keys(self, table_name: str) -> list[dict[str, Any]]:
        _, fks = self._load_table_metadata(table_name)
        return list(fks)


_LOADER_CACHE: dict[str, SQLiteDataFrameLoader] = {}
_LOADER_CACHE_LOCK = threading.Lock()


def get_loader(db_path: Path) -> SQLiteDataFrameLoader:
    key = str(Path(db_path).resolve())
    with _LOADER_CACHE_LOCK:
        loader = _LOADER_CACHE.get(key)
        mtime = os.path.getmtime(key) if os.path.exists(key) else 0.0
        if loader is None or loader._mtime != mtime:
            loader = SQLiteDataFrameLoader(Path(key))
            loader._mtime = mtime
            _LOADER_CACHE[key] = loader
    return loader


_PARAM_PATTERN = re.compile(r":([A-Za-z_][A-Za-z0-9_]*)")
_SQLITE_DATETIME_RE = re.compile(r"(?i)(?<!sqlite_)\bdatetime\s*\(")
_SQLITE_STRFTIME_RE = re.compile(r"(?i)(?<!sqlite_)\bstrftime\s*\(")

# Match datetime('now', '<modifier>') with SQLite modifier syntax.
# Captures: sign (+/-), amount (digits), unit (seconds/minutes/hours/days/months/years).
_DATETIME_NOW_MODIFIER_RE = re.compile(
    r"""(?ix)\bdatetime\s*\(\s*'now'\s*,\s*'([+-]?\s*\d+)\s+(seconds?|minutes?|hours?|days?|months?|years?)'\s*\)"""
)
# Match datetime('now', 'start of <unit>') truncation modifiers.
_DATETIME_START_OF_RE = re.compile(
    r"""(?ix)\bdatetime\s*\(\s*'now'\s*,\s*'start\s+of\s+(month|year|day)'\s*\)"""
)
# Match DATE('now') or DATE('now', modifier) patterns.
_DATE_NOW_RE = re.compile(r"""(?ix)\bDATE\s*\(\s*'now'\s*\)""")
_DATE_NOW_MODIFIER_RE = re.compile(
    r"""(?ix)\bDATE\s*\(\s*'now'\s*,\s*'([+-]?\s*\d+)\s+(seconds?|minutes?|hours?|days?|months?|years?)'\s*\)"""
)


def _normalize_params(sql: str, params: Any | None) -> tuple[str, Sequence[Any]]:
    if params is None:
        return sql, ()
    if isinstance(params, Mapping):
        ordered: list[Any] = []

        def _repl(match: re.Match[str]) -> str:
            name = match.group(1)
            if name not in params:
                raise KeyError(f"Missing SQL parameter: {name}")
            ordered.append(params[name])
            return "?"

        prepared = _PARAM_PATTERN.sub(_repl, sql)
        return prepared, tuple(ordered)
    if isinstance(params, (list, tuple)):
        return sql, tuple(params)
    return sql, (params,)


def _normalize_unit(unit: str) -> str:
    """Normalize SQLite time unit to DuckDB INTERVAL unit (singular uppercase)."""
    u = unit.strip().upper().rstrip("S")  # remove trailing 's' for plural
    mapping = {"SECOND": "SECOND", "MINUTE": "MINUTE", "HOUR": "HOUR",
               "DAY": "DAY", "MONTH": "MONTH", "YEAR": "YEAR"}
    return mapping.get(u, u)


def _rewrite_datetime_modifier(m: re.Match) -> str:
    """Convert datetime('now', '+/-N unit') to DuckDB interval arithmetic."""
    raw_amount = m.group(1).replace(" ", "")
    unit = _normalize_unit(m.group(2))
    amount = int(raw_amount)
    if amount >= 0:
        return f"(CURRENT_TIMESTAMP + INTERVAL '{amount}' {unit})"
    else:
        return f"(CURRENT_TIMESTAMP - INTERVAL '{-amount}' {unit})"


def _rewrite_start_of(m: re.Match) -> str:
    """Convert datetime('now', 'start of month') to DuckDB DATE_TRUNC."""
    unit = m.group(1).lower()
    return f"DATE_TRUNC('{unit}', CURRENT_TIMESTAMP)"


def _rewrite_date_modifier(m: re.Match) -> str:
    """Convert DATE('now', '+/-N unit') to DuckDB interval arithmetic on CURRENT_DATE."""
    raw_amount = m.group(1).replace(" ", "")
    unit = _normalize_unit(m.group(2))
    amount = int(raw_amount)
    if amount >= 0:
        return f"(CURRENT_DATE + INTERVAL '{amount}' {unit})"
    else:
        return f"(CURRENT_DATE - INTERVAL '{-amount}' {unit})"


def _rewrite_sql(sql: str) -> str:
    """Apply lightweight rewrites so legacy SQLite SQL runs in DuckDB."""
    # First, rewrite multi-arg datetime/DATE patterns to DuckDB interval syntax.
    updated = _DATETIME_NOW_MODIFIER_RE.sub(_rewrite_datetime_modifier, sql)
    updated = _DATETIME_START_OF_RE.sub(_rewrite_start_of, updated)
    updated = _DATE_NOW_MODIFIER_RE.sub(_rewrite_date_modifier, updated)
    updated = _DATE_NOW_RE.sub("CURRENT_DATE", updated)
    # Then rewrite any remaining single-arg datetime/strftime to shim macros.
    updated = _SQLITE_DATETIME_RE.sub("sqlite_datetime(", updated)
    updated = _SQLITE_STRFTIME_RE.sub("sqlite_strftime(", updated)
    return updated


_MISSING_TABLE_RE = re.compile(r'(?:Table|Relation) with name "?(?P<table>[^"\s]+)"? does not exist', re.I)


class DuckDBDataFrameQuery:
    """
    Execute SQL statements against in-memory pandas DataFrames by delegating
    evaluation to DuckDB. This keeps the contract SQL assets unchanged while
    avoiding a live SQLite database dependency.
    """

    def __init__(self, frames: Mapping[str, pd.DataFrame], loader: SQLiteDataFrameLoader | None = None):
        self._conn = duckdb.connect(database=":memory:")
        self._loader = loader
        self._registered: set[str] = set()
        self._register_frames(frames)
        self._register_sqlite_macros()

    def _register_frames(self, frames: Mapping[str, pd.DataFrame]) -> None:
        for name, frame in frames.items():
            if frame is None:
                continue
            self._register_frame(name, frame)

    def _register_frame(self, name: str, frame: pd.DataFrame) -> None:
        if not name or name in self._registered:
            return
        self._conn.register(name, frame)
        self._registered.add(name)

    def _try_register_missing_table(self, exc: Exception) -> bool:
        if self._loader is None:
            return False
        match = _MISSING_TABLE_RE.search(str(exc))
        if not match:
            return False
        table = match.group("table")
        if not table or table in self._registered:
            return False
        try:
            frame = self._loader.frame(table)
        except Exception:
            return False
        self._register_frame(table, frame)
        return True

    def _register_sqlite_macros(self) -> None:
        """Install lightweight SQLite compatibility macros for DuckDB execution."""
        self._conn.execute(
            """
            CREATE MACRO IF NOT EXISTS sqlite_datetime(x) AS (
                CASE
                    WHEN x IS NULL THEN NULL
                    WHEN LOWER(CAST(x AS VARCHAR)) = 'now' THEN CURRENT_TIMESTAMP
                    WHEN TRY_CAST(x AS DOUBLE) IS NOT NULL THEN TO_TIMESTAMP(CAST(x AS DOUBLE))
                    ELSE TRY_CAST(x AS TIMESTAMP)
                END
            )
            """
        )
        self._conn.execute(
            """
            CREATE MACRO IF NOT EXISTS sqlite_strftime(fmt, value, modifier := NULL) AS (
                CASE
                    WHEN value IS NULL THEN NULL
                    ELSE STRFTIME(sqlite_datetime(value), fmt)
                END
            )
            """
        )
        # Alias the macros to the SQLite function names so legacy SQL keeps working.
        self._conn.execute("CREATE MACRO IF NOT EXISTS datetime(x) AS sqlite_datetime(x)")
        self._conn.execute(
            "CREATE MACRO IF NOT EXISTS strftime(fmt, value, modifier := NULL) AS sqlite_strftime(fmt, value, modifier)"
        )

    def execute(self, sql: str, params: Any | None = None) -> pd.DataFrame:
        prepared_sql, ordered_params = _normalize_params(sql, params)
        rewritten_sql = _rewrite_sql(prepared_sql)
        attempts = 0
        while True:
            try:
                result = self._conn.execute(rewritten_sql, ordered_params)
                return result.fetchdf()
            except duckdb.Error as exc:  # pragma: no cover - surfaced to caller
                if attempts < 5 and self._try_register_missing_table(exc):
                    attempts += 1
                    continue
                raise RuntimeError(f"DuckDB execution failed: {exc}") from exc

    def close(self) -> None:
        self._conn.close()


def eager_load_enabled() -> bool:
    """Return True if DataFrame eager loading is enabled."""
    flag = os.getenv("NEURA_DATAFRAME_EAGER_LOAD", "false")
    return str(flag).strip().lower() in {"1", "true", "yes"}
