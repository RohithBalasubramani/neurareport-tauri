from __future__ import annotations

import importlib
import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


api = importlib.import_module("backend.api")
utils_module = importlib.import_module("backend.app.services.utils")
write_artifact_manifest = utils_module.write_artifact_manifest
write_json_atomic = utils_module.write_json_atomic
contract_test_module = importlib.import_module("backend.tests.test_api_mapping_approve_contract_v2")
PNG_BYTES = contract_test_module.PNG_BYTES
_make_template_dir = contract_test_module._make_template_dir


@pytest.fixture
def client():
    return TestClient(api.app)


def test_manifest_contains_contract_artifacts(monkeypatch, tmp_path, client):
    template_id = "00000000-0000-0000-0000-000000000002"
    uploads_root = tmp_path
    monkeypatch.setattr(api, "UPLOAD_ROOT", uploads_root)
    monkeypatch.setattr(api, "UPLOAD_ROOT_BASE", uploads_root)

    template_dir = _make_template_dir(uploads_root, template_id)

    db_path = tmp_path / "db.sqlite"
    db_path.touch()

    monkeypatch.setattr(api, "_db_path_from_payload_or_default", lambda _: db_path)
    monkeypatch.setattr(
        api,
        "get_parent_child_info",
        lambda _: {
            "parent table": "batches",
            "child table": "lines",
            "parent_columns": ["batch_id", "batch_date"],
            "child_columns": ["batch_id", "line_date", "material", "qty"],
        },
    )
    monkeypatch.setattr(api, "compute_db_signature", lambda _: "sig")

    def fake_build_or_load_contract_v2(
        *,
        template_dir: Path,
        catalog,
        final_template_html: str,
        schema,
        auto_mapping_proposal,
        mapping_override,
        user_instructions: str,
        dialect_hint: str | None,
        db_signature: str | None = None,
        key_tokens=None,
        prompt_builder=None,
        prompt_version=None,
    ):
        contract_path = template_dir / "contract.json"
        overview_path = template_dir / "overview.md"
        step5_path = template_dir / "step5_requirements.json"
        meta_path = template_dir / "contract_v2_meta.json"

        contract_payload = {
            "tokens": schema,
            "mapping": auto_mapping_proposal.get("mapping", {}),
            "join": {
                "parent_table": "batches",
                "parent_key": "batch_id",
                "child_table": "lines",
                "child_key": "batch_id",
            },
            "date_columns": {"batches": "batch_date", "lines": "line_date"},
            "reshape_rules": [],
            "row_computed": {},
            "totals_math": {},
            "formatters": {},
            "order_by": {"rows": ["material_name ASC"]},
            "filters": {},
        }
        write_json_atomic(contract_path, contract_payload, ensure_ascii=False, indent=2)
        overview_path.write_text("# Contract Overview", encoding="utf-8")
        write_json_atomic(
            step5_path,
            {
                "datasets": {},
                "parameters": {},
                "transformations": [],
                "edge_cases": [],
                "dialect_notes": [],
                "artifact_expectations": {},
            },
            ensure_ascii=False,
            indent=2,
        )
        write_json_atomic(
            meta_path, {"assumptions": [], "warnings": [], "validation": {}}, ensure_ascii=False, indent=2
        )

        write_artifact_manifest(
            template_dir,
            step="contract_build_v2_test",
            files={
                "contract.json": contract_path,
                "overview.md": overview_path,
                "step5_requirements.json": step5_path,
                "contract_v2_meta.json": meta_path,
            },
            inputs=[],
            correlation_id=None,
        )

        return {
            "contract": contract_payload,
            "overview_md": "# Contract Overview",
            "step5_requirements": {},
            "assumptions": [],
            "warnings": [],
            "validation": {"unknown_columns": [], "unknown_tokens": [], "token_coverage": {}},
            "artifacts": {
                "contract": contract_path,
                "overview": overview_path,
                "step5_requirements": step5_path,
                "meta": meta_path,
            },
            "meta": {"assumptions": [], "warnings": [], "validation": {}},
            "cached": False,
        }

    monkeypatch.setattr(api, "build_or_load_contract_v2", fake_build_or_load_contract_v2)
    monkeypatch.setattr(api, "render_html_to_png", lambda *_, **__: None)

    def fake_panel(html_path: Path, dest_png: Path, **kwargs):
        dest_png.write_bytes(PNG_BYTES)
        return dest_png

    monkeypatch.setattr(api, "render_panel_preview", fake_panel)

    payload = {
        "mapping": {
            "report_title": "batches.title",
            "material_name": "lines.material",
            "qty": "lines.qty",
            "total_qty": "lines.qty",
        },
        "connection_id": "test-connection",
        "user_values_text": "",
        "user_instructions": "Manifest check instruction.",
    }

    response = client.post(
        f"/templates/{template_id}/mapping/approve",
        json=payload,
        headers={"x-correlation-id": "manifest-test"},
    )
    assert response.status_code == 200

    manifest_path = template_dir / "artifact_manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("files", {})
    assert "overview.md" in files
    assert "step5_requirements.json" in files
