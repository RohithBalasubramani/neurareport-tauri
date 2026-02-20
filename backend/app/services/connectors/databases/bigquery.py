"""Google BigQuery Connector.

Connector for Google BigQuery using google-cloud-bigquery.
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
class BigQueryConnector(ConnectorBase):
    """Google BigQuery database connector."""

    connector_id = "bigquery"
    connector_name = "Google BigQuery"
    connector_type = ConnectorType.DATABASE
    auth_types = [AuthType.SERVICE_ACCOUNT]
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
        """Establish connection to BigQuery."""
        try:
            from google.cloud import bigquery
            from google.oauth2 import service_account

            credentials_path = self.config.get("credentials_path")
            credentials_json = self.config.get("credentials_json")
            project_id = self.config.get("project_id")

            if credentials_json:
                import json
                if isinstance(credentials_json, str):
                    try:
                        credentials_json = json.loads(credentials_json)
                    except json.JSONDecodeError:
                        raise ConnectionError("Invalid credentials JSON format")
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_json
                )
            elif credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
            else:
                # Use default credentials
                credentials = None

            self._client = bigquery.Client(
                project=project_id,
                credentials=credentials,
            )
            self._connected = True
            return True
        except ConnectionError:
            self._connected = False
            raise
        except Exception as e:
            self._connected = False
            raise ConnectionError("Failed to connect to BigQuery") from e

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

            # Run a simple query
            query = "SELECT 1"
            query_job = self._client.query(query)
            list(query_job.result())

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
        schemas: list[str] = []

        # List datasets (schemas)
        datasets = list(self._client.list_datasets())
        schemas = [ds.dataset_id for ds in datasets]

        # For each dataset, list tables
        for dataset in datasets:
            dataset_id = dataset.dataset_id
            dataset_tables = list(self._client.list_tables(dataset_id))

            for table_ref in dataset_tables:
                table = self._client.get_table(table_ref)
                columns = [
                    ColumnInfo(
                        name=field.name,
                        data_type=field.field_type,
                        nullable=field.mode == "NULLABLE",
                    )
                    for field in table.schema
                ]
                tables.append(TableInfo(
                    name=table.table_id,
                    schema_name=dataset_id,
                    columns=columns,
                    row_count=table.num_rows,
                    size_bytes=table.num_bytes,
                ))

        return SchemaInfo(tables=tables, schemas=schemas)

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

        try:
            from google.cloud import bigquery

            # Add LIMIT if not present
            query_upper = query.upper().strip()
            if query_upper.startswith("SELECT") and "LIMIT" not in query_upper:
                query = f"{query} LIMIT {limit}"

            job_config = bigquery.QueryJobConfig()
            if parameters:
                job_config.query_parameters = [
                    bigquery.ScalarQueryParameter(k, "STRING", v)
                    for k, v in parameters.items()
                ]

            query_job = self._client.query(query, job_config=job_config)
            results = query_job.result()

            columns = [field.name for field in results.schema]
            rows = [[cell for cell in row.values()] for row in results]

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
                "project_id": {"type": "string", "description": "GCP Project ID"},
                "credentials_path": {"type": "string", "description": "Path to service account JSON"},
                "credentials_json": {"type": "object", "description": "Service account credentials JSON"},
            },
            "required": ["project_id"],
        }
