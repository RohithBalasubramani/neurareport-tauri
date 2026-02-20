import json
import uuid
from types import SimpleNamespace

import pytest

from backend import api
from backend.app.services.mapping import AutoMapInline
from backend.app.services.mapping.AutoMapInline import (
    MappingInlineResult,
    MappingInlineValidationError,
)
from backend.app.services.mapping.HeaderMapping import REPORT_SELECTED_VALUE
from backend.app.services.prompts import llm_prompts


def _dummy_response(payload: dict) -> SimpleNamespace:
    content = json.dumps(payload)
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


def _basic_schema() -> dict:
    return {
        "scalars": ["report_title", "report_date"],
        "row_tokens": [],
        "totals": [],
    }


def _basic_html() -> str:
    return "<html><body><h1>{report_title}</h1><p>Date: {report_date}</p></body></html>"


def test_llm_call_3_happy_path(monkeypatch):
    html = _basic_html()
    catalog = ["reports.report_date"]
    schema = _basic_schema()

    payload = {
        "mapping": {"report_date": "reports.report_date"},
        "token_samples": {
            "report_title": "Consumption Report",
            "report_date": "2023-01-01",
        },
        "meta": {"unresolved": [], "hints": {}},
    }

    monkeypatch.setattr(AutoMapInline, "call_chat_completion", lambda *args, **kwargs: _dummy_response(payload))
    monkeypatch.setattr(AutoMapInline, "get_openai_client", lambda: object())

    result = AutoMapInline.run_llm_call_3(
        html,
        catalog,
        schema,
        llm_prompts.PROMPT_VERSION,
        png_path="",
        cache_key="cache-key-1",
    )

    assert result.mapping == {"report_date": "reports.report_date"}
    assert result.constant_replacements["report_title"] == "Consumption Report"
    assert result.token_samples["report_title"] == "Consumption Report"
    assert result.token_samples["report_date"] == "2023-01-01"
    assert "Consumption Report" in result.html_constants_applied
    assert result.prompt_meta["cache_key"] == "cache-key-1"


def test_llm_call_3_allows_missing_tokens_when_enabled(monkeypatch):
    html = "<html><body><table><tr><td>DATE</td></tr></table></body></html>"
    catalog = ["neuract__Flowmeters.timestamp_utc"]
    schema = _basic_schema()

    payload = {
        "mapping": {"date": "neuract__Flowmeters.timestamp_utc"},
        "token_samples": {},
        "meta": {"unresolved": [], "hints": {}},
    }

    monkeypatch.setattr(AutoMapInline, "call_chat_completion", lambda *args, **kwargs: _dummy_response(payload))
    monkeypatch.setattr(AutoMapInline, "get_openai_client", lambda: object())

    result_default = AutoMapInline.run_llm_call_3(
        html,
        catalog,
        schema,
        llm_prompts.PROMPT_VERSION,
        png_path="",
        cache_key="cache-key-missing-tokens",
    )
    assert result_default.mapping == {}

    result_allowed = AutoMapInline.run_llm_call_3(
        html,
        catalog,
        schema,
        llm_prompts.PROMPT_VERSION,
        png_path="",
        cache_key="cache-key-missing-tokens-allowed",
        allow_missing_tokens=True,
    )
    assert result_allowed.mapping == {"date": "neuract__Flowmeters.timestamp_utc"}


def test_llm_call_3_remaps_row_prefix_tokens(monkeypatch):
    html = "<html><body><table><tbody><tr><td>{row_date}</td><td>{row_volume}</td></tr></tbody></table></body></html>"
    catalog = ["neuract__Flowmeters.timestamp_utc", "neuract__Flowmeters.volume"]
    schema = {
        "scalars": [],
        "row_tokens": ["row_date", "row_volume"],
        "totals": [],
    }

    payload = {
        "mapping": {
            "date": "neuract__Flowmeters.timestamp_utc",
            "volume": "neuract__Flowmeters.volume",
        },
        "token_samples": {
            "row_date": "2025-01-01",
            "row_volume": "123.4",
        },
        "meta": {"unresolved": [], "hints": {}},
    }

    monkeypatch.setattr(AutoMapInline, "call_chat_completion", lambda *args, **kwargs: _dummy_response(payload))
    monkeypatch.setattr(AutoMapInline, "get_openai_client", lambda: object())

    result = AutoMapInline.run_llm_call_3(
        html,
        catalog,
        schema,
        llm_prompts.PROMPT_VERSION,
        png_path="",
        cache_key="cache-key-row-remap",
    )

    assert result.mapping == {
        "row_date": "neuract__Flowmeters.timestamp_utc",
        "row_volume": "neuract__Flowmeters.volume",
    }


