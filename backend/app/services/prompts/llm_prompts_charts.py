# mypy: ignore-errors
from __future__ import annotations

import json
from textwrap import dedent
from typing import Any, Iterable, Mapping, Sequence

CHART_SUGGEST_PROMPT_VERSION = "chart_suggestions_v1"

# Small catalog of reusable chart templates that the LLM can reference via chartTemplateId.
CHART_TEMPLATE_CATALOG: dict[str, dict[str, Any]] = {
    "time_series_basic": {
        "id": "time_series_basic",
        "description": "Trend over an ordered index (typically time or batch_index) for one or two numeric metrics.",
        "recommended_chart_type": "line",
        "recommended_use": "Use when xField is an ordered index such as time or batch_index and yFields are numeric measures.",
        "recharts": {
            "component": "LineChart",
            "props": {
                "margin": {"top": 8, "right": 16, "bottom": 24, "left": 0},
                "cartesianGrid": {"strokeDasharray": "3 3"},
            },
        },
    },
    "top_n_categories": {
        "id": "top_n_categories",
        "description": "Ranked comparison of the largest categories by a numeric metric (e.g. rows).",
        "recommended_chart_type": "bar",
        "recommended_use": "Use when xField is a categorical label and yFields contains a single numeric metric you want to rank by size.",
        "recharts": {
            "component": "BarChart",
            "props": {
                "layout": "vertical",
                "margin": {"top": 8, "right": 16, "bottom": 16, "left": 0},
            },
        },
    },
    "distribution_histogram": {
        "id": "distribution_histogram",
        "description": "Histogram-style distribution of a numeric metric, approximated with a bar chart.",
        "recommended_chart_type": "bar",
        "recommended_use": "Use when xField is a numeric metric and you conceptually bucket values into ranges to show their distribution.",
        "recharts": {
            "component": "BarChart",
            "props": {
                "margin": {"top": 8, "right": 16, "bottom": 24, "left": 0},
                "cartesianGrid": {"strokeDasharray": "3 3"},
            },
        },
    },
}


def _to_pretty_json(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=isinstance(value, Mapping))
    except Exception:
        return json.dumps(str(value), ensure_ascii=False)


CHART_SUGGEST_PROMPT_TEMPLATE = dedent(
    """
    You are an analytics assistant helping a user explore report batch discovery data in NeuraReport.

    DATA CONTEXT
    - Each row in the dataset represents a single batch for the selected template and date range.
    - Available fields are described in FIELD_CATALOG_JSON below. You MUST treat those field names as the only columns
      you can reference in charts (for xField, yFields, and groupField).
    - DATA_STATS_JSON provides basic statistics over the dataset (counts, totals, min/max/avg) so you can prioritise
      interesting views.
    - KEY_FILTERS_JSON describes any key token filters that have been applied.

    CHART SPEC CONTRACT
    You must return a single JSON object with this exact shape:
      {{
        "charts": [
          {{
            "id": "short_unique_id",
            "type": "bar" | "line" | "pie" | "scatter",
            "xField": "<field name from FIELD_CATALOG_JSON>",
            "yFields": ["<field name>", "..."],
            "groupField": "<field name>" | null,
            "aggregation": "sum" | "avg" | "count" | "none" | null,
            "chartTemplateId": "time_series_basic" | "top_n_categories" | "distribution_histogram" | null,
            "title": "Concise chart title",
            "description": "Short explanation of what the chart shows and why it is useful"
          }},
          ...
        ]
      }}

    RULES
    - Propose between 2 and 5 charts that best answer the user's question while remaining faithful to the available fields.
    - Prefer highlighting metrics that show strong variation (e.g., largest numeric totals, widest min/max range) using DATA_STATS_JSON.
    - Use only field names that appear in FIELD_CATALOG_JSON for xField, yFields, and groupField.
    - Prefer using chartTemplateId values as follows when they fit:
        * "time_series_basic": xField is an ordered index (e.g. "batch_index") and yFields are numeric metrics such as "rows".
        * "top_n_categories": xField is categorical (e.g. "batch_id") and yFields contains a single numeric metric to compare.
        * "distribution_histogram": xField is a numeric metric and you conceptually bucket values into ranges to show distribution.
      It is still valid to omit chartTemplateId for free-form charts.
    - For "pie" charts, use xField as the category label and yFields[0] as the numeric value.
    - For "scatter" charts, use xField as the numeric/ordered axis and yFields[0] as the numeric dependent variable.
    - If the question references measures that are not present in FIELD_CATALOG_JSON, fall back to useful, honest charts
      based on the available fields (e.g., largest batches by rows, relationship between parent and child rows, distributions).
    - Do NOT include any commentary, markdown code fences, or extra top-level keys; return only the JSON object.

    TEMPLATE_ID: {template_id}
    TEMPLATE_KIND: {template_kind}
    DATE_RANGE:
      start_date: {start_date}
      end_date: {end_date}

    KEY_FILTERS_JSON:
    {key_values_json}

    FIELD_CATALOG_JSON:
    {field_catalog_json}

    DATA_STATS_JSON:
    {data_stats_json}

    CHART_TEMPLATE_CATALOG_JSON:
    {template_catalog_json}

    USER_QUESTION:
    {user_question}
    """
).strip()


def build_chart_suggestions_prompt(
    *,
    template_id: str,
    kind: str,
    start_date: str,
    end_date: str,
    key_values: Mapping[str, Any] | None,
    field_catalog: Iterable[Mapping[str, Any]] | Sequence[Mapping[str, Any]],
    data_stats: Mapping[str, Any] | None = None,
    question: str | None = None,
) -> str:
    key_values_json = _to_pretty_json(key_values or {})
    field_catalog_json = _to_pretty_json(list(field_catalog or []))
    data_stats_json = _to_pretty_json(data_stats or {})
    template_catalog_json = _to_pretty_json(CHART_TEMPLATE_CATALOG)
    user_question = (question or "").strip() or "Suggest several informative charts using the available fields."

    prompt = CHART_SUGGEST_PROMPT_TEMPLATE
    prompt = prompt.replace("{template_id}", template_id)
    prompt = prompt.replace("{template_kind}", (kind or "pdf").lower())
    prompt = prompt.replace("{start_date}", start_date)
    prompt = prompt.replace("{end_date}", end_date)
    prompt = prompt.replace("{key_values_json}", key_values_json)
    prompt = prompt.replace("{field_catalog_json}", field_catalog_json)
    prompt = prompt.replace("{data_stats_json}", data_stats_json)
    prompt = prompt.replace("{template_catalog_json}", template_catalog_json)
    prompt = prompt.replace("{user_question}", user_question)
    return prompt
