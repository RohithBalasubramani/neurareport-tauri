# mypy: ignore-errors
from __future__ import annotations

import base64
import json
import re
from functools import lru_cache
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, Iterable, Mapping

PROMPT_VERSION = "llm_call_3_df_v2"
PROMPT_VERSION_3_5 = "v5"
PROMPT_VERSION_4 = "v3_df"

# Legacy aliases kept for import compatibility
PROMPT_VERSION_DF = PROMPT_VERSION
PROMPT_VERSION_4_DF = PROMPT_VERSION_4
LLM_CALL_PROMPTS: Dict[str, str] = {
    "llm_call_1": dedent(
        """\
        Produce a COMPLETE, self-contained HTML document (<!DOCTYPE html> ...) with inline <style>. It must visually photocopy the given PDF page image as closely as possible. Mirror fonts, spacing, borders, alignment, and table layouts. Tables must use border-collapse, 1px borders, and table-layout: fixed for neat alignment.

        SCHEMA USAGE
        - If a SCHEMA is provided below, use ONLY placeholders from that SCHEMA exactly as written (same names).
        - If SCHEMA is NOT provided, FIRST infer a compact schema (see SCHEMA_JSON rules below) and then use ONLY those tokens in the HTML.
        - In HTML, placeholders must be written as {token_name} (single braces). In SCHEMA_JSON they appear WITHOUT braces.
        - If a value is not in SCHEMA/SCHEMA_JSON, render it as literal text. If a token exists in SCHEMA/SCHEMA_JSON but does not appear on this page, omit it.

        TOKEN NAMING CONVENTIONS (when inferring — NOT when a SCHEMA is provided)
        - Use lowercase_snake_case for all token names.
        - Scalar tokens (header/footer fields): use descriptive names like `report_title`, `plant_name`, `from_date`, `to_date`, `print_date`, `page_info`.
        - Row tokens (repeating data columns): prefix with `row_` e.g. `row_material_name`, `row_quantity`, `row_amount`.
        - Total tokens (summary/aggregate values): prefix with `total_` e.g. `total_quantity`, `total_amount`.
        - Choose names that describe the data semantics (what the field represents), not the visual appearance.

        REPEATABLE BLOCK (edge case)
        - If the page clearly contains repeating sections (visually identical blocks stacked vertically), output ONE prototype of that block wrapped exactly as:
        <!-- BEGIN:BLOCK_REPEAT batches -->
        <section class='batch-block'>...</section>
        <!-- END:BLOCK_REPEAT -->
        - Place header/footer OUTSIDE these markers. Do NOT clone or duplicate multiple blocks.

        ROW PROTOTYPES
        - For tables with repeating rows, output headers in <thead> and a single prototype row inside <tbody><tr>...</tr></tbody>.
        - The prototype row contains one {row_*} token per cell, matching the header above it.
        - Keep any final summary/total row outside <tbody> (e.g. in a <tfoot> or a separate element after the table).

        STRUCTURE & CSS
        - The result must be printable: use @page size A4 with sensible margins.
        - Prefer flowing layout (avoid fixed heights). Do NOT use position:fixed or position:absolute on headers or footers — these overlap table content on long reports. Keep footers in normal document flow so they render after the content.
        - Reproduce what is visible — draw ONLY the rules/lines that exist in the image. Default to no borders and transparent backgrounds; add borders per edge only where a line is visible.
        - Use table markup ONLY for true grids and structured data (never div-based). Use borderless tables or simple divs for key/value areas. Avoid unnecessary nested tables or enclosing frames.
        - Right-align numeric columns where appropriate; keep typographic rhythm tight enough to match the PDF.

        PROJECT-SPECIFIC ADDITIONS
        - Add a minimal set of CSS custom properties to make column widths and key spacings easy to refine later (e.g., :root { --col-1-w: 24mm; --row-gap: 2mm; }). Use these variables inside the CSS you produce.
        - Add stable IDs for major zones only (no extra wrappers): #report-header, #data-table (main grid), #report-totals (if present). Do NOT add decorative containers.
        - For every table header cell, include a data-label attribute with the visible header text normalized to lowercase_snake_case (e.g., <th data-label="material_name">Material Name</th>). The visible text inside the <th> must remain unchanged — only the attribute value is normalized.

        OUTPUT RULES
        - No lorem ipsum or sample values. No external resources.
        - No comments except the repeat markers if applicable.
        - Do NOT rename or invent tokens beyond SCHEMA/SCHEMA_JSON.
        - Return ONLY the outputs described below — no markdown fences, no explanations, no prose.

        OUTPUT FORMAT
        1) First, the RAW HTML between these exact markers:
        <!--BEGIN_HTML-->
        ...full html...
        <!--END_HTML-->

        2) Then, the SCHEMA JSON between these markers:
        <!--BEGIN_SCHEMA_JSON-->
        {
          "scalars": ["report_title", "plant_name", "from_date"],
          "row_tokens": ["row_material_name", "row_quantity", "row_amount"],
          "totals": ["total_quantity", "total_amount"],
          "notes": ""
        }
        <!--END_SCHEMA_JSON-->
        IMPORTANT: The token names above are only illustrative examples of the NAMING CONVENTION. You must replace them with the actual tokens you discovered from THIS page. Never copy these example names verbatim.

        If SCHEMA is provided below, ensure SCHEMA_JSON you output matches it exactly (names and membership). If SCHEMA is not provided, infer SCHEMA_JSON consistently with the placeholders you used in the HTML (one-to-one, no extras, no omissions).

        [INPUTS]
        - PDF page image is attached.
        - SCHEMA (may be absent):
        SCHEMA:
        {schema_str}
        """
    ).strip(),
    "llm_call_2": dedent(
        """\
        Compare these two images: REFERENCE (the original PDF page) vs RENDER (your current HTML output).
        Goal: refine the HTML/CSS so the rendered output becomes a near-perfect PHOTOCOPY of the reference.

        STRICT RULES — violations will cause rejection
        1. Do NOT rename, add, remove, or reorder any {{token}} placeholders. Keep every token exactly as it appears in the current HTML.
        2. Do NOT change the number of repeating sections, table rows, <tbody> blocks, or repeat markers.
        3. If repeat markers (<!-- BEGIN:BLOCK_REPEAT ... -->) are present, keep them unchanged with exactly one prototype inside.
        4. Prefer CSS-only edits. Only add minimal HTML structural wrappers (e.g., <colgroup>) when CSS alone cannot achieve the alignment.

        CSS REFINEMENT STRATEGY (in priority order)
        1. First, tune existing CSS custom properties (--col-1-w, --col-2-w, --row-gap, etc.).
        2. If custom properties are insufficient, edit CSS rules directly.
        3. Use millimetre-based sizing for print fidelity (widths, padding, margins in mm).
        4. Right-align numeric columns; use font-variant-numeric: tabular-nums for digit alignment.
        5. Match borders/lines exactly as visible in the reference — per-edge borders only, no shadows or rounded corners.
        6. Never use position:fixed/absolute on headers/footers (causes overlap on long reports).
        7. Never scale the page via CSS transforms — correct geometry through widths, margins, padding, line-height instead.

        VISUAL MATCHING
        Identify and correct EVERY visible discrepancy: geometry, proportions, typography, line metrics, borders, column widths, text alignment, spacing, and header/footer placement. Derive all values from the reference image. The result must be indistinguishable from the reference when printed.

        OUTPUT — return ONLY this, nothing else:
        <!--BEGIN_HTML-->
        ...full refined html (<!DOCTYPE html> ... with inline <style>)...
        <!--END_HTML-->

        No markdown fences, no commentary, no prose before or after the markers.

        [INPUTS]
        SCHEMA:
        {schema_str}

        [REFERENCE_IMAGE]
        (embedded image URL)

        [RENDER_IMAGE]
        (embedded image URL)

        [CURRENT_HTML]
        {current_html}
        """
    ).strip(),
}

