from __future__ import annotations

import json
from typing import Any, Callable, Mapping, Optional, Sequence

from fastapi import HTTPException

from backend.app.services.prompts.llm_prompts_charts import CHART_TEMPLATE_CATALOG
from backend.app.repositories.state import state_store
from backend.app.schemas.generate.charts import ChartSpec, ChartSuggestPayload, ChartSuggestResponse

VALID_CHART_TYPES = {"bar", "line", "pie", "scatter"}
VALID_AGGREGATIONS = {"sum", "avg", "count", "none"}
NUMERIC_TYPES = {"number", "numeric", "float", "int", "integer", "decimal"}
DATETIME_TYPES = {"datetime", "date", "timestamp", "time"}
CATEGORICAL_TYPES = {"string", "category", "categorical", "text"}


def _field_category(raw_type: Any) -> str:
    normalized = str(raw_type or "").strip().lower()
    if normalized in NUMERIC_TYPES:
        return "numeric"
    if normalized in DATETIME_TYPES:
        return "datetime"
    return "categorical"


def _build_field_lookup(field_catalog: Sequence[Mapping[str, Any]] | None) -> dict[str, tuple[str, str]]:
    lookup: dict[str, tuple[str, str]] = {}
    for field in field_catalog or []:
        if not isinstance(field, Mapping):
            continue
        name = str(field.get("name") or "").strip()
        if not name:
            continue
        field_type = str(field.get("type") or "").strip().lower() or "string"
        lookup[name.lower()] = (name, field_type)
    return lookup


def _normalize_chart_type(raw: Any) -> str | None:
    text = str(raw or "").strip().lower()
    if not text:
        return None
    alias_map = {
        "barchart": "bar",
        "bar chart": "bar",
        "column": "bar",
        "columnchart": "bar",
        "linechart": "line",
        "line chart": "line",
        "piechart": "pie",
        "scatterplot": "scatter",
        "scatter plot": "scatter",
    }
    candidates = {
        text,
        text.replace("_", " "),
        text.replace("-", " "),
        text.replace("chart", "").strip(),
        text.replace("chart", "").replace("_", " ").replace("-", " ").strip(),
    }
    for candidate in candidates:
        candidate_clean = candidate.replace(" ", "")
        if candidate in VALID_CHART_TYPES:
            return candidate
        if candidate_clean in VALID_CHART_TYPES:
            return candidate_clean
        if candidate_clean in alias_map:
            return alias_map[candidate_clean]
    return None


def _normalize_aggregation(raw: Any) -> str | None:
    if raw is None:
        return None
    text = str(raw).strip().lower()
    if not text:
        return None
    return text if text in VALID_AGGREGATIONS else None


def _normalize_field_name(raw: Any, field_lookup: Mapping[str, tuple[str, str]]) -> tuple[str | None, str | None]:
    text = str(raw or "").strip()
    if not text:
        return None, None
    match = field_lookup.get(text.lower())
    if not match:
        return None, None
    return match


def _normalize_template_id(raw: Any, *, chart_type: str, x_category: str, y_fields: Sequence[str]) -> str | None:
    template_id = str(raw or "").strip()
    if not template_id or template_id not in CHART_TEMPLATE_CATALOG:
        return None
    if template_id == "time_series_basic":
        if x_category not in {"numeric", "datetime"} or not y_fields or chart_type not in {"line", "bar"}:
            return None
    elif template_id == "top_n_categories":
        if x_category != "categorical" or len(y_fields) != 1:
            return None
    elif template_id == "distribution_histogram":
        if x_category != "numeric" or chart_type not in {"bar", "line"}:
            return None
    return template_id


