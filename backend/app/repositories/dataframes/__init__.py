"""Shared DataFrame helpers for SQL-lite pipelines."""

from .sqlite_loader import DuckDBDataFrameQuery, SQLiteDataFrameLoader
from .sqlite_shim import connect, DataFrameConnection, DataFrameCursor, Row
from .store import (
    DataFrameStore,
    dataframe_store,
    get_dataframe_store,
    ensure_connection_loaded,
)

__all__ = [
    "SQLiteDataFrameLoader",
    "DuckDBDataFrameQuery",
    "connect",
    "DataFrameConnection",
    "DataFrameCursor",
    "Row",
    "DataFrameStore",
    "dataframe_store",
    "get_dataframe_store",
    "ensure_connection_loaded",
]
