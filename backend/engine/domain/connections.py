"""Connection domain entities.

A Connection represents a data source (database) that can be queried.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid


class ConnectionType(str, Enum):
    """Types of database connections."""

    SQLITE = "sqlite"
    POSTGRES = "postgres"  # Future
    MYSQL = "mysql"  # Future


class ConnectionStatus(str, Enum):
    """Health status of a connection."""

    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class TableInfo:
    """Information about a database table."""

    name: str
    columns: List[str]
    row_count: Optional[int] = None
    primary_key: Optional[str] = None


@dataclass(frozen=True)
class SchemaInfo:
    """Database schema information."""

    tables: List[TableInfo]
    catalog: List[str]  # table.column format

    @property
    def table_names(self) -> List[str]:
        return [t.name for t in self.tables]


@dataclass
class ConnectionTest:
    """Result of testing a connection."""

    success: bool
    latency_ms: Optional[float] = None
    error: Optional[str] = None
    tested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    table_count: Optional[int] = None
    total_rows: Optional[int] = None


@dataclass
class Connection:
    """A database connection configuration.

    Connections are used to access data for report generation.
    """

    connection_id: str
    name: str
    connection_type: ConnectionType
    path: Path
    status: ConnectionStatus = ConnectionStatus.UNKNOWN
    schema_info: Optional[SchemaInfo] = None
    last_test: Optional[ConnectionTest] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_used_at: Optional[datetime] = None
    last_used_template: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    @classmethod
    def create_sqlite(
        cls,
        name: str,
        path: Path,
        connection_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Connection:
        return cls(
            connection_id=connection_id or str(uuid.uuid4()),
            name=name,
            connection_type=ConnectionType.SQLITE,
            path=path.resolve(),
            **kwargs,
        )

    def record_test(self, test: ConnectionTest) -> None:
        self.last_test = test
        self.status = (
            ConnectionStatus.HEALTHY
            if test.success
            else ConnectionStatus.UNAVAILABLE
        )
        self.updated_at = datetime.now(timezone.utc)

    def record_use(self, template_id: str) -> None:
        self.last_used_at = datetime.now(timezone.utc)
        self.last_used_template = template_id
        self.updated_at = datetime.now(timezone.utc)

    def update_schema(self, schema: SchemaInfo) -> None:
        self.schema_info = schema
        self.updated_at = datetime.now(timezone.utc)

    @property
    def catalog(self) -> List[str]:
        if self.schema_info:
            return self.schema_info.catalog
        return []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "connection_id": self.connection_id,
            "name": self.name,
            "connection_type": self.connection_type.value,
            "path": str(self.path),
            "status": self.status.value,
            "schema_info": {
                "tables": [
                    {
                        "name": t.name,
                        "columns": t.columns,
                        "row_count": t.row_count,
                        "primary_key": t.primary_key,
                    }
                    for t in self.schema_info.tables
                ],
                "catalog": self.schema_info.catalog,
            }
            if self.schema_info
            else None,
            "last_test": {
                "success": self.last_test.success,
                "latency_ms": self.last_test.latency_ms,
                "error": self.last_test.error,
                "tested_at": self.last_test.tested_at.isoformat(),
                "table_count": self.last_test.table_count,
            }
            if self.last_test
            else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "last_used_template": self.last_used_template,
            "description": self.description,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Connection:
        schema_data = data.get("schema_info")
        schema_info = None
        if schema_data:
            tables = [
                TableInfo(
                    name=t["name"],
                    columns=t["columns"],
                    row_count=t.get("row_count"),
                    primary_key=t.get("primary_key"),
                )
                for t in schema_data.get("tables", [])
            ]
            schema_info = SchemaInfo(
                tables=tables,
                catalog=schema_data.get("catalog", []),
            )

        test_data = data.get("last_test")
        last_test = None
        if test_data:
            tested_at = test_data.get("tested_at")
            if isinstance(tested_at, str):
                tested_at = datetime.fromisoformat(tested_at)
            last_test = ConnectionTest(
                success=test_data["success"],
                latency_ms=test_data.get("latency_ms"),
                error=test_data.get("error"),
                tested_at=tested_at or datetime.now(timezone.utc),
                table_count=test_data.get("table_count"),
            )

        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        last_used_at = data.get("last_used_at")
        if isinstance(last_used_at, str):
            last_used_at = datetime.fromisoformat(last_used_at)

        return cls(
            connection_id=data["connection_id"],
            name=data["name"],
            connection_type=ConnectionType(data.get("connection_type", "sqlite")),
            path=Path(data["path"]),
            status=ConnectionStatus(data.get("status", "unknown")),
            schema_info=schema_info,
            last_test=last_test,
            created_at=created_at or datetime.now(timezone.utc),
            updated_at=updated_at or datetime.now(timezone.utc),
            last_used_at=last_used_at,
            last_used_template=data.get("last_used_template"),
            description=data.get("description"),
            tags=data.get("tags", []),
        )