_INPUT_MARKER = "[INPUTS]"
_CALL3_PROMPT_SECTION_DF = """
You are a meticulous report auto-mapping analyst. You are given the FULL HTML of a report template and a RICH DB CATALOG that includes column types and sample values.

YOUR TWO TASKS:
A) AUTO-MAPPING — Map every placeholder token in the HTML to its data source from the CATALOG.
B) CONSTANT DISCOVERY — Identify tokens whose values are static and record their literal values.

--------------------------------------------------------------------------------
MAPPING RULES — CRITICAL CONSTRAINTS FOR DATAFRAME MODE
1. Output ONLY simple "table.column" references from the CATALOG. NEVER output SQL expressions, functions (SUM, STRFTIME, CONCAT, CASE, COALESCE, etc.), or any code.
2. Every mapping value must be ONE of:
   a) A catalog column in exact "table.column" format (e.g., "orders.customer_name").
   b) A parameter passthrough in "params.param_name" format (e.g., "params.plant_name").
   c) The literal string "To Be Selected..." for date-range and page/filter tokens (from_date, to_date, start_date, end_date, page_info, page_number, and similar).
   d) The literal string "UNRESOLVED" when no clear single-column source exists.
3. If a token requires combining, formatting, or computing from multiple columns, set mapping to "UNRESOLVED" and describe the operation in meta.hints.
4. Use the CATALOG's data types and sample values to make accurate mapping decisions. Match token semantics to column semantics (numeric tokens → numeric columns, date tokens → date columns, text tokens → text columns).
5. Never invent table or column names. Never emit legacy wrappers (DERIVED:, TABLE_COLUMNS[...], COLUMN_EXP[...]).

HEADER KEYING
- If a <th> has data-label, use that value (lowercase_snake_case) as the mapping key ONLY when the same token also appears as a {placeholder} in the HTML or in SCHEMA.
- Otherwise, normalize the visible header text.

FUZZY MATCHING
- Match tokens to catalog columns considering common abbreviations:
  * "qty" ↔ "quantity", "amt" ↔ "amount", "desc" ↔ "description"
  * "sl"/"serial"/"sno" ↔ "sl_no", "wt" ↔ "weight", "pct"/"%" ↔ "percent"
- Always match against actual CATALOG column names.

AGGREGATE / MULTI-COLUMN HEADERS
- If a header represents an aggregate across multiple columns, set mapping to UNRESOLVED and record in meta.hints:
  {"op": "SUM", "over": ["table.col1", "table.col2", ...]}
  or {"op": "concat", "columns": ["table.col_a", "table.col_b"]}

CONSTANT PLACEHOLDERS
- Report ONLY tokens that are truly constant across ALL runs (page titles, company name, static captions).
- NEVER mark as constant: dates, row values, totals, page numbers, or anything in schema.row_tokens / schema.totals.
- Remove constant tokens from "mapping" but keep them in "token_samples".

TOKEN SNAPSHOT
- Emit a "token_samples" dict listing EVERY placeholder token from the HTML (exact name, no braces).
- For each token, output the literal string visible on the PDF. Use "NOT_VISIBLE" or "UNREADABLE" as fallback — never leave blank.

INPUTS
[FULL_HTML]
{html_for_llm}
[CATALOG]
{catalog_json}
Optional:
[SCHEMA_JSON]
{schema_json_if_any}
[REFERENCE_PNG_HINT]
"A screenshot of the reference PDF was used to create this template; treat visible page titles/branding as likely constants."

OUTPUT — return ONLY this JSON object, no markdown fences, no commentary, no text before or after:
{
  "mapping": {
    "<token>": "<table.column | params.param_name | To Be Selected... | UNRESOLVED>"
  },
  "token_samples": {
    "<token>": "<literal string from PDF>"
  },
  "meta": {
    "unresolved": ["<token>", "..."],
    "hints": {
      "<token>": { "op": "SUM|CONCAT|FORMAT", "columns": ["table.col1", "table.col2"] }
    }
  }
}

VALIDATION CHECKLIST (verify before responding):
- Every mapping value is a simple "table.column" reference, "params.*", "To Be Selected...", or "UNRESOLVED". NO SQL functions or expressions.
- Every token from the HTML appears in either "mapping" or "token_samples".
- Constants removed from mapping still appear in token_samples.
- No empty string values in token_samples.
- Output is a single valid JSON object with no surrounding text.
""".strip()


