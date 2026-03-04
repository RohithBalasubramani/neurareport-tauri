"""Report generation pipeline.

This replaces the monolithic ReportGenerate.fill_and_print() function
with a composable, observable, testable pipeline.
"""

from __future__ import annotations

import ast
import json
import logging
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.engine.core.errors import ValidationError, NotFoundError
from backend.engine.domain.contracts import Contract
from backend.engine.domain.reports import OutputFormat, RenderRequest, RenderOutput, Report
from backend.engine.adapters.databases import DataSource, SQLiteDataSource
from backend.engine.adapters.rendering import (
    HTMLRenderer,
    PDFRenderer,
    DOCXRenderer,
    XLSXRenderer,
    RenderContext,
)
from prefect import flow, task
try:
    from prefect.task_runners import SequentialTaskRunner
except ImportError:
    # Prefect 3.x removed SequentialTaskRunner - use default synchronous execution
    SequentialTaskRunner = None
from .base import Pipeline, PipelineContext, Step, StepResult

logger = logging.getLogger("neura.pipelines.report")


@dataclass
class ReportPipelineContext(PipelineContext):
    """Context specific to report generation."""

    # Input
    request: Optional[RenderRequest] = None
    template_path: Optional[Path] = None
    contract_path: Optional[Path] = None
    db_path: Optional[Path] = None

    # Intermediate
    contract: Optional[Contract] = None
    template_html: Optional[str] = None
    data_scalars: Dict[str, Any] = field(default_factory=dict)
    data_rows: List[Dict[str, Any]] = field(default_factory=list)
    data_totals: Dict[str, Any] = field(default_factory=dict)
    filled_html: Optional[str] = None

    # Output
    outputs: List[RenderOutput] = field(default_factory=list)
    report: Optional[Report] = None


# === Pipeline Steps ===


def validate_request(ctx: ReportPipelineContext) -> None:
    """Validate the render request."""
    if not ctx.request:
        raise ValidationError(message="No render request provided")

    if not ctx.request.template_id:
        raise ValidationError(message="template_id is required")

    if not ctx.request.connection_id:
        raise ValidationError(message="connection_id is required")

    logger.info(
        "report_request_validated",
        extra={
            "template_id": ctx.request.template_id,
            "connection_id": ctx.request.connection_id,
            "correlation_id": ctx.correlation_id,
        },
    )


def load_contract(ctx: ReportPipelineContext) -> Contract:
    """Load and parse the contract file."""
    if not ctx.contract_path or not ctx.contract_path.exists():
        raise NotFoundError(message="Contract file not found")

    contract_data = json.loads(ctx.contract_path.read_text(encoding="utf-8"))
    contract = Contract.from_dict(contract_data, ctx.request.template_id)

    # Validate contract
    issues = contract.validate()
    if issues:
        logger.warning(
            "contract_validation_warnings",
            extra={"issues": issues, "correlation_id": ctx.correlation_id},
        )

    ctx.contract = contract
    logger.info(
        "contract_loaded",
        extra={
            "template_id": ctx.request.template_id,
            "tokens": len(contract.tokens.all_tokens()),
            "correlation_id": ctx.correlation_id,
        },
    )
    return contract


def load_template(ctx: ReportPipelineContext) -> str:
    """Load the template HTML."""
    if not ctx.template_path or not ctx.template_path.exists():
        raise NotFoundError(message="Template HTML file not found")

    ctx.template_html = ctx.template_path.read_text(encoding="utf-8")
    logger.info(
        "template_loaded",
        extra={
            "path": str(ctx.template_path),
            "size_bytes": len(ctx.template_html),
            "correlation_id": ctx.correlation_id,
        },
    )
    return ctx.template_html


