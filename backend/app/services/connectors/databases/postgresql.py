"""
PostgreSQL Connector - Connect to PostgreSQL databases.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

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

logger = logging.getLogger("neura.connectors.postgresql")


@register_connector
class PostgreSQLConnector(ConnectorBase):
    """PostgreSQL database connector using asyncpg."""

    connector_id = "postgresql"
    connector_name = "PostgreSQL"
    connector_type = ConnectorType.DATABASE
    auth_types = [AuthType.BASIC, AuthType.CONNECTION_STRING]
    capabilities = [
        ConnectorCapability.READ,
        ConnectorCapability.WRITE,
        ConnectorCapability.SCHEMA_DISCOVERY,
        ConnectorCapability.QUERY,
    ]
    free_tier = True

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._pool = None

    async def connect(self) -> bool:
        """Establish connection to PostgreSQL."""
        try:
            import asyncpg

            # Check if connection string provided
            if "connection_string" in self.config:
                self._pool = await asyncpg.create_pool(
                    self.config["connection_string"],
                    min_size=1,
                    max_size=5,
                )
            else:
                self._pool = await asyncpg.create_pool(
                    host=self.config.get("host", "localhost"),
                    port=self.config.get("port", 5432),
                    user=self.config.get("username"),
                    password=self.config.get("password"),
                    database=self.config.get("database"),
                    ssl=self.config.get("ssl", False),
                    min_size=1,
                    max_size=5,
                )

            self._connected = True
            logger.info(f"Connected to PostgreSQL: {self.config.get('host', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self._connected = False
            raise

    async def disconnect(self) -> None:
        """Close PostgreSQL connection."""
        if self._pool:
            await self._pool.close()
            self._pool = None
        self._connected = False
        logger.info("Disconnected from PostgreSQL")

    async def test_connection(self) -> ConnectionTest:
        """Test PostgreSQL connection."""
        start = time.perf_counter()
        try:
            if not self._pool:
                await self.connect()

            async with self._pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")

            latency_ms = (time.perf_counter() - start) * 1000
            return ConnectionTest(
                success=True,
                latency_ms=latency_ms,
                details={"version": "PostgreSQL"},
            )
        except Exception as e:
            logger.warning("connection_test_failed", exc_info=True)
            return ConnectionTest(
                success=False,
                error="Connection test failed",
            )

    async def discover_schema(self) -> SchemaInfo:
        """Discover PostgreSQL schema."""
        if not self._pool:
            await self.connect()

        tables = []
        views = []
        schemas = []

        async with self._pool.acquire() as conn:
            # Get schemas
            schema_rows = await conn.fetch("""
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                ORDER BY schema_name
            """)
            schemas = [row["schema_name"] for row in schema_rows]

            # Get tables
            table_rows = await conn.fetch("""
                SELECT
                    t.table_schema,
                    t.table_name,
                    t.table_type
                FROM information_schema.tables t
                WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema')
                ORDER BY t.table_schema, t.table_name
            """)

            for row in table_rows:
                # Get columns for this table
                column_rows = await conn.fetch("""
                    SELECT
                        c.column_name,
                        c.data_type,
                        c.is_nullable,
                        c.column_default,
                        CASE WHEN pk.column_name IS NOT NULL THEN TRUE ELSE FALSE END as is_primary_key
                    FROM information_schema.columns c
                    LEFT JOIN (
                        SELECT ku.column_name, ku.table_name, ku.table_schema
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage ku
                            ON tc.constraint_name = ku.constraint_name
                            AND tc.table_schema = ku.table_schema
                        WHERE tc.constraint_type = 'PRIMARY KEY'
                    ) pk ON c.column_name = pk.column_name
                        AND c.table_name = pk.table_name
                        AND c.table_schema = pk.table_schema
                    WHERE c.table_schema = $1 AND c.table_name = $2
                    ORDER BY c.ordinal_position
                """, row["table_schema"], row["table_name"])

                columns = [
                    ColumnInfo(
                        name=col["column_name"],
                        data_type=col["data_type"],
                        nullable=col["is_nullable"] == "YES",
                        primary_key=col["is_primary_key"],
                        default_value=col["column_default"],
                    )
                    for col in column_rows
                ]

                table_info = TableInfo(
                    name=row["table_name"],
                    schema_name=row["table_schema"],
                    columns=columns,
                )

                if row["table_type"] == "VIEW":
                    views.append(table_info)
                else:
                    tables.append(table_info)

        return SchemaInfo(tables=tables, views=views, schemas=schemas)

    async def execute_query(
        self,
        query: str,
        parameters: Optional[dict] = None,
        limit: int = 1000,
    ) -> QueryResult:
        """Execute a SQL query."""
        if not self._pool:
            await self.connect()

        start = time.perf_counter()
        try:
            async with self._pool.acquire() as conn:
                # Add LIMIT if not present
                query_lower = query.lower().strip()
                if query_lower.startswith("select") and "limit" not in query_lower:
                    query = f"{query} LIMIT {limit}"

                # Execute query
                if parameters:
                    rows = await conn.fetch(query, *parameters.values())
                else:
                    rows = await conn.fetch(query)

                execution_time = (time.perf_counter() - start) * 1000

                if not rows:
                    return QueryResult(
                        columns=[],
                        rows=[],
                        row_count=0,
                        execution_time_ms=execution_time,
                    )

                # Extract column names
                columns = list(rows[0].keys())

                # Convert to list of lists
                data = [[row[col] for col in columns] for row in rows]

                return QueryResult(
                    columns=columns,
                    rows=data,
                    row_count=len(data),
                    execution_time_ms=execution_time,
                    truncated=len(data) >= limit,
                )
        except Exception as e:
            logger.exception("query_execution_failed")
            execution_time = (time.perf_counter() - start) * 1000
            return QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                execution_time_ms=execution_time,
                error="Query execution failed",
            )

    @classmethod
    def get_config_schema(cls) -> dict[str, Any]:
        """Get configuration schema for PostgreSQL."""
        return {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "description": "Database host",
                    "default": "localhost",
                },
                "port": {
                    "type": "integer",
                    "description": "Database port",
                    "default": 5432,
                },
                "database": {
                    "type": "string",
                    "description": "Database name",
                },
                "username": {
                    "type": "string",
                    "description": "Username",
                },
                "password": {
                    "type": "string",
                    "format": "password",
                    "description": "Password",
                },
                "ssl": {
                    "type": "boolean",
                    "description": "Use SSL connection",
                    "default": False,
                },
                "connection_string": {
                    "type": "string",
                    "description": "Full connection string (alternative to individual fields)",
                },
            },
            "required": ["database", "username", "password"],
        }
