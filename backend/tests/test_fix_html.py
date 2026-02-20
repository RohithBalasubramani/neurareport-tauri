from __future__ import annotations

import asyncio
import base64
import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import backend.api as api
from backend.app.services.templates import TemplateVerify as tv

PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
)


def _write_png(path: Path) -> None:
    path.write_bytes(PNG_BYTES)


def _make_initial_html() -> str:
    return """<!DOCTYPE html>
<html>
<head>
<style>
table { width: 100%; border-collapse: collapse; }
</style>
</head>
<body>
<table id="data-table">
<thead>
  <tr><th data-label="amount">{amount_label}</th></tr>
</thead>
<tbody>
<!-- BEGIN:BLOCK_REPEAT ROW -->
  <tr><td>{amount}</td></tr>
<!-- END:BLOCK_REPEAT ROW -->
</tbody>
</table>
</body>
</html>"""


def test_request_fix_html_success(monkeypatch, tmp_path: Path) -> None:
    html_path = tmp_path / "template_p1.html"
    html_path.write_text(_make_initial_html(), encoding="utf-8")

    reference_png = tmp_path / "reference_p1.png"
    render_png = tmp_path / "render_p1.png"
    _write_png(reference_png)
    _write_png(render_png)

    schema_path = tmp_path / "schema_ext.json"
    schema_path.write_text(json.dumps({"scalars": ["{amount}"]}), encoding="utf-8")

    refined_html = _make_initial_html().replace(
        "border-collapse: collapse;",
        "border-collapse: collapse; border: 0.2mm solid #000;",
    )

    def fake_call_chat_completion(client, model, messages, description):
        content = f"<!--BEGIN_HTML-->{refined_html}<!--END_HTML-->"
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])

    render_calls: list[Path] = []

    def fake_render_html_to_png(html_path_arg: Path, out_png_path: Path, *, page_size: str = "A4") -> None:
        render_calls.append(out_png_path)
        _write_png(out_png_path)

    monkeypatch.setattr(tv, "get_openai_client", lambda: object())
    monkeypatch.setattr(tv, "call_chat_completion", fake_call_chat_completion)
    monkeypatch.setattr(tv, "render_html_to_png", fake_render_html_to_png)

    def fake_panel_preview(html_path_arg: Path, dest_png: Path, **kwargs) -> Path:
        dest_png.write_bytes(PNG_BYTES)
        return dest_png

    monkeypatch.setattr(tv, "render_panel_preview", fake_panel_preview)
    result = tv.request_fix_html(
        tmp_path,
        html_path,
        schema_path,
        reference_png,
        render_png,
        0.9123,
    )

    assert result["accepted"] is True
    assert render_calls, "expected render_html_to_png to run"
    refined_text = html_path.read_text(encoding="utf-8")
    assert "0.2mm solid" in refined_text

    metrics_path: Path = result["metrics_path"]
    assert metrics_path.exists()
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert metrics == {
        "accepted": True,
        "rejected_reason": None,
    }
    render_after: Path = result["render_after_path"]
    assert render_after.exists()


def test_request_fix_html_reject_token_drift(monkeypatch, tmp_path: Path) -> None:
    html_path = tmp_path / "template_p1.html"
    html_path.write_text(_make_initial_html(), encoding="utf-8")

    reference_png = tmp_path / "reference_p1.png"
    render_png = tmp_path / "render_p1.png"
    _write_png(reference_png)
    _write_png(render_png)

    drifted_html = _make_initial_html().replace("{amount}", "{amount_new}")

    def fake_call_chat_completion(client, model, messages, description):
        content = f"<!--BEGIN_HTML-->{drifted_html}<!--END_HTML-->"
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])

    monkeypatch.setattr(tv, "get_openai_client", lambda: object())
    monkeypatch.setattr(tv, "call_chat_completion", fake_call_chat_completion)
    monkeypatch.setattr(
        tv,
        "render_html_to_png",
        lambda *args, **kwargs: pytest.fail("render_html_to_png should not run on rejection"),
    )
    monkeypatch.setattr(
        tv,
        "render_panel_preview",
        lambda *args, **kwargs: pytest.fail("render_panel_preview should not run on rejection"),
    )
    result = tv.request_fix_html(
        tmp_path,
        html_path,
        None,
        reference_png,
        render_png,
        0.91,
    )

    assert result["accepted"] is False
    assert result["rejected_reason"] == "token_drift"
    metrics = json.loads(result["metrics_path"].read_text(encoding="utf-8"))
    assert metrics == {"accepted": False, "rejected_reason": "token_drift"}
    assert not (tmp_path / "render_p1_after.png").exists()
    roundtrip_html = html_path.read_text(encoding="utf-8")
    assert "{amount}" in roundtrip_html