def _normalize_chart_suggestion(
    item: Mapping[str, Any],
    *,
    idx: int,
    field_lookup: Mapping[str, tuple[str, str]],
) -> ChartSpec | None:
    if not isinstance(item, Mapping):
        return None

    chart_type = _normalize_chart_type(item.get("type"))
    if not chart_type:
        return None

    x_field, x_type = _normalize_field_name(item.get("xField"), field_lookup)
    if not x_field:
        return None

    y_fields_raw = item.get("yFields")
    y_candidates: Sequence[Any] | None
    if isinstance(y_fields_raw, str):
        y_candidates = [y_fields_raw]
    elif isinstance(y_fields_raw, Sequence):
        y_candidates = y_fields_raw
    else:
        single = item.get("yField") or item.get("y")
        if isinstance(single, str) and single.strip():
            y_candidates = [single]
        else:
            return None

    y_field_info: list[tuple[str, str]] = []
    seen_y: set[str] = set()
    for raw_y in y_candidates:
        name, ftype = _normalize_field_name(raw_y, field_lookup)
        if not name or name in seen_y:
            continue
        y_field_info.append((name, ftype or "string"))
        seen_y.add(name)
    if not y_field_info:
        return None

    group_field, group_type = _normalize_field_name(item.get("groupField"), field_lookup)
    if group_field and _field_category(group_type) != "categorical":
        group_field = None

    x_category = _field_category(x_type)
    numeric_y_fields = [name for name, ftype in y_field_info if _field_category(ftype) == "numeric"]

    if chart_type == "pie":
        if x_category != "categorical":
            return None
        if not numeric_y_fields:
            return None
        y_fields = [numeric_y_fields[0]]
    else:
        if chart_type in ("line", "scatter") and x_category not in {"numeric", "datetime"}:
            return None
        if chart_type == "bar" and x_category not in {"numeric", "datetime", "categorical"}:
            return None
        if not numeric_y_fields:
            return None
        y_fields = numeric_y_fields

    aggregation = _normalize_aggregation(item.get("aggregation"))
    chart_template_id = _normalize_template_id(
        item.get("chartTemplateId"),
        chart_type=chart_type,
        x_category=x_category,
        y_fields=y_fields,
    )

    style = item.get("style")
    style_payload = dict(style) if isinstance(style, Mapping) else None

    normalized: dict[str, Any] = {
        "id": str(item.get("id") or f"chart_{idx + 1}"),
        "type": chart_type,
        "xField": x_field,
        "yFields": y_fields,
        "groupField": group_field,
        "aggregation": aggregation,
        "chartTemplateId": chart_template_id,
        "style": style_payload,
    }
    title = item.get("title")
    description = item.get("description")
    if isinstance(title, str) and title.strip():
        normalized["title"] = title.strip()
    if isinstance(description, str) and description.strip():
        normalized["description"] = description.strip()

    try:
        return ChartSpec(**normalized)
    except Exception:
        return None