@lru_cache(maxsize=1)
def _load_llm_call_3_section() -> tuple[str, str]:
    section = _CALL3_PROMPT_SECTION_DF
    if _INPUT_MARKER in section:
        system, remainder = section.split(_INPUT_MARKER, 1)
        system_text = system.strip()
        user_template = f"{_INPUT_MARKER}{remainder}".strip()
    else:
        system_text = section.strip()
        user_template = ""
    return system_text, user_template


# Legacy alias
_load_llm_call_3_section_df = _load_llm_call_3_section


def _sanitize_html(html: str) -> str:
    """
    Strip comments, scripts, and excessive whitespace to keep prompts compact.
    """
    html = html or ""
    # remove script tags/HTML comments but preserve repeat markers and inline CSS
    comment_re = re.compile(r"(?is)<!--(?!\s*(BEGIN:BLOCK_REPEAT|END:BLOCK_REPEAT)).*?-->")
    script_re = re.compile(r"(?is)<script\b[^>]*>.*?</script>")
    collapsed = script_re.sub("", comment_re.sub("", html))
    collapsed = re.sub(r"[ \t]{2,}", " ", collapsed)
    collapsed = re.sub(r"\n{3,}", "\n\n", collapsed)
    return collapsed.strip()


def _format_catalog(catalog: Iterable[str]) -> str:
    catalog_list = [str(item).strip() for item in catalog]
    return json.dumps(catalog_list, ensure_ascii=False, indent=2)


