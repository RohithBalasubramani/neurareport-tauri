from __future__ import annotations

from types import SimpleNamespace

from backend.app.services.generate.chart_suggestions_service import suggest_charts
from backend.app.schemas.generate.charts import ChartSuggestPayload


def test_chart_suggestions_fallback_when_llm_returns_empty(tmp_path):
    # Minimal fixtures
    template_id = "tpl-1"
    payload = ChartSuggestPayload(
        start_date="2024-01-01",
        end_date="2024-01-31",
        question="",
        include_sample_data=False,
    )

    # Fake discover function: return a small batch set with numeric and category fields.
    def discover_fn(**_kwargs):
        return {
            "batches": [
                {"id": "b1", "rows": 10, "parent": 2},
                {"id": "b2", "rows": 5, "parent": 1},
            ],
            "batch_metadata": {"b1": {"category": "North"}, "b2": {"category": "South"}},
            "field_catalog": [
                {"name": "rows", "type": "number"},
                {"name": "parent", "type": "number"},
                {"name": "category", "type": "categorical"},
                {"name": "time", "type": "datetime"},
            ],
        }

    def build_field_catalog_fn(batches):
        # Return the supplied catalog plus simple stats
        rows_vals = [b.get("rows", 0) for b in batches]
        return [
            {"name": "rows", "type": "number"},
            {"name": "parent", "type": "number"},
            {"name": "category", "type": "categorical"},
            {"name": "time", "type": "datetime"},
        ], {
            "rows": {"min": min(rows_vals), "max": max(rows_vals), "avg": sum(rows_vals) / len(rows_vals)},
        }

    def build_metrics_fn(batches, metadata, limit=100):
        metrics = []
        for idx, batch in enumerate(batches[:limit], start=1):
            bid = batch.get("id") or idx
            meta = metadata.get(str(bid), {})
            metrics.append(
                {
                    "batch_index": idx,
                    "batch_id": bid,
                    "rows": batch.get("rows", 0),
                    "parent": batch.get("parent", 0),
                    "category": meta.get("category"),
                }
            )
        return metrics

    # Prompt builder is irrelevant here; call_chat_completion returns empty charts.
    def build_prompt_fn(**_kwargs):
        return "prompt"

    def call_chat_completion_fn(**_kwargs):
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{"charts": []}'))])

    db_path = tmp_path / "db.sqlite"
    db_path.write_bytes(b"")
    contract_path = tmp_path / "contract.json"
    contract_path.write_text("{}")

    class _Logger:
        def info(self, *args, **kwargs):
            return None

        def warning(self, *args, **kwargs):
            return None

        def exception(self, *args, **kwargs):
            return None

    logger = _Logger()

    charts_response = suggest_charts(
        template_id,
        payload,
        kind="pdf",
        correlation_id=None,
        template_dir_fn=lambda tpl, kind="pdf": tmp_path,
        db_path_fn=lambda conn_id: db_path,
        load_contract_fn=lambda *_: None,
        clean_key_values_fn=lambda kv: kv,
        discover_fn=discover_fn,
        build_field_catalog_fn=build_field_catalog_fn,
        build_metrics_fn=build_metrics_fn,
        build_prompt_fn=build_prompt_fn,
        call_chat_completion_fn=call_chat_completion_fn,
        model="mock",
        strip_code_fences_fn=lambda text: text,
        logger=logger,
    )

    # Auto-correction should produce fallback charts from available fields.
    assert charts_response.charts, "Expected fallback charts when LLM returns none"
    chart_types = {chart.type for chart in charts_response.charts}
    assert chart_types & {"bar", "line"}, "Expected at least bar/line charts in fallback"