def load_data(ctx: ReportPipelineContext) -> Dict[str, Any]:
    """Load data from the database using the contract."""
    if not ctx.db_path or not ctx.db_path.exists():
        raise NotFoundError(message="Database file not found")

    if not ctx.contract:
        raise ValidationError(message="Contract not loaded")

    datasource = SQLiteDataSource(ctx.db_path)

    try:
        # Load scalar values
        ctx.data_scalars = _load_scalars(datasource, ctx.contract, ctx.request)

        # Load row data
        ctx.data_rows = _load_rows(datasource, ctx.contract, ctx.request)

        # Calculate totals
        ctx.data_totals = _calculate_totals(ctx.data_rows, ctx.contract)

        logger.info(
            "data_loaded",
            extra={
                "scalars": len(ctx.data_scalars),
                "rows": len(ctx.data_rows),
                "totals": len(ctx.data_totals),
                "correlation_id": ctx.correlation_id,
            },
        )

        return {
            "scalars": ctx.data_scalars,
            "rows": ctx.data_rows,
            "totals": ctx.data_totals,
        }
    finally:
        datasource.close()


def _load_scalars(
    datasource: DataSource,
    contract: Contract,
    request: RenderRequest,
) -> Dict[str, Any]:
    """Load scalar values from database."""
    scalars: dict[str, Any] = {}

    select_parts: list[str] = []
    ordered_tokens: list[str] = []
    for token in contract.tokens.scalars:
        expr = contract.get_mapping(token)
        if not expr:
            continue
        select_parts.append(f"{expr} AS [{token}]")
        ordered_tokens.append(token)

    if select_parts:
        try:
            result = datasource.execute_query(f"SELECT {', '.join(select_parts)}")
            if result.rows:
                row = result.rows[0]
                for idx, token in enumerate(ordered_tokens):
                    try:
                        scalars[token] = row[idx]
                    except Exception:
                        scalars[token] = None
        except Exception as exc:
            logger.warning(
                "scalar_batch_load_failed",
                extra={"error": str(exc), "token_count": len(ordered_tokens)},
            )
            # Fall back to per-token queries for resilience
            for token in ordered_tokens:
                expr = contract.get_mapping(token)
                if not expr:
                    continue
                try:
                    result = datasource.execute_query(f"SELECT {expr} AS value")
                    if result.rows:
                        scalars[token] = result.rows[0][0]
                except Exception as e:
                    logger.warning(
                        "scalar_load_failed",
                        extra={"token": token, "error": str(e)},
                    )
                    scalars[token] = None

    # Add date range if provided
    if request.start_date:
        scalars["START_DATE"] = request.start_date
    if request.end_date:
        scalars["END_DATE"] = request.end_date

    return scalars


