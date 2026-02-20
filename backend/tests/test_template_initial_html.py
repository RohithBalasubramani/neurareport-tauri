from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.app.services.templates import TemplateVerify as tv
from backend.app.services.utils import write_json_atomic
from backend.app.services.utils.artifacts import MANIFEST_NAME, write_artifact_manifest


class _DummyMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _DummyChoice:
    def __init__(self, content: str) -> None:
        self.message = _DummyMessage(content)


class _DummyResponse:
    def __init__(self, content: str) -> None:
        self.choices = [_DummyChoice(content)]


def _make_png(path: Path) -> None:
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"  # PNG signature
        b"\x00\x00\x00\rIHDR"  # minimal header chunk (width/height zeroed ok for base64)
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
        b"\x90wS\xde\x00\x00\x00\x00IEND\xaeB`\x82"
    )


@pytest.fixture
def stubbed_llm(monkeypatch):
    def factory(content: str):
        def _fake_call(client, **kwargs):
            return _DummyResponse(content)

        monkeypatch.setattr(tv, "call_chat_completion", _fake_call)
        monkeypatch.setattr(tv, "get_openai_client", lambda: object())

    return factory


def test_request_initial_html_with_schema(tmp_path: Path, stubbed_llm):
    html_section = """<!DOCTYPE html>
<html><body><span class="title">{{ report_title }}</span><table><tr><td>{line_amount}</td></tr></table><footer>{grand_total}</footer></body></html>"""
    schema_section = json.dumps(
        {
            "scalars": ["report_title"],
            "row_tokens": ["line_amount"],
            "totals": ["grand_total"],
            "notes": "",
        }
    )
    content = f"""<!--BEGIN_HTML-->
{html_section}
<!--END_HTML-->
<!--BEGIN_SCHEMA_JSON-->
{schema_section}
<!--END_SCHEMA_JSON-->"""

    stubbed_llm(content)

    png_path = tmp_path / "reference_p1.png"
    _make_png(png_path)
    pdf_path = tmp_path / "source.pdf"
    pdf_path.write_bytes(b"%PDF")

    result = tv.request_initial_html(png_path, schema_json={}, layout_hints=None)
    assert result.schema == {
        "scalars": ["report_title"],
        "row_tokens": ["line_amount"],
        "totals": ["grand_total"],
        "notes": "",
    }
    assert "{report_title}" in result.html
    assert "{{" not in result.html

    html_path = tmp_path / "template_p1.html"
    tv.save_html(html_path, result.html)
    assert html_path.exists()

    schema_path = tmp_path / "schema_ext.json"
    write_json_atomic(
        schema_path,
        result.schema,
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
        step="test_schema_ext",
    )
    payload = json.loads(schema_path.read_text(encoding="utf-8"))
    assert payload["scalars"] == ["report_title"]

    manifest_path = write_artifact_manifest(
        tmp_path,
        step="unit_test",
        files={
            "source.pdf": pdf_path,
            "reference_p1.png": png_path,
            "template_p1.html": html_path,
            "schema_ext.json": schema_path,
        },
        inputs=[str(pdf_path)],
        correlation_id="unit",
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert MANIFEST_NAME == manifest_path.name
    assert "schema_ext.json" in manifest["files"]


def test_request_initial_html_without_schema(tmp_path: Path, stubbed_llm):
    html_section = "<html><body><p>{{missing_schema}}</p></body></html>"
    content = f"""<!--BEGIN_HTML-->
{html_section}
<!--END_HTML-->"""

    stubbed_llm(content)

    png_path = tmp_path / "reference_p1.png"
    _make_png(png_path)

    result = tv.request_initial_html(png_path, schema_json=None, layout_hints=None)
    assert result.schema is None
    assert "{missing_schema}" in result.html
    assert "{{" not in result.html

    html_path = tmp_path / "template_p1.html"
    tv.save_html(html_path, result.html)
    assert html_path.exists()
    saved_html = html_path.read_text(encoding="utf-8")
    assert "{missing_schema}" in saved_html

    # ensure schema file is not created when schema is absent
    schema_path = tmp_path / "schema_ext.json"
    assert not schema_path.exists()
