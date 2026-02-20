"""Snowflake Database Connector.

Connector for Snowflake using snowflake-connector-python.
"""
from __future__ import annotations

import logging
import re
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Identifiers must be alphanumeric / underscores
_SAFE_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _quote_identifier(value: str, label: str = "identifier") -> str:
    """Validate and double-quote a SQL identifier to prevent injection."""
    if not value or not _SAFE_IDENTIFIER_RE.match(value):
        raise ValueError(f"Invalid SQL {label}: {value!r}")
    return f'"{value}"'

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
class SnowflakeConnector(ConnectorBase):
    """Snowflake database connector."""

    connector_id = "snowflake"
    connector_name = "Snowflake"
    connector_type = ConnectorType.DATABASE
    auth_types = [AuthType.BASIC, AuthType.API_KEY]
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
        """Establish connection to Snowflake."""
        try:
            import snowflake.connector

            self._connection = snowflake.connector.connect(
                user=self.config.get("username"),
                password=self.config.get("password"),
                account=self.config.get("account"),
                warehouse=self.config.get("warehouse"),
                database=self.config.get("database"),
                schema=self.config.get("schema", "PUBLIC"),
                role=self.config.get("role"),
            )
            self._connected = True
            return True
        except Exception as e:
            self._connected = False
            raise ConnectionError("Failed to connect to Snowflake") from e

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
        cursor.execute("SHOW SCHEMAS")
        schemas = [row[1] for row in cursor.fetchall()]

        # Get tables
        cursor.execute("SHOW TABLES")
        for row in cursor.fetchall():
            table_name = row[1]
            schema_name = row[3]
            columns = await self._get_columns(schema_name, table_name)
            tables.append(TableInfo(
                name=table_name,
                schema_name=schema_name,
                columns=columns,
            ))

        # Get views
        cursor.execute("SHOW VIEWS")
        for row in cursor.fetchall():
            view_name = row[1]
            schema_name = row[3]
            views.append(TableInfo(
                name=view_name,
                schema_name=schema_name,
            ))

        cursor.close()
        return SchemaInfo(tables=tables, views=views, schemas=schemas)

    async def _get_columns(self, schema_name: str, table_name: str) -> list[ColumnInfo]:
        """Get columns for a table."""
        safe_schema = _quote_identifier(schema_name, "schema name")
        safe_table = _quote_identifier(table_name, "table name")
        cursor = self._connection.cursor()
        cursor.execute(f"DESCRIBE TABLE {safe_schema}.{safe_table}")

        columns = []
        for row in cursor.fetchall():
            columns.append(ColumnInfo(
                name=row[0],
                data_type=row[1],
                nullable=row[3] == "Y",
                primary_key=row[5] == "Y",
                default_value=row[4],
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
            # Add LIMIT if not present
            query_upper = query.upper().strip()
            if query_upper.startswith("SELECT") and "LIMIT" not in query_upper:
                query = f"{query} LIMIT {limit}"

            if parameters:
                cursor.execute(query, parameters)
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
                "account": {"type": "string", "description": "Snowflake account identifier"},
                "username": {"type": "string"},
                "password": {"type": "string", "format": "password"},
                "warehouse": {"type": "string"},
                "database": {"type": "string"},
                "schema": {"type": "string", "default": "PUBLIC"},
                "role": {"type": "string"},
            },
            "required": ["account", "username", "password", "warehouse", "database"],
        }