def _load_rows(
    datasource: DataSource,
    contract: Contract,
    request: RenderRequest,
) -> List[Dict[str, Any]]:
    """Load row data from database."""
    if not contract.tokens.row_tokens:
        return []

    # Build SELECT clause from mappings
    select_parts = []
    for token in contract.tokens.row_tokens:
        expr = contract.get_mapping(token)
        if expr:
            select_parts.append(f"{expr} AS [{token}]")

    if not select_parts:
        return []

    def _extract_table(expr: str) -> str:
        if not expr:
            return ""
        match = re.search(r"(?:^|[^A-Za-z0-9_])\[?([A-Za-z_][\w]*)\]?\s*\.", str(expr))
        return match.group(1) if match else ""

    def _infer_row_tables() -> List[str]:
        tables: List[str] = []
        seen: set[str] = set()
        for token in contract.tokens.row_tokens:
            expr = contract.get_mapping(token) or ""
            table = _extract_table(expr)
            if table and table not in seen:
                seen.add(table)
                tables.append(table)
        return tables

    join = contract.join
    parent_table = join.parent_table if join else ""
    child_table = join.child_table if join else ""
    parent_key = join.parent_key if join else ""
    child_key = join.child_key if join else ""

    row_tables = _infer_row_tables()

    if not parent_table:
        if len(row_tables) == 1:
            parent_table = row_tables[0]
        elif len(row_tables) > 1:
            logger.warning(
                "row_load_ambiguous_tables",
                extra={
                    "template_id": contract.template_id,
                    "tables": row_tables,
                },
            )
            return []
    if not parent_table:
        logger.warning(
            "row_load_missing_parent_table",
            extra={"template_id": contract.template_id},
        )
        return []

    # Build query (simplified - handles optional joins)
    query = f"SELECT {', '.join(select_parts)} FROM [{parent_table}]"
    if child_table and parent_key and child_key:
        query += (
            f" LEFT JOIN [{child_table}] ON [{parent_table}].[{parent_key}]"
            f" = [{child_table}].[{child_key}]"
        )

    # Add WHERE clause for date range
    conditions = []
    date_column = ""
    date_table = ""
    if contract.date_columns:
        row_date_candidates = [
            table for table in row_tables if contract.date_columns.get(table)
        ]
        if len(row_date_candidates) == 1:
            date_table = row_date_candidates[0]
            date_column = contract.date_columns.get(date_table, "")
        elif len(row_date_candidates) > 1:
            logger.warning(
                "row_load_ambiguous_date_tables",
                extra={
                    "template_id": contract.template_id,
                    "tables": row_date_candidates,
                },
            )
        else:
            parent_date = contract.date_columns.get(parent_table, "")
            child_date = contract.date_columns.get(child_table, "") if child_table else ""
            if parent_date:
                date_column = parent_date
                date_table = parent_table
            elif child_date:
                date_column = child_date
                date_table = child_table
    _DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    if request.start_date or request.end_date:
        if date_column:
            date_expr = date_column
            if "." not in date_expr and date_table:
                date_expr = f"{date_table}.{date_expr}"
            if request.start_date:
                if not _DATE_RE.match(request.start_date):
                    raise ValidationError(message="Invalid start_date format: expected YYYY-MM-DD")
                conditions.append(f"date({date_expr}) >= date('{request.start_date}')")
            if request.end_date:
                if not _DATE_RE.match(request.end_date):
                    raise ValidationError(message="Invalid end_date format: expected YYYY-MM-DD")
                conditions.append(f"date({date_expr}) <= date('{request.end_date}')")
        else:
            logger.warning(
                "row_load_missing_date_column",
                extra={
                    "template_id": contract.template_id,
                    "start_date": request.start_date,
                    "end_date": request.end_date,
                },
            )

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Add ORDER BY
    if contract.row_order:
        safe_order_terms = []
        for term in contract.row_order:
            stripped = term.strip()
            parts = stripped.rsplit(None, 1)
            if len(parts) == 2 and parts[1].upper() in ("ASC", "DESC"):
                safe_order_terms.append(f"[{parts[0]}] {parts[1]}")
            else:
                safe_order_terms.append(f"[{stripped}]")
        query += f" ORDER BY {', '.join(safe_order_terms)}"

    try:
        result = datasource.execute_query(query)
        return result.to_dicts()
    except Exception as e:
        logger.warning("row_load_failed", extra={"error": str(e)})
        return []


def _calculate_totals(
    rows: List[Dict[str, Any]],
    contract: Contract,
) -> Dict[str, Any]:
    """Calculate totals from row data."""
    totals = {}

    def _is_simple_row_ref(expr: str) -> Optional[str]:
        normalized = expr.strip()
        if not normalized:
            return None
        if normalized.lower().startswith("rows."):
            candidate = normalized.split(".", 1)[1]
            return candidate if candidate in contract.tokens.row_tokens else None
        if normalized in contract.tokens.row_tokens:
            return normalized
        return None

    for token in contract.tokens.totals:
        expr = (contract.totals_math.get(token) or "").strip()
        mapping_expr = (contract.get_mapping(token) or "").strip()

        if not expr and mapping_expr:
            expr = mapping_expr

        if expr:
            row_ref = _is_simple_row_ref(expr)
            if row_ref:
                try:
                    totals[token] = sum(float(row.get(row_ref, 0) or 0) for row in rows)
                except (ValueError, TypeError):
                    totals[token] = 0
            else:
                totals[token] = _eval_total_expr(expr, rows, totals)
            continue

        logger.warning(
            "totals_missing_math",
            extra={"total_token": token},
        )

    return totals


