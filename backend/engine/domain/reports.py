"""Report domain entities.

A Report represents a generated document from a template + contract + data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import re
import uuid


class OutputFormat(str, Enum):
    """Supported output formats."""

    HTML = "html"
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"


class ReportStatus(str, Enum):
    """Status of a report generation."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Batch:
    """A batch of data for report generation.

    Reports can be generated for multiple batches in one run.
    """

    batch_id: str
    row_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KeyValue:
    """A key-value filter for report generation."""

    key: str
    value: str

    def to_sql_condition(self, table: Optional[str] = None) -> str:
        """Generate SQL WHERE condition for this key-value."""
        # Validate key is a safe SQL identifier (alphanumeric + underscore only)
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', self.key):
            raise ValueError(f"Invalid SQL identifier in key: {self.key}")

        # Validate table name if provided
        if table and not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
            raise ValueError(f"Invalid SQL identifier in table: {table}")

        safe_key = f"[{self.key}]"
        col = f"[{table}].{safe_key}" if table else safe_key
        safe_value = self.value.replace("'", "''")
        return f"{col} = '{safe_value}'"


@dataclass
class RenderRequest:
    """Request to render a report.

    This is the input to the report rendering pipeline.
    """

    template_id: str
    connection_id: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    batch_ids: Optional[List[str]] = None
    key_values: Optional[List[KeyValue]] = None
    output_formats: List[OutputFormat] = field(
        default_factory=lambda: [OutputFormat.HTML, OutputFormat.PDF]
    )
    email_recipients: Optional[List[str]] = None
    email_subject: Optional[str] = None
    email_message: Optional[str] = None
    correlation_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.template_id:
            raise ValueError("template_id is required")
        if not self.connection_id:
            raise ValueError("connection_id is required")


@dataclass
class RenderOutput:
    """Output artifact from rendering.

    Each format produces one RenderOutput.
    """

    format: OutputFormat
    path: Path
    size_bytes: int
    checksum: Optional[str] = None
    url: Optional[str] = None


@dataclass
class Report:
    """A generated report.

    This is the result of processing a RenderRequest.
    """

    report_id: str
    template_id: str
    template_name: str
    connection_id: str
    connection_name: Optional[str]
    status: ReportStatus
    outputs: List[RenderOutput] = field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    batch_ids: Optional[List[str]] = None
    key_values: Optional[List[KeyValue]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    correlation_id: Optional[str] = None
    schedule_id: Optional[str] = None
    schedule_name: Optional[str] = None

    @classmethod
    def create(
        cls,
        template_id: str,
        template_name: str,
        connection_id: str,
        connection_name: Optional[str] = None,
        **kwargs: Any,
    ) -> Report:
        return cls(
            report_id=str(uuid.uuid4()),
            template_id=template_id,
            template_name=template_name,
            connection_id=connection_id,
            connection_name=connection_name,
            status=ReportStatus.PENDING,
            **kwargs,
        )

    def start(self) -> None:
        self.status = ReportStatus.RUNNING
        self.started_at = datetime.now(timezone.utc)

    def succeed(self, outputs: List[RenderOutput]) -> None:
        self.status = ReportStatus.SUCCEEDED
        self.outputs = outputs
        self.completed_at = datetime.now(timezone.utc)

    def fail(self, error: str) -> None:
        self.status = ReportStatus.FAILED
        self.error = error
        self.completed_at = datetime.now(timezone.utc)

    def cancel(self) -> None:
        self.status = ReportStatus.CANCELLED
        self.completed_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "template_id": self.template_id,
            "template_name": self.template_name,
            "connection_id": self.connection_id,
            "connection_name": self.connection_name,
            "status": self.status.value,
            "outputs": [
                {
                    "format": o.format.value,
                    "path": str(o.path),
                    "size_bytes": o.size_bytes,
                    "url": o.url,
                }
                for o in self.outputs
            ],
            "start_date": self.start_date,
            "end_date": self.end_date,
            "batch_ids": self.batch_ids,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True)
class DataWindow:
    """A window of data for report generation."""

    start_date: Optional[str]
    end_date: Optional[str]
    filters: List[KeyValue] = field(default_factory=list)

    def to_sql_conditions(self, date_column: str = "date") -> List[str]:
        """Generate SQL WHERE conditions."""
        conditions = []
        if self.start_date:
            conditions.append(f"{date_column} >= '{self.start_date}'")
        if self.end_date:
            conditions.append(f"{date_column} <= '{self.end_date}'")
        for kv in self.filters:
            conditions.append(kv.to_sql_condition())
        return conditions
