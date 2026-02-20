from __future__ import annotations

import importlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

artifacts_module = importlib.import_module("backend.app.services.utils.artifacts")
write_artifact_manifest = artifacts_module.write_artifact_manifest

lock_module = importlib.import_module("backend.app.services.utils.lock")
acquire_template_lock = lock_module.acquire_template_lock

validation_module = importlib.import_module("backend.app.services.utils.validation")
SchemaValidationError = validation_module.SchemaValidationError
validate_mapping_schema = validation_module.validate_mapping_schema

pipeline_module = importlib.import_module("scripts.verify_pipeline")
verify_pipeline = pipeline_module.verify_pipeline

TEMPLATE_ID = "ad6a0b1f-d98a-41c2-8ffe-8b651de9100f"
UPLOADS_ROOT = REPO_ROOT / "samples" / "uploads"


def _lookup_check(checks: list[Any], name: str) -> Any:
    for check in checks:
        if check.name == name:
            return check
    raise AssertionError(f"Check {name} not found in {checks}")


def _clear_fail_hook() -> None:
    os.environ.pop("NEURA_FAIL_AFTER_STEP", None)


def test_verify_pipeline_success():
    _clear_fail_hook()
    success, checks = verify_pipeline(TEMPLATE_ID, UPLOADS_ROOT)
    assert success, "Expected verification to succeed for fixture template"

    contract_check = _lookup_check(checks, "contract_schema")
    assert contract_check.ok

    manifest_check = _lookup_check(checks, "artifact_manifest")
    assert manifest_check.ok

    staleness_check = _lookup_check(checks, "artifact_staleness")
    assert staleness_check.ok

    images_check = _lookup_check(checks, "report_final_images")
    assert images_check.ok


def test_verify_pipeline_simulate_flag():
    _clear_fail_hook()
    success, checks = verify_pipeline(TEMPLATE_ID, UPLOADS_ROOT, simulate=["mapping_save"])
    assert success
    sim_check = _lookup_check(checks, "simulate_mapping_save")
    assert sim_check.ok, sim_check.detail


@pytest.mark.parametrize(
    "template_id,expected_check",
    [
        ("invalid-id", "template_id_format"),
        ("00000000-0000-0000-0000-000000000000", "template_dir_exists"),
    ],
)
def test_verify_pipeline_failure_cases(template_id: str, expected_check: str):
    success, checks = verify_pipeline(template_id, UPLOADS_ROOT)
    assert not success
    assert checks[0].name in {expected_check, "template_dir_exists"}
    assert not checks[0].ok


def test_template_lock_non_blocking(tmp_path: Path):
    lock_dir = tmp_path / "tmpl"
    lock_dir.mkdir()

    with acquire_template_lock(lock_dir, "mapping", "corr-1"):
        with acquire_template_lock(lock_dir, "mapping", "corr-2"):
            pass


def test_validate_mapping_schema_rejects_invalid():
    with pytest.raises(SchemaValidationError):
        validate_mapping_schema([{"header": "A"}])


def test_staleness_detection(tmp_path: Path):
    uploads_root = tmp_path
    tid = "00000000-0000-0000-0000-000000000123"
    tdir = uploads_root / tid
    tdir.mkdir(parents=True, exist_ok=True)

    (tdir / "source.pdf").write_bytes(b"%PDF")
    (tdir / "reference_p1.png").write_bytes(b"\x89PNG\r\n")
    (tdir / "template_p1.html").write_text("<html><body>Template</body></html>", encoding="utf-8")
    report_html = tdir / "report_final.html"
    report_html.write_text('<html><body><img src="reference_p1.png" /></body></html>', encoding="utf-8")

    mapping_path = tdir / "mapping_pdf_labels.json"
    mapping_data = [
        {"header": "H", "placeholder": "{H}", "mapping": "table.col"},
    ]
    mapping_path.write_text(json.dumps(mapping_data), encoding="utf-8")

    contract_path = tdir / "contract.json"
    contract_data = {
        "mapping": {"H": "table.col"},
        "join": {
            "parent_table": "table",
            "parent_key": "id",
            "child_table": "table",
            "child_key": "id",
        },
        "date_columns": {"table": "created_at"},
        "header_tokens": ["H"],
        "row_tokens": ["H"],
        "totals": {},
        "row_order": ["id"],
        "literals": {},
    }
    contract_path.write_text(json.dumps(contract_data), encoding="utf-8")

    # create manifest using helper for checksum accuracy
    write_artifact_manifest(
        tdir,
        step="test_setup",
        files={
            "report_final.html": report_html,
            "template_p1.html": tdir / "template_p1.html",
            "mapping_pdf_labels.json": mapping_path,
            "contract.json": contract_path,
        },
        inputs=[],
        correlation_id="test",
    )

    filled_html = tdir / "filled_1.html"
    filled_pdf = tdir / "filled_1.pdf"
    filled_html.write_text("<html></html>", encoding="utf-8")
    filled_pdf.write_bytes(b"%PDF")

    # manipulate mtimes to force stale detection failure
    now = time.time()
    os.utime(mapping_path, (now, now))
    os.utime(contract_path, (now - 60, now - 60))
    os.utime(report_html, (now - 120, now - 120))

    success, checks = verify_pipeline(tid, uploads_root)
    assert not success, "Staleness should fail verification"
    stale_check = _lookup_check(checks, "artifact_staleness")
    assert not stale_check.ok
