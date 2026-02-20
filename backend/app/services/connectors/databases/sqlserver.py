"""SQL Server Database Connector.

Connector for Microsoft SQL Server using pymssql.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)

from ..base import (
    AuthType,
    ColumnInfo,
    ConnectionTest,
    ConnectorBase,
    ConnectorCapability,
    ConnectorType,
    QueryResult,
    SchemaInfo,
    TableInfo,
)
from ..registry import register_connector


@register_connector
class SQLServerConnector(ConnectorBase):
    """Microsoft SQL Server database connector."""

    connector_id = "sqlserver"
    connector_name = "Microsoft SQL Server"
    connector_type = ConnectorType.DATABASE
    auth_types = [AuthType.BASIC, AuthType.CONNECTION_STRING]
    capabilities = [
        ConnectorCapability.READ,
        ConnectorCapability.WRITE,
        ConnectorCapability.QUERY,
        ConnectorCapability.SCHEMA_DISCOVERY,
    ]
    free_tier = True

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._connection = None

    async def connect(self) -> bool:
        """Establish connection to SQL Server."""
        try:
            import pymssql

            self._connection = pymssql.connect(
                server=self.config.get("host", "localhost"),
                port=self.config.get("port", 1433),
                user=self.config.get("username"),
                password=self.config.get("password"),
                database=self.config.get("database"),
                as_dict=False,
            )
            self._connected = True
            return True
        except Exception as e:
            self._connected = False
            raise ConnectionError("Failed to connect to SQL Server") from e

    async def disconnect(self) -> None:
        """Close the connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
        self._connected = False

    async def test_connection(self) -> ConnectionTest:
        """Test the connection."""
        start_time = time.time()
        try:
            if not self._connected:
                await self.connect()

            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()

            latency = (time.time() - start_time) * 1000
            return ConnectionTest(success=True, latency_ms=latency)
        except Exception as e:
            logger.warning("connection_test_failed", exc_info=True)
            return ConnectionTest(success=False, error="Connection test failed")

    async def discover_schema(self) -> SchemaInfo:
        """Discover database schema."""
        if not self._connected:
            await self.connect()

        tables: list[TableInfo] = []
        views: list[TableInfo] = []
        schemas: list[str] = []

        cursor = self._connection.cursor()

        # Get schemas
        cursor.execute("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('sys', 'guest', 'INFORMATION_SCHEMA')
        """)
        schemas = [row[0] for row in cursor.fetchall()]

        # Get tables
        cursor.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
        """)
        for schema_name, table_name in cursor.fetchall():
            columns = await self._get_columns(schema_name, table_name)
            tables.append(TableInfo(
                name=table_name,
                schema_name=schema_name,
                columns=columns,
            ))

        # Get views
        cursor.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type = 'VIEW'
        """)
        for schema_name, view_name in cursor.fetchall():
            views.append(TableInfo(
                name=view_name,
                schema_name=schema_name,
            ))

        cursor.close()
        return SchemaInfo(tables=tables, views=views, schemas=schemas)

    async def _get_columns(self, schema_name: str, table_name: str) -> list[ColumnInfo]:
        """Get columns for a table."""
        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """, (schema_name, table_name))

        columns = []
        for name, dtype, nullable, default in cursor.fetchall():
            columns.append(ColumnInfo(
                name=name,
                data_type=dtype,
                nullable=nullable == "YES",
                default_value=default,
            ))

        cursor.close()
        return columns

    async def execute_query(
        self,
        query: str,
        parameters: Optional[dict] = None,
        limit: int = 1000,
    ) -> QueryResult:
        """Execute a SQL query."""
        if not self._connected:
            await self.connect()

        start_time = time.time()
        cursor = self._connection.cursor()

        try:
            # Add TOP clause if not present
            query_upper = query.upper().strip()
            if query_upper.startswith("SELECT") and "TOP" not in query_upper:
                query = query.replace("SELECT", f"SELECT TOP {limit}", 1)

            if parameters:
                cursor.execute(query, tuple(parameters.values()))
            else:
                cursor.execute(query)

            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = [list(row) for row in cursor.fetchall()]
            else:
                columns = []
                rows = []

            execution_time = (time.time() - start_time) * 1000
            cursor.close()

            return QueryResult(
                columns=columns,
                rows=rows,
                row_count=len(rows),
                execution_time_ms=execution_time,
                truncated=len(rows) >= limit,
            )
        except Exception as e:
            cursor.close()
            logger.exception("query_execution_failed")
            return QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                execution_time_ms=(time.time() - start_time) * 1000,
                error="Query execution failed",
            )

    @classmethod
    def get_config_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "host": {"type": "string", "description": "Server hostname"},
                "port": {"type": "integer", "default": 1433},
                "username": {"type": "string"},
                "password": {"type": "string", "format": "password"},
                "database": {"type": "string"},
            },
            "required": ["host", "username", "password", "database"],
        }
