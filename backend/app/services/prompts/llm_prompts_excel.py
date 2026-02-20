# mypy: ignore-errors
from __future__ import annotations

import json
from functools import lru_cache
from textwrap import dedent
from typing import Any, Dict, Iterable, Mapping

from . import llm_prompts as _pdf_prompts

EXCEL_PROMPT_VERSION = "excel_llm_call_3_v1"
EXCEL_PROMPT_VERSION_3_5 = "excel_llm_call_3_5_v1"
EXCEL_PROMPT_VERSION_4 = "excel_llm_call_4_v2"
EXCEL_PROMPT_VERSION_5 = "excel_llm_call_5_v1"

_INPUT_MARKER = "[INPUTS]"

_sanitize_html = _pdf_prompts._sanitize_html
_format_catalog = _pdf_prompts._format_catalog
_format_schema = _pdf_prompts._format_schema

EXCEL_LLM_CALL_1_PROMPT = dedent(
    """
Produce a COMPLETE, self-contained HTML document (<!DOCTYPE html> ...) with inline <style>. Treat the provided Excel
worksheet prototype HTML (tokens already annotated) as the blueprint and recreate the worksheet layout as a
print-ready template.

PLACEHOLDER & SCHEMA RULES
- Placeholders must use single braces: {token}. Never invent tokens beyond those in SCHEMA_JSON (if provided) or the
  supplied row_* tokens present in the prototype. Re-use them verbatim.
- Emit exactly ONE prototype <tbody><tr>...</tr></tbody> row for repeating data. Do not duplicate multiple data rows.
- Totals/footers that remain dynamic should use tokens; static captions (titles, notes) must remain literal strings.
- Keep casing/spelling from the worksheet prototype for visible labels.

STRUCTURE & CSS
- Use a semantic table for the data grid (table-layout: fixed, border-collapse: collapse). Apply borders only where the
  worksheet shows lines (default to 1px solid #999 for visible lines). Align numeric columns to the right.
- Provide minimal wrappers with stable IDs for major regions (#report-header, #data-table, #report-totals, etc.).
- Include @page { size: A4; margin: sensible } so the HTML prints like a sheet export.
- If the layout implies repeating batch blocks outside the table, wrap the prototype inside:
    <!-- BEGIN:BLOCK_REPEAT batches -->
    <section class="batch-block">...</section>
    <!-- END:BLOCK_REPEAT -->
  Keep headers/footers outside those markers.

PROTOTYPE NOTES
- The supplied HTML already encodes preface rows, column order, and row_* tokens. Preserve that structure while
  improving styling/printability.

OUTPUT FORMAT
1) RAW HTML between these markers:
   <!--BEGIN_HTML-->
   ... full html ...
   <!--END_HTML-->
2) Matching SCHEMA JSON (scalars, row_tokens, totals, notes) between:
   <!--BEGIN_SCHEMA_JSON-->
   { ... }
   <!--END_SCHEMA_JSON-->
Schema tokens must align 1:1 with placeholders in your HTML.

Return ONLY those markers—no markdown fences or commentary.

[INPUTS]
SHEET_SNAPSHOT_JSON:
{sheet_snapshot}

SHEET_PROTOTYPE_HTML:
{sheet_html}

SCHEMA (may be empty):
{schema_str}
"""
).strip()


def build_excel_llm_call_1_prompt(sheet_snapshot: str, sheet_html: str, schema_str: str) -> str:
    snapshot_payload = sheet_snapshot.strip() or "{}"
    sheet_html_payload = sheet_html.strip() or "<html></html>"
    schema_payload = schema_str.strip() or "{}"
    return (
        EXCEL_LLM_CALL_1_PROMPT.replace("{sheet_snapshot}", snapshot_payload)
        .replace("{sheet_html}", sheet_html_payload)
        .replace("{schema_str}", schema_payload)
    )

