"""SQLite database adapter implementation using DataFrames.

All database access goes through pandas DataFrames and DuckDB for query execution.
This eliminates direct SQLite connections after initial table loading.
"""

from __future__ import annotations

import logging
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence

from .dataframes import (
    SQLiteDataFrameLoader,
    DuckDBDataFrameQuery,
    sqlite_shim,
    get_dataframe_store,
    ensure_connection_loaded,
)
from .dataframes.sqlite_loader import eager_load_enabled
from backend.engine.domain.connections import ConnectionTest, SchemaInfo, TableInfo
from .base import DataSource, QueryResult, SchemaDiscovery

logger = logging.getLogger("neura.adapters.sqlite")


class DataFrameConnectionPool:
    """DataFrame-based connection pool using sqlite_shim.

    Instead of managing raw SQLite connections, this manages DataFrameConnections
    that execute queries against in-memory DataFrames via DuckDB.
    """

    def __init__(
        self,
        path: Path,
        readonly: bool = True,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        self._path = path.resolve()
        self._readonly = readonly
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._lock = threading.Lock()
        self._closed = False
        self._active_count = 0

        # Pre-load DataFrames for this database
        from .dataframes.sqlite_loader import get_loader
        self._loader = get_loader(self._path)
        self._loader.frames()  # Eagerly load all tables
        logger.info(f"Loaded {len(self._loader.table_names())} tables into DataFrames for {self._path}")

    def _create_connection(self) -> sqlite_shim.DataFrameConnection:
        """Create a new DataFrame connection."""
        return sqlite_shim.connect(str(self._path))

    @contextmanager
    def acquire(self):
        """Acquire a connection from the pool."""
        if self._closed:
            raise RuntimeError("Connection pool is closed")

        with self._lock:
            self._active_count += 1

        conn = self._create_connection()
        try:
            yield conn
        except Exception:
            raise
        finally:
            try:
                conn.close()
            except Exception as e:
                logger.debug("Connection close failed: %s", e)
            with self._lock:
                self._active_count = max(0, self._active_count - 1)

    def close(self) -> None:
        """Close the pool."""
        self._closed = True

    def status(self) -> Dict[str, Any]:
        """Get pool status."""
        return {
            "pool_size": self._pool_size,
            "active_connections": self._active_count,
            "tables_loaded": len(self._loader.table_names()),
            "closed": self._closed,
        }


# Keep old name for backwards compatibility
SQLiteConnectionPool = DataFrameConnectionPool


class DataFrameSchemaDiscovery(SchemaDiscovery):
    """Schema discovery using DataFrames instead of direct SQLite queries."""

    def __init__(self, loader: SQLiteDataFrameLoader) -> None:
        self._loader = loader
        self._table_info_cache: Dict[str, List[dict]] = {}

    def discover_tables(self) -> List[TableInfo]:
        """Discover all tables from DataFrames."""
        table_names = self._loader.table_names()

        if not table_names:
            return []

        # Prefetch table info
        self._prefetch_table_info(table_names)

        # Get row counts from DataFrames
        row_counts = self._batch_get_row_counts(table_names)

        tables = []
        for table_name in table_names:
            columns, pk = self._get_cached_table_info(table_name)
            tables.append(
                TableInfo(
                    name=table_name,
                    columns=columns,
                    row_count=row_counts.get(table_name, 0),
                    primary_key=pk,
                )
            )
        return tables

    def _prefetch_table_info(self, table_names: List[str]) -> None:
        """Prefetch table info using DataFrame loader."""
        for table_name in table_names:
            try:
                info = self._loader.pragma_table_info(table_name)
                self._table_info_cache[table_name] = info
            except Exception as e:
                logger.debug(f"Failed to get table info for {table_name}: {e}")
                self._table_info_cache[table_name] = []

    def _get_cached_table_info(self, table_name: str) -> tuple[List[str], Optional[str]]:
        """Get columns and primary key from cache."""
        info = self._table_info_cache.get(table_name, [])
        columns = [row.get("name", "") for row in info]
        pk = None
        for row in info:
            if row.get("pk"):
                pk = row.get("name")
                break
        return columns, pk

    def _batch_get_row_counts(self, table_names: List[str]) -> Dict[str, int]:
        """Get row counts from DataFrames."""
        counts = {}
        for table_name in table_names:
            try:
                frame = self._loader.frame(table_name)
                counts[table_name] = len(frame)
            except Exception as e:
                logger.debug(f"Failed to get row count for {table_name}: {e}")
                counts[table_name] = 0
        return counts

    def discover_columns(self, table_name: str) -> List[str]:
        """Discover columns from DataFrame."""
        if table_name in self._table_info_cache:
            return [row.get("name", "") for row in self._table_info_cache[table_name]]
        try:
            frame = self._loader.frame(table_name)
            return list(frame.columns)
        except Exception:
            return []

    def build_catalog(self, tables: List[TableInfo]) -> List[str]:
        """Build table.column catalog."""
        catalog = []
        for table in tables:
            for column in table.columns:
                catalog.append(f"{table.name}.{column}")
        return catalog

    def _get_row_count(self, table_name: str) -> int:
        """Get row count from DataFrame."""
        try:
            frame = self._loader.frame(table_name)
            return len(frame)
        except Exception as e:
            logger.debug(f"Failed to get row count for {table_name}: {e}")
            return 0

    def _get_primary_key(self, table_name: str) -> Optional[str]:
        """Get primary key column from table info."""
        try:
            info = self._loader.pragma_table_info(table_name)
            for row in info:
                if row.get("pk"):
                    return row.get("name")
            return None
        except Exception as e:
            logger.debug(f"Failed to get primary key for {table_name}: {e}")
            return None


# Keep old name for backwards compatibility
SQLiteSchemaDiscovery = DataFrameSchemaDiscovery


class DataFrameDataSource:
    """DataFrame-based implementation of DataSource interface.

    All queries execute against in-memory DataFrames via DuckDB,
    eliminating direct SQLite database access after initial load.
    """

    def __init__(
        self,
        path: Path,
        *,
        readonly: bool = True,
        use_pool: bool = False,
        pool_size: int = 5,
    ) -> None:
        self._path = path.resolve()
        self._readonly = readonly
        self._use_pool = use_pool
        self._pool: Optional[DataFrameConnectionPool] = None

        # Load DataFrames for this database
        from .dataframes.sqlite_loader import get_loader
        self._loader = get_loader(self._path)
        if eager_load_enabled():
            self._loader.frames()  # Eagerly load all tables

        if use_pool:
            self._pool = DataFrameConnectionPool(
                path=self._path,
                readonly=readonly,
                pool_size=pool_size,
            )

        logger.info(f"DataFrameDataSource initialized with {len(self._loader.table_names())} tables")

    @property
    def path(self) -> Path:
        return self._path

    @contextmanager
    def _get_connection(self):
        """Get a DataFrame connection."""
        if self._pool is not None:
            with self._pool.acquire() as conn:
                yield conn
            return

        # Direct connection
        conn = sqlite_shim.connect(str(self._path))
        try:
            yield conn
        finally:
            conn.close()

    def test_connection(self) -> ConnectionTest:
        """Test the connection and return health info."""
        start = time.perf_counter()
        try:
            # Test by accessing DataFrame loader
            table_names = self._loader.table_names()
            table_count = len(table_names)

            # Verify we can access at least one table
            if table_names:
                _ = self._loader.frame(table_names[0])

            latency = (time.perf_counter() - start) * 1000
            return ConnectionTest(
                success=True,
                latency_ms=latency,
                tested_at=datetime.now(timezone.utc),
                table_count=table_count,
            )
        except Exception as e:
            latency = (time.perf_counter() - start) * 1000
            logger.exception("SQLite connection test failed")
            return ConnectionTest(
                success=False,
                latency_ms=latency,
                error="Connection test failed",
                tested_at=datetime.now(timezone.utc),
            )

    def discover_schema(self) -> SchemaInfo:
        """Discover the database schema from DataFrames."""
        discovery = DataFrameSchemaDiscovery(self._loader)
        return discovery.discover()

    def execute_query(
        self,
        query: str,
        parameters: Optional[Sequence[Any]] = None,
    ) -> QueryResult:
        """Execute a query against DataFrames and return results."""
        start = time.perf_counter()
        with self._get_connection() as conn:
            conn.row_factory = sqlite_shim.Row
            cursor = conn.execute(query, parameters or ())
            rows_raw = cursor.fetchall()
            columns = list(rows_raw[0].keys()) if rows_raw else []
            rows = [list(row) for row in rows_raw]
            execution_time = (time.perf_counter() - start) * 1000

        return QueryResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            query=query,
            execution_time_ms=execution_time,
        )

    def stream_query(
        self,
        query: str,
        parameters: Optional[Sequence[Any]] = None,
        batch_size: int = 1000,
    ) -> Iterator[QueryResult]:
        """Stream query results in batches from DataFrames."""
        start = time.perf_counter()

        # Execute full query and yield in batches
        with self._get_connection() as conn:
            conn.row_factory = sqlite_shim.Row
            cursor = conn.execute(query, parameters or ())
            first_batch = cursor.fetchmany(batch_size)
            columns = list(first_batch[0].keys()) if first_batch else []

            batch = first_batch
            while batch:
                execution_time = (time.perf_counter() - start) * 1000
                yield QueryResult(
                    columns=columns,
                    rows=[list(row) for row in batch],
                    row_count=len(batch),
                    query=query,
                    execution_time_ms=execution_time,
                )
                batch = cursor.fetchmany(batch_size)

    def get_table_columns(self, table_name: str) -> List[str]:
        """Get column names from DataFrame."""
        try:
            frame = self._loader.frame(table_name)
            return list(frame.columns)
        except Exception:
            return []

    def get_row_count(self, table_name: str) -> int:
        """Get row count from DataFrame."""
        try:
            frame = self._loader.frame(table_name)
            return len(frame)
        except Exception:
            return 0

    def close(self) -> None:
        """Close the pool."""
        if self._pool:
            self._pool.close()
            self._pool = None

    def pool_status(self) -> Optional[Dict[str, Any]]:
        """Get connection pool status if pooling is enabled."""
        if self._pool:
            return self._pool.status()
        return {
            "tables_loaded": len(self._loader.table_names()),
            "pooling_enabled": False,
        }

    def __del__(self) -> None:
        self.close()


# Keep old name for backwards compatibility
SQLiteDataSource = DataFrameDataSource
