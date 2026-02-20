"""Base interfaces for database adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Protocol, Sequence

import pandas as pd

from backend.engine.domain.connections import SchemaInfo, TableInfo, ConnectionTest


@dataclass(frozen=True)
class QueryResult:
    """Result of a database query."""

    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    query: str
    execution_time_ms: float

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame."""
        return pd.DataFrame(self.rows, columns=self.columns)

    def to_dicts(self) -> List[Dict[str, Any]]:
        """Convert to list of dictionaries."""
        return [dict(zip(self.columns, row)) for row in self.rows]


class DataSource(Protocol):
    """Interface for data source access.

    DataSources provide read-only access to databases.
    All data for report generation flows through this interface.
    """

    @property
    def path(self) -> Path:
        """Get the path to the data source."""
        ...

    def test_connection(self) -> ConnectionTest:
        """Test the connection and return health info."""
        ...

    def discover_schema(self) -> SchemaInfo:
        """Discover the database schema."""
        ...

    def execute_query(
        self,
        query: str,
        parameters: Optional[Sequence[Any]] = None,
    ) -> QueryResult:
        """Execute a query and return results."""
        ...

    def stream_query(
        self,
        query: str,
        parameters: Optional[Sequence[Any]] = None,
        batch_size: int = 1000,
    ) -> Iterator[QueryResult]:
        """Stream query results in batches."""
        ...

    def get_table_columns(self, table_name: str) -> List[str]:
        """Get column names for a table."""
        ...

    def get_row_count(self, table_name: str) -> int:
        """Get row count for a table."""
        ...


class SchemaDiscovery(ABC):
    """Abstract base for schema discovery implementations."""

    @abstractmethod
    def discover_tables(self) -> List[TableInfo]:
        """Discover all tables."""
        pass

    @abstractmethod
    def discover_columns(self, table_name: str) -> List[str]:
        """Discover columns for a table."""
        pass

    @abstractmethod
    def build_catalog(self, tables: List[TableInfo]) -> List[str]:
        """Build table.column catalog."""
        pass

    def discover(self) -> SchemaInfo:
        """Full schema discovery."""
        tables = self.discover_tables()
        catalog = self.build_catalog(tables)
        return SchemaInfo(tables=tables, catalog=catalog)