_EXCEL_CALL3_PROMPT_SECTION = dedent(
    """
You are a meticulous report auto-mapping analyst. You are given the FULL HTML of an Excel-rendered worksheet template and a DB CATALOG.

YOUR TWO TASKS:
A) AUTO-MAPPING — Map every placeholder token in the HTML to its data source from the CATALOG.
B) CONSTANT DISCOVERY — Identify tokens whose values are static and record their literal values.

MAPPING RULES — CRITICAL: NO SQL EXPRESSIONS
1. Output ONLY simple "table.column" references from the CATALOG. NEVER output SQL expressions, functions, or any code.
2. Every mapping value must be ONE of:
   a) A catalog column in exact "table.column" format.
   b) A parameter passthrough in "params.param_name" format.
   c) The literal string "To Be Selected..." for date-range and page/filter tokens.
   d) The literal string "UNRESOLVED" when no clear single-column source exists.
3. If a token requires combining, formatting, or computing from multiple columns, set mapping to "UNRESOLVED" and describe the operation in meta.hints.
4. Never invent table or column names. Never emit legacy wrappers (DERIVED:, TABLE_COLUMNS[...], COLUMN_EXP[...]).

HEADER KEYING
- If a <th> has data-label, use that value (lowercase_snake_case) as the mapping key.

FUZZY MATCHING
- Match tokens to catalog columns considering common abbreviations:
  * "qty" ↔ "quantity", "amt" ↔ "amount", "wt" ↔ "weight", "pct" ↔ "percent"

AGGREGATE / MULTI-COLUMN HEADERS
- Set mapping to UNRESOLVED and record in meta.hints:
  {{"op": "SUM", "over": ["table.col1", "table.col2", ...]}}

CONSTANT PLACEHOLDERS
- Report ONLY tokens that are truly constant across ALL runs.
- NEVER mark as constant: dates, row values, totals, page numbers.
- Remove constant tokens from "mapping" but keep them in "token_samples".

TOKEN SNAPSHOT
- Emit a "token_samples" dict listing EVERY placeholder token. Use "NOT_VISIBLE" as fallback.

INPUTS
[FULL_HTML]
{html_for_llm}
[CATALOG]
{catalog_json}
Optional:
[SCHEMA_JSON]
{schema_json_if_any}
[REFERENCE_PNG_HINT]
"A screenshot of the Excel worksheet was used to create this template; treat visible sheet titles/branding as likely constants."

OUTPUT — return ONLY this JSON object, no markdown, no commentary:
{{
  "mapping": {{
    "<token>": "<table.column | params.param_name | To Be Selected... | UNRESOLVED>"
  }},
  "token_samples": {{
    "<token>": "<literal string>"
  }},
  "meta": {{
    "unresolved": ["<token>"],
    "hints": {{
      "<token>": {{ "op": "SUM", "over": ["table.col1", "table.col2"] }}
    }}
  }}
}}

VALIDATION: Every mapping value must be a simple "table.column", "params.*", "To Be Selected...", or "UNRESOLVED". NO SQL.
"""
).strip()


@lru_cache(maxsize=1)
def _load_excel_llm_call_3_section() -> tuple[str, str]:
    section = _EXCEL_CALL3_PROMPT_SECTION
    if _INPUT_MARKER in section:
        system, remainder = section.split(_INPUT_MARKER, 1)
        system_text = system.strip()
        user_template = f"{_INPUT_MARKER}{remainder}".strip()
    else:
        system_text = section
        user_template = ""
    return system_text, user_template


