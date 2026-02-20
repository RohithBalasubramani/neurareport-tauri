"""
MySQL Connector - Connect to MySQL/MariaDB databases.
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

logger = logging.getLogger("neura.connectors.mysql")


@register_connector
class MySQLConnector(ConnectorBase):
    """MySQL/MariaDB database connector using pymysql."""

    connector_id = "mysql"
    connector_name = "MySQL / MariaDB"
    connector_type = ConnectorType.DATABASE
    auth_types = [AuthType.BASIC]
    capabilities = [
        ConnectorCapability.READ,
        ConnectorCapability.WRITE,
        ConnectorCapability.SCHEMA_DISCOVERY,
        ConnectorCapability.QUERY,
    ]
    free_tier = True

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._connection = None

    async def connect(self) -> bool:
        """Establish connection to MySQL."""
        try:
            import pymysql

            self._connection = pymysql.connect(
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", 3306),
                user=self.config.get("username"),
                password=self.config.get("password"),
                database=self.config.get("database"),
                charset=self.config.get("charset", "utf8mb4"),
                cursorclass=pymysql.cursors.DictCursor,
                ssl=self.config.get("ssl"),
            )

            self._connected = True
            logger.info(f"Connected to MySQL: {self.config.get('host', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MySQL: {e}")
            self._connected = False
            raise

    async def disconnect(self) -> None:
        """Close MySQL connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
        self._connected = False
        logger.info("Disconnected from MySQL")

    async def test_connection(self) -> ConnectionTest:
        """Test MySQL connection."""
        start = time.perf_counter()
        try:
            if not self._connection:
                await self.connect()

            with self._connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

            latency_ms = (time.perf_counter() - start) * 1000
            return ConnectionTest(
                success=True,
                latency_ms=latency_ms,
                details={"version": "MySQL/MariaDB"},
            )
        except Exception as e:
            logger.warning("connection_test_failed", exc_info=True)
            return ConnectionTest(
                success=False,
                error="Connection test failed",
            )

    async def discover_schema(self) -> SchemaInfo:
        """Discover MySQL schema."""
        if not self._connection:
            await self.connect()

        tables = []
        views = []
        database = self.config.get("database")

        with self._connection.cursor() as cursor:
            # Get tables
            cursor.execute("""
                SELECT TABLE_NAME, TABLE_TYPE
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME
            """, (database,))
            table_rows = cursor.fetchall()

            for row in table_rows:
                table_name = row["TABLE_NAME"]

                # Get columns
                cursor.execute("""
                    SELECT
                        COLUMN_NAME,
                        DATA_TYPE,
                        IS_NULLABLE,
                        COLUMN_DEFAULT,
                        COLUMN_KEY
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                    ORDER BY ORDINAL_POSITION
                """, (database, table_name))
                column_rows = cursor.fetchall()

                columns = [
                    ColumnInfo(
                        name=col["COLUMN_NAME"],
                        data_type=col["DATA_TYPE"],
                        nullable=col["IS_NULLABLE"] == "YES",
                        primary_key=col["COLUMN_KEY"] == "PRI",
                        default_value=col["COLUMN_DEFAULT"],
                    )
                    for col in column_rows
                ]

                table_info = TableInfo(
                    name=table_name,
                    schema_name=database,
                    columns=columns,
                )

                if row["TABLE_TYPE"] == "VIEW":
                    views.append(table_info)
                else:
                    tables.append(table_info)

        return SchemaInfo(tables=tables, views=views, schemas=[database])

    async def execute_query(
        self,
        query: str,
        parameters: Optional[dict] = None,
        limit: int = 1000,
    ) -> QueryResult:
        """Execute a SQL query."""
        if not self._connection:
            await self.connect()

        start = time.perf_counter()
        try:
            # Add LIMIT if not present
            query_lower = query.lower().strip()
            if query_lower.startswith("select") and "limit" not in query_lower:
                query = f"{query} LIMIT {limit}"

            with self._connection.cursor() as cursor:
                if parameters:
                    cursor.execute(query, tuple(parameters.values()))
                else:
                    cursor.execute(query)

                rows = cursor.fetchall()
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
        """Get configuration schema for MySQL."""
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
                    "default": 3306,
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
                "charset": {
                    "type": "string",
                    "description": "Character set",
                    "default": "utf8mb4",
                },
            },
            "required": ["database", "username", "password"],
        }
