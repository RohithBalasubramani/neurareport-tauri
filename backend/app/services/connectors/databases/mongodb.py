"""
MongoDB Connector - Connect to MongoDB databases.
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

logger = logging.getLogger("neura.connectors.mongodb")


@register_connector
class MongoDBConnector(ConnectorBase):
    """MongoDB database connector using pymongo."""

    connector_id = "mongodb"
    connector_name = "MongoDB"
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
        self._client = None
        self._db = None

    async def connect(self) -> bool:
        """Establish connection to MongoDB."""
        try:
            from pymongo import MongoClient

            # Check if connection string provided
            if "connection_string" in self.config:
                self._client = MongoClient(self.config["connection_string"])
            else:
                host = self.config.get("host", "localhost")
                port = self.config.get("port", 27017)
                username = self.config.get("username")
                password = self.config.get("password")

                if username and password:
                    uri = f"mongodb://{username}:{password}@{host}:{port}/"
                else:
                    uri = f"mongodb://{host}:{port}/"

                self._client = MongoClient(uri)

            # Select database
            database = self.config.get("database", "test")
            self._db = self._client[database]

            # Test connection
            self._client.server_info()

            self._connected = True
            logger.info(f"Connected to MongoDB: {self.config.get('host', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._connected = False
            raise

    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
        self._connected = False
        logger.info("Disconnected from MongoDB")

    async def test_connection(self) -> ConnectionTest:
        """Test MongoDB connection."""
        start = time.perf_counter()
        try:
            if not self._client:
                await self.connect()

            self._client.server_info()

            latency_ms = (time.perf_counter() - start) * 1000
            return ConnectionTest(
                success=True,
                latency_ms=latency_ms,
                details={"version": "MongoDB"},
            )
        except Exception as e:
            logger.exception("MongoDB connection test failed")
            return ConnectionTest(
                success=False,
                error="Connection test failed",
            )

    async def discover_schema(self) -> SchemaInfo:
        """Discover MongoDB collections and sample schema."""
        if not self._db:
            await self.connect()

        tables = []  # Collections in MongoDB

        # Get collection names
        collection_names = self._db.list_collection_names()

        for coll_name in collection_names:
            collection = self._db[coll_name]

            # Sample documents to infer schema
            sample = collection.find_one()
            columns = []

            if sample:
                for key, value in sample.items():
                    data_type = self._infer_type(value)
                    columns.append(ColumnInfo(
                        name=key,
                        data_type=data_type,
                        nullable=True,
                        primary_key=(key == "_id"),
                    ))

            # Get estimated count
            try:
                row_count = collection.estimated_document_count()
            except Exception as e:
                logger.debug("Failed to get collection count: %s", e)
                row_count = None

            tables.append(TableInfo(
                name=coll_name,
                columns=columns,
                row_count=row_count,
            ))

        return SchemaInfo(
            tables=tables,
            schemas=[self.config.get("database", "test")],
        )

    async def execute_query(
        self,
        query: str,
        parameters: Optional[dict] = None,
        limit: int = 1000,
    ) -> QueryResult:
        """
        Execute a MongoDB query.

        Query format: collection_name or JSON query spec
        """
        if not self._db:
            await self.connect()

        start = time.perf_counter()
        try:
            import json

            # Parse query
            # Format: {"collection": "users", "filter": {"age": {"$gt": 25}}}
            # Or just collection name: "users"
            if query.startswith("{"):
                query_spec = json.loads(query)
                collection_name = query_spec.get("collection")
                filter_spec = query_spec.get("filter", {})
                projection = query_spec.get("projection")
                sort = query_spec.get("sort")
            else:
                collection_name = query.strip()
                filter_spec = parameters or {}
                projection = None
                sort = None

            collection = self._db[collection_name]

            # Build query
            cursor = collection.find(filter_spec, projection)

            if sort:
                cursor = cursor.sort(list(sort.items()))

            cursor = cursor.limit(limit)

            # Fetch results
            documents = list(cursor)
            execution_time = (time.perf_counter() - start) * 1000

            if not documents:
                return QueryResult(
                    columns=[],
                    rows=[],
                    row_count=0,
                    execution_time_ms=execution_time,
                )

            # Extract column names from first document
            columns = list(documents[0].keys())

            # Convert to list of lists
            data = []
            for doc in documents:
                row = []
                for col in columns:
                    val = doc.get(col)
                    # Convert ObjectId to string
                    if hasattr(val, "__str__") and type(val).__name__ == "ObjectId":
                        val = str(val)
                    row.append(val)
                data.append(row)

            return QueryResult(
                columns=columns,
                rows=data,
                row_count=len(data),
                execution_time_ms=execution_time,
                truncated=len(data) >= limit,
            )
        except Exception as e:
            execution_time = (time.perf_counter() - start) * 1000
            logger.exception("MongoDB query execution failed")
            return QueryResult(
                columns=[],
                rows=[],
                row_count=0,
                execution_time_ms=execution_time,
                error="Query execution failed",
            )

    def _infer_type(self, value: Any) -> str:
        """Infer MongoDB field type from value."""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "double"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        elif hasattr(value, "__class__"):
            type_name = type(value).__name__
            if type_name == "ObjectId":
                return "objectId"
            elif type_name == "datetime":
                return "date"
        return "unknown"

    @classmethod
    def get_config_schema(cls) -> dict[str, Any]:
        """Get configuration schema for MongoDB."""
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
                    "default": 27017,
                },
                "database": {
                    "type": "string",
                    "description": "Database name",
                    "default": "test",
                },
                "username": {
                    "type": "string",
                    "description": "Username (optional)",
                },
                "password": {
                    "type": "string",
                    "format": "password",
                    "description": "Password (optional)",
                },
                "connection_string": {
                    "type": "string",
                    "description": "Full MongoDB connection string (alternative)",
                },
            },
            "required": ["database"],
        }