def build_excel_llm_call_3_prompt(
    html: str,
    catalog: Iterable[str],
    schema_json: Dict[str, Any] | None = None,
    *,
    sample_data: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    system_template, user_template = _load_excel_llm_call_3_section()
    if not user_template:
        user_template = system_template
        system_template = (
            "You are the Excel auto-mapping analyst. Follow the subsequent instructions exactly and return JSON only."
        )

    html_block = _sanitize_html(html)
    catalog_block = _format_catalog(catalog)
    schema_block = _format_schema(schema_json)
    sample_block = json.dumps(sample_data, ensure_ascii=False, indent=2) if sample_data else ""

    user_payload = user_template
    for placeholder, value in (
        ("{html_for_llm}", html_block),
        ("{catalog_json}", catalog_block),
        ("{schema_json_if_any}", schema_block),
        ("{sample_row_json_if_any}", sample_block),
    ):
        user_payload = user_payload.replace(placeholder, value)

    return {
        "system": system_template.strip(),
        "user": user_payload.strip(),
        "attachments": [],
        "version": EXCEL_PROMPT_VERSION,
    }


EXCEL_LLM_CALL_3_5_PROMPT: Dict[str, str] = {
    "system": dedent(
        """\
        You are the Step 3.5 corrections specialist.
        Your responsibilities:
        A) Apply every explicit user instruction to the HTML template. Text edits, structural tweaks, CSS adjustments, and token changes are all allowed when the user asks. Do not invent changes or perform a wholesale redesign unless the user requests it.
        B) Inline any token whose mapping (or explicit user instruction) marks it as a constant (e.g., mapping value "INPUT_SAMPLE"). Use the literals provided in `mapping_context.token_samples` whenever available—copy the string exactly.
        C) Produce a `page_summary` that captures the page's business/data content for Step 4: list the constants you inlined, key field values, notable numeric totals, dates, codes, unresolved tokens, and uncertainties. Do not rehash layout, typography, or other presentation details unless they directly affect data interpretation.

        Core invariants (must hold unless a user instruction explicitly overrides them):
        1) Preserve the DOM hierarchy, repeat markers, data-region attributes, and row prototypes; only adjust them when the user explicitly says so.
        2) Preserve all remaining dynamic tokens exactly (examples: "{token}", "{{ token }}", "<span id='tok-x'>{{token}}</span>"). Only inline tokens you were instructed to convert to constants.
        3) Keep the HTML self-contained (no external resources or <script> tags). Maintain semantic structure.

        Hints:
        - The `mapping_context.mapping` object reflects the latest binding state after Step 3 and any overrides. Tokens mapped to "INPUT_SAMPLE" must be inlined; leave tokens mapped to DuckDB SQL expressions or table columns untouched unless instructed otherwise.
        - The `mapping_context.token_samples` dictionary lists the literal strings extracted in Step 3 for every placeholder. Inline tokens using these values exactly.
        - `mapping_context.sample_tokens` / `mapping_context.inline_tokens` highlight placeholders the user wants to double-check; use these cues when reporting lingering uncertainties in the page summary.
        - When provided, `reference_worksheet_html` contains a data-only rendering of the worksheet used to derive the template. Use it only to confirm literal strings; do not re-map tokens based on it.
        - `user_input` contains the authoritative instructions for this pass. Follow it exactly.

        Output (strict JSON, no markdown fences, no extra keys):
        {
          "final_template_html": "<string>",  // template after applying user instructions and inlining required constants
          "page_summary": "<string>"          // thorough prose description of the worksheet; must be non-empty
        }

        Validation checklist before responding:
        - Tokens remaining in "final_template_html" match the original tokens minus those explicitly inlined as constants.
        - Repeat markers, <tbody> counts, row prototypes, and data-region attributes are unchanged unless the user asked to modify them.
        - HTML stays free of external resources/scripts and contains no accidental literal leak of unresolved token data.
        - "page_summary" is a detailed narrative (>1 sentence) that reports the exact values you inlined (including any best-guess readings), important metrics, unresolved fields, and uncertainties, without digressing into layout or styling trivia.
        - JSON is valid (UTF-8), strings escaped properly, and only the two required keys are present.




        """
    ).strip(),
    "user": "USER (JSON payload):\n{payload}",
}


def build_excel_llm_call_3_5_prompt(
    *,
    template_html: str,
    schema: Mapping[str, Any] | None,
    user_input: str,
    page_png_path: str | None = None,
    reference_worksheet_html: str | None = None,
    mapping_context: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    schema_payload = dict(schema or {})
    payload: Dict[str, Any] = {
        "template_html": template_html,
        "schema": schema_payload,
        "user_input": user_input or "",
    }
    if mapping_context:
        payload["mapping_context"] = dict(mapping_context)
    if isinstance(reference_worksheet_html, str) and reference_worksheet_html.strip():
        payload["reference_worksheet_html"] = reference_worksheet_html

    # Prefer full worksheet HTML when provided; otherwise, attach optional page image as a fallback.
    from pathlib import Path as _Path  # local import to avoid cycles

    try:
        _build_data_uri = _pdf_prompts._build_data_uri  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover

        def _null_build_data_uri(_p):  # type: ignore
            return None

        _build_data_uri = _null_build_data_uri  # type: ignore

    data_uri = None if reference_worksheet_html else _build_data_uri(_Path(page_png_path) if page_png_path else None)
    payload_json = json.dumps(payload, ensure_ascii=False, indent=2)
    user_content = [{"type": "text", "text": EXCEL_LLM_CALL_3_5_PROMPT["user"].format(payload=payload_json)}]
    if data_uri:
        user_content.append({"type": "image_url", "image_url": {"url": data_uri, "detail": "high"}})

    messages = [{"role": "user", "content": user_content}]

    return {
        "system": EXCEL_LLM_CALL_3_5_PROMPT["system"],
        "messages": messages,
        "version": EXCEL_PROMPT_VERSION_3_5,
    }


EXCEL_LLM_CALL_4_SYSTEM_PROMPT = dedent(
    """\
    LLM CALL 4 — Contract Builder (Excel, DataFrame Mode)
    You build the complete mapping contract for an Excel worksheet report using a pandas DataFrame pipeline. NO SQL ANYWHERE.

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
    - formatters: "percent(2)", "date(YYYY-MM-DD)", "number(2)", etc.
    - unresolved: must be [].
    - header_tokens: copy of tokens.scalars array.
    - row_tokens: copy of tokens.row_tokens array.

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
    """
).strip()


def build_excel_llm_call_4_prompt(
    *,
    final_template_html: str,
    page_summary: str,
    schema: Mapping[str, Any] | None,
    auto_mapping_proposal: Mapping[str, Any],
    mapping_override: Mapping[str, Any] | None,
    user_instructions: str,
    catalog: Iterable[str],
    key_tokens: Iterable[str] | None = None,
    dialect_hint: str | None = None,  # kept for call-site compat, ignored
) -> Dict[str, Any]:
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
        "system": EXCEL_LLM_CALL_4_SYSTEM_PROMPT,
        "messages": messages,
        "version": EXCEL_PROMPT_VERSION_4,
    }


# ------------------------- LLM CALL 5 (Excel) -------------------------
EXCEL_LLM_CALL_5_PROMPT = {
    "system": dedent(
        """\
        LLM CALL 5 — Contract Finalizer (Excel, DataFrame Mode)
        You finalize the contract from Step 4 for the pandas DataFrame Excel report pipeline. NO SQL.

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
          "key_tokens": ["param_a", "param_b"]
        }
        """
    ).strip(),
}


@lru_cache(maxsize=1)
def get_excel_prompt_generator_assets() -> Dict[str, str]:
    """Return the Excel-specific system/user templates for LLM CALL 5."""
    return dict(EXCEL_LLM_CALL_5_PROMPT)


__all__ = [
    "EXCEL_PROMPT_VERSION",
    "EXCEL_PROMPT_VERSION_3_5",
    "EXCEL_PROMPT_VERSION_4",
    "EXCEL_PROMPT_VERSION_5",
    "build_excel_llm_call_1_prompt",
    "build_excel_llm_call_3_prompt",
    "build_excel_llm_call_3_5_prompt",
    "build_excel_llm_call_4_prompt",
    "get_excel_prompt_generator_assets",
]