def _eval_total_expr(
    expr: str,
    rows: List[Dict[str, Any]],
    totals: Dict[str, Any],
) -> Any:
    """Evaluate a totals expression safely."""
    if not expr:
        return None

    normalized = re.sub(r"\brows\.", "", expr.strip(), flags=re.IGNORECASE)
    normalized = re.sub(r"\btotals\.", "", normalized, flags=re.IGNORECASE)

    if "CASE" in normalized.upper():
        logger.warning(
            "totals_expr_unsupported_case",
            extra={"expr": expr},
        )
        return None

    replacements = {
        "SUM": "sum_",
        "COUNT": "count_",
        "AVG": "avg_",
        "MIN": "min_",
        "MAX": "max_",
        "NULLIF": "nullif",
        "COALESCE": "coalesce",
    }
    for sql_name, py_name in replacements.items():
        normalized = re.sub(
            rf"\b{sql_name}\b", py_name, normalized, flags=re.IGNORECASE
        )

    column_values: Dict[str, List[Any]] = {}
    for row in rows:
        for key, value in row.items():
            column_values.setdefault(key, []).append(value)

    def _as_number(value: Any) -> Optional[float]:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _numeric(values: List[Any]) -> List[float]:
        return [num for num in (_as_number(val) for val in values) if num is not None]

    def sum_(values: List[Any]) -> float:
        nums = _numeric(values)
        return float(sum(nums)) if nums else 0.0

    def count_(values: List[Any]) -> int:
        return len([val for val in values if val is not None])

    def avg_(values: List[Any]) -> float:
        nums = _numeric(values)
        return float(sum(nums) / len(nums)) if nums else 0.0

    def min_(values: List[Any]) -> float:
        nums = _numeric(values)
        return float(min(nums)) if nums else 0.0

    def max_(values: List[Any]) -> float:
        nums = _numeric(values)
        return float(max(nums)) if nums else 0.0

    def nullif(a: Any, b: Any) -> Any:
        return None if a == b else a

    def coalesce(*args: Any) -> Any:
        for item in args:
            if item is not None:
                return item
        return None

    allowed_funcs = {
        "sum_": sum_,
        "count_": count_,
        "avg_": avg_,
        "min_": min_,
        "max_": max_,
        "nullif": nullif,
        "coalesce": coalesce,
    }
    allowed_names = set(column_values.keys()) | set(totals.keys())
    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Call,
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
    )

    try:
        tree = ast.parse(normalized, mode="eval")
        for node in ast.walk(tree):
            if not isinstance(node, allowed_nodes):
                raise ValueError(f"Unsupported expression node: {type(node).__name__}")
            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name) or node.func.id not in allowed_funcs:
                    raise ValueError("Unsupported function in totals expression")
            if isinstance(node, ast.Name):
                if node.id not in allowed_funcs and node.id not in allowed_names:
                    raise ValueError(f"Unknown name '{node.id}' in totals expression")
        context = {**allowed_funcs, **column_values, **totals}
        # SECURITY: eval is sandboxed via AST whitelist above (allowed_nodes + allowed_funcs) and __builtins__={}.
        return eval(compile(tree, "<totals_expr>", "eval"), {"__builtins__": {}}, context)  # noqa: S307
    except (ValueError, TypeError, ZeroDivisionError, SyntaxError) as exc:
        logger.warning(
            "totals_expr_eval_failed",
            extra={"expr": expr, "error": str(exc)},
        )
        return None


def render_html(ctx: ReportPipelineContext) -> Path:
    """Render filled HTML from template and data."""
    if not ctx.template_html:
        raise ValidationError(message="Template HTML not loaded")

    renderer = HTMLRenderer()
    output_dir = ctx.template_path.parent
    output_path = output_dir / f"filled_{int(datetime.now(timezone.utc).timestamp())}.html"

    # Combine all data for token substitution
    all_data = {
        **ctx.data_scalars,
        **{f"row_{i}_{k}": v for i, row in enumerate(ctx.data_rows) for k, v in row.items()},
        **ctx.data_totals,
        "ROW_COUNT": len(ctx.data_rows),
        "GENERATED_AT": datetime.now(timezone.utc).isoformat(),
    }

    render_ctx = RenderContext(
        template_html=ctx.template_html,
        data=all_data,
        output_format=OutputFormat.HTML,
        output_path=output_path,
    )

    result = renderer.render(render_ctx)
    if not result.success:
        raise Exception(f"HTML rendering failed: {result.error}")

    ctx.filled_html = output_path.read_text(encoding="utf-8")
    ctx.outputs.append(
        RenderOutput(
            format=OutputFormat.HTML,
            path=output_path,
            size_bytes=result.size_bytes,
        )
    )

    logger.info(
        "html_rendered",
        extra={
            "path": str(output_path),
            "size_bytes": result.size_bytes,
            "correlation_id": ctx.correlation_id,
        },
    )

    return output_path


