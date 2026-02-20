import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.app.services.mapping import CorrectionsPreview as cp_module
from backend.app.services.mapping.CorrectionsPreview import run_corrections_preview

TEMPLATE_HTML = """<!doctype html>
<html>
  <body>
    <h1>{report_title}</h1>
    <!--BEGIN:BLOCK_REPEAT rows-->
    <table data-region="rows">
      <tbody>
        <tr><td>{row_value}</td></tr>
      </tbody>
    </table>
    <!--END:BLOCK_REPEAT rows-->
  </body>
</html>"""


FAKE_RESPONSE = {
    "final_template_html": TEMPLATE_HTML,
    "page_summary": ("Full-width header titled {report_title}, followed by a single-column table listing {row_value}."),
}


def _fake_response():
    content = json.dumps(FAKE_RESPONSE)
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


def write_fixture_files(base_dir: Path):
    base_dir.mkdir(parents=True, exist_ok=True)
    (base_dir / "template_p1.html").write_text(TEMPLATE_HTML, encoding="utf-8")
    (base_dir / "reference_p1.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    mapping_payload = {
        "mapping": {"row_value": "reports.value"},
        "meta": {"unresolved": ["row_value"]},
    }
    (base_dir / "mapping_step3.json").write_text(json.dumps(mapping_payload), encoding="utf-8")
    schema_payload = {
        "scalars": ["report_title"],
        "row_tokens": ["row_value"],
        "totals": [],
        "notes": "",
    }
    (base_dir / "schema_ext.json").write_text(json.dumps(schema_payload), encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def monkeypatched_llm(monkeypatch):
    monkeypatch.setattr(cp_module, "get_openai_client", lambda: object())
    monkeypatch.setattr(cp_module, "call_chat_completion", lambda *args, **kwargs: _fake_response())


def test_corrections_preview_integration(tmp_path, monkeypatched_llm):
    upload_dir = tmp_path / "tmpl"
    write_fixture_files(upload_dir)

    result = run_corrections_preview(
        upload_dir=upload_dir,
        template_html_path=upload_dir / "template_p1.html",
        mapping_step3_path=upload_dir / "mapping_step3.json",
        schema_ext_path=upload_dir / "schema_ext.json",
        user_input="Fix spelling mistakes",
        page_png_path=upload_dir / "reference_p1.png",
        model_selector="test-model",
    )

    assert result["summary"]["constants_inlined"] == 0
    assert "page_summary" in result["processed"]
    assert result["processed"]["page_summary"]
    assert not result["cache_hit"]

    template_html_after = (upload_dir / "template_p1.html").read_text(encoding="utf-8")
    page_summary_text = (upload_dir / "page_summary.txt").read_text(encoding="utf-8")
    stage_payload = read_json(upload_dir / "stage_3_5.json")

    assert template_html_after == TEMPLATE_HTML
    assert "header" in page_summary_text.lower()
    assert stage_payload["cache_key"] == result["cache_key"]

    manifest = read_json(upload_dir / "artifact_manifest.json")
    files = manifest["files"]
    assert "page_summary.txt" in files.values()

    mapping_labels = read_json(upload_dir / "mapping_pdf_labels.json")
    assert mapping_labels == [{"header": "row_value", "placeholder": "{row_value}", "mapping": "reports.value"}]

    # Second run should be served from cache.
    cached = run_corrections_preview(
        upload_dir=upload_dir,
        template_html_path=upload_dir / "template_p1.html",
        mapping_step3_path=upload_dir / "mapping_step3.json",
        schema_ext_path=upload_dir / "schema_ext.json",
        user_input="Fix spelling mistakes",
        page_png_path=upload_dir / "reference_p1.png",
        model_selector="test-model",
    )
    assert cached["cache_hit"]
    assert cached["cache_key"] == result["cache_key"]


def test_corrections_preview_updates_mapping_override(tmp_path, monkeypatched_llm):
    upload_dir = tmp_path / "tmpl"
    write_fixture_files(upload_dir)

    run_corrections_preview(
        upload_dir=upload_dir,
        template_html_path=upload_dir / "template_p1.html",
        mapping_step3_path=upload_dir / "mapping_step3.json",
        schema_ext_path=upload_dir / "schema_ext.json",
        user_input="",
        page_png_path=upload_dir / "reference_p1.png",
        model_selector="test-model",
        mapping_override={"row_value": "INPUT_SAMPLE", "extra_token": "params.foo"},
    )

    mapping_labels = read_json(upload_dir / "mapping_pdf_labels.json")
    assert mapping_labels[0]["mapping"] == "INPUT_SAMPLE"
    # Extra keys should be added as new entries
    headers = {entry["header"] for entry in mapping_labels}
    assert {"row_value", "extra_token"} <= headers


def test_mapping_labels_display_alias_for_report_selected(tmp_path, monkeypatched_llm):
    upload_dir = tmp_path / "tmpl"
    write_fixture_files(upload_dir)

    mapping_path = upload_dir / "mapping_step3.json"
    mapping_doc = read_json(mapping_path)
    mapping_doc["mapping"]["from_date"] = "INPUT_SAMPLE"
    mapping_doc["mapping"]["page_info"] = "INPUT_SAMPLE"
    mapping_path.write_text(json.dumps(mapping_doc), encoding="utf-8")

    schema_path = upload_dir / "schema_ext.json"
    schema_doc = read_json(schema_path)
    schema_doc["scalars"].extend(["from_date", "page_info"])
    schema_path.write_text(json.dumps(schema_doc), encoding="utf-8")

    run_corrections_preview(
        upload_dir=upload_dir,
        template_html_path=upload_dir / "template_p1.html",
        mapping_step3_path=mapping_path,
        schema_ext_path=schema_path,
        user_input="",
        page_png_path=upload_dir / "reference_p1.png",
        model_selector="test-model",
    )

    mapping_labels = read_json(upload_dir / "mapping_pdf_labels.json")
    alias_entries = {
        entry["header"]: entry["mapping"] for entry in mapping_labels if entry["header"] in {"from_date", "page_info"}
    }
    assert alias_entries == {
        "from_date": "To Be Selected in report generator",
        "page_info": "To Be Selected in report generator",
    }
