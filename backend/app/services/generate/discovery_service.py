from __future__ import annotations

import json
from typing import Any, Callable, Mapping, Optional

from fastapi import HTTPException

from backend.app.services.reports.discovery_metrics import build_discovery_schema, build_resample_support
from backend.app.repositories.state import state_store


def discover_reports(
    payload,
    *,
    kind: str,
    template_dir_fn: Callable[[str], Any],
    db_path_fn: Callable[[Optional[str]], Any],
    load_contract_fn: Callable[[Any], Any],
    clean_key_values_fn: Callable[[Optional[dict]], Optional[dict]],
    discover_fn: Callable[..., Mapping[str, Any]],
    build_field_catalog_fn: Callable[[list], tuple[list, Mapping[str, Any]]],
    build_batch_metrics_fn: Callable[[list, Mapping[str, Any]], list],
    load_manifest_fn: Callable[[Any], Mapping[str, Any]],
    manifest_endpoint_fn: Callable[[str], str],
    logger,
):
    def _normalize_field_catalog(raw_catalog) -> list[dict[str, str]]:
        normalized: list[dict[str, str]] = []
        if not isinstance(raw_catalog, list):
            return normalized
        for entry in raw_catalog:
            if not isinstance(entry, Mapping):
                continue
            name = str(entry.get("name") or "").strip()
            if not name:
                continue
            field_type = str(entry.get("type") or "unknown").strip()
            description = str(entry.get("description") or "").strip()
            source = str(entry.get("source") or entry.get("table") or "computed").strip() or "computed"
            normalized.append(
                {
                    "name": name,
                    "type": field_type,
                    "description": description,
                    "source": source,
                }
            )
        return normalized

    template_dir = template_dir_fn(payload.template_id)
    db_path = db_path_fn(payload.connection_id)
    if not db_path.exists():
        logger.error("Database not found at path %s for connection_id=%s", db_path, payload.connection_id)
        raise HTTPException(status_code=400, detail={"code": "db_not_found", "message": "Database not found for the specified connection."})

    try:
        load_contract_fn(template_dir)
    except Exception as exc:
        logger.exception(
            "contract_artifacts_load_failed",
            extra={
                "event": "contract_artifacts_load_failed",
                "template_id": payload.template_id,
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
        logger.exception("Invalid contract.json for template_id=%s", payload.template_id)
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
        logger.exception("Discovery failed for template_id=%s, connection_id=%s", payload.template_id, payload.connection_id)
        raise HTTPException(status_code=500, detail={"code": "discovery_failed", "message": "Discovery failed. Please retry or contact support."})

    manifest_data = load_manifest_fn(template_dir) or {}
    manifest_url = manifest_endpoint_fn(payload.template_id)
    tpl_record = state_store.get_template_record(payload.template_id) or {}
    tpl_name = tpl_record.get("name") or f"Template {payload.template_id[:8]}"
    state_store.set_last_used(payload.connection_id, payload.template_id)

    batches_raw = summary.get("batches") or []
    if not isinstance(batches_raw, list):
        batches_raw = []

    raw_batch_metadata = summary.get("batch_metadata")
    batch_metadata: dict[str, dict[str, object]] = raw_batch_metadata if isinstance(raw_batch_metadata, Mapping) else {}

    raw_field_catalog = summary.get("field_catalog")
    raw_stats = summary.get("data_stats")
    if not isinstance(raw_field_catalog, list):
        raw_field_catalog, raw_stats = build_field_catalog_fn(batches_raw)
    field_catalog = _normalize_field_catalog(raw_field_catalog)
    if not field_catalog:
        fallback_catalog, raw_stats = build_field_catalog_fn(batches_raw)
        field_catalog = _normalize_field_catalog(fallback_catalog)
    data_stats = raw_stats if isinstance(raw_stats, Mapping) else {}

    discovery_schema = summary.get("discovery_schema")
    if not isinstance(discovery_schema, Mapping):
        discovery_schema = build_discovery_schema(field_catalog)

    batch_metrics = summary.get("batch_metrics")
    if not isinstance(batch_metrics, list):
        batch_metrics = build_batch_metrics_fn(batches_raw, batch_metadata)
    batch_metrics = batch_metrics if isinstance(batch_metrics, list) else []

    numeric_bins = summary.get("numeric_bins")
    category_groups = summary.get("category_groups")
    if not isinstance(numeric_bins, Mapping) or not isinstance(category_groups, Mapping):
        resample_support = build_resample_support(
            field_catalog,
            batch_metrics,
            schema=discovery_schema,
            default_metric=(discovery_schema or {}).get("defaults", {}).get("metric"),
        )
        numeric_bins = resample_support.get("numeric_bins", {})
        category_groups = resample_support.get("category_groups", {})

    def _time_bounds() -> tuple[str | None, str | None]:
        timestamps = []
        for meta in batch_metadata.values():
            if not isinstance(meta, Mapping):
                continue
            ts = meta.get("time")
            if ts:
                timestamps.append(ts)
        if not timestamps:
            return None, None
        try:
            ts_sorted = sorted(timestamps)
            return ts_sorted[0], ts_sorted[-1]
        except Exception:
            return None, None

    time_start, time_end = _time_bounds()

    return {
        "template_id": payload.template_id,
        "name": tpl_name,
        "batches": [
            {
                "id": b["id"],
                "rows": b["rows"],
                "parent": b["parent"],
                "selected": True,
                "time": (batch_metadata.get(str(b["id"])) or {}).get("time"),
                "category": (batch_metadata.get(str(b["id"])) or {}).get("category"),
            }
            for b in batches_raw
        ],
        "batches_count": summary["batches_count"],
        "rows_total": summary["rows_total"],
        "manifest_url": manifest_url,
        "manifest_produced_at": manifest_data.get("produced_at"),
        "field_catalog": field_catalog,
        "batch_metrics": batch_metrics,
        "discovery_schema": discovery_schema,
        "numeric_bins": numeric_bins,
        "category_groups": category_groups,
        "date_range": {
            "start": payload.start_date,
            "end": payload.end_date,
            "time_start": time_start,
            "time_end": time_end,
        },
        "data_stats": data_stats,
    }