def render_pdf(ctx: ReportPipelineContext) -> Optional[Path]:
    """Render PDF from HTML."""
    if not ctx.filled_html:
        raise ValidationError(message="HTML not rendered")

    if OutputFormat.PDF not in ctx.request.output_formats:
        return None

    renderer = PDFRenderer()
    output_dir = ctx.template_path.parent
    output_path = output_dir / f"filled_{int(datetime.now(timezone.utc).timestamp())}.pdf"

    render_ctx = RenderContext(
        template_html=ctx.filled_html,
        data={},
        output_format=OutputFormat.PDF,
        output_path=output_path,
    )

    result = renderer.render(render_ctx)
    if not result.success:
        logger.error("pdf_render_failed", extra={"error": result.error})
        return None

    ctx.outputs.append(
        RenderOutput(
            format=OutputFormat.PDF,
            path=output_path,
            size_bytes=result.size_bytes,
        )
    )

    logger.info(
        "pdf_rendered",
        extra={
            "path": str(output_path),
            "size_bytes": result.size_bytes,
            "correlation_id": ctx.correlation_id,
        },
    )

    return output_path


def render_docx(ctx: ReportPipelineContext) -> Optional[Path]:
    """Render DOCX from HTML."""
    if OutputFormat.DOCX not in ctx.request.output_formats:
        return None

    if not ctx.filled_html:
        return None

    renderer = DOCXRenderer()
    output_dir = ctx.template_path.parent
    output_path = output_dir / f"filled_{int(datetime.now(timezone.utc).timestamp())}.docx"

    render_ctx = RenderContext(
        template_html=ctx.filled_html,
        data={},
        output_format=OutputFormat.DOCX,
        output_path=output_path,
    )

    result = renderer.render(render_ctx)
    if not result.success:
        logger.warning("docx_render_failed", extra={"error": result.error})
        return None

    ctx.outputs.append(
        RenderOutput(
            format=OutputFormat.DOCX,
            path=output_path,
            size_bytes=result.size_bytes,
        )
    )

    return output_path


def render_xlsx(ctx: ReportPipelineContext) -> Optional[Path]:
    """Render XLSX from HTML tables."""
    if OutputFormat.XLSX not in ctx.request.output_formats:
        return None

    if not ctx.filled_html:
        return None

    renderer = XLSXRenderer()
    output_dir = ctx.template_path.parent
    output_path = output_dir / f"filled_{int(datetime.now(timezone.utc).timestamp())}.xlsx"

    render_ctx = RenderContext(
        template_html=ctx.filled_html,
        data={"scalars": ctx.data_scalars, "rows": ctx.data_rows},
        output_format=OutputFormat.XLSX,
        output_path=output_path,
    )

    result = renderer.render(render_ctx)
    if not result.success:
        logger.warning("xlsx_render_failed", extra={"error": result.error})
        return None

    ctx.outputs.append(
        RenderOutput(
            format=OutputFormat.XLSX,
            path=output_path,
            size_bytes=result.size_bytes,
        )
    )

    return output_path


def finalize_report(ctx: ReportPipelineContext) -> Report:
    """Create the final report record."""
    report = Report(
        report_id=str(uuid.uuid4()),
        template_id=ctx.request.template_id,
        template_name=ctx.request.template_id,  # Would come from template record
        connection_id=ctx.request.connection_id,
        connection_name=None,
        status="succeeded",
        outputs=ctx.outputs,
        start_date=ctx.request.start_date,
        end_date=ctx.request.end_date,
        correlation_id=ctx.correlation_id,
        started_at=ctx.started_at,
        completed_at=datetime.now(timezone.utc),
    )

    ctx.report = report
    return report


# === Prefect Tasks + Flow ===


@task(name="validate_request")
def validate_request_task(ctx: ReportPipelineContext) -> None:
    validate_request(ctx)


@task(name="load_contract")
def load_contract_task(ctx: ReportPipelineContext) -> Contract:
    return load_contract(ctx)


@task(name="load_template")
def load_template_task(ctx: ReportPipelineContext) -> str:
    return load_template(ctx)


@task(name="load_data", retries=1, retry_delay_seconds=1)
def load_data_task(ctx: ReportPipelineContext) -> Dict[str, Any]:
    return load_data(ctx)


