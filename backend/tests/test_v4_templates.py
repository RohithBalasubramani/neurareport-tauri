from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path

import pytest
from starlette.datastructures import UploadFile

from backend.app.utils.errors import AppError
from backend.app.services.templates.service import TemplateService
from backend.app.repositories.state import StateStore


def _zip_bytes(contents: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w") as zf:
        for name, data in contents.items():
            zf.writestr(name, data)
    return buf.getvalue()


@pytest.fixture()
def temp_state(tmp_path, monkeypatch):
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    os.environ["NEURA_STATE_DIR"] = str(state_dir)
    store = StateStore(base_dir=state_dir)
    # Patch global used by TemplateService to isolate tests
    import backend.app.services.templates.service as tsvc

    tsvc.state_store = store
    return store


@pytest.mark.asyncio
async def test_template_import_writes_state(temp_state, tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    excel_uploads = tmp_path / "excel"
    excel_uploads.mkdir()

    manifest_payload = b'{"artifacts":{"template_html_url":"/uploads/x.html"}}'
    zip_bytes = _zip_bytes(
        {
            "artifact_manifest.json": manifest_payload,
            "template_p1.html": b"<html></html>",
        }
    )
    upload = UploadFile(filename="tpl.zip", file=io.BytesIO(zip_bytes))

    service = TemplateService(uploads_root=uploads, excel_uploads_root=excel_uploads, max_bytes=1024 * 1024)
    result = await service.import_zip(upload, display_name="My Template", correlation_id="cid-123")

    assert result["template_id"]
    assert temp_state.list_templates()
    rec = temp_state.list_templates()[0]
    assert rec["name"] == "My Template"
    assert rec["artifacts"].get("template_html_url")


@pytest.mark.asyncio
async def test_template_import_rejects_oversize(tmp_path, monkeypatch):
    uploads = tmp_path / "uploads"
    excel_uploads = tmp_path / "excel"
    uploads.mkdir()
    excel_uploads.mkdir()
    big_bytes = b"a" * 2048
    upload = UploadFile(filename="big.zip", file=io.BytesIO(big_bytes))
    service = TemplateService(uploads_root=uploads, excel_uploads_root=excel_uploads, max_bytes=64)
    with pytest.raises(AppError) as exc:
        await service.import_zip(upload, display_name=None, correlation_id=None)
    assert exc.value.code == "upload_too_large"
