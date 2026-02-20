from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from backend.app.schemas.generate.charts import ChartSuggestPayload
from backend.app.services.generate import chart_suggestions_service as svc
from backend.app.services.reports.discovery_metrics import build_batch_field_catalog_and_stats


class DummyResponse:
    def __init__(self, content: str):
        self.choices = [
            SimpleNamespace(message=SimpleNamespace(content=content)),
        ]


def _logger():
    return SimpleNamespace(
        info=lambda *_, **__: None,
        warning=lambda *_, **__: None,
        exception=lambda *_, **__: None,
    )


def _build_field_catalog(batches):
    return build_batch_field_catalog_and_stats(batches)


def _build_metrics(batches, metadata, limit):
    rows = []
    for idx, batch in enumerate(batches[:limit]):
        rows.append(
            {
                "batch_index": idx + 1,
                "batch_id": batch.get("id"),
                "rows": batch.get("rows", 0),
                "parent": batch.get("parent", 0),
                "rows_per_parent": (batch.get("rows", 0) / (batch.get("parent", 1) or 1))
                if batch.get("parent")
                else batch.get("rows", 0),
            }
        )
    return rows


def _call(**_kwargs):
    return DummyResponse('{"charts":[{"id":"chart_1","type":"bar","xField":"batch_index","yFields":["rows"]}]}')


def _make_summary(batches, batch_metadata=None):
    return {
        "batches": batches,
        "batches_count": len(batches),
        "rows_total": sum(int(item.get("rows", 0)) for item in batches),
        "batch_metadata": batch_metadata or {},
    }


def _suggest(template_id, payload, summary_ref, template_dir, db_path, *, metrics_fn=_build_metrics, call_fn=_call):
    discover = lambda **_kwargs: summary_ref  # noqa: E731
    return svc.suggest_charts(
        template_id,
        payload,
        kind="pdf",
        correlation_id=None,
        template_dir_fn=lambda *_: template_dir,
        db_path_fn=lambda *_: db_path,
        load_contract_fn=lambda *_: None,
        clean_key_values_fn=lambda kv: kv,
        discover_fn=discover,
        build_field_catalog_fn=_build_field_catalog,
        build_metrics_fn=metrics_fn,
        build_prompt_fn=lambda **_kwargs: "{}",
        call_chat_completion_fn=call_fn,
        model="gpt",
        strip_code_fences_fn=lambda x: x,
        logger=_logger(),
    )


@pytest.fixture
def chart_suggest_setup(monkeypatch, tmp_path):
    template_dir = tmp_path / "tpl"
    template_dir.mkdir()
    (template_dir / "contract.json").write_text("{}")
    db_path = template_dir / "db.sqlite"
    db_path.touch()

    batches: list[dict[str, object]] = [
        {"id": "batch_1", "rows": 25, "parent": 5},
        {"id": "batch_2", "rows": 30, "parent": 3},
    ]
    summary = _make_summary(batches, {"batch_1": {"time": "2024-01-01", "category": "North"}})

    monkeypatch.setattr(svc.state_store, "set_last_used", lambda *_args, **_kwargs: None)

    return summary, template_dir, db_path


def test_sample_data_only_returned_when_requested(chart_suggest_setup):
    summary, template_dir, db_path = chart_suggest_setup
    payload = ChartSuggestPayload(
        start_date="2024-01-01",
        end_date="2024-01-31",
        key_values=None,
        question="Show rows",
    )
    response = _suggest("tpl_1", payload, summary, template_dir, db_path)
    assert response.sample_data is None

    payload_with_sample = ChartSuggestPayload(
        start_date="2024-01-01",
        end_date="2024-01-31",
        key_values=None,
        question="Show rows",
        include_sample_data=True,
    )
    response_with_sample = _suggest("tpl_1", payload_with_sample, summary, template_dir, db_path)
    assert isinstance(response_with_sample.sample_data, list)
    assert len(response_with_sample.sample_data) == 2
    first_row = response_with_sample.sample_data[0]
    for field in ("batch_index", "batch_id", "rows", "parent", "rows_per_parent"):
        assert field in first_row
    assert response_with_sample.sample_data[0]["batch_index"] == 1


