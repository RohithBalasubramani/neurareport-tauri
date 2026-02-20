"""Elasticsearch Connector.

Connector for Elasticsearch using elasticsearch-py.
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
class ElasticsearchConnector(ConnectorBase):
    """Elasticsearch connector."""

    connector_id = "elasticsearch"
    connector_name = "Elasticsearch"
    connector_type = ConnectorType.DATABASE
    auth_types = [AuthType.BASIC, AuthType.API_KEY, AuthType.NONE]
    capabilities = [
        ConnectorCapability.READ,
        ConnectorCapability.WRITE,
        ConnectorCapability.QUERY,
        ConnectorCapability.SCHEMA_DISCOVERY,
    ]
    free_tier = True

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._client = None

    async def connect(self) -> bool:
        """Establish connection to Elasticsearch."""
        try:
            from elasticsearch import Elasticsearch

            hosts = self.config.get("hosts", ["http://localhost:9200"])
            if isinstance(hosts, str):
                hosts = [hosts]

            auth_type = self.config.get("auth_type", "none")

            if auth_type == "basic":
                self._client = Elasticsearch(
                    hosts,
                    basic_auth=(
                        self.config.get("username"),
                        self.config.get("password"),
                    ),
                    verify_certs=self.config.get("verify_certs", True),
                )
            elif auth_type == "api_key":
                self._client = Elasticsearch(
                    hosts,
                    api_key=self.config.get("api_key"),
                    verify_certs=self.config.get("verify_certs", True),
                )
            else:
                self._client = Elasticsearch(
                    hosts,
                    verify_certs=self.config.get("verify_certs", False),
                )

            self._connected = True
            return True
        except Exception as e:
            self._connected = False
            raise ConnectionError("Failed to connect to Elasticsearch") from e

    async def disconnect(self) -> None:
        """Close the connection."""
        if self._client:
            self._client.close()
            self._client = None
        self._connected = False

    async def test_connection(self) -> ConnectionTest:
        """Test the connection."""
        start_time = time.time()
        try:
            if not self._connected:
                await self.connect()

            info = self._client.info()
            latency = (time.time() - start_time) * 1000

            return ConnectionTest(
                success=True,
                latency_ms=latency,
                details={
                    "cluster_name": info.get("cluster_name"),
                    "version": info.get("version", {}).get("number"),
                },
            )
        except Exception as e:
            logger.warning("connection_test_failed", exc_info=True)
            return ConnectionTest(success=False, error="Connection test failed")

    async def discover_schema(self) -> SchemaInfo:
        """Discover indices (tables) and their mappings."""
        if not self._connected:
            await self.connect()

        tables: list[TableInfo] = []

        # Get all indices
        indices = self._client.indices.get_alias(index="*")

        for index_name in indices.keys():
            # Skip system indices
            if index_name.startswith("."):
                continue

            # Get mapping
            mapping = self._client.indices.get_mapping(index=index_name)
            properties = mapping.get(index_name, {}).get("mappings", {}).get("properties", {})

            columns = []
            for field_name, field_info in properties.items():
                columns.append(ColumnInfo(
                    name=field_name,
                    data_type=field_info.get("type", "object"),
                    nullable=True,
                ))

            # Get document count
            count_response = self._client.count(index=index_name)
            row_count = count_response.get("count", 0)

            tables.append(TableInfo(
                name=index_name,
                columns=columns,
                row_count=row_count,
            ))

        return SchemaInfo(tables=tables)

    async def execute_query(
        self,
        query: str,
        parameters: Optional[dict] = None,
        limit: int = 1000,
    ) -> QueryResult:
        """Execute a search query."""
        if not self._connected:
            await self.connect()

        start_time = time.time()

        try:
            import json

            # Parse query - expect JSON or simple index search
            index = None
            if query.strip().startswith("{"):
                query_body = json.loads(query)
            else:
                # Simple search on index
                parts = query.split(":", 1)
                if len(parts) == 2:
                    index = parts[0].strip()
                    search_term = parts[1].strip()
                    query_body = {
                        "query": {
                            "query_string": {"query": search_term}
                        }
                    }
                else:
                    index = query.strip()
                    query_body = {"query": {"match_all": {}}}

            if index is None:
                index = parameters.get("index", "*") if parameters else "*"

            response = self._client.search(
                index=index,
                body=query_body,
                size=limit,
            )

            hits = response.get("hits", {}).get("hits", [])

            if hits:
                # Extract columns from first hit
                first_source = hits[0].get("_source", {})
                columns = ["_id", "_index"] + list(first_source.keys())

                rows = []
                for hit in hits:
                    source = hit.get("_source", {})
                    row = [hit.get("_id"), hit.get("_index")]
                    row.extend(source.get(col) for col in list(first_source.keys()))
                    rows.append(row)
            else:
                columns = []
                rows = []

            execution_time = (time.time() - start_time) * 1000

            return QueryResult(
                columns=columns,
                rows=rows,
                row_count=len(rows),
                execution_time_ms=execution_time,
                truncated=len(rows) >= limit,
            )
        except Exception as e:
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
                "hosts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["http://localhost:9200"],
                    "description": "Elasticsearch hosts",
                },
                "auth_type": {
                    "type": "string",
                    "enum": ["none", "basic", "api_key"],
                    "default": "none",
                },
                "username": {"type": "string"},
                "password": {"type": "string", "format": "password"},
                "api_key": {"type": "string"},
                "verify_certs": {"type": "boolean", "default": True},
            },
            "required": ["hosts"],
        }
