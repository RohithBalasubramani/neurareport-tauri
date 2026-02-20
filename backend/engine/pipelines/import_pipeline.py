"""Template import pipeline.

Handles importing templates from ZIP files or individual documents.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import uuid
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.engine.core.errors import ValidationError
from backend.engine.domain.templates import Template, TemplateKind, TemplateStatus, Artifact
from backend.engine.adapters.extraction import PDFExtractor, ExcelExtractor
from prefect import flow, task
try:
    from prefect.task_runners import SequentialTaskRunner
except ImportError:
    # Prefect 3.x removed SequentialTaskRunner - use default synchronous execution
    SequentialTaskRunner = None
from .base import Pipeline, PipelineContext, Step

logger = logging.getLogger("neura.pipelines.import")


@dataclass
class ImportPipelineContext(PipelineContext):
    """Context specific to template import."""

    # Input
    source_path: Optional[Path] = None
    template_name: Optional[str] = None
    template_kind: TemplateKind = TemplateKind.PDF
    output_dir: Optional[Path] = None

    # Intermediate
    extracted_dir: Optional[Path] = None
    source_files: List[Path] = field(default_factory=list)
    html_content: Optional[str] = None
    extracted_tables: List[Dict[str, Any]] = field(default_factory=list)
    detected_tokens: List[str] = field(default_factory=list)

    # Output
    template: Optional[Template] = None
    artifacts: List[Artifact] = field(default_factory=list)


# === Pipeline Steps ===


def validate_import(ctx: ImportPipelineContext) -> None:
    """Validate the import request."""
    if not ctx.source_path:
        raise ValidationError(message="No source path provided")

    if not ctx.source_path.exists():
        raise ValidationError(message=f"Source file not found: {ctx.source_path}")

    if not ctx.template_name:
        ctx.template_name = ctx.source_path.stem

    # Determine kind from file type
    suffix = ctx.source_path.suffix.lower()
    if suffix in (".xlsx", ".xls", ".xlsm"):
        ctx.template_kind = TemplateKind.EXCEL
    elif suffix == ".pdf":
        ctx.template_kind = TemplateKind.PDF
    elif suffix == ".zip":
        # Will determine from contents
        pass

    logger.info(
        "import_validated",
        extra={
            "source": str(ctx.source_path),
            "kind": ctx.template_kind.value,
            "correlation_id": ctx.correlation_id,
        },
    )


def extract_archive(ctx: ImportPipelineContext) -> Path:
    """Extract ZIP archive if needed."""
    if ctx.source_path.suffix.lower() != ".zip":
        # Not a ZIP, use source directly
        ctx.source_files = [ctx.source_path]
        return ctx.source_path

    # Create extraction directory
    extract_dir = ctx.output_dir / f"import_{uuid.uuid4().hex[:8]}"
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(ctx.source_path, "r") as zf:
        zf.extractall(extract_dir)

    ctx.extracted_dir = extract_dir

    # Find source files
    ctx.source_files = list(extract_dir.glob("**/*"))
    ctx.source_files = [f for f in ctx.source_files if f.is_file()]

    # Determine kind from contents
    for f in ctx.source_files:
        if f.suffix.lower() in (".xlsx", ".xls"):
            ctx.template_kind = TemplateKind.EXCEL
            break
        elif f.suffix.lower() == ".pdf":
            ctx.template_kind = TemplateKind.PDF
            break
        elif f.suffix.lower() == ".html":
            ctx.template_kind = TemplateKind.PDF  # HTML template for PDF output
            break

    logger.info(
        "archive_extracted",
        extra={
            "files": len(ctx.source_files),
            "kind": ctx.template_kind.value,
            "correlation_id": ctx.correlation_id,
        },
    )

    return extract_dir


def extract_content(ctx: ImportPipelineContext) -> Dict[str, Any]:
    """Extract content from source files."""
    if ctx.template_kind == TemplateKind.EXCEL:
        return _extract_excel(ctx)
    else:
        return _extract_pdf(ctx)


def _extract_pdf(ctx: ImportPipelineContext) -> Dict[str, Any]:
    """Extract content from PDF source."""
    # Look for HTML file first (pre-converted template)
    html_files = [f for f in ctx.source_files if f.suffix.lower() == ".html"]
    if html_files:
        ctx.html_content = html_files[0].read_text(encoding="utf-8")
        return {"html": ctx.html_content}

    # Otherwise extract from PDF
    pdf_files = [f for f in ctx.source_files if f.suffix.lower() == ".pdf"]
    if not pdf_files:
        raise ValidationError(message="No PDF or HTML file found")

    extractor = PDFExtractor()
    result = extractor.extract(pdf_files[0])

    ctx.extracted_tables = [t.to_dict() for t in result.tables]

    # Build HTML from extracted content
    ctx.html_content = _build_html_from_extraction(result)

    return {
        "html": ctx.html_content,
        "tables": ctx.extracted_tables,
        "page_count": result.page_count,
    }


def _extract_excel(ctx: ImportPipelineContext) -> Dict[str, Any]:
    """Extract content from Excel source."""
    excel_files = [
        f for f in ctx.source_files
        if f.suffix.lower() in (".xlsx", ".xls", ".xlsm")
    ]
    if not excel_files:
        raise ValidationError(message="No Excel file found")

    extractor = ExcelExtractor()
    result = extractor.extract(excel_files[0])

    ctx.extracted_tables = [t.to_dict() for t in result.tables]

    # Build HTML from extracted content
    ctx.html_content = _build_html_from_extraction(result)

    return {
        "html": ctx.html_content,
        "tables": ctx.extracted_tables,
        "sheet_count": len(result.tables),
    }


def _build_html_from_extraction(result) -> str:
    """Build HTML document from extraction result."""
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '<meta charset="UTF-8">',
        "<style>",
        "table { border-collapse: collapse; width: 100%; }",
        "th, td { border: 1px solid black; padding: 8px; text-align: left; }",
        "th { background-color: #f2f2f2; }",
        "</style>",
        "</head>",
        "<body>",
    ]

    for table in result.tables:
        html_parts.append("<table>")
        html_parts.append("<thead><tr>")
        for header in table.headers:
            html_parts.append(f"<th>{header}</th>")
        html_parts.append("</tr></thead>")
        html_parts.append("<tbody>")
        for row in table.rows:
            html_parts.append("<tr>")
            for cell in row:
                html_parts.append(f"<td>{cell}</td>")
            html_parts.append("</tr>")
        html_parts.append("</tbody>")
        html_parts.append("</table>")
        html_parts.append("<br>")

    html_parts.extend(["</body>", "</html>"])
    return "\n".join(html_parts)


def detect_tokens(ctx: ImportPipelineContext) -> List[str]:
    """Detect placeholder tokens in the template."""
    import re

    if not ctx.html_content:
        return []

    # Find {{token}} patterns
    pattern = r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}"
    matches = re.findall(pattern, ctx.html_content)

    ctx.detected_tokens = list(set(matches))

    logger.info(
        "tokens_detected",
        extra={
            "count": len(ctx.detected_tokens),
            "tokens": ctx.detected_tokens[:10],
            "correlation_id": ctx.correlation_id,
        },
    )

    return ctx.detected_tokens


def create_template_record(ctx: ImportPipelineContext) -> Template:
    """Create the template record."""
    template_id = str(uuid.uuid4())

    # Create template directory
    template_dir = ctx.output_dir / template_id
    template_dir.mkdir(parents=True, exist_ok=True)

    # Save HTML
    html_path = template_dir / "template_p1.html"
    if ctx.html_content:
        html_path.write_text(ctx.html_content, encoding="utf-8")
        ctx.artifacts.append(
            Artifact(
                name="template_p1.html",
                path=html_path,
                artifact_type="html",
                size_bytes=html_path.stat().st_size,
                created_at=datetime.now(timezone.utc),
            )
        )

    # Copy original source
    if ctx.source_path and ctx.source_path.exists():
        source_copy = template_dir / f"original{ctx.source_path.suffix}"
        shutil.copy2(ctx.source_path, source_copy)
        ctx.artifacts.append(
            Artifact(
                name=source_copy.name,
                path=source_copy,
                artifact_type="source",
                size_bytes=source_copy.stat().st_size,
            )
        )

    # Create template
    from backend.engine.domain.templates import TemplateSchema

    ctx.template = Template(
        template_id=template_id,
        name=ctx.template_name,
        kind=ctx.template_kind,
        status=TemplateStatus.DRAFT,
        schema=TemplateSchema(
            scalars=[t for t in ctx.detected_tokens if not t.startswith("row_")],
            row_tokens=[t for t in ctx.detected_tokens if t.startswith("row_")],
            totals=[t for t in ctx.detected_tokens if t.startswith("total_")],
            placeholders_found=len(ctx.detected_tokens),
        ),
        artifacts=ctx.artifacts,
        source_file=ctx.source_path.name if ctx.source_path else None,
    )

    # Save template metadata
    meta_path = template_dir / "template_meta.json"
    meta_path.write_text(
        json.dumps(ctx.template.to_dict(), indent=2, default=str),
        encoding="utf-8",
    )

    logger.info(
        "template_created",
        extra={
            "template_id": template_id,
            "name": ctx.template_name,
            "kind": ctx.template_kind.value,
            "artifacts": len(ctx.artifacts),
            "correlation_id": ctx.correlation_id,
        },
    )

    return ctx.template


# === Prefect Tasks + Flow ===


@task(name="validate_import")
def validate_import_task(ctx: ImportPipelineContext) -> None:
    validate_import(ctx)


@task(name="extract_archive")
def extract_archive_task(ctx: ImportPipelineContext) -> Path:
    return extract_archive(ctx)


@task(name="extract_content")
def extract_content_task(ctx: ImportPipelineContext) -> Dict[str, Any]:
    return extract_content(ctx)


@task(name="detect_tokens")
def detect_tokens_task(ctx: ImportPipelineContext) -> List[str]:
    return detect_tokens(ctx)


@task(name="create_template")
def create_template_task(ctx: ImportPipelineContext) -> Template:
    return create_template_record(ctx)


_flow_kwargs = {"name": "template_import"}
if SequentialTaskRunner is not None:
    _flow_kwargs["task_runner"] = SequentialTaskRunner()

@flow(**_flow_kwargs)
def import_template_flow(
    source_path: Path,
    output_dir: Path,
    *,
    template_name: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Template:
    ctx = ImportPipelineContext(
        correlation_id=correlation_id or str(uuid.uuid4()),
        source_path=source_path,
        template_name=template_name,
        output_dir=output_dir,
    )
    validate_import_task(ctx)
    extract_archive_task(ctx)
    extract_content_task(ctx)
    detect_tokens_task(ctx)
    create_template_task(ctx)
    return ctx.template


# === Pipeline Factory ===


class ImportPipeline:
    """Template import pipeline wrapper."""

    def __init__(self, output_dir: Path) -> None:
        self._output_dir = output_dir
        self._pipeline = create_import_pipeline()

    def execute(
        self,
        source_path: Path,
        *,
        template_name: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Template:
        """Execute the import pipeline."""
        engine = os.getenv("NEURA_PIPELINE_ENGINE", "prefect").strip().lower()
        if engine == "prefect":
            return import_template_flow(
                source_path=source_path,
                output_dir=self._output_dir,
                template_name=template_name,
                correlation_id=correlation_id,
            )

        ctx = ImportPipelineContext(
            correlation_id=correlation_id or str(uuid.uuid4()),
            source_path=source_path,
            template_name=template_name,
            output_dir=self._output_dir,
        )
        result = self._pipeline.execute_sync(ctx)
        if not result.success:
            raise Exception(f"Import pipeline failed: {result.error}")
        return ctx.template


def create_import_pipeline() -> Pipeline:
    """Create the template import pipeline."""
    return Pipeline(
        name="template_import",
        steps=[
            Step(
                name="validate",
                fn=validate_import,
                label="Validate import",
            ),
            Step(
                name="extract_archive",
                fn=extract_archive,
                label="Extract archive",
            ),
            Step(
                name="extract_content",
                fn=extract_content,
                label="Extract content",
            ),
            Step(
                name="detect_tokens",
                fn=detect_tokens,
                label="Detect tokens",
            ),
            Step(
                name="create_template",
                fn=create_template_record,
                label="Create template",
            ),
        ],
    )