def test_llm_call_3_allows_extra_token_samples_when_flag_set(monkeypatch):
    html = "<html><body><table><tr><td>DATE</td></tr></table></body></html>"
    catalog = ["neuract__Flowmeters.timestamp_utc"]
    schema = _basic_schema()

    payload = {
        "mapping": {"date": "neuract__Flowmeters.timestamp_utc"},
        "token_samples": {"date": "2024-01-01"},
        "meta": {"unresolved": [], "hints": {}},
    }

    monkeypatch.setattr(AutoMapInline, "call_chat_completion", lambda *args, **kwargs: _dummy_response(payload))
    monkeypatch.setattr(AutoMapInline, "get_openai_client", lambda: object())

    with pytest.raises(MappingInlineValidationError):
        AutoMapInline.run_llm_call_3(
            html,
            catalog,
            schema,
            llm_prompts.PROMPT_VERSION,
            png_path="",
            cache_key="cache-key-extra-token-samples",
        )

    result_allowed = AutoMapInline.run_llm_call_3(
        html,
        catalog,
        schema,
        llm_prompts.PROMPT_VERSION,
        png_path="",
        cache_key="cache-key-extra-token-samples-allowed",
        allow_missing_tokens=True,
    )
    assert result_allowed.mapping == {"date": "neuract__Flowmeters.timestamp_utc"}


def test_llm_call_3_coerces_report_filters_to_input_sample(monkeypatch):
    html = "<html><body><p>{from_date}</p><p>{to_date}</p></body></html>"
    catalog: list[str] = []
    schema = {
        "scalars": ["from_date", "to_date"],
        "row_tokens": [],
        "totals": [],
    }

    payload = {
        "mapping": {"from_date": "params.from_date", "to_date": "To Be Selected in Report generator"},
        "token_samples": {
            "from_date": "01-Jan-2023",
            "to_date": "31-Jan-2023",
        },
        "meta": {"unresolved": [], "hints": {}},
    }

    monkeypatch.setattr(AutoMapInline, "call_chat_completion", lambda *args, **kwargs: _dummy_response(payload))
    monkeypatch.setattr(AutoMapInline, "get_openai_client", lambda: object())

    result = AutoMapInline.run_llm_call_3(
        html,
        catalog,
        schema,
        llm_prompts.PROMPT_VERSION,
        png_path="",
        cache_key="cache-key-date-filters",
    )

    assert result.mapping["from_date"] == REPORT_SELECTED_VALUE
    assert result.mapping["to_date"] == REPORT_SELECTED_VALUE


def test_llm_call_3_coerces_page_tokens(monkeypatch):
    html = "<html><body><footer>{page_label}</footer></body></html>"
    catalog: list[str] = []
    schema = {
        "scalars": ["page_label"],
        "row_tokens": [],
        "totals": [],
    }

    payload = {
        "mapping": {"page_label": "To Be Selected in generator"},
        "token_samples": {"page_label": "Page 1 of 1"},
        "meta": {"unresolved": [], "hints": {}},
    }

    monkeypatch.setattr(AutoMapInline, "call_chat_completion", lambda *args, **kwargs: _dummy_response(payload))
    monkeypatch.setattr(AutoMapInline, "get_openai_client", lambda: object())

    result = AutoMapInline.run_llm_call_3(
        html,
        catalog,
        schema,
        llm_prompts.PROMPT_VERSION,
        png_path="",
        cache_key="cache-key-page-label",
    )

    assert result.mapping["page_label"] == REPORT_SELECTED_VALUE


def test_llm_call_3_rejects_token_rename(monkeypatch):
    html = _basic_html()
    catalog = ["reports.report_date"]
    schema = _basic_schema()

    payload = {
        "mapping": {
            "report_title_v2": "reports.report_title",
            "report_date": "reports.report_date",
        },
        "token_samples": {
            "report_title": "Consumption Report",
            "report_date": "2023-01-01",
        },
        "meta": {"unresolved": [], "hints": {}},
    }

    monkeypatch.setattr(AutoMapInline, "call_chat_completion", lambda *args, **kwargs: _dummy_response(payload))
    monkeypatch.setattr(AutoMapInline, "get_openai_client", lambda: object())

    with pytest.raises(MappingInlineValidationError):
        AutoMapInline.run_llm_call_3(
            html,
            catalog,
            schema,
            llm_prompts.PROMPT_VERSION,
            png_path="",
            cache_key="cache-key-rename",
        )


def test_llm_call_3_rejects_date_inline(monkeypatch):
    html = _basic_html()
    catalog = ["reports.report_date"]
    schema = _basic_schema()

    payload = {
        "mapping": {},
        "token_samples": {
            "report_title": "Consumption Report",
            "report_date": "2024-01-01",
        },
        "meta": {"unresolved": [], "hints": {}},
    }

    monkeypatch.setattr(AutoMapInline, "call_chat_completion", lambda *args, **kwargs: _dummy_response(payload))
    monkeypatch.setattr(AutoMapInline, "get_openai_client", lambda: object())

    with pytest.raises(MappingInlineValidationError):
        AutoMapInline.run_llm_call_3(
            html,
            catalog,
            schema,
            llm_prompts.PROMPT_VERSION,
            png_path="",
            cache_key="cache-key-date",
        )


