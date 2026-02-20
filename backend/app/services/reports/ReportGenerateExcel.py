# mypy: ignore-errors
"""Excel-specific report generation pipeline.

This module mirrors the baseline `ReportGenerate` implementation so the
Excel ingestion flow can evolve independently (e.g., different token
rules, workbook-aware helpers) without perturbing the PDF path.
"""

import asyncio
import contextlib
import json
import logging
import os
import re
from backend.app.repositories.dataframes import sqlite_shim as sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

logger = logging.getLogger(__name__)

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None  # type: ignore

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None  # type: ignore

try:
    import fitz
except ImportError:  # pragma: no cover
    fitz = None  # type: ignore

try:
    from skimage.metrics import structural_similarity as ssim
except ImportError:  # pragma: no cover
    ssim = None  # type: ignore

try:
    from playwright.async_api import async_playwright
except ImportError:  # pragma: no cover
    async_playwright = None  # type: ignore

def _run_async(coro):
    """Run an async coroutine safely whether or not an event loop is running."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    return asyncio.run(coro)


from .contract_adapter import ContractAdapter, format_decimal_str
from .date_utils import get_col_type, mk_between_pred_for_date
from .discovery_excel import discover_batches_and_counts as discover_batches_excel
from backend.app.repositories.dataframes import DuckDBDataFrameQuery, SQLiteDataFrameLoader
from .common_helpers import (
    _format_for_token,
    _has_time_component,
    _parse_date_like,
    _raise_no_block,
    _segment_has_any_token,
    _select_prototype_block,
    _strip_found_block,
    _token_regex,
    _find_or_infer_batch_block,
    _find_rowish_block,
    _extract_page_metrics,
    detect_date_column,
    sub_token,
    blank_known_tokens,
    html_without_batch_blocks,
)
_TABLE_RE = re.compile(r"(?is)<table\b[^>]*>(?P<body>.*?)</table>")
_ROW_RE = re.compile(r"(?is)<tr\b[^>]*>(?P<body>.*?)</tr>")
_CELL_RE = re.compile(r"(?is)<t(?:d|h)\b[^>]*>.*?</t(?:d|h)>")
_ROW_ONLY_RE = re.compile(r"(?is)<tr\b[^>]*>")
_COLSPAN_RE = re.compile(r'(?is)colspan\s*=\s*["\']?(\d+)["\']?')

_EXCEL_PRINT_STYLE_ID = "excel-print-sizing"
_EXCEL_PRINT_MARGIN_MM = 10
_DEFAULT_EXCEL_PRINT_SCALE = 0.82
_MIN_EXCEL_PRINT_SCALE = 0.4
_MAX_EXCEL_PRINT_SCALE = 0.97
_PAGE_HEIGHT_PX = 980
_BASE_ROW_HEIGHT_PX = 28
_EXCEL_STYLE_BLOCK_RE = re.compile(r'(?is)<style\b[^>]*id=["\']excel-print-sizing["\'][^>]*>.*?</style>')

_DATE_PARAM_START_ALIASES = {
    "start_ts_utc",
    "start_ts",
    "start_timestamp",
    "start_datetime",
    "start_date",
    "start_dt",
    "start_iso",
    "start_date_utc",
    "from_ts_utc",
    "from_ts",
    "from_timestamp",
    "from_datetime",
    "from_date",
    "from_dt",
    "from_iso",
    "from_date_utc",
    "range_start",
    "period_start",
}

_DATE_PARAM_END_ALIASES = {
    "end_ts_utc",
    "end_ts",
    "end_timestamp",
    "end_datetime",
    "end_date",
    "end_dt",
    "end_iso",
    "end_date_utc",
    "to_ts_utc",
    "to_ts",
    "to_timestamp",
    "to_datetime",
    "to_date",
    "to_dt",
    "to_iso",
    "to_date_utc",
    "range_end",
    "period_end",
}


def _clamp_excel_print_scale(scale: float | None) -> float:
    if scale is None or not isinstance(scale, (float, int)):
        return _DEFAULT_EXCEL_PRINT_SCALE
    return max(_MIN_EXCEL_PRINT_SCALE, min(float(scale), _MAX_EXCEL_PRINT_SCALE))


def _estimate_excel_print_scale(column_count: int) -> float:
    count = max(0, int(column_count))
    if count <= 8:
        return 0.98
    if count <= 12:
        return 0.9
    if count <= 16:
        return 0.82
    if count <= 20:
        return 0.74
    if count <= 24:
        return 0.68
    if count <= 30:
        return 0.6
    if count <= 36:
        return 0.52
    if count <= 44:
        return 0.48
    return 0.44


def _count_table_columns(html_text: str) -> int:
    max_cols = 0
    for table_match in _TABLE_RE.finditer(html_text or ""):
        table_body = table_match.group("body") or ""
        for row_match in _ROW_RE.finditer(table_body):
            row_html = row_match.group("body") or ""
            total = 0
            for cell_match in _CELL_RE.finditer(row_html):
                cell_html = cell_match.group(0)
                span_match = _COLSPAN_RE.search(cell_html)
                span = 1
                if span_match:
                    try:
                        span = max(1, int(span_match.group(1)))
                    except (TypeError, ValueError):
                        span = 1
                total += span
            if total:
                max_cols = max(max_cols, total)
        if max_cols:
            break
    return max_cols


def _count_table_rows(html_text: str) -> int:
    return len(_ROW_ONLY_RE.findall(html_text or ""))


def _estimate_rows_per_page(scale: float) -> int:
    clamped = _clamp_excel_print_scale(scale)
    if clamped <= 0:
        return 1
    capacity = int((_PAGE_HEIGHT_PX / _BASE_ROW_HEIGHT_PX) / clamped)
    return max(1, capacity)


def _inject_excel_print_styles(
    html_text: str,
    *,
    scale: float | None = None,
    rows_per_page: int | None = None,
) -> str:
    """
    Ensure Excel-generated reports include print-specific CSS that
    switches pages to landscape and downscales the rendered content.
    """
    scale_value = _clamp_excel_print_scale(scale)
    scale_str = f"{scale_value:.4f}".rstrip("0").rstrip(".")
    pagination_css = ""
    if rows_per_page and rows_per_page > 0:
        pagination_css = (
            "@media print {\n"
            f"  tbody tr:nth-of-type({rows_per_page}n+1):not(:first-child) {{\n"
            "    break-before: page;\n"
            "    page-break-before: always;\n"
            "  }\n"
            "}\n"
        )

    style_block = (
        f'\n<style id="{_EXCEL_PRINT_STYLE_ID}">\n'
        f":root {{ --excel-print-scale: {scale_str}; }}\n"
        "@page {\n"
        "  size: A4 landscape;\n"
        f"  margin: {_EXCEL_PRINT_MARGIN_MM}mm;\n"
        "}\n"
        "html, body {\n"
        "  margin: 0 auto;\n"
        "  padding: 0;\n"
        "  background: #fff;\n"
        "  max-width: calc(100% / var(--excel-print-scale));\n"
        "}\n"
        "body {\n"
        "  width: calc(100% / var(--excel-print-scale));\n"
        "  min-height: calc(100% / var(--excel-print-scale));\n"
        "  transform-origin: top left;\n"
        "}\n"
        "table {\n"
        "  width: 100% !important;\n"
        "  table-layout: fixed;\n"
        "  border-collapse: collapse;\n"
        "}\n"
        "th, td {\n"
        "  word-break: break-word;\n"
        "  white-space: normal;\n"
        "}\n"
        "@media screen {\n"
        "  body {\n"
        "    transform: scale(var(--excel-print-scale));\n"
        "  }\n"
        "}\n"
        "@media print {\n"
        "  body {\n"
        "    transform: scale(var(--excel-print-scale));\n"
        "    zoom: 1;\n"
        "  }\n"
        "}\n"
        f"{pagination_css}"
        "</style>\n"
    )

    if _EXCEL_STYLE_BLOCK_RE.search(html_text):
        return _EXCEL_STYLE_BLOCK_RE.sub(style_block, html_text, count=1)

    head_close = re.search(r"(?is)</head>", html_text)
    if head_close:
        idx = head_close.start()
        return f"{html_text[:idx]}{style_block}{html_text[idx:]}"

    return f"{style_block}{html_text}"




# ======================================================
# ENTRYPOINT: DB-driven fill + PDF (no LLM here anymore)
# ======================================================
def fill_and_print(
    OBJ: dict,
    TEMPLATE_PATH: Path,
    DB_PATH: Path,
    OUT_HTML: Path,
    OUT_PDF: Path,
    START_DATE: str,
    END_DATE: str,
    batch_ids: list[str] | None = None,
    KEY_VALUES: dict | None = None,
    GENERATOR_BUNDLE: dict | None = None,
    __force_single: bool = False,
    BRAND_KIT_ID: str | None = None,
):
    """
    DB-driven renderer:
      - Assumes TEMPLATE_PATH is already the *final shell* produced at Approve (auto_fill.py)
        containing a single prototype batch block.
      - Renders header tokens (parent row per batch), row repeater (child rows), totals, literals.
      - Writes OUT_HTML and prints OUT_PDF via Playwright.

    API contract preserved (same signature).
    """

    # ---- Guard required inputs ----
    for name in ("OBJ", "TEMPLATE_PATH", "DB_PATH", "START_DATE", "END_DATE"):
        if locals().get(name) is None:
            raise NameError(f"Missing required variable: `{name}`")

    # Ensure output dir exists
    OUT_DIR = OUT_HTML.parent
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    def _log_debug(*parts: object) -> None:
        message = " ".join(str(part) for part in parts)
        logger.debug(message)

    _log_debug(
        "=== fill_and_print call ===",
        "force_single" if __force_single else "fanout_root",
        "KEY_VALUES raw=",
        KEY_VALUES or {},
    )

    # ---- Load the final shell HTML (created during Approve) ----
    from ..utils.html import _fix_fixed_footers
    html = _fix_fixed_footers(TEMPLATE_PATH.read_text(encoding="utf-8"))

    # ---- Inject brand kit CSS if requested ----
    if BRAND_KIT_ID:
        try:
            from backend.app.services.design.service import design_service
            brand_css = design_service.generate_brand_css_from_id(BRAND_KIT_ID)
            if brand_css:
                from .ReportGenerate import _inject_brand_css
                html = _inject_brand_css(html, brand_css)
                logger.debug("Brand kit CSS injected (Excel path): %s", BRAND_KIT_ID)
        except Exception:
            logger.warning("Failed to inject brand kit CSS (Excel path)", exc_info=True)

    # Support both SQLite and PostgreSQL connections via ConnectionRef
    if hasattr(DB_PATH, 'is_postgresql') and DB_PATH.is_postgresql:
        from backend.legacy.utils.connection_utils import get_loader_for_ref
        dataframe_loader = get_loader_for_ref(DB_PATH)
    else:
        dataframe_loader = SQLiteDataFrameLoader(DB_PATH)

    TOKEN_RE = re.compile(r"\{\{?\s*([A-Za-z0-9_\-\.]+)\s*\}\}?")
    TEMPLATE_TOKENS = {m.group(1) for m in TOKEN_RE.finditer(html)}

    # ---- Unpack contract ----
    OBJ = OBJ or {}
    contract_adapter = ContractAdapter(OBJ)
    PLACEHOLDER_TO_COL = contract_adapter.mapping
    param_token_set = {token for token in (contract_adapter.param_tokens or []) if token}

    join_raw = OBJ.get("join", {}) or {}
    JOIN = {
        "parent_table": contract_adapter.parent_table or join_raw.get("parent_table", ""),
        "child_table": contract_adapter.child_table or join_raw.get("child_table", ""),
        "parent_key": contract_adapter.parent_key or join_raw.get("parent_key", ""),
        "child_key": contract_adapter.child_key or join_raw.get("child_key", ""),
    }

    DATE_COLUMNS = contract_adapter.date_columns or (OBJ.get("date_columns", {}) or {})

    HEADER_TOKENS = contract_adapter.scalar_tokens or OBJ.get("header_tokens", [])
    ROW_TOKENS = contract_adapter.row_tokens or OBJ.get("row_tokens", [])
    row_token_count = sum(1 for tok in ROW_TOKENS if isinstance(tok, str) and tok.strip())
    TOTALS = contract_adapter.totals_mapping or OBJ.get("totals", {})
    ROW_ORDER = contract_adapter.row_order or OBJ.get("row_order", ["ROWID"])
    LITERALS = {
        str(token): "" if value is None else str(value) for token, value in (OBJ.get("literals", {}) or {}).items()
    }
    FORMATTERS = contract_adapter.formatters
    key_values_map: dict[str, list[str]] = {}
    if KEY_VALUES:
        for token, raw_value in KEY_VALUES.items():
            name = str(token or "").strip()
            if not name:
                continue
            values: list[str] = []
            if isinstance(raw_value, (list, tuple, set)):
                seen = set()
                for item in raw_value:
                    text = str(item or "").strip()
                    if text and text not in seen:
                        seen.add(text)
                        values.append(text)
            else:
                text = str(raw_value or "").strip()
                if text:
                    values = [text]
            if values:
                key_values_map[name] = values

    _DIRECT_COLUMN_RE = re.compile(r"^(?P<table>[A-Za-z_][\w]*)\.(?P<column>[A-Za-z_][\w]*)$")
    _SQL_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def _safe_ident(name: str) -> str:
        if _SQL_IDENT_RE.match(name):
            return name
        safe = str(name).replace('"', '""')
        return f'"{safe}"'

    def _resolve_token_column(token: str) -> tuple[str, str] | None:
        mapping_expr = PLACEHOLDER_TO_COL.get(token)
        if isinstance(mapping_expr, str):
            match = _DIRECT_COLUMN_RE.match(mapping_expr.strip())
            if match:
                return match.group("table"), match.group("column")
        required_filters = contract_adapter.required_filters
        optional_filters = contract_adapter.optional_filters
        filter_expr = (required_filters.get(token) or optional_filters.get(token) or "").strip()
        match = _DIRECT_COLUMN_RE.match(filter_expr)
        if match:
            return match.group("table"), match.group("column")
        return None

    def _canonicalize_case(table: str, column: str, raw_value: str) -> str:
        normalized_table = str(table or "").strip().lower()
        normalized_column = str(column or "").strip().lower()
        normalized_value = str(raw_value or "").strip()
        cache_key = (normalized_table, normalized_column, normalized_value.lower())
        if cache_key in _canonicalize_cache:
            return _canonicalize_cache[cache_key]
        canonical = normalized_value
        if not normalized_table or not normalized_column or not normalized_value:
            _canonicalize_cache[cache_key] = canonical
            return canonical
        try:
            frame = dataframe_loader.frame(table)
        except Exception:
            _canonicalize_cache[cache_key] = canonical
            return canonical
        if column not in frame.columns:
            _canonicalize_cache[cache_key] = canonical
            return canonical
        series = frame[column]
        try:
            matches = series.dropna().astype(str)
        except Exception:
            matches = series.dropna().apply(lambda v: str(v))
        lower_target = normalized_value.lower()
        mask = matches.str.lower() == lower_target
        filtered = matches[mask]
        if not filtered.empty:
            canonical = str(filtered.iloc[0])
        _canonicalize_cache[cache_key] = canonical
        return canonical

    _canonicalize_cache: dict[tuple[str, str, str], str] = {}

    for token, values in list(key_values_map.items()):
        resolved = _resolve_token_column(token)
        if not resolved:
            continue
        table_name, column_name = resolved
        if not table_name or not column_name:
            continue
        updated_values: list[str] = []
        changed = False
        for value in values:
            if not isinstance(value, str) or not value.strip():
                updated_values.append(value)
                continue
            canon = _canonicalize_case(table_name, column_name, value.strip())
            if canon != value:
                changed = True
            updated_values.append(canon)
        if changed:
            key_values_map[token] = updated_values

    for token, values in key_values_map.items():
        LITERALS[token] = ", ".join(values)

    alias_link_map: dict[str, str] = {}
    recipe_key_values = key_values_map.get("row_recipe_code")
    if recipe_key_values:
        alias_link_map = {
            "recipe_code": "row_recipe_code",
            "filter_recipe_code": "row_recipe_code",
        }
        literal_value = ", ".join(recipe_key_values)
        for alias in alias_link_map.keys():
            LITERALS[alias] = literal_value

    multi_key_selected = any(len(values) > 1 for values in key_values_map.values())

    def _first_alias_value(token: str) -> str | None:
        source = alias_link_map.get(token)
        if not source:
            return None
        return _first_key_value(key_values_map.get(source, []))

    def _apply_alias_params(target: dict[str, Any]) -> None:
        if not alias_link_map:
            return
        for alias in alias_link_map:
            if alias in target and str(target[alias] or "").strip():
                continue
            alias_value = _first_alias_value(alias)
            if alias_value is not None:
                target[alias] = alias_value

    _log_debug("Normalized key_values_map", key_values_map, "multi_key_selected", multi_key_selected)

    def _first_key_value(values: list[str]) -> str | None:
        for val in values:
            text = str(val or "").strip()
            if text:
                return text
        return None

    def _iter_key_combinations(values_map: dict[str, list[str]]) -> Iterable[dict[str, str]]:
        if not values_map:
            yield {}
            return
        tokens: list[str] = []
        value_lists: list[list[str]] = []
        for token, raw_values in values_map.items():
            unique: list[str] = []
            seen_local: set[str] = set()
            for val in raw_values:
                text = str(val or "").strip()
                if not text or text in seen_local:
                    continue
                seen_local.add(text)
                unique.append(text)
            if unique:
                tokens.append(token)
                value_lists.append(unique)
        if not tokens:
            yield {}
            return
        max_combos_raw = os.getenv("NEURA_REPORT_MAX_KEY_COMBINATIONS", "50")
        try:
            max_combos = int(max_combos_raw)
        except ValueError:
            max_combos = 50
        max_combos = max(1, max_combos)
        estimated = 1
        for values in value_lists:
            estimated *= max(1, len(values))
            if estimated > max_combos:
                raise ValueError(
                    f"Too many key combinations ({estimated} > {max_combos}). "
                    "Narrow key selections or reduce multi-select values."
                )
        for combo in product(*value_lists):
            yield {token: value for token, value in zip(tokens, combo)}

    _PLAYWRIGHT_ROW_FRIENDLY_LIMIT = 6000

    async def html_to_pdf_async(html_path: Path, pdf_path: Path, base_dir: Path, pdf_scale: float | None = None):
        if async_playwright is None:
            logger.warning("Playwright not available; skipping PDF generation.")
            return

        html_path_resolved = html_path.resolve()
        html_source = html_path_resolved.read_text(encoding="utf-8", errors="ignore")
        approx_row_count = html_source.lower().count("<tr")
        base_dir_resolved = (base_dir or html_path.parent).resolve()
        pdf_path_resolved = pdf_path.resolve()
        base_url = base_dir_resolved.as_uri()

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = None
            try:
                context = await browser.new_context(base_url=base_url)
                page = await context.new_page()
                await page.set_content(html_source, wait_until="networkidle")
                await page.emulate_media(media="print")
                scale_value = pdf_scale or 1.0
                if not isinstance(scale_value, (int, float)):
                    scale_value = 1.0
                scale_value = max(0.1, min(float(scale_value), 2.0))
                try:
                    await page.pdf(
                        path=str(pdf_path_resolved),
                        format="A4",
                        landscape=True,
                        print_background=True,
                        margin={"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
                        prefer_css_page_size=True,
                        scale=scale_value,
                    )
                except Exception as exc:
                    if approx_row_count >= _PLAYWRIGHT_ROW_FRIENDLY_LIMIT:
                        raise RuntimeError(
                            (
                                "PDF rendering failed because the report contains "
                                f"approximately {approx_row_count:,} table rows, which exceeds the printable limit. "
                                "Please filter the data further or split the report into smaller chunks and try again."
                            )
                        ) from exc
                    raise
            finally:
                if context is not None:
                    await context.close()
                await browser.close()

    def _combine_html_documents(html_sections: list[str]) -> str:
        if not html_sections:
            return ""
        combined_body: list[str] = []
        doc_type = ""
        head_html = ""

        head_pattern = re.compile(r"(?is)<head\b[^>]*>(?P<head>.*)</head>")
        body_pattern = re.compile(r"(?is)<body\b[^>]*>(?P<body>.*)</body>")
        doctype_pattern = re.compile(r"(?is)^\s*<!DOCTYPE[^>]*>", re.MULTILINE)

        for idx, raw_html in enumerate(html_sections):
            text = raw_html or ""
            if idx == 0:
                doctype_match = doctype_pattern.search(text)
                if doctype_match:
                    doc_type = doctype_match.group(0).strip()
                    text = text[doctype_match.end() :]
                head_match = head_pattern.search(text)
                if head_match:
                    head_html = head_match.group(0).strip()
                body_match = body_pattern.search(text)
                if body_match:
                    section_body = body_match.group("body").strip()
                else:
                    section_body = text.strip()
                combined_body.append(f'<div class="nr-key-section" data-nr-section="1">\n{section_body}\n</div>')
            else:
                body_match = body_pattern.search(text)
                section = body_match.group("body").strip() if body_match else text.strip()
                combined_body.append(
                    f'<div class="nr-key-section" data-nr-section="{idx + 1}" style="page-break-before: always;">\n{section}\n</div>'
                )

        doc_lines = []
        if doc_type:
            doc_lines.append(doc_type)
        doc_lines.append("<html>")
        if head_html:
            doc_lines.append(head_html)
        doc_lines.append("<body>")
        doc_lines.append("\n\n".join(combined_body))
        doc_lines.append("</body>")
        doc_lines.append("</html>")
        return "\n".join(doc_lines)

    def _value_has_content(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, (int, float, Decimal)):
            return value != 0
        text = str(value).strip()
        if not text:
            return False
        try:
            num = Decimal(text)
        except Exception:
            return True
        else:
            return num != 0

    def _row_has_significant_data(row: Mapping[str, Any], columns: list[str]) -> bool:
        return _row_has_any_data(row, (), columns)

    def _token_values_have_data(row: Mapping[str, Any], tokens: list[str]) -> bool:
        return _row_has_any_data(row, tokens, ())

    def _row_has_any_data(row: Mapping[str, Any], tokens: Sequence[str], columns: Sequence[str]) -> bool:
        for token in tokens:
            if not token:
                continue
            if _value_has_content(_value_for_token(row, token)):
                return True
        for col in columns:
            if not col:
                continue
            if _value_has_content(row.get(col)):
                return True
        for key, value in row.items():
            if not isinstance(key, str):
                continue
            if _is_counter_field(key):
                continue
            if _value_has_content(value):
                return True
        return False

    def _is_counter_field(name: str | None) -> bool:
        if not name:
            return False
        if not isinstance(name, str):
            name = str(name)
        normalized = re.sub(r"[^a-z0-9]", "", name.lower())
        if not normalized:
            return False
        if normalized in {
            "row",
            "rowid",
            "rowno",
            "rownum",
            "rownumber",
            "rowindex",
            "rowcounter",
            "srno",
            "sno",
        }:
            return True
        counter_markers = ("serial", "sequence", "seq", "counter")
        if any(marker in normalized for marker in counter_markers):
            return True
        counter_suffixes = (
            "slno",
            "srno",
            "sno",
            "snum",
            "snumber",
            "sl",
            "no",
            "num",
            "number",
            "idx",
            "index",
        )
        return any(normalized.endswith(suffix) and normalized.startswith("row") for suffix in counter_suffixes)

    def _reindex_serial_fields(rows: list[dict], tokens: Sequence[str], columns: Sequence[str]) -> None:
        serial_tokens = [tok for tok in tokens if tok and _is_counter_field(tok)]
        serial_columns = [col for col in columns if col and _is_counter_field(col)]
        if not serial_tokens and not serial_columns:
            return
        for idx, row in enumerate(rows, start=1):
            for tok in serial_tokens:
                row[tok] = idx
            for col in serial_columns:
                row[col] = idx

    def _value_for_token(row: Mapping[str, Any], token: str) -> Any:
        if not token:
            return None
        if token in row:
            return row[token]
        normalized = str(token).lower()
        for key in row.keys():
            if isinstance(key, str) and key.lower() == normalized:
                return row[key]
        mapped = PLACEHOLDER_TO_COL.get(token)
        if mapped:
            col = _extract_col_name(mapped)
            if col:
                if col in row:
                    return row[col]
                for key in row.keys():
                    if isinstance(key, str) and key.lower() == col.lower():
                        return row[key]
        return None

    def _prune_placeholder_rows(rows: Sequence[Mapping[str, Any]], tokens: Sequence[str]) -> list[dict[str, Any]]:
        material_tokens = [tok for tok in tokens if tok and "material" in tok.lower()]
        pruned: list[dict[str, Any]] = []
        for row in rows:
            keep = True
            for tok in material_tokens:
                if not _value_has_content(_value_for_token(row, tok)):
                    keep = False
                    break
            if keep:
                pruned.append(dict(row))
        return pruned if pruned else [dict(row) for row in rows]

    def _filter_rows_for_render(
        rows: Sequence[Mapping[str, Any]],
        row_tokens_template: Sequence[str],
        row_columns: Sequence[str],
        *,
        treat_all_as_data: bool,
    ) -> list[dict[str, Any]]:
        if not rows:
            return []

        if treat_all_as_data:
            prepared = [dict(row) for row in rows]
        else:
            significant_tokens = [tok for tok in row_tokens_template if tok and not _is_counter_field(tok)]
            significant_columns = [col for col in row_columns if col and not _is_counter_field(col)]
            prepared: list[dict[str, Any]] = []
            for row in rows:
                if significant_tokens or significant_columns:
                    if not _row_has_any_data(row, significant_tokens, significant_columns):
                        continue
                prepared.append(dict(row))

        if prepared:
            _reindex_serial_fields(prepared, row_tokens_template, row_columns)
        return prepared

    if multi_key_selected and not __force_single:
        html_sections: list[str] = []
        tmp_outputs: list[tuple[Path, Path]] = []
        try:
            for idx, combo in enumerate(_iter_key_combinations(key_values_map), start=1):
                selection: dict[str, str] = {token: value for token, value in combo.items()}
                if alias_link_map:
                    for alias, source in alias_link_map.items():
                        if alias not in selection and source in selection:
                            selection[alias] = selection[source]
                _log_debug("Fanout iteration", idx, "selection", selection)
                tmp_html = OUT_HTML.with_name(f"{OUT_HTML.stem}__key{idx}.html")
                tmp_pdf = OUT_PDF.with_name(f"{OUT_PDF.stem}__key{idx}.pdf")
                result = fill_and_print(
                    OBJ=OBJ,
                    TEMPLATE_PATH=TEMPLATE_PATH,
                    DB_PATH=DB_PATH,
                    OUT_HTML=tmp_html,
                    OUT_PDF=tmp_pdf,
                    START_DATE=START_DATE,
                    END_DATE=END_DATE,
                    batch_ids=None,
                    KEY_VALUES=selection or None,
                    GENERATOR_BUNDLE=GENERATOR_BUNDLE,
                    __force_single=True,
                )
                html_sections.append(Path(result["html_path"]).read_text(encoding="utf-8", errors="ignore"))
                tmp_outputs.append((Path(result["html_path"]), Path(result["pdf_path"])))

            if not html_sections:
                return {"html_path": str(OUT_HTML), "pdf_path": str(OUT_PDF), "rows_rendered": False}

            combined_html = _combine_html_documents(html_sections)
            column_count = max(row_token_count, _count_table_columns(combined_html))
            excel_print_scale = _estimate_excel_print_scale(column_count)
            row_count = _count_table_rows(combined_html)
            rows_per_page = _estimate_rows_per_page(excel_print_scale)
            if row_count <= rows_per_page:
                rows_per_page = None
            combined_html = _inject_excel_print_styles(
                combined_html,
                scale=excel_print_scale,
                rows_per_page=rows_per_page,
            )
            OUT_HTML.write_text(combined_html, encoding="utf-8")
            _run_async(
                html_to_pdf_async(
                    OUT_HTML,
                    OUT_PDF,
                    TEMPLATE_PATH.parent,
                    pdf_scale=excel_print_scale,
                )
            )
            return {"html_path": str(OUT_HTML), "pdf_path": str(OUT_PDF), "rows_rendered": True}
        finally:
            for tmp_html_path, tmp_pdf_path in tmp_outputs:
                for path_sel in (tmp_html_path, tmp_pdf_path):
                    with contextlib.suppress(FileNotFoundError):
                        path_sel.unlink()

    def _get_literal_raw(token: str) -> str:
        if token not in LITERALS:
            return ""
        raw = LITERALS[token]
        return "" if raw is None else str(raw)

    def _literal_has_content(token: str) -> bool:
        return bool(_get_literal_raw(token).strip())

    def _first_nonempty_literal(tokens: Iterable[str]) -> tuple[str | None, str | None]:
        for tok in tokens:
            raw = _get_literal_raw(tok)
            if raw.strip():
                return tok, raw
        return None, None

    def _record_special_value(target: dict[str, str], token: str, value: str) -> None:
        existing_raw = _get_literal_raw(token)
        if existing_raw.strip():
            target[token] = existing_raw
        else:
            target[token] = value
            if token in LITERALS:
                LITERALS[token] = value

    def _filter_tokens_without_literal(tokens: set[str]) -> set[str]:
        return {tok for tok in tokens if not _literal_has_content(tok)}

    BEGIN_TAG = "<!-- BEGIN:BATCH (auto) -->"
    END_TAG = "<!-- END:BATCH (auto) -->"
    try:
        prototype_block, start0, end_last = _select_prototype_block(html, ROW_TOKENS)
    except Exception as exc:
        _raise_no_block(html, exc)
    shell_prefix = html[:start0] + BEGIN_TAG
    shell_suffix = END_TAG + html[end_last:]

    parent_table = JOIN.get("parent_table", "")
    parent_key = JOIN.get("parent_key", "")
    child_table = JOIN.get("child_table", "")
    child_key = JOIN.get("child_key", "")

    # --- Additive: auto-detect date columns if missing from contract ---
    for _tbl in (parent_table, child_table):
        if _tbl and _tbl not in DATE_COLUMNS:
            _auto = detect_date_column(DB_PATH, _tbl)
            if _auto:
                DATE_COLUMNS[_tbl] = _auto
                logger.info("date_column_auto_detected table=%s col=%s", _tbl, _auto)

    parent_date = DATE_COLUMNS.get(parent_table, "")
    child_date = DATE_COLUMNS.get(child_table, "")
    order_col = ROW_ORDER[0] if ROW_ORDER else "ROWID"
    if isinstance(order_col, str) and order_col.upper() != "ROWID":
        mapped_order = PLACEHOLDER_TO_COL.get(order_col, order_col)
        if isinstance(mapped_order, str):
            mapped_order = mapped_order.strip()
            if "." in mapped_order:
                mapped_order = mapped_order.split(".", 1)[1].strip()
            if mapped_order:
                order_col = mapped_order

    def _normalize_token_name(name: str) -> str:
        return re.sub(r"[^a-z0-9]", "", name.lower())

    token_index: dict[str, set[str]] = defaultdict(set)
    all_candidate_tokens = (
        set(TEMPLATE_TOKENS) | set(HEADER_TOKENS) | set(ROW_TOKENS) | set(TOTALS.keys()) | set(LITERALS.keys())
    )

    def _token_synonym_keys(norm: str) -> set[str]:
        """
        Generate lightweight normalization aliases so that abbreviated tokens like
        `pg_total` or `page_num` still map onto the same lookup keys as their
        longer forms without needing every variant enumerated manually.
        """
        if not norm:
            return set()
        aliases = {norm}
        replacements: tuple[tuple[str, str], ...] = (
            ("pg", "page"),
            ("num", "number"),
            ("no", "number"),
            ("cnt", "count"),
            ("ttl", "total"),
        )
        for src, dest in replacements:
            if src in norm and dest not in norm:
                aliases.add(norm.replace(src, dest))
        # Avoid generating implausible short aliases (e.g., converting a lone "no"
        # in tokens unrelated to pagination), but include a fallback where a token
        # is exactly "pg" so that later lookups on "page" resolve.
        if norm == "pg":
            aliases.add("page")
        return {alias for alias in aliases if alias}

    for tok in all_candidate_tokens:
        norm = _normalize_token_name(tok)
        for key in _token_synonym_keys(norm):
            token_index[key].add(tok)

    def _tokens_for_keys(keys: set[str]) -> set[str]:
        found: set[str] = set()
        for key in keys:
            found.update(token_index.get(key, set()))
        return found

    def _format_for_db(dt_obj: datetime | None, raw_value, include_time_default: bool) -> str:
        """
        Normalize input dates for SQLite bindings:
          - prefer ISO 8601 date or datetime strings
          - fall back to trimmed raw strings when parsing fails
        """
        if dt_obj:
            include_time = include_time_default or bool(
                dt_obj.hour or dt_obj.minute or dt_obj.second or dt_obj.microsecond
            )
            if include_time:
                return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
            return dt_obj.strftime("%Y-%m-%d")
        return "" if raw_value is None else str(raw_value).strip()

    def _run_generator_entrypoints(
        entrypoints: dict,
        sql_params: dict[str, object],
        df_loader: SQLiteDataFrameLoader,
    ) -> dict[str, list[dict[str, object]]]:
        if not entrypoints:
            return {}
        alias_fix_patterns = [
            re.compile(r"\brows\.", re.IGNORECASE),
            re.compile(r"\brows_agg\.", re.IGNORECASE),
        ]

        def _wrap_date_param(sql_text: str, param: str) -> str:
            pattern = re.compile(rf":{param}\b")

            def _replace(match: re.Match[str]) -> str:
                start = match.start()
                prefix = sql_text[:start].rstrip()
                prefix_lower = prefix.lower()
                if prefix_lower.endswith("date(") or prefix_lower.endswith("datetime("):
                    return match.group(0)
                return f"DATE({match.group(0)})"

            return pattern.sub(_replace, sql_text)

        def _prepare_sql(sql_text: str) -> str:
            updated = re.sub(r"PARAM:([A-Za-z0-9_]+)", r":\1", sql_text)
            if "DATE(" not in updated.upper():
                return updated
            for param in ("from_date", "to_date"):
                updated = _wrap_date_param(updated, param)
            return updated

        def _attempt_sql_fix(sql_text: str, exc: Exception | None) -> str | None:
            if exc is None:
                return None
            message = str(exc).lower()
            if "no such column" not in message:
                return None
            fixed_sql = sql_text
            for pattern in alias_fix_patterns:
                fixed_sql = pattern.sub("", fixed_sql)
            return fixed_sql if fixed_sql != sql_text else None

        frames = df_loader.frames()
        query_engine = DuckDBDataFrameQuery(frames)
        try:
            results: dict[str, list[dict[str, object]]] = {}
            for name in ("header", "rows", "totals"):
                sql = entrypoints.get(name)
                if not sql:
                    results[name] = []
                    continue
                current_sql = _prepare_sql(sql)
                last_error: Exception | None = None
                for attempt in range(2):
                    try:
                        df_rows = query_engine.execute(current_sql, sql_params)
                    except Exception as exc:
                        last_error = exc
                        fixed_sql = _attempt_sql_fix(current_sql, exc)
                        if fixed_sql is not None and fixed_sql != current_sql:
                            current_sql = fixed_sql
                            continue
                        raise
                    else:
                        last_error = None
                        results[name] = df_rows.to_dict("records")
                        break
                else:
                    assert last_error is not None
                    raise last_error
            return results
        finally:
            query_engine.close()

    start_dt = _parse_date_like(START_DATE)
    end_dt = _parse_date_like(END_DATE)
    print_dt = datetime.now(timezone.utc)

    start_has_time = _has_time_component(START_DATE, start_dt)
    end_has_time = _has_time_component(END_DATE, end_dt)

    START_DATE_KEYS = {"fromdate", "datefrom", "startdate", "periodstart", "rangefrom", "fromdt", "startdt"}
    END_DATE_KEYS = {"todate", "dateto", "enddate", "periodend", "rangeto", "todt", "enddt"}
    PRINT_DATE_KEYS = {
        "printdate",
        "printedon",
        "printeddate",
        "generatedon",
        "generateddate",
        "rundate",
        "runon",
        "generatedat",
    }
    PAGE_NO_KEYS = {
        "page",
        "pageno",
        "pagenum",
        "pagenumber",
        "pageindex",
        "pageidx",
        "pagecurrent",
        "currentpage",
        "currpage",
        "pgno",
        "pgnum",
        "pgnumber",
        "pgindex",
        "pgcurrent",
    }
    PAGE_COUNT_KEYS = {
        "pagecount",
        "pagecounts",
        "totalpages",
        "pagestotal",
        "pages",
        "pagetotal",
        "totalpage",
        "pagecounttotal",
        "totalpagecount",
        "pagescount",
        "countpages",
        "lastpage",
        "finalpage",
        "maxpage",
        "pgtotal",
        "totalpg",
        "pgcount",
        "countpg",
        "pgs",
        "pgscount",
        "pgstotal",
        "totalpgs",
    }
    PAGE_LABEL_KEYS = {
        "pagelabel",
        "pageinfo",
        "pagesummary",
        "pagefooter",
        "pagefootertext",
        "pageindicator",
        "pagecaption",
        "pagefooterlabel",
        "pagetext",
        "pagefooterinfo",
        "pagehint",
    }

    special_values: dict[str, str] = {}

    start_tokens = _tokens_for_keys(START_DATE_KEYS)
    end_tokens = _tokens_for_keys(END_DATE_KEYS)
    print_tokens = _tokens_for_keys(PRINT_DATE_KEYS)
    page_number_tokens = _tokens_for_keys(PAGE_NO_KEYS)
    page_count_tokens = _tokens_for_keys(PAGE_COUNT_KEYS)
    page_label_tokens = _tokens_for_keys(PAGE_LABEL_KEYS)

    for tok in start_tokens:
        _record_special_value(
            special_values,
            tok,
            _format_for_token(tok, start_dt, include_time_default=start_has_time),
        )
    for tok in end_tokens:
        _record_special_value(
            special_values,
            tok,
            _format_for_token(tok, end_dt, include_time_default=end_has_time),
        )

    _, print_literal_value = _first_nonempty_literal(print_tokens)
    parsed_print_dt = _parse_date_like(print_literal_value) if print_literal_value else None
    print_dt_source = parsed_print_dt or print_dt
    print_has_time = _has_time_component(print_literal_value, parsed_print_dt)

    for tok in print_tokens:
        if print_literal_value and not parsed_print_dt:
            value = print_literal_value
        else:
            value = _format_for_token(tok, print_dt_source, include_time_default=print_has_time)
        _record_special_value(special_values, tok, value)

    page_number_tokens = _filter_tokens_without_literal(page_number_tokens)
    page_count_tokens = _filter_tokens_without_literal(page_count_tokens)
    page_label_tokens = _filter_tokens_without_literal(page_label_tokens)

    post_literal_specials = {tok: val for tok, val in special_values.items() if tok not in LITERALS}

    _ident_re = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def qident(name: str) -> str:
        if _ident_re.match(name):
            return name
        safe = name.replace('"', '""')
        return f'"{safe}"'

    # ---- Composite-key helpers ----
    def _parse_key_cols(key_spec: str) -> list[str]:
        return [c.strip() for c in str(key_spec).split(",") if c and c.strip()]

    def _key_expr(cols: list[str]) -> str:
        parts = [f"COALESCE(CAST({qident(c)} AS TEXT),'')" for c in cols]
        if not parts:
            return "''"
        expr = parts[0]
        for p in parts[1:]:
            expr = f"{expr} || '|' || {p}"
        return expr

    def _split_bid(bid: str, n: int) -> list[str]:
        parts = str(bid).split("|")
        if len(parts) != n:
            raise ValueError(f"Composite key mismatch: expected {n} parts, got {len(parts)} in {bid!r}")
        return parts

    def _looks_like_composite_id(x: str, n: int) -> bool:
        return isinstance(x, str) and x.count("|") == (n - 1)

    pcols = _parse_key_cols(parent_key)
    ccols = _parse_key_cols(child_key)

    has_child = bool(child_table and ccols)
    parent_table_lc = parent_table.lower()
    child_table_lc = child_table.lower()
    parent_filter_map: dict[str, list[str]] = {}
    child_filter_map: dict[str, list[str]] = {}
    if key_values_map:
        for token, values in key_values_map.items():
            mapping_value = PLACEHOLDER_TO_COL.get(token)
            if not isinstance(mapping_value, str):
                continue
            target = mapping_value.strip()
            if not target or target.upper().startswith("PARAM:") or "." not in target:
                continue
            table_name, column_name = target.split(".", 1)
            table_name = table_name.strip(' "`[]')
            column_name = column_name.strip(' "`[]')
            if not column_name:
                continue
            table_key = table_name.lower()
            if table_key in (parent_table_lc, "header"):
                bucket = list(parent_filter_map.get(column_name, []))
                for val in values:
                    if val not in bucket:
                        bucket.append(val)
                if bucket:
                    parent_filter_map[column_name] = bucket
            if has_child and table_key in (child_table_lc, "rows"):
                bucket = list(child_filter_map.get(column_name, []))
                for val in values:
                    if val not in bucket:
                        bucket.append(val)
                if bucket:
                    child_filter_map[column_name] = bucket
    parent_filter_items = list(parent_filter_map.items())
    child_filter_items = list(child_filter_map.items())
    parent_filter_sqls: list[str] = []
    parent_filter_values: list[str] = []
    for col, values in parent_filter_items:
        normalized: list[str] = []
        for val in values:
            if not isinstance(val, str):
                continue
            text = val.strip()
            if text and text not in normalized:
                normalized.append(text)
        if not normalized:
            continue
        if len(normalized) == 1:
            parent_filter_sqls.append(f"{qident(col)} = ?")
        else:
            placeholders = ", ".join("?" for _ in normalized)
            parent_filter_sqls.append(f"{qident(col)} IN ({placeholders})")
        parent_filter_values.extend(normalized)
    parent_filter_values_tuple = tuple(parent_filter_values)

    child_filter_sqls: list[str] = []
    child_filter_values: list[str] = []
    for col, values in child_filter_items:
        normalized: list[str] = []
        for val in values:
            if not isinstance(val, str):
                continue
            text = val.strip()
            if text and text not in normalized:
                normalized.append(text)
        if not normalized:
            continue
        if len(normalized) == 1:
            child_filter_sqls.append(f"{qident(col)} = ?")
        else:
            placeholders = ", ".join("?" for _ in normalized)
            child_filter_sqls.append(f"{qident(col)} IN ({placeholders})")
        child_filter_values.extend(normalized)
    child_filter_values_tuple = tuple(child_filter_values)

    def _merge_predicate(base_sql: str, extras: list[str]) -> str:
        if not extras:
            return base_sql
        extras_joined = " AND ".join(extras)
        base_sql = (base_sql or "1=1").strip()
        return f"({base_sql}) AND {extras_joined}"

    # --- Date predicates and adapters (handle missing/invalid date columns)
    parent_type = get_col_type(DB_PATH, parent_table, parent_date)
    child_type = get_col_type(DB_PATH, child_table, child_date)
    parent_pred, adapt_parent = mk_between_pred_for_date(parent_date, parent_type)
    child_pred, adapt_child = mk_between_pred_for_date(child_date, child_type)
    parent_where_clause = _merge_predicate(parent_pred, parent_filter_sqls)
    child_where_clause = _merge_predicate(child_pred, child_filter_sqls) if has_child else child_pred
    db_start = _format_for_db(start_dt, START_DATE, start_has_time)
    db_end = _format_for_db(end_dt, END_DATE, end_has_time)
    PDATE = tuple(adapt_parent(db_start, db_end))  # () if 1=1
    CDATE = tuple(adapt_child(db_start, db_end)) if has_child else tuple()  # () if 1=1
    parent_params_all = tuple(PDATE) + parent_filter_values_tuple
    child_params_all = tuple(CDATE) + child_filter_values_tuple if has_child else tuple()

    sql_params: dict[str, object] = {
        "from_date": db_start,
        "to_date": db_end,
    }

    for token in contract_adapter.param_tokens:
        if token in ("from_date", "to_date"):
            continue
        if token in key_values_map:
            first_value = _first_key_value(key_values_map[token])
            if first_value is not None:
                sql_params[token] = first_value
        elif alias_link_map.get(token):
            alias_value = _first_alias_value(token)
            if alias_value is not None:
                sql_params[token] = alias_value
        elif token in LITERALS:
            sql_params[token] = LITERALS[token]
        elif token in special_values:
            sql_params[token] = special_values[token]
        else:
            sql_params.setdefault(token, "")

    _apply_alias_params(sql_params)

    def _apply_date_param_defaults(target: dict[str, object]) -> None:
        if not isinstance(target, dict):
            return

        def _inject(names: set[str], default_value: str) -> None:
            if not default_value:
                return
            for alias in names:
                if alias not in param_token_set and alias not in target:
                    continue
                current = target.get(alias)
                if isinstance(current, str):
                    if current.strip():
                        continue
                elif current not in (None, ""):
                    continue
                target[alias] = default_value

        _inject(_DATE_PARAM_START_ALIASES, db_start)
        _inject(_DATE_PARAM_END_ALIASES, db_end)

    _apply_date_param_defaults(sql_params)

    if "recipe_code" in sql_params:
        _log_debug(
            "[multi-debug] generator param binding",
            "force_single" if __force_single else "fanout_root",
            "key_values=",
            key_values_map,
            "recipe_code=",
            sql_params.get("recipe_code"),
        )

    if GENERATOR_BUNDLE is None:
        generator_dir = TEMPLATE_PATH.parent / "generator"
        meta_path = generator_dir / "generator_assets.json"
        if meta_path.exists():
            try:
                meta_payload = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception:
                meta_payload = None
            else:
                bundle: dict[str, object] = {"meta": meta_payload}
                output_schemas_path = generator_dir / "output_schemas.json"
                if output_schemas_path.exists():
                    try:
                        bundle["output_schemas"] = json.loads(output_schemas_path.read_text(encoding="utf-8"))
                    except Exception:
                        pass
                GENERATOR_BUNDLE = bundle

    generator_results: dict[str, list[dict[str, object]]] | None = None

    # --- DataFrame pipeline ---
    if not multi_key_selected:
        try:
            from .dataframe_pipeline import DataFramePipeline

            df_value_filters: dict[str, list] = {}
            if key_values_map:
                for name, values in key_values_map.items():
                    df_value_filters[name] = values

            pipeline = DataFramePipeline(
                contract_adapter=contract_adapter,
                loader=dataframe_loader,
                params=sql_params,
                start_date=sql_params.get("start_date") or sql_params.get("from_date"),
                end_date=sql_params.get("end_date") or sql_params.get("to_date"),
                value_filters=df_value_filters,
            )
            generator_results = pipeline.execute()
            if not any(generator_results.get(s) for s in ("header", "rows", "totals")):
                logger.warning("DataFrame pipeline returned empty results; falling back to SQL path")
                generator_results = None
        except Exception as exc:
            logger.warning("DataFrame pipeline failed; falling back to SQL path: %s", exc)
            generator_results = None

    # ---- Normalize / auto-discover BATCH_IDS ----
    if generator_results is None:
        need_discover = False
        existing = batch_ids

        if isinstance(existing, str):
            existing = [existing]

        if not existing:
            need_discover = True
        else:
            if not isinstance(existing, (list, tuple)):
                need_discover = True
            else:
                existing = list(existing)
                if len(pcols) > 1:
                    if any(not _looks_like_composite_id(i, len(pcols)) for i in existing):
                        logger.debug("Provided BATCH_IDS do not match composite key format; falling back to auto-discovery.")
                        need_discover = True

        if need_discover:
            discovery_summary = discover_batches_excel(
                db_path=DB_PATH,
                contract=OBJ,
                start_date=START_DATE,
                end_date=END_DATE,
                key_values=key_values_map,
            )
            BATCH_IDS = [str(batch["id"]) for batch in discovery_summary.get("batches", [])]
        else:
            BATCH_IDS = existing
    else:
        BATCH_IDS = ["__GENERATOR_SINGLE__"]

    _log_debug("BATCH_IDS:", len(BATCH_IDS or []), (BATCH_IDS or [])[:20] if BATCH_IDS else [])
    # ---- Only touch tokens outside <style>/<script> ----
    def format_token_value(token: str, raw_value: Any) -> str:
        return contract_adapter.format_value(token, raw_value)


    def _inject_page_counter_spans(
        html_in: str,
        page_tokens: set[str],
        count_tokens: set[str],
        label_tokens: set[str] | None = None,
    ) -> str:
        tokens_to_remove = (
            {tok for tok in page_tokens if tok}
            | {tok for tok in count_tokens if tok}
            | {tok for tok in (label_tokens or set()) if tok}
        )
        if not tokens_to_remove:
            return html_in

        token_pattern = "|".join(re.escape(tok) for tok in tokens_to_remove)
        placeholder_pattern = rf"(?:\{{\{{\s*(?:{token_pattern})\s*\}}\}}|\{{\s*(?:{token_pattern})\s*\}})"
        placeholder_re = re.compile(placeholder_pattern)
        element_re = re.compile(
            rf"(?is)<(?P<tag>[a-z0-9:_-]+)(?:\s[^>]*)?>(?:(?!</(?P=tag)>).)*?{placeholder_pattern}(?:(?!</(?P=tag)>).)*?</(?P=tag)>"
        )
        line_re = re.compile(rf"(?im)^[^\n]*{placeholder_pattern}[^\n]*\n?")

        def _remove_blocks(text: str) -> str:
            while True:
                text, count = element_re.subn("", text)
                if count == 0:
                    break
            text = line_re.sub("", text)
            text = placeholder_re.sub("", text)
            return text

        return _remove_blocks(html_in)

    # ---- Helpers to find tbody / row template (improved) ----
    def best_rows_tbody(inner_html: str, allowed_tokens: set):
        tbodys = list(re.finditer(r"(?is)<tbody\b[^>]*>(.*?)</tbody>", inner_html))
        best = (None, None, -1)  # (match, inner, hits)
        for m in tbodys:
            tin = m.group(1)
            hits = 0
            for trm in re.finditer(r"(?is)<tr\b[^>]*>.*?</tr>", tin):
                tr_html = trm.group(0)
                toks = re.findall(r"\{\{\s*([^}\n]+?)\s*\}\}|\{\s*([^}\n]+?)\s*\}", tr_html)
                flat = [a.strip() if a else b.strip() for (a, b) in toks]
                hits += sum(1 for t in flat if t in allowed_tokens)
            if hits > best[2]:
                best = (m, tin, hits)
        if best[0] is not None:
            return best[0], best[1]
        return (tbodys[0], tbodys[0].group(1)) if tbodys else (None, None)

    def find_row_template(tbody_inner: str, allowed_tokens: set):
        for m in re.finditer(r"(?is)<tr\b[^>]*>.*?</tr>", tbody_inner):
            tr_html = m.group(0)
            toks = re.findall(r"\{\{\s*([^}\n]+?)\s*\}\}|\{\s*([^}\n]+?)\s*\}", tr_html)
            flat = []
            for a, b in toks:
                if a:
                    flat.append(a.strip())
                if b:
                    flat.append(b.strip())
            flat = [t for t in flat if t in allowed_tokens]
            if flat:
                return tr_html, (m.start(0), m.end(0)), sorted(set(flat), key=len, reverse=True)
        return None, None, []

    def majority_table_for_tokens(tokens, mapping):
        from collections import Counter

        tbls = []
        for t in tokens:
            tc = mapping.get(t, "")
            if "." in tc:
                tbls.append(tc.split(".", 1)[0])
        return Counter(tbls).most_common(1)[0][0] if tbls else None

    # ---- Pre-compute minimal column sets ----
    def _extract_col_name(mapping_value: str | None) -> str | None:
        if not isinstance(mapping_value, str):
            return None
        target = mapping_value.strip()
        if "." not in target:
            return None
        return target.split(".", 1)[1].strip() or None

    header_cols = sorted({col for t in HEADER_TOKENS for col in [_extract_col_name(PLACEHOLDER_TO_COL.get(t))] if col})
    row_cols = sorted({col for t in ROW_TOKENS for col in [_extract_col_name(PLACEHOLDER_TO_COL.get(t))] if col})

    totals_by_table = defaultdict(lambda: defaultdict(list))
    total_token_to_target = {}

    for token, raw_target in TOTALS.items():
        if isinstance(raw_target, dict):
            continue  # Declarative op spec — handled by DF pipeline, not SQL prefetch
        target = (raw_target or PLACEHOLDER_TO_COL.get(token, "")).strip()
        if not target or "." not in target:
            continue
        table_name, col_name = [part.strip() for part in target.split(".", 1)]
        if not table_name or not col_name:
            continue
        totals_by_table[table_name][col_name].append(token)
        total_token_to_target[token] = (table_name, col_name)

    def _coerce_total_value(raw):
        if raw is None:
            return None, "0"
        try:
            decimal_value = Decimal(str(raw).strip())
        except (InvalidOperation, ValueError, TypeError, AttributeError):
            return None, "0"
        if not decimal_value.is_finite():
            return None, "0"
        formatted = format_decimal_str(decimal_value, max_decimals=3) or "0"
        return float(decimal_value), formatted

    totals_accum = defaultdict(float)
    last_totals_per_token = {token: "0" for token in TOTALS}

    child_totals_cols = {col: list(tokens) for col, tokens in totals_by_table.get(child_table, {}).items()}
    # ---- Render all batches ----
    rendered_blocks = []
    generator_header_replacements: dict[str, str] | None = None
    if generator_results is not None:
        block_html = prototype_block

        header_rows = generator_results.get("header") or []
        header_row = header_rows[0] if header_rows else {}
        header_token_values: dict[str, str] = {}
        for t in HEADER_TOKENS:
            if t in header_row:
                value = header_row[t]
                formatted_value = format_token_value(t, value)
                block_html = sub_token(block_html, t, formatted_value)
                header_token_values[t] = formatted_value
        if header_token_values:
            generator_header_replacements = header_token_values

        allowed_row_tokens = {t for t in PLACEHOLDER_TO_COL.keys() if t not in TOTALS} - set(HEADER_TOKENS)
        rows_data = generator_results.get("rows") or []
        filtered_rows: list[dict[str, Any]] = []
        row_tokens_in_template: list[str] = []

        if rows_data:
            tbody_m, tbody_inner = best_rows_tbody(block_html, allowed_row_tokens)
            if tbody_m and tbody_inner:
                row_template, row_span, row_tokens_in_template = find_row_template(tbody_inner, allowed_row_tokens)
                if row_template and row_tokens_in_template:
                    row_columns_template = [
                        _extract_col_name(PLACEHOLDER_TO_COL.get(tok)) or "" for tok in row_tokens_in_template
                    ]
                    render_columns = list(row_tokens_in_template)
                    filtered_rows = _filter_rows_for_render(
                        rows_data,
                        row_tokens_in_template,
                        render_columns,
                        treat_all_as_data=bool(__force_single),
                    )
                    filtered_rows = _prune_placeholder_rows(filtered_rows, row_tokens_in_template)
                    if __force_single:
                        _log_debug(
                            f"[multi-debug] generator rows: total={len(rows_data)}, filtered={len(filtered_rows)}, key_values={KEY_VALUES}"
                        )
                    if filtered_rows:
                        parts: list[str] = []
                        for row in filtered_rows:
                            tr = row_template
                            for tok in row_tokens_in_template:
                                val = _value_for_token(row, tok)
                                tr = sub_token(tr, tok, format_token_value(tok, val))
                            parts.append(tr)
                        new_tbody_inner = tbody_inner[: row_span[0]] + "\n".join(parts) + tbody_inner[row_span[1] :]
                        block_html = block_html[: tbody_m.start(1)] + new_tbody_inner + block_html[tbody_m.end(1) :]
            else:
                tr_tokens = [
                    m.group(1) or m.group(2)
                    for m in re.finditer(r"\{\{\s*([^}\n]+?)\s*\}\}|\{\s*([^}\n]+?)\s*\}", block_html)
                ]
                row_tokens_in_template = [t.strip() for t in tr_tokens if t and t.strip() in allowed_row_tokens]
                if row_tokens_in_template:
                    row_columns_template = [
                        _extract_col_name(PLACEHOLDER_TO_COL.get(tok)) or "" for tok in row_tokens_in_template
                    ]
                    render_columns = list(row_tokens_in_template)
                    filtered_rows = _filter_rows_for_render(
                        rows_data,
                        row_tokens_in_template,
                        render_columns,
                        treat_all_as_data=bool(__force_single),
                    )
                    filtered_rows = _prune_placeholder_rows(filtered_rows, row_tokens_in_template)
                    if __force_single:
                        _log_debug(
                            f"[multi-debug] generator rows (no tbody): total={len(rows_data)}, filtered={len(filtered_rows)}, key_values={KEY_VALUES}"
                        )
                    if filtered_rows:
                        parts = []
                        for row in filtered_rows:
                            tr = prototype_block
                            for tok in row_tokens_in_template:
                                val = _value_for_token(row, tok)
                                tr = sub_token(tr, tok, format_token_value(tok, val))
                            parts.append(tr)
                        block_html = "\n".join(parts)

        if filtered_rows:
            totals_row = (generator_results.get("totals") or [{}])[0]
            for token in TOTALS:
                value = totals_row.get(token)
                formatted = format_token_value(token, value)
                block_html = sub_token(block_html, token, formatted)
                last_totals_per_token[token] = formatted
                target = total_token_to_target.get(token)
                if target:
                    fv, _formatted = _coerce_total_value(value)
                    if fv is not None:
                        totals_accum[target] = totals_accum.get(target, 0.0) + fv

            rendered_blocks.append(block_html)
        else:
            _log_debug("Generator SQL produced no usable row data after filtering; skipping block.")

    # ---- Assemble full document ----
    rows_rendered = bool(rendered_blocks)
    if not rows_rendered:
        _log_debug("No rendered blocks generated for this selection.")

    html_multi = shell_prefix + "\n".join(rendered_blocks) + shell_suffix

    for tok, val in post_literal_specials.items():
        html_multi = sub_token(html_multi, tok, val if val is not None else "")

    if page_number_tokens or page_count_tokens or page_label_tokens:
        html_multi = _inject_page_counter_spans(html_multi, page_number_tokens, page_count_tokens, page_label_tokens)

    if total_token_to_target:
        overall_formatted = {}
        for (table_name, col_name), total in totals_accum.items():
            _, formatted = _coerce_total_value(total)
            overall_formatted[(table_name, col_name)] = formatted

        for token, target in total_token_to_target.items():
            table_name, col_name = target
            value = overall_formatted.get((table_name, col_name), last_totals_per_token.get(token, "0"))
            html_multi = sub_token(html_multi, token, value)

    if generator_header_replacements:
        for token, value in generator_header_replacements.items():
            html_multi = sub_token(html_multi, token, value)

    # Apply literals globally
    for t, s in LITERALS.items():
        html_multi = sub_token(html_multi, t, s)

    # Blank any remaining known tokens
    ALL_KNOWN_TOKENS = set(HEADER_TOKENS) | set(ROW_TOKENS) | set(TOTALS.keys()) | set(LITERALS.keys())
    html_multi = blank_known_tokens(html_multi, ALL_KNOWN_TOKENS)

    # Strip internal BATCH markers — they are pipeline internals and must not leak into output
    html_multi = html_multi.replace(BEGIN_TAG, "").replace(END_TAG, "")

    column_count = max(row_token_count, _count_table_columns(html_multi))
    excel_print_scale = _estimate_excel_print_scale(column_count)
    row_count = _count_table_rows(html_multi)
    rows_per_page = _estimate_rows_per_page(excel_print_scale)
    if row_count <= rows_per_page:
        rows_per_page = None
    html_multi = _inject_excel_print_styles(
        html_multi,
        scale=excel_print_scale,
        rows_per_page=rows_per_page,
    )

    # write to the path requested by the API
    OUT_HTML.write_text(html_multi, encoding="utf-8")
    _log_debug("Wrote HTML:", OUT_HTML)

    _log_debug("BATCH_IDS:", len(BATCH_IDS or []), (BATCH_IDS or [])[:20] if BATCH_IDS else [])

    _run_async(
        html_to_pdf_async(
            OUT_HTML,
            OUT_PDF,
            TEMPLATE_PATH.parent,
            pdf_scale=excel_print_scale,
        )
    )
    _log_debug("Wrote PDF via Playwright:", OUT_PDF)

    return {"html_path": str(OUT_HTML), "pdf_path": str(OUT_PDF), "rows_rendered": rows_rendered}


# keep CLI usage (unchanged)
if __name__ == "__main__":
    print("Module ready for API integration. Call fill_and_print(...) from your FastAPI endpoint.")
