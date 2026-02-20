"""Template domain entities.

A Template is a document blueprint that can be filled with data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid


class TemplateKind(str, Enum):
    """Types of templates."""

    PDF = "pdf"
    EXCEL = "excel"


class TemplateStatus(str, Enum):
    """Template lifecycle status."""

    DRAFT = "draft"
    ANALYZING = "analyzing"
    MAPPED = "mapped"
    APPROVED = "approved"
    FAILED = "failed"


@dataclass(frozen=True)
class Artifact:
    """A file artifact associated with a template."""

    name: str
    path: Path
    artifact_type: str
    size_bytes: Optional[int] = None
    checksum: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class TemplateSchema:
    """Schema extracted from a template."""

    scalars: List[str] = field(default_factory=list)
    row_tokens: List[str] = field(default_factory=list)
    totals: List[str] = field(default_factory=list)
    tables_detected: List[str] = field(default_factory=list)
    placeholders_found: int = 0


@dataclass
class Template:
    """A report template.

    Templates contain:
    - Source document (HTML)
    - Extracted schema (tokens/placeholders)
    - Associated contract (after mapping)
    - Generated artifacts
    """

    template_id: str
    name: str
    kind: TemplateKind
    status: TemplateStatus
    schema: Optional[TemplateSchema] = None
    contract_id: Optional[str] = None
    artifacts: List[Artifact] = field(default_factory=list)
    source_file: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_run_at: Optional[datetime] = None
    run_count: int = 0
    tags: List[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        kind: TemplateKind = TemplateKind.PDF,
        template_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Template:
        return cls(
            template_id=template_id or str(uuid.uuid4()),
            name=name,
            kind=kind,
            status=TemplateStatus.DRAFT,
            **kwargs,
        )

    def record_run(self) -> None:
        self.run_count += 1
        self.last_run_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def transition_to(self, status: TemplateStatus) -> None:
        self.status = status
        self.updated_at = datetime.now(timezone.utc)

    def add_artifact(self, artifact: Artifact) -> None:
        # Remove existing artifact with same name
        self.artifacts = [a for a in self.artifacts if a.name != artifact.name]
        self.artifacts.append(artifact)
        self.updated_at = datetime.now(timezone.utc)

    def get_artifact(self, name: str) -> Optional[Artifact]:
        for artifact in self.artifacts:
            if artifact.name == name:
                return artifact
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "kind": self.kind.value,
            "status": self.status.value,
            "schema": {
                "scalars": self.schema.scalars,
                "row_tokens": self.schema.row_tokens,
                "totals": self.schema.totals,
                "tables_detected": self.schema.tables_detected,
                "placeholders_found": self.schema.placeholders_found,
            }
            if self.schema
            else None,
            "contract_id": self.contract_id,
            "artifacts": [
                {
                    "name": a.name,
                    "path": str(a.path),
                    "artifact_type": a.artifact_type,
                    "size_bytes": a.size_bytes,
                }
                for a in self.artifacts
            ],
            "source_file": self.source_file,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "run_count": self.run_count,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Template:
        schema_data = data.get("schema")
        schema = None
        if schema_data:
            schema = TemplateSchema(
                scalars=schema_data.get("scalars", []),
                row_tokens=schema_data.get("row_tokens", []),
                totals=schema_data.get("totals", []),
                tables_detected=schema_data.get("tables_detected", []),
                placeholders_found=schema_data.get("placeholders_found", 0),
            )

        artifacts = []
        for a in data.get("artifacts", []):
            artifacts.append(
                Artifact(
                    name=a["name"],
                    path=Path(a["path"]),
                    artifact_type=a["artifact_type"],
                    size_bytes=a.get("size_bytes"),
                )
            )

        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        last_run_at = data.get("last_run_at")
        if isinstance(last_run_at, str):
            last_run_at = datetime.fromisoformat(last_run_at)

        return cls(
            template_id=data["template_id"],
            name=data["name"],
            kind=TemplateKind(data.get("kind", "pdf")),
            status=TemplateStatus(data.get("status", "draft")),
            schema=schema,
            contract_id=data.get("contract_id"),
            artifacts=artifacts,
            source_file=data.get("source_file"),
            description=data.get("description"),
            created_at=created_at or datetime.now(timezone.utc),
            updated_at=updated_at or datetime.now(timezone.utc),
            last_run_at=last_run_at,
            run_count=data.get("run_count", 0),
            tags=data.get("tags", []),
        )