def _normalize_schema_payload(schema: Mapping[str, Any] | None) -> Dict[str, Any]:
    base = {
        "scalars": [],
        "row_tokens": [],
        "totals": [],
        "notes": "",
    }
    if not isinstance(schema, Mapping):
        return base

    def _collect(key: str) -> list[str]:
        values = schema.get(key, [])
        if isinstance(values, Iterable) and not isinstance(values, (str, bytes)):
            return [str(item).strip() for item in values if str(item).strip()]
        return []

    base["scalars"] = _collect("scalars")
    base["row_tokens"] = _collect("row_tokens")
    base["totals"] = _collect("totals")

    notes = schema.get("notes")
    if notes is not None:
        base["notes"] = str(notes)
    return base


def _format_schema(schema: Dict[str, Any] | None) -> str:
    normalized = _normalize_schema_payload(schema)
    return json.dumps(normalized, ensure_ascii=False, indent=2, sort_keys=True)


def _row_token_hint(schema: Mapping[str, Any] | None) -> str:
    normalized = _normalize_schema_payload(schema)
    row_tokens = [tok for tok in normalized.get("row_tokens", []) if str(tok).lower().startswith("row_")]
    if not row_tokens:
        return ""

    preview = ", ".join(row_tokens[:8])
    if len(row_tokens) > 8:
        preview += ", ..."

    hint_lines = [
        "ROW TOKEN NAMING",
        "- The HTML template exposes repeating-row placeholders that already include the `row_` prefix.",
        "- When producing the mapping, reference those tokens verbatim (including the prefix and casing).",
        f"- Example row tokens: {preview}",
    ]
    return "\n".join(hint_lines)


def build_llm_call_3_prompt(
    html: str,
    catalog: Iterable[str],
    schema_json: Dict[str, Any] | None = None,
    *,
    rich_catalog_text: str | None = None,
) -> Dict[str, Any]:
    """
    Build the system/user payload for LLM Call 3 (auto-map + constant discovery).

    Uses the DataFrame-mode prompt which forbids SQL expressions and only allows
    simple table.column references in mapping values.
    """
    system_template, user_template = _load_llm_call_3_section()

    if not user_template:
        user_template = system_template
        system_template = (
            "You are a meticulous analyst that performs report auto-mapping and constant inlining. "
            "Follow the subsequent instructions strictly."
        )

    html_block = _sanitize_html(html)
    catalog_block = rich_catalog_text if rich_catalog_text else _format_catalog(catalog)
    schema_block = _format_schema(schema_json)
    row_hint = _row_token_hint(schema_json)

    user_payload = user_template
    for placeholder, value in (
        ("{html_for_llm}", html_block),
        ("{catalog_json}", catalog_block),
        ("{schema_json_if_any}", schema_block),
    ):
        user_payload = user_payload.replace(placeholder, value)

    if row_hint:
        user_payload = f"{user_payload.strip()}\n\n{row_hint}"

    attachments: list[dict[str, Any]] = []
    if "[REFERENCE_PNG_HINT]" not in user_payload:
        attachments.append(
            {
                "type": "text",
                "text": (
                    "[REFERENCE_PNG_HINT]\n"
                    '"A screenshot of the reference PDF was used to create this template; '
                    'treat visible page titles/branding as likely constants."'
                ),
            }
        )

    return {
        "system": system_template.strip(),
        "user": user_payload.strip(),
        "attachments": attachments,
        "version": PROMPT_VERSION,
    }


LLM_CALL_3_5_PROMPT: Dict[str, str] = {
    "system": dedent(
        """\
        You are the Step 3.5 corrections specialist in a report generation pipeline.

        YOUR THREE RESPONSIBILITIES:
        A) Apply every explicit user instruction to the HTML template (text edits, CSS tweaks, structural changes, token modifications). Do not invent changes beyond what the user asks.
        B) Inline constants: Replace any token whose mapping value is "INPUT_SAMPLE" with the literal value from `mapping_context.token_samples`. Copy the string exactly as provided.
        C) Produce a `page_summary` narrative for Step 4 that captures: constants you inlined (with their exact values), key field meanings, notable numeric totals, dates, codes, unresolved tokens, and uncertainties.

        INVARIANTS (must hold unless user explicitly overrides):
        1. Preserve the DOM hierarchy, repeat markers (<!-- BEGIN:BLOCK_REPEAT -->), data-region attributes, and <tbody> row prototypes exactly.
        2. Preserve all remaining dynamic tokens exactly as written ({token}, {{token}}, etc.). Only inline tokens mapped to "INPUT_SAMPLE".
        3. Keep HTML self-contained — no external resources, no <script> tags.

        DATA SOURCES:
        - `mapping_context.mapping`: current binding state. Tokens mapped to "INPUT_SAMPLE" → inline. Tokens mapped to table.column or SQL → leave untouched.
        - `mapping_context.token_samples`: literal strings for every placeholder. Use these exact values when inlining.
        - `mapping_context.sample_tokens` / `mapping_context.inline_tokens`: tokens the user wants double-checked. Report uncertainties about these in page_summary.
        - `user_input`: authoritative instructions for this pass. Follow exactly.
        - Reference PNG (if attached): visual context only.

        OUTPUT — strict JSON, no markdown fences, no extra keys:
        {
          "final_template_html": "<string>",
          "page_summary": "<string>"
        }

        VALIDATION CHECKLIST:
        - Remaining tokens in final_template_html = original tokens minus those explicitly inlined.
        - Repeat markers, <tbody> counts, row prototypes unchanged (unless user asked to modify).
        - No external resources, no scripts, no accidental literal leak of unresolved tokens.
        - page_summary is a detailed narrative (>1 sentence): exact inlined values, important metrics, unresolved fields, uncertainties. No layout/styling details.
        - JSON is valid UTF-8 with properly escaped strings. Only two keys: final_template_html, page_summary.
        """
    ).strip(),
    "user": dedent(
        """\
        The actual payload will be provided as a JSON object with these fields:
        {
          "template_html": "<HTML template with dynamic tokens>",
          "schema": { "scalars": [...], "row_tokens": [...], "totals": [...] },
          "mapping_context": {
            "mapping": { "<token>": "<table.column | INPUT_SAMPLE | UNRESOLVED>" },
            "mapping_override": { "<token>": "INPUT_SAMPLE" },
            "sample_tokens": ["<tokens to double-check>"],
            "token_samples": { "<token>": "<literal value from PDF>" }
          },
          "user_input": "<free-form user instructions>"
        }
        """
    ).strip(),
}