@task(name="render_html")
def render_html_task(ctx: ReportPipelineContext) -> Path:
    return render_html(ctx)


@task(name="render_pdf", timeout_seconds=120)
def render_pdf_task(ctx: ReportPipelineContext) -> Optional[Path]:
    return render_pdf(ctx)


@task(name="render_docx")
def render_docx_task(ctx: ReportPipelineContext) -> Optional[Path]:
    return render_docx(ctx)


@task(name="render_xlsx")
def render_xlsx_task(ctx: ReportPipelineContext) -> Optional[Path]:
    return render_xlsx(ctx)


@task(name="finalize")
def finalize_report_task(ctx: ReportPipelineContext) -> Report:
    return finalize_report(ctx)


_flow_kwargs = {"name": "report_generation"}
if SequentialTaskRunner is not None:
    _flow_kwargs["task_runner"] = SequentialTaskRunner()

@flow(**_flow_kwargs)
def report_generation_flow(
    request: RenderRequest,
    template_path: Path,
    contract_path: Path,
    db_path: Path,
    correlation_id: Optional[str] = None,
) -> Report:
    ctx = ReportPipelineContext(
        correlation_id=correlation_id or str(uuid.uuid4()),
        request=request,
        template_path=template_path,
        contract_path=contract_path,
        db_path=db_path,
    )
    validate_request_task(ctx)
    load_contract_task(ctx)
    load_template_task(ctx)
    load_data_task(ctx)
    render_html_task(ctx)
    if OutputFormat.PDF in request.output_formats:
        render_pdf_task(ctx)
    if OutputFormat.DOCX in request.output_formats:
        render_docx_task(ctx)
    if OutputFormat.XLSX in request.output_formats:
        render_xlsx_task(ctx)
    finalize_report_task(ctx)
    return ctx.report


# === Pipeline Factory ===


class ReportPipeline:
    """Report generation pipeline wrapper."""

    def __init__(self) -> None:
        self._pipeline = create_report_pipeline()

    def execute(
        self,
        request: RenderRequest,
        template_path: Path,
        contract_path: Path,
        db_path: Path,
        *,
        correlation_id: Optional[str] = None,
    ) -> Report:
        """Execute the report pipeline."""
        engine = os.getenv("NEURA_PIPELINE_ENGINE", "prefect").strip().lower()
        if engine == "prefect":
            return report_generation_flow(
                request=request,
                template_path=template_path,
                contract_path=contract_path,
                db_path=db_path,
                correlation_id=correlation_id,
            )

        ctx = ReportPipelineContext(
            correlation_id=correlation_id or str(uuid.uuid4()),
            request=request,
            template_path=template_path,
            contract_path=contract_path,
            db_path=db_path,
        )
        result = self._pipeline.execute_sync(ctx)
        if not result.success:
            raise Exception(f"Report pipeline failed: {result.error}")
        return ctx.report


def create_report_pipeline() -> Pipeline:
    """Create the report generation pipeline."""
    return Pipeline(
        name="report_generation",
        steps=[
            Step(
                name="validate",
                fn=validate_request,
                label="Validate request",
            ),
            Step(
                name="load_contract",
                fn=load_contract,
                label="Load contract",
            ),
            Step(
                name="load_template",
                fn=load_template,
                label="Load template",
            ),
            Step(
                name="load_data",
                fn=load_data,
                label="Load data",
                retries=1,
            ),
            Step(
                name="render_html",
                fn=render_html,
                label="Render HTML",
            ),
            Step(
                name="render_pdf",
                fn=render_pdf,
                label="Render PDF",
                timeout_seconds=120.0,
                guard=lambda ctx: OutputFormat.PDF in ctx.request.output_formats,
            ),
            Step(
                name="render_docx",
                fn=render_docx,
                label="Render DOCX",
                guard=lambda ctx: OutputFormat.DOCX in ctx.request.output_formats,
            ),
            Step(
                name="render_xlsx",
                fn=render_xlsx,
                label="Render XLSX",
                guard=lambda ctx: OutputFormat.XLSX in ctx.request.output_formats,
            ),
            Step(
                name="finalize",
                fn=finalize_report,
                label="Finalize report",
            ),
        ],
    )
