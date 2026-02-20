from __future__ import annotations

from backend.app.services.reports.discovery_metrics import (
    bin_numeric_metric,
    build_discovery_schema,
    build_resample_support,
    group_metrics_by_field,
)


def test_build_discovery_schema_classifies_fields_and_defaults():
    catalog = [
        {"name": "time", "type": "datetime"},
        {"name": "category", "type": "string"},
        {"name": "rows", "type": "number", "description": "row count"},
        {"name": "revenue", "type": "numeric"},
    ]

    schema = build_discovery_schema(catalog)

    assert schema["defaults"]["dimension"] == "time"
    assert schema["defaults"]["metric"] == "rows"

    metrics = {item["name"]: item for item in schema["metrics"]}
    assert metrics["rows"]["bucketable"] is True
    assert metrics["revenue"]["bucketable"] is True

    dims = {item["name"]: item for item in schema["dimensions"]}
    assert dims["time"]["kind"] == "temporal"
    assert dims["time"]["bucketable"] is True
    assert dims["category"]["kind"] == "categorical"
    assert dims["category"]["bucketable"] is False
    assert dims["rows"]["kind"] == "numeric"
    assert dims["rows"]["bucketable"] is True


def test_bin_numeric_metric_builds_expected_buckets():
    metrics = [
        {"batch_id": "a", "rows": 1},
        {"batch_id": "b", "rows": 3},
        {"batch_id": "c", "rows": 8},
    ]

    buckets = bin_numeric_metric(metrics, "rows", bucket_count=2)

    assert len(buckets) == 2
    first, second = buckets

    assert first["count"] == 2
    assert set(first["batch_ids"]) == {"a", "b"}
    assert second["count"] == 1
    assert second["batch_ids"] == ["c"]
    assert first["sum"] + second["sum"] == 12


def test_group_metrics_by_field_supports_average():
    metrics = [
        {"batch_id": "a", "rows": 5, "region": "east"},
        {"batch_id": "b", "rows": 15, "region": "east"},
        {"batch_id": "c", "rows": 10, "region": "west"},
    ]

    groups = group_metrics_by_field(metrics, "region", metric_field="rows", aggregation="avg")

    grouped = {item["key"]: item for item in groups}
    assert grouped["east"]["value"] == 10.0
    assert grouped["east"]["count"] == 2
    assert grouped["west"]["value"] == 10.0
    assert grouped["west"]["batch_ids"] == ["c"]


def test_build_resample_support_buckets_and_groups():
    catalog = [
        {"name": "rows", "type": "number"},
        {"name": "region", "type": "string"},
    ]
    metrics = [
        {"batch_id": "a", "rows": 5, "region": "north"},
        {"batch_id": "b", "rows": 15, "region": "north"},
        {"batch_id": "c", "rows": 10, "region": "south"},
    ]

    support = build_resample_support(catalog, metrics, default_metric="rows", bucket_count=2)

    assert "rows" in support["numeric_bins"]
    assert len(support["numeric_bins"]["rows"]) == 2
    assert "region" in support["category_groups"]
    grouped = {row["key"]: row for row in support["category_groups"]["region"]}
    assert grouped["north"]["value"] == 20.0
