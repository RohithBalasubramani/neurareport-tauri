from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
)


def _write_png(path: Path) -> None:
    path.write_bytes(PNG_BYTES)



from backend import api  # noqa: E402
from backend.app.repositories.state import StateStore  # noqa: E402
from backend.app.services.utils import (  # noqa: E402
    write_artifact_manifest,
    write_json_atomic,
)


@pytest.fixture
def client(tmp_path, monkeypatch):
    uploads_root = tmp_path / "uploads"
    uploads_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(api, "UPLOAD_ROOT", uploads_root)
    monkeypatch.setattr(api, "UPLOAD_ROOT_BASE", uploads_root)
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    test_state_store = StateStore(state_dir)
    monkeypatch.setattr(api, "state_store", test_state_store)
    monkeypatch.setattr("backend.app.repositories.state.state_store", test_state_store)
    monkeypatch.setattr("backend.app.repositories.state.store.state_store", test_state_store)
    return TestClient(api.app)


def _setup_template_dir(root: Path, template_id: str) -> Path:
    tdir = root / template_id
    tdir.mkdir(parents=True, exist_ok=True)
    # minimal persisted artifacts from prior steps
    (tdir / "overview.md").write_text("# Overview", encoding="utf-8")
    write_json_atomic(
        tdir / "step5_requirements.json",
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
    _write_png(tdir / "reference_p1.png")
    return tdir


def _fake_service(template_dir: Path, *, dialect: str, invalid: bool, needs: list[str]) -> Dict[str, Any]:
    generator_dir = template_dir / "generator"
    generator_dir.mkdir(parents=True, exist_ok=True)
    contract_path = template_dir / "contract.json"
    write_json_atomic(
        contract_path,
        {"tokens": {"scalars": ["h1"], "row_tokens": ["r1"], "totals": ["t1"]}},
        ensure_ascii=False,
        indent=2,
    )
    sql_path = generator_dir / "sql_pack.sql"
    sql_path.write_text("-- SQL SCRIPT", encoding="utf-8")
    output_schemas_path = generator_dir / "output_schemas.json"
    output_payload = {"header": ["h1"], "rows": ["r1"], "totals": ["t1"]}
    write_json_atomic(output_schemas_path, output_payload, ensure_ascii=False, indent=2)
    meta_path = generator_dir / "generator_assets.json"
    meta_payload = {
        "dialect": dialect,
        "params": {"required": ["from_date", "to_date"], "optional": []},
        "entrypoints": {"header": "SELECT 1 AS h1", "rows": "SELECT 1 AS r1", "totals": "SELECT 1 AS t1"},
        "needs_user_fix": needs,
        "notes": "",
        "invalid": invalid,
        "dry_run": None,
        "summary": {"mock": True},
    }
    write_json_atomic(meta_path, meta_payload, ensure_ascii=False, indent=2)

    write_artifact_manifest(
        template_dir,
        step="generator_assets_v1_test",
        files={
            "contract.json": contract_path,
            "sql_pack.sql": sql_path,
            "output_schemas.json": output_schemas_path,
            "generator_assets.json": meta_path,
        },
        inputs=["test"],
        correlation_id=None,
    )

    return {
        "artifacts": {
            "contract": contract_path,
            "sql_pack": sql_path,
            "output_schemas": output_schemas_path,
            "generator_assets": meta_path,
        },
        "needs_user_fix": needs,
        "invalid": invalid,
        "dialect": dialect,
        "params": meta_payload["params"],
        "dry_run": None,
        "cached": False,
        "summary": meta_payload["summary"],
    }


def _parse_events(response):
    lines = [line for line in response.content.decode("utf-8").splitlines() if line.strip()]
    return [json.loads(line) for line in lines]


def _request_payload() -> dict[str, Any]:
    return {
        "step4_output": {
            "contract": {"tokens": {"scalars": ["h1"], "row_tokens": ["r1"], "totals": ["t1"]}},
            "overview_md": "# Overview",
            "step5_requirements": {},
        },
        "final_template_html": "<html>{h1}</html>",
        "reference_pdf_image": None,
        "catalog": ["batches.h1"],
        "dialect": "duckdb",
        "params": ["from_date", "to_date"],
        "sample_params": {"from_date": "2025-01-01", "to_date": "2025-01-31"},
        "force_rebuild": False,
    }


def test_generator_assets_v1_happy_path(tmp_path, client, monkeypatch):
    template_id = "00000000-0000-0000-0000-000000000002"
    template_dir = _setup_template_dir(api.UPLOAD_ROOT, template_id)

    def fake_build(*, template_dir: Path, dialect: str, **kwargs: Any) -> Dict[str, Any]:
        return _fake_service(template_dir, dialect=dialect, invalid=False, needs=[])

    monkeypatch.setattr(api, "build_generator_assets_from_payload", fake_build)

    response = client.post(f"/templates/{template_id}/generator-assets/v1", json=_request_payload())
    assert response.status_code == 200
    events = _parse_events(response)
    result_event = next(evt for evt in events if evt.get("event") == "result")
    data = result_event
    assert data["invalid"] is False
    assert data["needs_user_fix"] == []
    assert data["dialect"] == "duckdb"
    assert data["params"]["required"] == ["from_date", "to_date"]

    assert data["artifacts"].get("contract")
    generator_dir = template_dir / "generator"
    assert (generator_dir / "sql_pack.sql").exists()
    assert (generator_dir / "output_schemas.json").exists()
    assert (generator_dir / "generator_assets.json").exists()
    assert (template_dir / "contract.json").exists()
    manifest_path = template_dir / "artifact_manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "contract.json" in manifest["files"]
    assert "sql_pack.sql" in manifest["files"]
    templates_state = api.state_store.list_templates()
    tpl_record = next(t for t in templates_state if t["id"] == template_id)
    assert tpl_record["artifacts"].get("contract_url")
    assert tpl_record["artifacts"].get("generator_sql_pack_url")
    generator_meta = tpl_record.get("generator") or {}
    assert generator_meta.get("dialect") == "duckdb"
    assert generator_meta.get("invalid") is False
    assert generator_meta.get("needsUserFix") == []


def test_generator_assets_v1_allowlist_violation(tmp_path, client, monkeypatch):
    template_id = "00000000-0000-0000-0000-000000000003"
    _setup_template_dir(api.UPLOAD_ROOT, template_id)

    def fake_build(*, template_dir: Path, dialect: str, **kwargs: Any) -> Dict[str, Any]:
        return _fake_service(template_dir, dialect=dialect, invalid=True, needs=["catalog_violation:lines.unknown"])

    monkeypatch.setattr(api, "build_generator_assets_from_payload", fake_build)

    response = client.post(f"/templates/{template_id}/generator-assets/v1", json=_request_payload())
    assert response.status_code == 200
    events = _parse_events(response)
    result_event = next(evt for evt in events if evt.get("event") == "result")
    data = result_event
    assert data["invalid"] is True
    assert "catalog_violation:lines.unknown" in data["needs_user_fix"]
    templates_state = api.state_store.list_templates()
    tpl_record = next(t for t in templates_state if t["id"] == template_id)
    generator_meta = tpl_record.get("generator") or {}
    assert generator_meta.get("invalid") is True
    assert any("catalog_violation:lines.unknown" in item for item in generator_meta.get("needsUserFix") or [])


def test_generator_assets_v1_missing_contract(client):
    template_id = "00000000-0000-0000-0000-000000000004"
    _setup_template_dir(api.UPLOAD_ROOT, template_id)
    response = client.post(
        f"/templates/{template_id}/generator-assets/v1",
        json={"final_template_html": "<html></html>"},
    )
    assert response.status_code == 422
