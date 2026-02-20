from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Sequence

import pandas as pd

from .sqlite_loader import DuckDBDataFrameQuery, get_loader, eager_load_enabled


class Error(Exception):
    """Base error matching sqlite3.Error."""


class OperationalError(Error):
    """Raised when SQL execution fails."""


class Row:
    """Lightweight sqlite3.Row replacement supporting dict + index access."""

    __slots__ = ("_columns", "_values", "_mapping")

    def __init__(self, columns: Sequence[str], values: Sequence[Any]):
        self._columns = list(columns)
        self._values = tuple(values)
        self._mapping = {col: value for col, value in zip(self._columns, self._values)}

    def __getitem__(self, key: int | str) -> Any:
        if isinstance(key, int):
            return self._values[key]
        return self._mapping[key]

    def keys(self) -> list[str]:
        return list(self._columns)

    def __iter__(self):
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __repr__(self) -> str:
        items = ", ".join(f"{col}={self._mapping[col]!r}" for col in self._columns)
        return f"Row({items})"


def _apply_row_factory(columns: list[str], values: Sequence[Any], factory: Any | None):
    if factory is None:
        return tuple(values)
    if factory is Row:
        return Row(columns, values)
    return factory(columns, values)


class DataFrameCursor:
    def __init__(self, connection: "DataFrameConnection"):
        self.connection = connection
        self._df: pd.DataFrame | None = None
        self._columns: list[str] = []
        self._pos = 0

    def execute(self, sql: str, params: Any | None = None) -> "DataFrameCursor":
        meta_df = self._try_meta_query(sql)
        if meta_df is not None:
            self._df = meta_df
            self._columns = list(meta_df.columns)
            self._pos = 0
            return self
        try:
            df = self.connection._query.execute(sql, params)
        except Exception as exc:  # pragma: no cover - propagated to caller
            raise OperationalError(str(exc)) from exc
        self._df = df
        self._columns = list(df.columns)
        self._pos = 0
        return self

    def _try_meta_query(self, sql: str) -> pd.DataFrame | None:
        sql_clean = (sql or "").strip()
        pragma_match = re.match(r"(?is)^PRAGMA\s+table_info\(['\"]?(?P<table>[^'\")]+)['\"]?\)\s*;?$", sql_clean)
        if pragma_match:
            table_name = pragma_match.group("table")
            try:
                rows = self.connection._loader.pragma_table_info(table_name)
            except Exception:
                rows = []
            data = [
                (
                    int(row.get("cid", 0)),
                    str(row.get("name", "")),
                    str(row.get("type", "")),
                    int(row.get("notnull", 0)),
                    row.get("dflt_value"),
                    int(row.get("pk", 0)),
                )
                for row in rows
            ]
            return pd.DataFrame(data, columns=["cid", "name", "type", "notnull", "dflt_value", "pk"])

        fk_match = re.match(r"(?is)^PRAGMA\s+foreign_key_list\(['\"]?(?P<table>[^'\")]+)['\"]?\)\s*;?$", sql_clean)
        if fk_match:
            table_name = fk_match.group("table")
            try:
                rows = self.connection._loader.foreign_keys(table_name)
            except Exception:
                rows = []
            data = [
                (
                    int(row.get("id", 0)),
                    int(row.get("seq", 0)),
                    str(row.get("table", "")),
                    str(row.get("from", "")),
                    str(row.get("to", "")),
                    str(row.get("on_update", "")),
                    str(row.get("on_delete", "")),
                    str(row.get("match", "")),
                )
                for row in rows
            ]
            return pd.DataFrame(
                data, columns=["id", "seq", "table", "from", "to", "on_update", "on_delete", "match"]
            )

        if "sqlite_master" in sql_clean.lower():
            names = [name for name in self.connection._loader.table_names() if not name.lower().startswith("sqlite_")]
            data = [(name,) for name in sorted(names)]
            return pd.DataFrame(data, columns=["name"])
        return None

    def fetchone(self):
        if self._df is None:
            return None
        if self._pos >= len(self._df):
            return None
        row = self._df.iloc[self._pos].tolist()
        self._pos += 1
        return _apply_row_factory(self._columns, row, self.connection.row_factory)

    def fetchall(self):
        rows = []
        while True:
            row = self.fetchone()
            if row is None:
                break
            rows.append(row)
        return rows

    def fetchmany(self, size: int = 1):
        if size is None:
            size = 1
        rows = []
        for _ in range(max(0, int(size))):
            row = self.fetchone()
            if row is None:
                break
            rows.append(row)
        return rows

    def __iter__(self):
        while True:
            row = self.fetchone()
            if row is None:
                return
            yield row


class DataFrameConnection:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self._loader = get_loader(self.db_path)
        if eager_load_enabled():
            frames = self._loader.frames()
        else:
            frames = {}
        self._query = DuckDBDataFrameQuery(frames, loader=self._loader)
        self.row_factory: Any | None = None

    def cursor(self) -> DataFrameCursor:
        return DataFrameCursor(self)

    def execute(self, sql: str, params: Any | None = None) -> DataFrameCursor:
        return self.cursor().execute(sql, params)

    def close(self) -> None:
        self._query.close()

    def commit(self) -> None:  # pragma: no cover - compatibility no-op
        return None

    def rollback(self) -> None:  # pragma: no cover - compatibility no-op
        return None

    def __enter__(self) -> "DataFrameConnection":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def connect(db_path: str | Path, **_kwargs) -> DataFrameConnection:
    """sqlite3.connect-compatible entrypoint backed by pandas DataFrames."""
    return DataFrameConnection(Path(db_path))