def test_sample_data_is_limited_to_100_rows(chart_suggest_setup):
    summary, template_dir, db_path = chart_suggest_setup
    large_batches = [{"id": f"batch_{i}", "rows": i, "parent": (i % 3) + 1} for i in range(150)]
    summary.update(_make_summary(large_batches))

    payload = ChartSuggestPayload(
        start_date="2024-01-01",
        end_date="2024-01-31",
        key_values=None,
        question="limit test",
        include_sample_data=True,
    )
    response = _suggest("tpl_limit", payload, summary, template_dir, db_path)
    assert response.sample_data is not None
    assert len(response.sample_data) == 100
    assert response.sample_data[0]["batch_index"] == 1
    assert response.sample_data[-1]["batch_index"] == 100


def test_sample_data_failure_does_not_block_response(chart_suggest_setup):
    summary, template_dir, db_path = chart_suggest_setup

    payload = ChartSuggestPayload(
        start_date="2024-01-01",
        end_date="2024-01-31",
        key_values=None,
        question="error tolerance",
        include_sample_data=True,
    )
    response = _suggest(
        "tpl_error",
        payload,
        summary,
        template_dir,
        db_path,
        metrics_fn=lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    assert response.sample_data is None
    assert isinstance(response.charts, list)
    assert response.charts, "charts should still be returned"


def test_malformed_chart_payload_is_sanitized(chart_suggest_setup):
    summary, template_dir, db_path = chart_suggest_setup

    def _bad_call(**_kwargs):
        payload = {
            "charts": [
                {
                    "id": None,
                    "type": "LineChart",
                    "xField": "BATCH_INDEX",
                    "yFields": ["rows", "category"],
                    "aggregation": "Sum",
                    "style": {"color": "blue"},
                    "unknown": "junk",
                },
                {"type": "pie", "xField": "rows", "yFields": ["category"]},
                {"type": "bar", "xField": "missing", "yFields": ["rows"]},
            ]
        }
        return DummyResponse(json.dumps(payload))

    payload = ChartSuggestPayload(
        start_date="2024-01-01",
        end_date="2024-01-31",
        key_values=None,
        question="malformed",
        include_sample_data=False,
    )
    response = _suggest("tpl_malformed", payload, summary, template_dir, db_path, call_fn=_bad_call)

    assert len(response.charts) == 1
    chart = response.charts[0]
    assert chart.type == "line"
    assert chart.xField == "batch_index"
    assert chart.yFields == ["rows"]
    assert chart.aggregation == "sum"
    assert chart.style == {"color": "blue"}


def test_template_ids_are_validated_against_catalog(chart_suggest_setup):
    summary, template_dir, db_path = chart_suggest_setup

    def _template_call(**_kwargs):
        payload = {
            "charts": [
                {
                    "type": "bar",
                    "xField": "category",
                    "yFields": ["rows"],
                    "chartTemplateId": "top_n_categories",
                },
                {
                    "type": "line",
                    "xField": "batch_index",
                    "yFields": ["rows"],
                    "chartTemplateId": "does_not_exist",
                },
                {
                    "type": "pie",
                    "xField": "category",
                    "yFields": ["rows"],
                    "chartTemplateId": "distribution_histogram",
                },
            ]
        }
        return DummyResponse(json.dumps(payload))

    payload = ChartSuggestPayload(
        start_date="2024-01-01",
        end_date="2024-01-31",
        key_values=None,
        question="template ids",
    )
    response = _suggest("tpl_tplid", payload, summary, template_dir, db_path, call_fn=_template_call)

    assert len(response.charts) == 3
    template_ids = [chart.chartTemplateId for chart in response.charts]
    assert template_ids[0] == "top_n_categories"
    assert template_ids[1] is None
    assert template_ids[2] is None