def _build_data_uri(path: Path | None) -> str | None:
    if not path or not path.exists():
        return None
    try:
        encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    except Exception:  # pragma: no cover
        return None
    return f"data:image/png;base64,{encoded}"


def build_llm_call_3_5_prompt(
    template_html: str,
    schema: Mapping[str, Any] | None,
    user_input: str,
    page_png_path: str | None = None,
    mapping_context: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    schema_payload = dict(schema or {})
    payload: Dict[str, Any] = {
        "template_html": template_html,
        "schema": schema_payload,
        "user_input": user_input or "",
    }

    if mapping_context:
        mapping_context_clean = dict(mapping_context)
        payload["mapping_context"] = mapping_context_clean

    data_uri = _build_data_uri(Path(page_png_path) if page_png_path else None)
    payload_json = json.dumps(payload, ensure_ascii=False, indent=2)
    user_content = [
        {
            "type": "text",
            "text": f"USER (JSON payload):\n{payload_json}",
        }
    ]
    if data_uri:
        user_content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": data_uri,
                    "detail": "high",
                },
            }
        )

    messages = [
        {
            "role": "user",
            "content": user_content,
        }
    ]

    return {
        "system": LLM_CALL_3_5_PROMPT["system"],
        "messages": messages,
        "version": PROMPT_VERSION_3_5,
    }