def test_fix_html_refine_stage_runs_even_when_target_met(monkeypatch, tmp_path: Path) -> None:
    # Ensure uploads land in temp sandbox
    monkeypatch.setattr(api, "UPLOAD_ROOT", tmp_path)
    monkeypatch.setattr(api, "UPLOAD_ROOT_BASE", tmp_path.resolve())

    # Stub state store to avoid global mutations
    class _DummyState:
        def upsert_template(self, *args, **kwargs):
            return None

        def set_last_used(self, *args, **kwargs):
            return None

    monkeypatch.setattr(api, "state_store", _DummyState())

    # Patch pipeline helpers
    def fake_pdf_to_pngs(pdf_path: Path, out_dir: Path, dpi: int = 400):
        target = out_dir / "reference_p1.png"
        _write_png(target)
        return [target]

    monkeypatch.setattr(api, "pdf_to_pngs", fake_pdf_to_pngs)
    monkeypatch.setattr(api, "get_layout_hints", lambda *args, **kwargs: {})

    initial_html = _make_initial_html()
    initial_result = SimpleNamespace(html=initial_html, schema=None)
    monkeypatch.setattr(api, "request_initial_html", lambda *args, **kwargs: initial_result)
    monkeypatch.setattr(api, "save_html", lambda path, text: Path(path).write_text(text, encoding="utf-8"))

    monkeypatch.setattr(api, "rasterize_html_to_png", lambda *args, **kwargs: PNG_BYTES)

    def fake_save_png(data: bytes, out_path: str) -> str:
        Path(out_path).write_bytes(data)
        return out_path

    monkeypatch.setattr(api, "save_png", fake_save_png)

    render_calls: list[Path] = []

    def fake_render_html_to_png(html_path: Path, out_png_path: Path, *, page_size: str = "A4") -> None:
        render_calls.append(out_png_path)
        _write_png(out_png_path)

    monkeypatch.setattr(api, "render_html_to_png", fake_render_html_to_png)

    def fake_panel(html_path: Path, dest_png: Path, **kwargs):
        dest_png.write_bytes(PNG_BYTES)
        return dest_png

    monkeypatch.setattr(api, "render_panel_preview", fake_panel)

    fix_calls: list[tuple] = []

    def fake_request_fix_html(
        template_dir: Path,
        html_path: Path,
        schema_path,
        reference_png: Path,
        render_png: Path,
        ssim_before: float,
    ):
        fix_calls.append((template_dir, html_path, reference_png, render_png, ssim_before))
        render_after = template_dir / "render_p1_after.png"
        render_after_full = template_dir / "render_p1_after_full.png"
        _write_png(render_after)
        _write_png(render_after_full)
        metrics_path = template_dir / "fix_metrics.json"
        metrics_path.write_text("{}", encoding="utf-8")
        return {
            "accepted": True,
            "rejected_reason": None,
            "render_after_path": render_after,
            "render_after_full_path": render_after_full,
            "metrics_path": metrics_path,
            "raw_response": "<!--BEGIN_HTML--><!--END_HTML-->",
        }

    monkeypatch.setattr(api, "request_fix_html", fake_request_fix_html)

    manifest_calls: list[dict] = []

    def fake_write_artifact_manifest(template_dir: Path, *, step: str, files: dict, inputs, correlation_id):
        manifest_calls.append(files)
        target = template_dir / "artifact_manifest.json"
        target.write_text("{}", encoding="utf-8")
        return target

    monkeypatch.setattr(api, "write_artifact_manifest", fake_write_artifact_manifest)

    monkeypatch.setenv("VERIFY_FIX_HTML_ENABLED", "true")
    monkeypatch.setenv("MAX_FIX_PASSES", "1")

    async def _run_verification() -> None:
        upload = api.UploadFile(file=io.BytesIO(b"%PDF-1.4\n"), filename="source.pdf")
        response = await api.verify_template(file=upload, connection_id="conn-1", refine_iters=0, request=None)

        chunks = [chunk async for chunk in response.body_iterator]
        events = []
        for chunk in chunks:
            text = chunk.decode("utf-8").strip()
            if not text:
                continue
            for part in text.split("`n"):
                part = part.strip()
                if part:
                    events.append(json.loads(part))

        fix_stage = next(
            ev
            for ev in events
            if ev.get("event") == "stage"
            and ev.get("label") == "Refining HTML layout fidelity..."
            and ev.get("status") == "complete"
        )
        assert fix_calls, "refinement pass should run"
        assert fix_stage["skipped"] is False
        assert fix_stage["fix_attempted"] is True
        assert fix_stage["fix_accepted"] is True

        result_event = next(ev for ev in events if ev.get("event") == "result")
        assert "render_png_url" in result_event["artifacts"]
        assert "render_after_png_url" in result_event["artifacts"]

        assert manifest_calls, "artifact manifest should be recorded"
        manifest_files = manifest_calls[-1]
        assert "render_p1.png" in manifest_files
        assert "render_p1_llm.png" in manifest_files
        assert "render_p1_after.png" in manifest_files
        assert "render_p1_after_full.png" in manifest_files
        assert "fix_metrics.json" in manifest_files

    asyncio.run(_run_verification())