def test_mapping_preview_cache_short_circuit(monkeypatch, tmp_path):
    monkeypatch.setattr(api, "UPLOAD_ROOT", tmp_path)
    monkeypatch.setattr(api, "UPLOAD_ROOT_BASE", tmp_path)

    template_id = str(uuid.uuid4())
    template_dir = tmp_path / template_id
    template_dir.mkdir(parents=True, exist_ok=True)

    initial_html = _basic_html()
    (template_dir / "template_p1.html").write_text(initial_html, encoding="utf-8")
    (template_dir / "source.pdf").write_bytes(b"%PDF-1.4")
    schema_ext = {
        "scalars": ["report_title", "report_date"],
        "row_tokens": [],
        "totals": [],
    }
    (template_dir / "schema_ext.json").write_text(json.dumps(schema_ext), encoding="utf-8")

    tmp_db_path = tmp_path / "dummy.db"
    tmp_db_path.write_bytes(b"\x00")

    monkeypatch.setattr(api, "resolve_db_path", lambda **kwargs: tmp_db_path)
    monkeypatch.setattr(api, "verify_sqlite", lambda path: None)
    monkeypatch.setattr(api, "compute_db_signature", lambda path: "sig")
    monkeypatch.setattr(api, "_build_catalog_from_db", lambda path: ["reports.report_date"])
    monkeypatch.setattr(
        api,
        "get_parent_child_info",
        lambda db_path: {
            "parent table": "reports",
            "child table": "reports",
            "parent_columns": ["report_date"],
            "child_columns": ["report_date"],
        },
    )
    monkeypatch.setattr(api.state_store, "get_template_record", lambda tid: {})
    monkeypatch.setattr(api.state_store, "upsert_template", lambda *args, **kwargs: {})

    applied_html = initial_html.replace("{report_title}", "Consumption Report")

    call_count = {"value": 0}

    def fake_run_llm_call_3(*args, **kwargs) -> MappingInlineResult:
        call_count["value"] += 1
        return MappingInlineResult(
            html_constants_applied=applied_html,
            mapping={"report_date": "reports.report_date"},
            constant_replacements={"report_title": "Consumption Report"},
            token_samples={
                "report_title": "Consumption Report",
                "report_date": "2023-01-01",
            },
            meta={"unresolved": [], "hints": {}},
            prompt_meta={},
            raw_payload={
                "mapping": {"report_date": "reports.report_date"},
                "token_samples": {
                    "report_title": "Consumption Report",
                    "report_date": "2023-01-01",
                },
                "constant_replacements": {"report_title": "Consumption Report"},
                "meta": {"unresolved": [], "hints": {}},
            },
        )

    monkeypatch.setattr(api, "run_llm_call_3", fake_run_llm_call_3)

    request = SimpleNamespace(state=SimpleNamespace(correlation_id="corr"))

    events_first = []
    pipeline_first = api._mapping_preview_pipeline(template_id, "conn", request, correlation_id="corr")
    try:
        while True:
            events_first.append(next(pipeline_first))
    except StopIteration as stop_first:
        response_first = stop_first.value

    assert call_count["value"] == 1
    assert response_first["constant_replacements_count"] == 1
    assert events_first[1]["status"] == "ok"

    # Simulate no further edits to the template (restore original HTML) to validate cache short-circuiting.
    (template_dir / "template_p1.html").write_text(initial_html, encoding="utf-8")

    events_second = []
    pipeline_second = api._mapping_preview_pipeline(template_id, "conn", request, correlation_id="corr")
    try:
        while True:
            events_second.append(next(pipeline_second))
    except StopIteration as stop_second:
        response_second = stop_second.value

    assert call_count["value"] == 1  # no additional LLM call
    assert events_second[1]["status"] == "cached"
    assert response_second["cache_key"] == response_first["cache_key"]


def test_mapping_allowlist_rejects_legacy_wrapper():
    errors = AutoMapInline._mapping_allowlist_errors({"total_set": "DERIVED:SUM(recipes.bin1_sp)"}, ["recipes.bin1_sp"])
    assert errors
    assert "legacy wrapper" in errors[0]


def test_mapping_allowlist_allows_params_reference():
    errors = AutoMapInline._mapping_allowlist_errors({"from_date": "params.from_date"}, ["recipes.bin1_sp"])
    assert errors == []


def test_mapping_allowlist_rejects_unknown_format():
    errors = AutoMapInline._mapping_allowlist_errors({"weird": "some_value"}, ["recipes.bin1_sp"])
    assert errors
    assert "DuckDB SQL expression" in errors[0]


def test_mapping_allowlist_allows_sql_fragment_without_columns():
    errors = AutoMapInline._mapping_allowlist_errors({"count_rows": "COUNT(*)"}, ["recipes.bin1_sp"])
    assert errors == []


def test_mapping_allowlist_allows_current_date_keyword():
    errors = AutoMapInline._mapping_allowlist_errors({"print_date": "CURRENT_DATE"}, [])
    assert errors == []
