from __future__ import annotations

import base64
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

PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
)


@pytest.fixture
def client():
    return TestClient(api.app)


def _make_template_dir(root: Path, template_id: str) -> Path:
    tdir = root / template_id
    tdir.mkdir(parents=True, exist_ok=True)
    # Minimal HTML containing tokens
    html_content = "<html>{material_name} {qty}</html>"
    (tdir / "report_final.html").write_text(html_content, encoding="utf-8")
    (tdir / "template_p1.html").write_text(html_content, encoding="utf-8")
    # Schema tokens for fallback
    schema_payload = {
        "scalars": ["report_title"],
        "row_tokens": ["material_name", "qty"],
        "totals": ["total_qty"],
        "notes": "",
    }
    write_json_atomic(tdir / "schema_ext.json", schema_payload, ensure_ascii=False, indent=2)
    mapping_step3 = {
        "mapping": {
            "report_title": "batches.title",
            "material_name": "lines.material",
            "qty": "lines.qty",
            "total_qty": "lines.qty",
        },
        "meta": {
            "unresolved": [],
        },
    }
    write_json_atomic(tdir / "mapping_step3.json", mapping_step3, ensure_ascii=False, indent=2)
    return tdir


def test_mapping_approve_emits_contract_stage(monkeypatch, tmp_path, client):
    template_id = "00000000-0000-0000-0000-000000000001"
    uploads_root = tmp_path
    monkeypatch.setattr(api, "UPLOAD_ROOT", uploads_root)
    monkeypatch.setattr(api, "UPLOAD_ROOT_BASE", uploads_root)

    template_dir = _make_template_dir(uploads_root, template_id)

    # Prepare a simple sqlite database path (file may remain empty).
    db_path = tmp_path / "db.sqlite"
    db_path.touch()

    monkeypatch.setattr(api, "_db_path_from_payload_or_default", lambda connection_id: db_path)
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
        overview_path.write_text("# Contract Overview\n\n- Details here.", encoding="utf-8")
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
            meta_path,
            {
                "assumptions": [],
                "warnings": [],
                "validation": {},
                "contract_payload": contract_payload,
                "overview_path": "overview.md",
                "step5_requirements_path": "step5_requirements.json",
            },
            ensure_ascii=False,
            indent=2,
        )

        write_artifact_manifest(
            template_dir,
            step="contract_build_v2_test",
            files={
                "overview.md": overview_path,
                "step5_requirements.json": step5_path,
                "contract_v2_meta.json": meta_path,
            },
            inputs=[],
            correlation_id=None,
        )

        return {
            "contract": contract_payload,
            "overview_md": "# Contract Overview\n\n- Details here.",
            "step5_requirements": {},
            "assumptions": [],
            "warnings": [],
            "validation": {
                "unknown_columns": [],
                "unknown_tokens": [],
                "token_coverage": {},
            },
            "artifacts": {
                "overview": overview_path,
                "step5_requirements": step5_path,
                "meta": meta_path,
            },
            "meta": {
                "assumptions": [],
                "warnings": [],
                "validation": {},
                "contract_payload": contract_payload,
            },
            "cached": False,
        }

    monkeypatch.setattr(api, "build_or_load_contract_v2", fake_build_or_load_contract_v2)
    monkeypatch.setattr(api, "render_html_to_png", lambda *_, **__: None)

    def fake_panel(html_path: Path, dest_png: Path, **kwargs):
        dest_png.write_bytes(PNG_BYTES)
        return dest_png

    monkeypatch.setattr(api, "render_panel_preview", fake_panel)

    def fake_build_generator_assets_from_payload(
        *,
        template_dir: Path,
        step4_output,
        final_template_html: str,
        reference_pdf_image,
        catalog_allowlist,
        dialect: str = "duckdb",
        params_spec=None,
        sample_params=None,
        force_rebuild: bool = False,
        key_tokens=None,
        require_contract_join: bool = True,
    ):
        generator_dir = template_dir / "generator"
        generator_dir.mkdir(parents=True, exist_ok=True)
        contract_path = template_dir / "contract.json"
        sql_pack_path = generator_dir / "sql_pack.sql"
        output_schemas_path = generator_dir / "output_schemas.json"
        assets_meta_path = generator_dir / "generator_assets.json"
        write_json_atomic(
            contract_path,
            step4_output.get("contract") or {},
            ensure_ascii=False,
            indent=2,
        )
        sql_pack_path.write_text("-- test sql pack", encoding="utf-8")
        write_json_atomic(
            output_schemas_path,
            {"header": [], "rows": [], "totals": []},
            ensure_ascii=False,
            indent=2,
        )
        write_json_atomic(
            assets_meta_path,
            {
                "needs_user_fix": [],
                "invalid": False,
                "dialect": dialect,
                "params": {"required": params_spec or [], "optional": []},
                "summary": {},
                "dry_run": {"sample_params": sample_params or {}},
            },
            ensure_ascii=False,
            indent=2,
        )
        return {
            "artifacts": {
                "contract": contract_path,
                "sql_pack": sql_pack_path,
                "output_schemas": output_schemas_path,
                "generator_assets": assets_meta_path,
            },
            "needs_user_fix": [],
            "invalid": False,
            "dialect": dialect,
            "params": {"required": params_spec or [], "optional": []},
            "summary": {},
            "dry_run": {"sample_params": sample_params or {}},
            "cached": False,
        }

    monkeypatch.setattr(
        api,
        "build_generator_assets_from_payload",
        fake_build_generator_assets_from_payload,
    )

    payload = {
        "mapping": {
            "report_title": "batches.title",
            "material_name": "lines.material",
            "qty": "lines.qty",
            "total_qty": "lines.qty",
        },
        "connection_id": "test-connection",
        "user_values_text": "",
        "user_instructions": "Summarize contract for testing.",
    }

    response = client.post(
        f"/templates/{template_id}/mapping/approve",
        json=payload,
        headers={"x-correlation-id": "test-correlation"},
    )
    assert response.status_code == 200
    lines = [line for line in response.content.decode("utf-8").splitlines() if line.strip()]
    events = [json.loads(line) for line in lines]

    stage_events = [evt for evt in events if evt.get("event") == "stage" and evt.get("stage") == "contract_build_v2"]
    assert stage_events, "Expected contract_build_v2 stage events"
    assert stage_events[0]["contract_ready"] is False
    assert stage_events[0].get("blueprint_ready") is True
    assert "overview_md" in stage_events[0]
    assert stage_events[-1]["contract_ready"] is True
    generator_stage_events = [
        evt for evt in events if evt.get("event") == "stage" and evt.get("stage") == "generator_assets_v1"
    ]
    assert generator_stage_events, "Expected generator_assets_v1 stage event"
    assert "contract" in (generator_stage_events[-1].get("artifacts") or {})

    result_events = [evt for evt in events if evt.get("event") == "result"]
    assert result_events, "Expected final result event"
    final_event = result_events[-1]
    assert final_event.get("contract_stage", {}).get("stage") == "contract_build_v2"
    assert final_event.get("generator_stage", {}).get("stage") == "generator_assets_v1"
    assert final_event.get("contract_stage", {}).get("contract_ready") is True
    assert (template_dir / "contract.json").exists()
