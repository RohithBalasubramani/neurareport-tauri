# mypy: ignore-errors
"""LLM prompts for document analysis and data extraction."""
from __future__ import annotations

import json
import logging
import re
from typing import Any

logger = logging.getLogger("neura.prompts.analysis")

DOCUMENT_ANALYSIS_PROMPT = """You are a data extraction specialist analyzing documents for NeuraReport.

DOCUMENT CONTEXT:
- Document type: {document_type}
- File name: {file_name}
- Pages/Sheets: {page_count}

EXTRACTED CONTENT:
{extracted_content}

TASK:
Extract all meaningful data from this document and return a structured JSON response.

OUTPUT FORMAT (return ONLY valid JSON, no markdown or commentary):
{{
  "summary": "Brief 1-2 sentence description of document contents",
  "tables": [
    {{
      "id": "table_1",
      "title": "Descriptive name for this table",
      "headers": ["Column1", "Column2", "Column3"],
      "rows": [
        ["value1", "value2", "value3"],
        ["value4", "value5", "value6"]
      ],
      "data_types": ["text", "numeric", "date"]
    }}
  ],
  "key_metrics": [
    {{
      "name": "metric_name",
      "value": 123.45,
      "unit": "USD" | "%" | "units" | null,
      "context": "Where this value appears or what it represents"
    }}
  ],
  "time_series_candidates": [
    {{
      "date_column": "column_name_with_dates",
      "value_columns": ["numeric_col1", "numeric_col2"],
      "frequency": "daily" | "weekly" | "monthly" | "yearly" | null,
      "table_id": "table_1"
    }}
  ],
  "chart_recommendations": [
    {{
      "type": "line" | "bar" | "pie" | "scatter",
      "title": "Suggested chart title",
      "x_field": "field_for_x_axis",
      "y_fields": ["field1", "field2"],
      "rationale": "Brief explanation of why this chart is useful"
    }}
  ]
}}

RULES:
1. Extract ALL tables from the document, even small ones
2. Identify numeric columns vs text/categorical columns
3. Detect date/time patterns for time series analysis
4. Suggest meaningful chart visualizations based on the data
5. Preserve original precision for numeric values
6. Use "numeric" for data_types when column contains numbers
7. Use "date" or "datetime" for date columns
8. Use "text" or "category" for text/categorical columns
9. Return ONLY valid JSON - no markdown code fences, no explanatory text
"""

CHART_SUGGESTION_PROMPT = """Based on the extracted data below, suggest the best visualizations.

DATA SUMMARY:
{data_summary}

FIELD CATALOG:
{field_catalog}

USER QUESTION (if provided):
{user_question}

Suggest 2-5 charts that would best visualize this data. Focus on:
- Time series trends if date fields exist
- Comparisons between categories
- Distributions of numeric values
- Relationships between numeric fields

Return ONLY valid JSON in this format:
{{
  "charts": [
    {{
      "id": "chart_1",
      "type": "line" | "bar" | "pie" | "scatter",
      "title": "Chart title",
      "xField": "field_name_for_x",
      "yFields": ["field1", "field2"],
      "groupField": "optional_grouping_field" | null,
      "aggregation": "sum" | "avg" | "count" | "none" | null,
      "description": "What insight this chart provides"
    }}
  ]
}}
"""


def strip_code_fences(text: str) -> str:
    """Remove markdown code fences from LLM output."""
    if not text:
        return ""
    text = text.strip()

    # Use regex to handle various code fence formats
    # Matches: ```json, ```JSON, ```js, ``` at start
    text = re.sub(r'^```(?:json|JSON|js)?\s*\n?', '', text)
    # Matches: ``` at end
    text = re.sub(r'\n?```\s*$', '', text)

    return text.strip()


def _extract_json_object(text: str) -> str | None:
    """
    Extract the first complete JSON object from text.
    Uses bracket counting to find matching braces.
    """
    if not text:
        return None

    # Find the first opening brace
    start = text.find('{')
    if start == -1:
        return None

    # Count braces to find matching close
    depth = 0
    in_string = False
    escape_next = False

    for i, char in enumerate(text[start:], start):
        if escape_next:
            escape_next = False
            continue

        if char == '\\' and in_string:
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]

    # If we get here, braces are unbalanced - try the greedy approach as fallback
    logger.warning("JSON extraction: unbalanced braces, attempting recovery")
    return None


