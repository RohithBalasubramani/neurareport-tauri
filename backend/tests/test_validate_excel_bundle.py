from __future__ import annotations

import json
from pathlib import Path

from scripts.validate_excel_bundle import validate_excel_upload


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _sample_contract() -> dict:
    return {
        "tokens": {"scalars": [], "row_tokens": ["row_value"], "totals": []},
        "mapping": {"row_value": "rows.row_value"},
        "join": {
            "parent_table": "batches",
            "parent_key": "id",
            "child_table": "rows",
            "child_key": "batch_id",
        },
        "date_columns": {},
        "filters": {},
        "reshape_rules": [
            {
                "purpose": "rows dataset",
                "strategy": "select",
                "alias": "rows",
                "from": "rows",
                "columns": [{"as": "row_value", "from": ["rows.row_value"]}],
            }
        ],
        "row_computed": {},
        "totals_math": {},
        "formatters": {},
        "order_by": {"rows": ["rows.row_value ASC"]},
        "header_tokens": [],
        "row_tokens": ["row_value"],
        "totals": {},
        "row_order": ["rows.row_value ASC"],
    }


def _sample_step5() -> dict:
    return {
        "parameters": {"required": [], "optional": []},
        "datasets": [
            {
                "alias": "rows",
                "source_table": "rows",
                "description": "",
                "columns": [{"as": "row_value", "from": "rows.row_value"}],
            }
        ],
        "reshape_rules": [],
        "order_by": ["rows.row_value ASC"],
        "row_order": ["rows.row_value ASC"],
    }


def _sample_generator_meta() -> dict:
    return {
        "dialect": "duckdb",
        "entrypoints": {
            "header": "SELECT 1",
            "rows": "SELECT 1 AS row_value",
            "totals": "SELECT 1",
        },
        "params": {"required": [], "optional": []},
        "needs_user_fix": [],
        "invalid": False,
        "summary": {},
        "cached": False,
        "key_tokens": [],
    }


def test_validate_excel_bundle_flags_missing_files(tmp_path):
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    issues = validate_excel_upload(bundle_dir)
    assert issues and "Missing required files" in issues[0]


def test_validate_excel_bundle_passes_with_valid_payload(tmp_path):
    bundle_dir = tmp_path / "bundle"
    generator_dir = bundle_dir / "generator"
    generator_dir.mkdir(parents=True)

    _write_json(bundle_dir / "contract.json", _sample_contract())
    _write_json(bundle_dir / "step5_requirements.json", _sample_step5())
    _write_json(generator_dir / "generator_assets.json", _sample_generator_meta())
    _write_json(generator_dir / "output_schemas.json", {"header": [], "rows": ["row_value"], "totals": []})
    (generator_dir / "sql_pack.sql").write_text(
        "-- HEADER SELECT --\nSELECT 1;\n-- ROWS SELECT --\nSELECT 1 AS row_value;\n-- TOTALS SELECT --\nSELECT 1;\n",
        encoding="utf-8",
    )

    issues = validate_excel_upload(bundle_dir)
    assert issues == []
