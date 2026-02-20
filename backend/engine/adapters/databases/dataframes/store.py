"""
Centralized DataFrame Store for connection-based DataFrame management.

This module provides a singleton store that:
1. Automatically loads all database tables as DataFrames when a connection is used
2. Caches DataFrames per connection_id for reuse
3. Provides a unified interface to access DataFrames across all services
4. Eliminates direct database access after initial load
"""

from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from .sqlite_loader import DuckDBDataFrameQuery, SQLiteDataFrameLoader, get_loader, eager_load_enabled

logger = logging.getLogger("neura.dataframes.store")


class DataFrameStore:
    """
    Centralized store for managing DataFrames by connection.

    All database interactions go through this store, ensuring:
    - Tables are loaded once as DataFrames and cached
    - All queries run against in-memory DataFrames via DuckDB
    - No direct database connections after initial load
    """

    _instance: Optional["DataFrameStore"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "DataFrameStore":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._loaders: Dict[str, SQLiteDataFrameLoader] = {}
        self._frames_cache: Dict[str, Dict[str, pd.DataFrame]] = {}
        self._db_paths: Dict[str, Path] = {}
        self._query_engines: Dict[str, DuckDBDataFrameQuery] = {}
        self._store_lock = threading.Lock()
        self._initialized = True
        logger.info("DataFrameStore initialized")

    def register_connection(self, connection_id: str, db_path: Path) -> None:
        """
        Register a database connection and load all tables as DataFrames.

        This should be called when a connection is established. All tables
        will be loaded into memory as DataFrames for subsequent queries.
        """
        db_path = Path(db_path).resolve()

        with self._store_lock:
            # Check if already registered with same path
            existing_path = self._db_paths.get(connection_id)
            if existing_path and existing_path == db_path:
                # Already registered, check if file modified
                loader = self._loaders.get(connection_id)
                if loader:
                    current_mtime = os.path.getmtime(db_path) if db_path.exists() else 0.0
                    if loader._mtime == current_mtime:
                        logger.debug(f"Connection {connection_id} already registered and up to date")
                        return

            logger.info(f"Loading DataFrames for connection {connection_id} from {db_path}")
            loader = get_loader(db_path)
            eager = eager_load_enabled()
            frames = loader.frames() if eager else {}

            # Close existing query engine if any
            existing_engine = self._query_engines.get(connection_id)
            if existing_engine:
                try:
                    existing_engine.close()
                except Exception as e:
                    logger.debug("Engine close failed: %s", e)

            # Store everything
            self._loaders[connection_id] = loader
            self._frames_cache[connection_id] = frames if frames else {}
            self._db_paths[connection_id] = db_path
            self._query_engines[connection_id] = DuckDBDataFrameQuery(frames, loader=loader)

            logger.info(
                f"Loaded {len(frames)} tables for connection {connection_id}: {list(frames.keys())}"
                if frames else f"Registered connection {connection_id} for lazy DataFrame loading"
            )

    def get_loader(self, connection_id: str) -> Optional[SQLiteDataFrameLoader]:
        """Get the loader for a connection."""
        with self._store_lock:
            return self._loaders.get(connection_id)

    def get_frames(self, connection_id: str) -> Dict[str, pd.DataFrame]:
        """Get all DataFrames for a connection."""
        with self._store_lock:
            return self._frames_cache.get(connection_id, {})

    def get_frame(self, connection_id: str, table_name: str) -> Optional[pd.DataFrame]:
        """Get a specific DataFrame for a connection."""
        frames = self.get_frames(connection_id)
        return frames.get(table_name)

    def get_query_engine(self, connection_id: str) -> Optional[DuckDBDataFrameQuery]:
        """Get the DuckDB query engine for a connection."""
        with self._store_lock:
            return self._query_engines.get(connection_id)

    def execute_query(
        self,
        connection_id: str,
        sql: str,
        params: Any = None,
    ) -> pd.DataFrame:
        """
        Execute a SQL query against the DataFrames for a connection.

        Returns results as a DataFrame.
        """
        engine = self.get_query_engine(connection_id)
        if engine is None:
            raise ValueError(f"Connection {connection_id} not registered in DataFrameStore")
        return engine.execute(sql, params)

    def execute_query_to_dicts(
        self,
        connection_id: str,
        sql: str,
        params: Any = None,
    ) -> list[dict[str, Any]]:
        """
        Execute a SQL query and return results as list of dicts.

        This is the preferred method for API responses.
        """
        df = self.execute_query(connection_id, sql, params)
        return df.to_dict("records")

    def get_table_names(self, connection_id: str) -> list[str]:
        """Get list of table names for a connection."""
        loader = self.get_loader(connection_id)
        if loader is None:
            return []
        return loader.table_names()

    def get_table_info(self, connection_id: str, table_name: str) -> list[dict[str, Any]]:
        """Get PRAGMA table_info equivalent for a table."""
        loader = self.get_loader(connection_id)
        if loader is None:
            return []
        return loader.pragma_table_info(table_name)

    def get_foreign_keys(self, connection_id: str, table_name: str) -> list[dict[str, Any]]:
        """Get foreign keys for a table."""
        loader = self.get_loader(connection_id)
        if loader is None:
            return []
        return loader.foreign_keys(table_name)

    def invalidate_connection(self, connection_id: str) -> None:
        """
        Invalidate cached DataFrames for a connection.

        Call this when the underlying database changes.
        """
        with self._store_lock:
            engine = self._query_engines.pop(connection_id, None)
            if engine:
                try:
                    engine.close()
                except Exception as e:
                    logger.debug("Engine close failed: %s", e)
            self._loaders.pop(connection_id, None)
            self._frames_cache.pop(connection_id, None)
            self._db_paths.pop(connection_id, None)
            logger.info(f"Invalidated DataFrames for connection {connection_id}")

    def is_registered(self, connection_id: str) -> bool:
        """Check if a connection is registered."""
        with self._store_lock:
            return connection_id in self._loaders

    def get_db_path(self, connection_id: str) -> Optional[Path]:
        """Get the database path for a connection."""
        with self._store_lock:
            return self._db_paths.get(connection_id)

    def status(self) -> dict[str, Any]:
        """Get store status."""
        with self._store_lock:
            return {
                "connections": list(self._loaders.keys()),
                "total_connections": len(self._loaders),
                "tables_per_connection": {
                    conn_id: len(frames)
                    for conn_id, frames in self._frames_cache.items()
                },
            }

    def clear(self) -> None:
        """Clear all cached DataFrames."""
        with self._store_lock:
            for engine in self._query_engines.values():
                try:
                    engine.close()
                except Exception as e:
                    logger.debug("Engine close failed: %s", e)
            self._loaders.clear()
            self._frames_cache.clear()
            self._db_paths.clear()
            self._query_engines.clear()
            logger.info("DataFrameStore cleared")


# Singleton instance
dataframe_store = DataFrameStore()


def get_dataframe_store() -> DataFrameStore:
    """Get the singleton DataFrameStore instance."""
    return dataframe_store


def ensure_connection_loaded(connection_id: str, db_path: Path) -> DataFrameStore:
    """
    Ensure a connection's DataFrames are loaded in the store.

    Convenience function that registers the connection if needed and returns the store.
    """
    store = get_dataframe_store()
    if not store.is_registered(connection_id):
        store.register_connection(connection_id, db_path)
    return store