LLM_CALL_4_SYSTEM_PROMPT_DF = dedent(
    """\
    LLM CALL 4 — Contract Builder (DataFrame Mode)
    You build the complete mapping contract for a pandas DataFrame report pipeline. NO SQL ANYWHERE.

    ═══════════════════════════════════════════════════════════════
    CRITICAL: This pipeline uses pandas DataFrames directly.
    NEVER emit SQL expressions, DuckDB functions, CASE/WHEN, SUM(), CONCAT(), or any code.
    All computations use declarative operation objects (see below).
    ═══════════════════════════════════════════════════════════════

    YOUR THREE OUTPUTS:
    1. overview_md — Markdown narrative summarizing the report logic.
    2. step5_requirements — Dataset descriptions, parameter semantics, transformation rules.
    3. contract — The authoritative mapping contract with declarative operations.

    CORE RULES:
    - Use ONLY columns from the CATALOG in "table.column" format. Never invent names.
    - Preserve every dynamic token from the schema exactly.
    - mapping_override is authoritative when provided.
    - key_tokens are required user filters → map as PARAM:<name>.

    MAPPING VALUES — each token must map to exactly one of:
    - "TABLE.COLUMN" (direct column from catalog)
    - "PARAM:name" (parameter passthrough)
    - "UNRESOLVED" (no source found — use sparingly, prefer resolving)

    ROW_COMPUTED — declarative ops for derived row columns. Each value is a dict:
      {"op": "subtract", "left": "<column_or_alias>", "right": "<column_or_alias>"}
      {"op": "add", "left": "<column_or_alias>", "right": "<column_or_alias>"}
      {"op": "multiply", "left": "<column_or_alias>", "right": "<column_or_alias_or_number>"}
      {"op": "divide", "numerator": "<column_or_alias>", "denominator": "<column_or_alias>"}
      {"op": "concat", "columns": ["col_a", "col_b"], "separator": " "}
      {"op": "format_date", "column": "<date_col>", "format": "%d-%m-%Y %H:%M:%S"}
      {"op": "format_number", "column": "<num_col>", "decimals": 2}
    "left", "right", "numerator", "denominator" can be: a column name (string), a numeric literal (number), or a nested op dict.

    TOTALS_MATH — declarative ops for aggregate totals. Each value is a dict:
      {"op": "sum", "column": "<row_token_name>"}
      {"op": "mean", "column": "<row_token_name>"}
      {"op": "count", "column": "<row_token_name>"}
      {"op": "min", "column": "<row_token_name>"}
      {"op": "max", "column": "<row_token_name>"}
      {"op": "divide", "numerator": {"op": "sum", "column": "col_a"}, "denominator": {"op": "sum", "column": "col_b"}}
    The "column" field in totals_math references ROW TOKEN names (the computed row values), not raw table columns.

    TOTALS (totals_mapping) — simple token-to-expression mapping for totals that mirrors the totals_math logic.
    Can be a dict of declarative ops (same format as totals_math) or a simple string reference.

    RESHAPE RULES:
    - Each rule: {"purpose": "≤15 words", "strategy": "UNION_ALL|MELT|NONE", "columns": [{"as": "alias", "from": ["table.col1", "table.col2", ...]}]}
    - "as" is the output column alias used in row tokens. "from" lists the source catalog columns to unpivot.
    - For MELT/UNION_ALL: each "from" array must have the same length across all columns entries.
    - If "from" values are literal constants (not column references), list them as string literals (e.g., ["1", "2", "3"]).

    CONTRACT STRUCTURE:
    - join: non-empty parent_table/parent_key required. If no child table, set child_table = parent_table, child_key = parent_key.
    - order_by.rows AND row_order: both non-empty arrays with identical content. Default ["ROWID"] if no logical ordering.
    - formatters: "percent(2)", "number(2)", "currency(2)", etc. Do NOT put "date()" in formatters for timestamp tokens.
    - unresolved: must be [].
    - header_tokens: copy of tokens.scalars array.
    - row_tokens: copy of tokens.row_tokens array.

    MANDATORY RULES (violations will be auto-corrected by post-processor):
    1. TIMESTAMP FORMATTING: Every token that maps to a timestamp/date column (timestamp_utc, timestamp, created_at, date, datetime) MUST have a row_computed entry:
       {"op": "format_date", "column": "<col>", "format": "%d-%m-%Y %H:%M:%S"}
       Do NOT use formatters "date(...)" for timestamps — always use row_computed.format_date.
    2. NUMERIC FORMATTING: Every token that maps to a numeric measurement column MUST have a formatters entry. Default: "number(2)". Use higher precision only when the domain requires it (e.g., pH sensors → "number(4)").
    3. DATE FILTERS: When date_columns is populated, filters.optional MUST contain:
       "date_from": "TABLE.date_column", "date_to": "TABLE.date_column"
       Never leave filters.optional empty when date_columns exists.
    4. DATE_COLUMNS: If ANY mapped column is a timestamp/date type, date_columns MUST be populated with {"TABLE": "column_name"}.
    5. CONSISTENCY: Use row_computed.format_date for timestamps and formatters for display formatting (number, percent, currency). Never mix — do not put "date()" in formatters for timestamp columns.

    ═══════════════════════════════════════════════════════════════
    INPUT PAYLOAD SHAPE:
    {
      "final_template_html": "<HTML with constants inlined>",
      "page_summary": "<narrative from Step 3.5>",
      "schema": { "scalars": [...], "row_tokens": [...], "totals": [...] },
      "auto_mapping_proposal": { "mapping": {...}, "join": {...}, "unresolved": [...] },
      "mapping_override": { "<token>": "<authoritative mapping>" },
      "user_instructions": "<free-form user guidance>",
      "key_tokens": ["<required filter tokens>"],
      "catalog": ["table.column", ...]
    }

    ═══════════════════════════════════════════════════════════════
    OUTPUT — return ONLY this JSON object, no markdown fences, no commentary:
    {
      "overview_md": "<Markdown: Executive Summary, Token Inventory, Mapping Table, Join & Date Rules, Transformations, Parameters>",
      "step5_requirements": {
        "datasets": {
          "header": {"description": "...", "columns": ["<scalar tokens>"]},
          "rows": {"description": "...", "columns": ["<row tokens>"], "grouping": [...], "ordering": [...]},
          "totals": {"description": "...", "columns": ["<totals tokens>"]}
        },
        "semantics": "<filter vs pass-through explanation>",
        "parameters": {
          "required": [{"name": "...", "type": "date|string"}],
          "optional": [{"name": "...", "type": "string"}]
        },
        "transformations": ["<reshape rules in plain English>"]
      },
      "contract": {
        "tokens": { "scalars": [...], "row_tokens": [...], "totals": [...] },
        "mapping": { "<token>": "<TABLE.COLUMN | PARAM:name | UNRESOLVED>" },
        "unresolved": [],
        "join": { "parent_table": "...", "parent_key": "...", "child_table": "...", "child_key": "..." },
        "date_columns": { "<table>": "<date_column>" },
        "filters": { "optional": { "<name>": "table.column" } },
        "reshape_rules": [
          { "purpose": "...", "strategy": "UNION_ALL|MELT|NONE", "columns": [{"as": "alias", "from": ["table.col1", "..."]}] }
        ],
        "row_computed": { "<token>": {"op": "...", "left": "...", "right": "..."} },
        "totals_math": { "<token>": {"op": "...", "column": "..."} },
        "totals": { "<token>": {"op": "...", "column": "..."} },
        "formatters": { "<token>": "<format spec>" },
        "order_by": { "rows": ["<column ASC|DESC>"] },
        "header_tokens": ["<scalar tokens copy>"],
        "row_tokens": ["<row tokens copy>"],
        "row_order": ["<column ASC|DESC>"],
        "literals": {},
        "notes": "<domain notes>"
      },
      "validation": {
        "unknown_tokens": [],
        "unknown_columns": [],
        "token_coverage": { "scalars_mapped_pct": 100, "row_tokens_mapped_pct": 100, "totals_mapped_pct": 100 }
      }
    }

    SELF-CHECK before responding:
    - NO SQL expressions anywhere (no SUM(), CASE, CONCAT, STRFTIME, etc.).
    - Every schema token appears in contract.mapping.
    - Every column reference exists in the CATALOG.
    - row_computed and totals_math values are ALL declarative op dicts, never strings.
    - order_by.rows and row_order are identical non-empty arrays.
    - join block has all four non-empty string fields.
    - Every reshape rule has a non-empty "purpose".
    - token_coverage is 100%.
    - Every timestamp-mapped token has row_computed.format_date with "%d-%m-%Y %H:%M:%S".
    - Every numeric column token has a formatters entry (e.g., "number(2)").
    - filters.optional has date_from/date_to when date_columns is non-empty.
    - No "date()" entries in formatters for tokens that have row_computed.format_date.
    """
).strip()