def _try_repair_json(text: str) -> dict[str, Any] | None:
    """Attempt to repair common JSON issues from LLM output."""
    if not text:
        return None

    working = text

    # Common LLM JSON issues
    repairs = [
        # Trailing commas before closing brackets
        (r',\s*([\]}])', r'\1'),
        # Single quotes instead of double
        (r"'([^']*)':", r'"\1":'),
        # Missing quotes around keys
        (r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3'),
        # JavaScript-style comments
        (r'//[^\n]*\n', '\n'),
        (r'/\*[\s\S]*?\*/', ''),
    ]

    for pattern, replacement in repairs:
        working = re.sub(pattern, replacement, working)

    try:
        return json.loads(working)
    except json.JSONDecodeError:
        return None


def parse_analysis_response(raw_response: str) -> dict[str, Any]:
    """Parse LLM response into structured analysis data."""
    default_response = {
        "summary": "",
        "tables": [],
        "key_metrics": [],
        "time_series_candidates": [],
        "chart_recommendations": [],
    }

    if not raw_response:
        return default_response

    cleaned = strip_code_fences(raw_response)

    # Try direct parse first
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return {
                "summary": data.get("summary", ""),
                "tables": data.get("tables", []),
                "key_metrics": data.get("key_metrics", []),
                "time_series_candidates": data.get("time_series_candidates", []),
                "chart_recommendations": data.get("chart_recommendations", []),
            }
    except json.JSONDecodeError:
        pass

    # Try to extract JSON object using bracket counting
    json_str = _extract_json_object(cleaned)
    if json_str:
        try:
            data = json.loads(json_str)
            if isinstance(data, dict):
                return {
                    "summary": data.get("summary", ""),
                    "tables": data.get("tables", []),
                    "key_metrics": data.get("key_metrics", []),
                    "time_series_candidates": data.get("time_series_candidates", []),
                    "chart_recommendations": data.get("chart_recommendations", []),
                }
        except json.JSONDecodeError:
            pass

    # Try JSON repair
    repaired = _try_repair_json(cleaned)
    if repaired:
        return {
            "summary": repaired.get("summary", ""),
            "tables": repaired.get("tables", []),
            "key_metrics": repaired.get("key_metrics", []),
            "time_series_candidates": repaired.get("time_series_candidates", []),
            "chart_recommendations": repaired.get("chart_recommendations", []),
        }

    logger.warning("Failed to parse LLM analysis response as JSON")
    return default_response


def build_analysis_prompt(
    document_type: str,
    file_name: str,
    page_count: int,
    extracted_content: str,
) -> str:
    """Build the document analysis prompt."""
    return DOCUMENT_ANALYSIS_PROMPT.format(
        document_type=document_type,
        file_name=file_name,
        page_count=page_count,
        extracted_content=extracted_content,
    )


def build_chart_suggestion_prompt(
    data_summary: str,
    field_catalog: str,
    user_question: str | None = None,
) -> str:
    """Build the chart suggestion prompt."""
    return CHART_SUGGESTION_PROMPT.format(
        data_summary=data_summary,
        field_catalog=field_catalog,
        user_question=user_question or "No specific question provided - suggest generally useful charts.",
    )


def infer_data_type(values: list[Any]) -> str:
    """
    Infer the data type from a list of sample values.
    Requires 70%+ matches for numeric/datetime classification.
    """
    if not values:
        return "text"

    date_patterns = [
        r"^\d{4}-\d{2}-\d{2}",  # ISO format: 2024-01-15
        r"^\d{2}/\d{2}/\d{4}",  # US format: 01/15/2024
        r"^\d{2}-\d{2}-\d{4}",  # EU format: 15-01-2024
        r"^\d{1,2}/\d{1,2}/\d{2,4}",  # Flexible: 1/5/24
        r"^\d{4}/\d{2}/\d{2}",  # YYYY/MM/DD
    ]

    numeric_count = 0
    date_count = 0
    total_valid = 0

    for val in values[:30]:  # Sample up to 30 values
        if val is None:
            continue
        str_val = str(val).strip()
        if not str_val:
            continue

        total_valid += 1

        # Check for date patterns
        is_date = False
        for pattern in date_patterns:
            if re.match(pattern, str_val):
                date_count += 1
                is_date = True
                break

        if is_date:
            continue

        # Check for numeric values
        try:
            # Handle common currency/percentage formats
            cleaned = str_val.replace(",", "").replace("$", "").replace("€", "").replace("£", "")
            cleaned = cleaned.replace("%", "").replace(" ", "").strip()
            if cleaned:
                float(cleaned)
                numeric_count += 1
        except (ValueError, TypeError):
            pass

    if total_valid == 0:
        return "text"

    # Require 70%+ matches for type classification
    date_ratio = date_count / total_valid
    numeric_ratio = numeric_count / total_valid

    if date_ratio >= 0.7:
        return "datetime"
    if numeric_ratio >= 0.7:
        return "numeric"

    return "text"


__all__ = [
    "DOCUMENT_ANALYSIS_PROMPT",
    "CHART_SUGGESTION_PROMPT",
    "strip_code_fences",
    "parse_analysis_response",
    "build_analysis_prompt",
    "build_chart_suggestion_prompt",
    "infer_data_type",
]
