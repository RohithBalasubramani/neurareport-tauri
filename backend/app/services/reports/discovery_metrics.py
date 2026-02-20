"""Shared helpers used by discovery flows to expose per-batch metrics."""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

__all__ = [
    "build_batch_field_catalog_and_stats",
    "build_batch_metrics",
    "build_discovery_schema",
    "bin_numeric_metric",
    "group_metrics_by_field",
    "build_resample_support",
]


def _coerce_number(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except Exception:
        return 0.0


def _normalize_type(raw: Any) -> str:
    """
    Collapse loose field types coming from discovery into a stable set we can reason about.

    Currently we normalise into: "number", "datetime", or "string".
    """
    text = str(raw or "").strip().lower()
    if text in {"number", "numeric", "float", "double", "integer", "int"}:
        return "number"
    if text in {"datetime", "timestamp", "date", "time"}:
        return "datetime"
    if text in {"category", "categorical"}:
        return "string"
    return "string"


def build_batch_field_catalog_and_stats(
    batches: Sequence[Mapping[str, Any]],
    *,
    time_source: str | None = None,
    categorical_fields: Sequence[str] | None = None,
    numeric_fields: Sequence[str] | None = None,
    field_sources: Mapping[str, str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows_values: list[float] = []
    parent_values: list[float] = []
    for raw in batches:
        if not isinstance(raw, Mapping):
            continue
        rows_val = raw.get("rows")
        parent_val = raw.get("parent")
        try:
            rows_num = float(rows_val)
        except Exception:
            rows_num = 0.0
        try:
            parent_num = float(parent_val)
        except Exception:
            parent_num = 0.0
        rows_values.append(rows_num)
        parent_values.append(parent_num)

    def _basic_stats(values: list[float]) -> dict[str, float]:
        if not values:
            return {"min": 0.0, "max": 0.0, "avg": 0.0}
        total = sum(values)
        return {
            "min": float(min(values)),
            "max": float(max(values)),
            "avg": float(total / len(values)),
        }

    stats: dict[str, Any] = {
        "batch_count": len(batches),
        "rows_total": int(sum(rows_values)),
        "rows_stats": _basic_stats(rows_values),
        "parent_stats": _basic_stats(parent_values),
    }

    sources: dict[str, str] = {str(k): str(v) for k, v in (field_sources or {}).items() if str(k).strip()}
    field_catalog: list[dict[str, Any]] = []
    seen: set[str] = set()

    def _add_field(name: str, ftype: str, description: str, *, source: str | None = None):
        key = (name or "").strip()
        if not key or key in seen:
            return
        field_catalog.append(
            {
                "name": key,
                "type": (ftype or "unknown").strip(),
                "description": description,
                "source": source or sources.get(key) or "computed",
            }
        )
        seen.add(key)

    _add_field(
        "batch_index",
        "numeric",
        "1-based index of the batch in discovery order.",
        source="computed",
    )
    _add_field(
        "batch_id",
        "categorical",
        "Batch identifier (composite key from join keys).",
        source="computed",
    )
    _add_field(
        "rows",
        "numeric",
        "Number of child rows in this batch.",
        source=sources.get("rows") or "child_rows",
    )
    _add_field(
        "parent",
        "numeric",
        "Number of parent rows associated with this batch.",
        source=sources.get("parent") or "parent_rows",
    )
    _add_field(
        "rows_per_parent",
        "numeric",
        "Child rows divided by parent rows (if parent is zero, treat as rows).",
        source="computed",
    )

    if time_source:
        time_desc = f"Earliest timestamp per batch sourced from {time_source}."
    else:
        time_desc = "Earliest timestamp associated with the batch (if available)."
    _add_field(
        "time",
        "time",
        time_desc,
        source=time_source or sources.get("time") or "computed",
    )

    cat_fields: list[str] = []
    if categorical_fields:
        for field in categorical_fields:
            text = str(field or "").strip()
            if text and text not in cat_fields:
                cat_fields.append(text)
    if cat_fields:
        primary_cat = cat_fields[0]
        _add_field(
            "category",
            "categorical",
            f"Categorical label derived from key column '{primary_cat}'.",
            source=sources.get(primary_cat) or "computed",
        )
        for field in cat_fields:
            _add_field(
                field,
                "categorical",
                f"Key column '{field}' used to build the batch identifier.",
                source=sources.get(field) or "computed",
            )
    else:
        _add_field(
            "category",
            "categorical",
            "Categorical label derived from key columns (if available).",
            source="computed",
        )

    for field in numeric_fields or []:
        fname = (field or "").strip()
        if not fname or fname in seen:
            continue
        _add_field(
            fname,
            "numeric",
            f"Numeric measure '{fname}' derived from discovery results.",
            source=sources.get(fname) or "computed",
        )

    return field_catalog, stats


def build_batch_metrics(
    batches: Sequence[Mapping[str, Any]],
    batch_metadata: Mapping[str, Any] | None,
    *,
    limit: int | None = None,
    extra_fields: Sequence[str] | None = None,
) -> list[dict[str, Any]]:
    metrics: list[dict[str, Any]] = []
    metadata_lookup: Mapping[str, Any] = batch_metadata if isinstance(batch_metadata, Mapping) else {}
    iterable: Sequence[Mapping[str, Any]] = batches
    if limit is not None:
        iterable = list(iterable)[:limit]

    extras: list[str] = []
    if extra_fields is None:
        seen_extras: set[str] = set()
        for meta in metadata_lookup.values():
            if not isinstance(meta, Mapping):
                continue
            for key in meta.keys():
                key_text = str(key or "").strip()
                if not key_text or key_text in ("time", "category") or key_text in seen_extras:
                    continue
                seen_extras.add(key_text)
        extras = sorted(seen_extras)
    else:
        extras = []
        for field in extra_fields:
            name = str(field or "").strip()
            if not name or name in ("time", "category") or name in extras:
                continue
            extras.append(name)

    for idx, raw in enumerate(iterable, start=1):
        if not isinstance(raw, Mapping):
            continue
        batch_id = raw.get("id")
        rows_val = _coerce_number(raw.get("rows"))
        parent_val = _coerce_number(raw.get("parent"))
        safe_parent = parent_val if parent_val not in (None, 0) else 1.0
        entry: dict[str, Any] = {
            "batch_index": idx,
            "batch_id": str(batch_id) if batch_id is not None else str(idx),
            "rows": rows_val,
            "parent": parent_val,
            "rows_per_parent": rows_val / safe_parent if safe_parent else rows_val,
        }
        meta = metadata_lookup.get(str(batch_id)) if batch_id is not None else None
        if isinstance(meta, Mapping):
            for key in ("time", "category"):
                if key in meta:
                    entry[key] = meta[key]
            for extra in extras:
                if extra in meta:
                    entry[extra] = meta[extra]
        metrics.append(entry)
    return metrics


# Discovery payload schema surfaced to the frontend and chart helpers:
# {
#   "metrics": [
#     {"name": "rows", "type": "number", "description": "...", "bucketable": true},
#     ...
#   ],
#   "dimensions": [
#     {"name": "time", "type": "datetime", "kind": "temporal", "bucketable": true},
#     {"name": "category", "type": "string", "kind": "categorical", "bucketable": false},
#     {"name": "batch_index", "type": "number", "kind": "numeric", "bucketable": true},
#     ...
#   ],
#   "defaults": {"dimension": "time", "metric": "rows"}
# }
def build_discovery_schema(field_catalog: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """
    Build a concise list of allowed metrics/dimensions from a field catalog.

    The schema is meant for the frontend to know which fields it can use for resampling
    (including numeric binning) and charting without guessing.
    """
    metrics: list[dict[str, Any]] = []
    dimensions: list[dict[str, Any]] = []
    seen_metric_names: set[str] = set()
    seen_dimension_names: set[str] = set()

    for field in field_catalog or []:
        name = str(field.get("name") or "").strip()
        if not name:
            continue
        normalized_type = _normalize_type(field.get("type"))
        description = str(field.get("description") or "").strip()
        base = {"name": name, "type": normalized_type}
        if description:
            base["description"] = description

        # Numeric fields can be treated both as metrics and as bucketable dimensions.
        if normalized_type == "number" and name not in seen_metric_names:
            metrics.append({**base, "bucketable": True})
            seen_metric_names.add(name)

        if name not in seen_dimension_names:
            kind = "categorical"
            bucketable = False
            if normalized_type == "datetime":
                kind = "temporal"
                bucketable = True
            elif normalized_type == "number":
                kind = "numeric"
                bucketable = True
            dimensions.append({**base, "kind": kind, "bucketable": bucketable})
            seen_dimension_names.add(name)

    def _pick_default_dimension() -> str:
        for preferred in ("time", "timestamp", "date"):
            if any(dim["name"] == preferred for dim in dimensions):
                return preferred
        for fallback in ("category", "batch_index"):
            if any(dim["name"] == fallback for dim in dimensions):
                return fallback
        return dimensions[0]["name"] if dimensions else "batch_index"

    def _pick_default_metric() -> str:
        for preferred in ("rows", "rows_per_parent", "parent"):
            if any(metric["name"] == preferred for metric in metrics):
                return preferred
        return metrics[0]["name"] if metrics else "rows"

    return {
        "metrics": metrics,
        "dimensions": dimensions,
        "defaults": {
            "dimension": _pick_default_dimension(),
            "metric": _pick_default_metric(),
        },
    }


def bin_numeric_metric(
    metrics: Sequence[Mapping[str, Any]],
    metric_name: str,
    *,
    bucket_count: int = 10,
    bucket_edges: Sequence[float] | None = None,
    value_range: tuple[float, float] | None = None,
) -> list[dict[str, Any]]:
    """
    Bucket a numeric metric into ranges and compute aggregates per bucket.

    Returns a list of buckets sorted by range:
      [
        {
          "bucket_index": 0,
          "start": <inclusive lower>,
          "end": <exclusive upper, inclusive for the last bucket>,
          "count": <rows in bucket>,
          "sum": <sum of metric>,
          "min": <min value>,
          "max": <max value>,
          "batch_ids": ["id_1", ...],
        },
        ...
      ]
    """
    if bucket_edges is not None:
        edges = sorted({float(v) for v in bucket_edges if v is not None})
        if len(edges) < 2:
            return []
    else:
        values = [_coerce_number(entry.get(metric_name)) for entry in metrics]
        if not values:
            return []
        min_value = float(values[0])
        max_value = float(values[0])
        for val in values[1:]:
            min_value = min(min_value, val)
            max_value = max(max_value, val)
        if value_range is not None:
            min_value = float(value_range[0])
            max_value = float(value_range[1])
        if max_value < min_value:
            min_value, max_value = max_value, min_value
        if bucket_count < 1:
            bucket_count = 1
        if max_value == min_value:
            edges = [min_value, max_value]
        else:
            step = (max_value - min_value) / bucket_count
            edges = [min_value + step * i for i in range(bucket_count)]
            edges.append(max_value)

    buckets: list[dict[str, Any]] = []
    for idx in range(len(edges) - 1):
        start = edges[idx]
        end = edges[idx + 1]
        buckets.append(
            {
                "bucket_index": idx,
                "start": start,
                "end": end,
                "count": 0,
                "sum": 0.0,
                "min": float("inf"),
                "max": float("-inf"),
                "batch_ids": [],
            }
        )

    for entry in metrics:
        value = _coerce_number(entry.get(metric_name))
        batch_id = entry.get("batch_id") or entry.get("id")
        target_idx = None
        for idx in range(len(edges) - 1):
            start = edges[idx]
            end = edges[idx + 1]
            is_last = idx == len(edges) - 2
            if (value >= start and value < end) or (is_last and value == end):
                target_idx = idx
                break
        if target_idx is None:
            continue
        bucket = buckets[target_idx]
        bucket["count"] += 1
        bucket["sum"] += value
        bucket["min"] = min(bucket["min"], value)
        bucket["max"] = max(bucket["max"], value)
        if batch_id is not None:
            batch_id_text = str(batch_id)
            if batch_id_text not in bucket["batch_ids"]:
                bucket["batch_ids"].append(batch_id_text)

    for bucket in buckets:
        if bucket["min"] == float("inf"):
            bucket["min"] = 0.0
        if bucket["max"] == float("-inf"):
            bucket["max"] = 0.0
    return buckets


def group_metrics_by_field(
    metrics: Sequence[Mapping[str, Any]],
    dimension_field: str,
    *,
    metric_field: str = "rows",
    aggregation: str = "sum",
) -> list[dict[str, Any]]:
    """
    Group metrics by a categorical field and aggregate a numeric metric.

    aggregation: one of ("sum", "avg", "min", "max", "count").
    """
    groups: dict[str, dict[str, Any]] = {}
    agg = aggregation.lower().strip()
    for entry in metrics:
        key_raw = entry.get(dimension_field)
        key = str(key_raw) if key_raw is not None else ""
        metric_value = _coerce_number(entry.get(metric_field))
        bucket = groups.setdefault(
            key,
            {
                "key": key,
                "label": key or "(empty)",
                "sum": 0.0,
                "count": 0,
                "min": float("inf"),
                "max": float("-inf"),
                "batch_ids": [],
            },
        )
        bucket["sum"] += metric_value
        bucket["count"] += 1
        bucket["min"] = min(bucket["min"], metric_value)
        bucket["max"] = max(bucket["max"], metric_value)
        batch_id = entry.get("batch_id") or entry.get("id")
        if batch_id is not None:
            batch_id_text = str(batch_id)
            if batch_id_text not in bucket["batch_ids"]:
                bucket["batch_ids"].append(batch_id_text)

    results: list[dict[str, Any]] = []
    for bucket in groups.values():
        value: float
        if agg == "avg":
            value = bucket["sum"] / bucket["count"] if bucket["count"] else 0.0
        elif agg == "min":
            value = 0.0 if bucket["min"] == float("inf") else bucket["min"]
        elif agg == "max":
            value = 0.0 if bucket["max"] == float("-inf") else bucket["max"]
        elif agg == "count":
            value = float(bucket["count"])
        else:
            value = bucket["sum"]
        results.append(
            {
                **bucket,
                "value": value,
            }
        )

    return sorted(results, key=lambda item: item["label"])


def build_resample_support(
    field_catalog: Iterable[Mapping[str, Any]],
    batch_metrics: Sequence[Mapping[str, Any]],
    *,
    schema: Mapping[str, Any] | None = None,
    default_metric: str | None = None,
    bucket_count: int = 10,
) -> dict[str, Any]:
    """
    Pre-compute numeric bins and categorical groups for the discovery payload.

    Shape:
      {
        "numeric_bins": {metric_name: <bin_numeric_metric output>},
        "category_groups": {dimension_name: <group_metrics_by_field output>}
      }
    """
    schema_data = schema if isinstance(schema, Mapping) else build_discovery_schema(field_catalog)
    numeric_bins: dict[str, list[dict[str, Any]]] = {}
    category_groups: dict[str, list[dict[str, Any]]] = {}
    defaults = schema_data.get("defaults") or {}
    metric_default = default_metric or defaults.get("metric") or "rows"

    for metric in schema_data.get("metrics", []):
        if not isinstance(metric, Mapping):
            continue
        name = str(metric.get("name") or "").strip()
        if not name:
            continue
        if not metric.get("bucketable"):
            continue
        if _normalize_type(metric.get("type")) != "number":
            continue
        numeric_bins[name] = bin_numeric_metric(batch_metrics, name, bucket_count=bucket_count)

    for dim in schema_data.get("dimensions", []):
        if not isinstance(dim, Mapping):
            continue
        name = str(dim.get("name") or "").strip()
        if not name:
            continue
        dim_kind = str(dim.get("kind") or dim.get("type") or "").lower()
        if dim_kind in {"categorical", "string"}:
            category_groups[name] = group_metrics_by_field(
                batch_metrics,
                name,
                metric_field=metric_default,
                aggregation="sum",
            )
        elif dim_kind in {"numeric", "number"} and dim.get("bucketable") and name not in numeric_bins:
            numeric_bins[name] = bin_numeric_metric(batch_metrics, name, bucket_count=bucket_count)

    return {
        "numeric_bins": numeric_bins,
        "category_groups": category_groups,
    }