LLM_CALL_5_PROMPT: Dict[str, str] = {
    "system": dedent(
        """\
        LLM CALL 5 — Contract Finalizer (DataFrame Mode)
        You finalize the contract from Step 4 for the pandas DataFrame report pipeline. NO SQL.

        ═══════════════════════════════════════════════════════════════
        CRITICAL: NEVER emit SQL expressions, DuckDB functions, or any code.
        All computations use declarative operation objects only.
        ═══════════════════════════════════════════════════════════════

        YOUR JOB:
        1. Copy the Step-4 contract exactly (same tokens, same declarative ops, same ordering).
        2. Validate and fill in any missing optional fields with sensible defaults.
        3. Ensure the contract is complete and ready for the DataFrame pipeline.

        RULES:
        - Treat `step4_output.contract` as authoritative. Do not add, drop, or rename tokens.
        - `mapping` values: only "TABLE.COLUMN", "PARAM:name", or "UNRESOLVED".
        - `row_computed` / `totals_math`: declarative op dicts only:
          {"op": "subtract|add|multiply|divide|sum|mean|count|min|max|concat|format_date|format_number", ...}
        - `totals` (totals_mapping): declarative op dicts mirroring totals_math.
        - Join block: non-empty parent_table/parent_key. If no child table, reuse parent.
        - `order_by.rows` and `row_order`: both non-empty arrays, identical content. Default ["ROWID"].
        - Every reshape rule must have a non-empty "purpose" (≤15 words).
        - `header_tokens`: copy of tokens.scalars. `row_tokens`: copy of tokens.row_tokens.
        - Verify timestamp tokens use row_computed.format_date with "%d-%m-%Y %H:%M:%S" (not formatters "date()").
        - Verify all numeric measurement tokens have formatters entries (e.g., "number(2)").
        - Verify filters.optional has date_from/date_to when date_columns exists.

        OUTPUT — return ONLY this JSON object, no markdown fences, no commentary:
        {
          "contract": {
            "tokens": { "scalars": [...], "row_tokens": [...], "totals": [...] },
            "mapping": { "<token>": "TABLE.COLUMN|PARAM:name|UNRESOLVED" },
            "join": { "parent_table": "...", "parent_key": "...", "child_table": "...", "child_key": "..." },
            "date_columns": { "<table>": "<date_column>" },
            "filters": { "optional": { "<name>": "table.column" } },
            "reshape_rules": [{"purpose": "...", "strategy": "UNION_ALL|MELT|NONE", "columns": [...]}],
            "row_computed": { "<token>": {"op": "...", ...} },
            "totals_math": { "<token>": {"op": "...", ...} },
            "totals": { "<token>": {"op": "...", ...} },
            "formatters": { "<token>": "<format spec>" },
            "order_by": { "rows": ["<column ASC|DESC>"] },
            "header_tokens": [...],
            "row_tokens": [...],
            "row_order": ["<column ASC|DESC>"],
            "literals": {},
            "notes": "..."
          },
          "invalid": false
        }

        SELF-CHECK:
        - NO SQL expressions anywhere.
        - Every token from Step-4 is present in mapping.
        - row_computed and totals_math are ALL declarative op dicts.
        - order_by.rows and row_order are identical non-empty arrays.
        - join block has all four non-empty string fields.
        """
    ).strip(),
    "user": dedent(
        """\
        {
          "final_template_html": "<HTML from Step 3.5>",
          "step4_output": {
            "contract": { /* Step-4 contract object */ },
            "overview_md": "Step-4 overview",
            "step5_requirements": { /* Step-4 requirements */ }
          },
          "key_tokens": ["..."],
          "catalog": ["table.column", "..."]
        }
        """
    ).strip(),
}