def suggest_charts(
    template_id: str,
    payload: ChartSuggestPayload,
    *,
    kind: str,
    correlation_id: Optional[str],
    template_dir_fn: Callable[[str], Any],
    db_path_fn: Callable[[Optional[str]], Any],
    load_contract_fn: Callable[[Any], Any],
    clean_key_values_fn: Callable[[Optional[dict]], Optional[dict]],
    discover_fn: Callable[..., Mapping[str, Any]],
    build_field_catalog_fn: Callable[[list], tuple[list, Mapping[str, Any]]],
    build_metrics_fn: Callable[[list, Mapping[str, Any], int], list],
    build_prompt_fn: Callable[..., str],
    call_chat_completion_fn: Callable[..., Any],
    model: str,
    strip_code_fences_fn: Callable[[str], str],
    logger,
) -> ChartSuggestResponse:
    template_dir = template_dir_fn(template_id)
    db_path = db_path_fn(payload.connection_id)
    if not db_path.exists():
        logger.error("Database not found at path: %s", db_path)
        raise HTTPException(status_code=400, detail={"code": "db_not_found", "message": "Database not found for the given connection."})

    try:
        load_contract_fn(template_dir)
    except Exception as exc:
        logger.exception(
            "chart_suggest_contract_load_failed",
            extra={
                "event": "chart_suggest_contract_load_failed",
                "template_id": template_id,
                "template_kind": kind,
                "correlation_id": correlation_id,
            },
        )
        raise HTTPException(status_code=500, detail={"code": "contract_load_failed", "message": "Failed to load contract artifacts."})

    contract_path = template_dir / "contract.json"
    if not contract_path.exists():
        raise HTTPException(
            status_code=400,
            detail={"code": "contract_not_ready", "message": "Contract artifacts missing. Approve mapping first."},
        )
    try:
        contract_payload = json.loads(contract_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.exception(
            "chart_suggest_contract_parse_failed",
            extra={
                "event": "chart_suggest_contract_parse_failed",
                "template_id": template_id,
                "template_kind": kind,
                "correlation_id": correlation_id,
            },
        )
        raise HTTPException(status_code=500, detail={"code": "contract_invalid", "message": "Invalid contract configuration."})

    key_values_payload = clean_key_values_fn(payload.key_values)

    try:
        summary = discover_fn(
            db_path=db_path,
            contract=contract_payload,
            start_date=payload.start_date,
            end_date=payload.end_date,
            key_values=key_values_payload,
        )
    except Exception as exc:
        logger.exception(
            "chart_suggest_discovery_failed",
            extra={
                "event": "chart_suggest_discovery_failed",
                "template_id": template_id,
                "template_kind": kind,
                "correlation_id": correlation_id,
            },
        )
        raise HTTPException(status_code=500, detail={"code": "discovery_failed", "message": "Data discovery failed."})

    batches = summary.get("batches") or []
    if not isinstance(batches, list):
        batches = []
    batch_metadata = summary.get("batch_metadata") or {}

    sample_data: list[dict[str, Any]] | None = None
    if payload.include_sample_data:
        try:
            sample_data = build_metrics_fn(batches, batch_metadata, limit=100)
        except Exception:
            sample_data = None
            logger.exception(
                "chart_suggest_sample_data_failed",
                extra={
                    "event": "chart_suggest_sample_data_failed",
                    "template_id": template_id,
                    "template_kind": kind,
                    "correlation_id": correlation_id,
                },
            )

    if not batches:
        logger.info(
            "chart_suggest_no_data",
            extra={
                "event": "chart_suggest_no_data",
                "template_id": template_id,
                "template_kind": kind,
                "correlation_id": correlation_id,
            },
        )
        sample_payload = sample_data if payload.include_sample_data else None
        if sample_payload is None and payload.include_sample_data:
            sample_payload = []
        return ChartSuggestResponse(charts=[], sample_data=sample_payload)

    field_catalog, stats = build_field_catalog_fn(batches)

    prompt = build_prompt_fn(
        template_id=template_id,
        kind=kind,
        start_date=payload.start_date,
        end_date=payload.end_date,
        key_values=key_values_payload,
        field_catalog=field_catalog,
        data_stats=stats,
        question=payload.question,
    )

    try:
        response = call_chat_completion_fn(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:
        logger.exception(
            "chart_suggest_llm_failed",
            extra={
                "event": "chart_suggest_llm_failed",
                "template_id": template_id,
                "template_kind": kind,
                "correlation_id": correlation_id,
            },
        )
        raise HTTPException(status_code=500, detail={"code": "chart_suggest_llm_failed", "message": "Chart suggestion generation failed."})

    raw_text = (response.choices[0].message.content or "").strip()
    parsed_text = strip_code_fences_fn(raw_text)

    charts: list[ChartSpec] = []
    field_lookup = _build_field_lookup(field_catalog)
    try:
        payload_json = json.loads(parsed_text)
    except Exception:
        logger.warning(
            "chart_suggest_json_parse_failed",
            extra={
                "event": "chart_suggest_json_parse_failed",
                "template_id": template_id,
                "template_kind": kind,
                "correlation_id": correlation_id,
            },
        )
        payload_json = {}

    raw_charts = payload_json.get("charts") if isinstance(payload_json, dict) else None
    if isinstance(raw_charts, list):
        for idx, item in enumerate(raw_charts):
            chart = _normalize_chart_suggestion(item, idx=idx, field_lookup=field_lookup)
            if chart:
                charts.append(chart)

    # Auto-correct: if no charts parsed, fall back to a simple default set based on available fields.
    if not charts:
        numeric_fields = [name for name, ftype in field_lookup.values() if _field_category(ftype) == "numeric"]
        time_like = [name for name, ftype in field_lookup.values() if _field_category(ftype) == "datetime"]
        categorical_fields = [name for name, ftype in field_lookup.values() if _field_category(ftype) == "categorical"]
        fallback_id = 0

        def _next_id():
            nonlocal fallback_id
            fallback_id += 1
            return f"fallback_{fallback_id}"

        if time_like and numeric_fields:
            charts.append(
                ChartSpec(
                    id=_next_id(),
                    type="line",
                    xField=time_like[0],
                    yFields=[numeric_fields[0]],
                    groupField=None,
                    aggregation="sum",
                    chartTemplateId="time_series_basic",
                    title=f"{numeric_fields[0]} over time",
                )
            )
        if categorical_fields and numeric_fields:
            charts.append(
                ChartSpec(
                    id=_next_id(),
                    type="bar",
                    xField=categorical_fields[0],
                    yFields=[numeric_fields[0]],
                    groupField=None,
                    aggregation="sum",
                    chartTemplateId="top_n_categories",
                    title=f"Top categories by {numeric_fields[0]}",
                )
            )
        if numeric_fields:
            charts.append(
                ChartSpec(
                    id=_next_id(),
                    type="bar",
                    xField=numeric_fields[0],
                    yFields=[numeric_fields[0]],
                    groupField=None,
                    aggregation="count",
                    chartTemplateId="distribution_histogram",
                    title=f"{numeric_fields[0]} distribution",
                )
            )

    state_store.set_last_used(payload.connection_id, template_id)

    logger.info(
        "chart_suggest_complete",
        extra={
            "event": "chart_suggest_complete",
            "template_id": template_id,
            "template_kind": kind,
            "charts_returned": len(charts),
            "correlation_id": correlation_id,
        },
    )
    return ChartSuggestResponse(
        charts=charts,
        sample_data=sample_data if payload.include_sample_data else None,
    )
