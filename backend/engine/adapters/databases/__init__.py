"""Database adapters for querying data sources."""

from .base import DataSource, QueryResult, SchemaDiscovery
from .sqlite import SQLiteDataSource

__all__ = [
    "DataSource",
    "QueryResult",
    "SchemaDiscovery",
    "SQLiteDataSource",
]