# Legacy alias for backwards compatibility
LLM_CALL_5_PROMPT_DF = LLM_CALL_5_PROMPT

PROMPT_LIBRARY: Dict[str, str] = {
    **LLM_CALL_PROMPTS,
    "llm_call_3_5_system": LLM_CALL_3_5_PROMPT["system"],
    "llm_call_3_5_user": LLM_CALL_3_5_PROMPT["user"],
    "llm_call_4_system": LLM_CALL_4_SYSTEM_PROMPT_DF,
    "llm_call_5_system": LLM_CALL_5_PROMPT["system"],
    "llm_call_5_user": LLM_CALL_5_PROMPT["user"],
}

# Legacy alias — SQL prompt removed, DF is the only mode
LLM_CALL_4_SYSTEM_PROMPT = LLM_CALL_4_SYSTEM_PROMPT_DF


def build_llm_call_4_prompt(
    *,
    final_template_html: str,
    page_summary: str,
    schema: Mapping[str, Any] | None,
    auto_mapping_proposal: Mapping[str, Any],
    mapping_override: Mapping[str, Any] | None,
    user_instructions: str,
    catalog: Iterable[str],
    dialect_hint: str | None = None,
    key_tokens: Iterable[str] | None = None,
) -> Dict[str, Any]:
    """
    Build the payload for LLM Call 4 (contract builder + overview).
    Always uses DataFrame mode — no SQL expressions in output.
    """
    system_text = LLM_CALL_4_SYSTEM_PROMPT_DF
    key_tokens_list: list[str] = []
    if key_tokens:
        seen: set[str] = set()
        for token in key_tokens:
            text = str(token or "").strip()
            if not text or text in seen:
                continue
            seen.add(text)
            key_tokens_list.append(text)
    payload: Dict[str, Any] = {
        "final_template_html": final_template_html,
        "page_summary": page_summary,
        "schema": dict(schema or {}),
        "auto_mapping_proposal": dict(auto_mapping_proposal or {}),
        "mapping_override": dict(mapping_override or {}),
        "user_instructions": user_instructions or "",
        "catalog": [str(item) for item in catalog],
    }
    if key_tokens_list:
        payload["key_tokens"] = key_tokens_list
    if dialect_hint is not None:
        payload["dialect_hint"] = str(dialect_hint)

    payload_json = json.dumps(payload, ensure_ascii=False, indent=2)
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": payload_json,
                }
            ],
        }
    ]

    return {
        "system": system_text,
        "messages": messages,
        "version": PROMPT_VERSION_4,
    }


@lru_cache(maxsize=1)
def get_prompt_generator_assets() -> Dict[str, str]:
    """Return the system and user template strings for LLM CALL 5 (DataFrame mode)."""
    return dict(LLM_CALL_5_PROMPT)


# Legacy alias
get_prompt_generator_assets_df = get_prompt_generator_assets


__all__ = [
    "build_llm_call_3_prompt",
    "build_llm_call_3_5_prompt",
    "PROMPT_VERSION",
    "PROMPT_VERSION_3_5",
    "PROMPT_VERSION_4",
    "PROMPT_VERSION_DF",
    "PROMPT_VERSION_4_DF",
    "build_llm_call_4_prompt",
    "LLM_CALL_PROMPTS",
    "PROMPT_LIBRARY",
    "get_prompt_generator_assets",
    "get_prompt_generator_assets_df",
]
