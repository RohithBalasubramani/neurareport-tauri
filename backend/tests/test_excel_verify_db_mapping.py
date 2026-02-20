from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from backend.app.services.excel import ExcelVerify as excel_verify_module
from backend.app.services.excel.ExcelVerify import xlsx_to_html_preview

openpyxl = pytest.importorskip("openpyxl")


def _make_sample_db(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE flows (
                timestamp_utc TEXT,
                di_raw_inlet_fm_3 REAL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE meta (
                plant TEXT,
                operator TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _make_sample_xlsx(xlsx_path: Path) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sample Sheet"
    ws.append(["DATE", "DI_RAW_INLET_FM_3"])
    ws.append(["2024-01-01", 123.45])
    wb.save(xlsx_path)


def test_excel_preview_injects_db_placeholders(tmp_path, monkeypatch):
    db_path = tmp_path / "sample.db"
    _make_sample_db(db_path)

    xlsx_path = tmp_path / "sample.xlsx"
    _make_sample_xlsx(xlsx_path)

    render_calls: list[Path] = []

    def fake_render_html_to_png(html_path: Path, out_png_path: Path, *, page_size: str = "A4", dpi: int = 144) -> None:
        render_calls.append(html_path)
        out_png_path.write_bytes(b"fake")

    # Mock the LLM call to prevent real API calls
    def fake_call_chat_completion(*args, **kwargs):
        # Create a mock response object with the expected structure
        class MockMessage:
            content = """<!--BEGIN_HTML-->
<html><head><meta charset='utf-8'>
<style>
  @page { size: A4; margin: 24mm; }
  body { font-family: Arial; }
  table { border-collapse: collapse; width: 100%; }
  th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
</style></head><body>
<table><thead><tr><th data-label="date">DATE</th><th data-label="di_raw_inlet_fm_3">DI_RAW_INLET_FM_3</th></tr></thead>
<tbody><tr><td>{row_date}</td><td>{row_di_raw_inlet_fm_3}</td></tr></tbody></table></body></html>
<!--END_HTML-->
<!--BEGIN_SCHEMA_JSON-->
{"columns": [{"column": "DATE", "tag": "date"}, {"column": "DI_RAW_INLET_FM_3", "tag": "di_raw_inlet_fm_3"}]}
<!--END_SCHEMA_JSON-->"""

        class MockChoice:
            message = MockMessage()

        class MockResponse:
            choices = [MockChoice()]

        return MockResponse()

    monkeypatch.setattr(excel_verify_module, "render_html_to_png", fake_render_html_to_png)
    monkeypatch.setattr(excel_verify_module, "call_chat_completion", fake_call_chat_completion)

    out_dir = tmp_path / "out"
    result = xlsx_to_html_preview(xlsx_path, out_dir, db_path=db_path)

    assert result.html_path.exists()
    assert result.png_path and result.png_path.exists()
    html_text = result.html_path.read_text(encoding="utf-8")

    assert '<th data-label="date">DATE</th>' in html_text
    assert '<th data-label="di_raw_inlet_fm_3">DI_RAW_INLET_FM_3</th>' in html_text
    assert "{row_date}" in html_text
    assert "{row_di_raw_inlet_fm_3}" in html_text
    assert "2024-01-01" not in html_text
    assert html_text.count("<tr>") == 2
    assert render_calls, "Expected preview PNG render to be invoked"
