from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

import pytest

from backend.app.services.generator import GeneratorAssetsV1 as generator_assets
from backend.app.services.utils.validation import (
    SchemaValidationError,
    validate_contract_v2,
    validate_generator_output_schemas,
    validate_generator_sql_pack,
)

PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
)


def _write_png(path: Path) -> None:
    path.write_bytes(PNG_BYTES)


def _make_contract(tokens: dict[str, list[str]]) -> dict[str, Any]:
    tokens_copy: dict[str, Any] = {
        key: list(value) if isinstance(value, list) else value for key, value in tokens.items()
    }
    row_tokens = list(tokens_copy.get("row_tokens") or [])
    columns = [
        {"as": token, "from": [f"lines.{token}"]} for token in row_tokens[:2] if isinstance(token, str) and token
    ]
    if not columns:
        columns = [{"as": "row_value", "from": ["lines.row_value"]}]
        if not row_tokens:
            row_tokens = ["row_value"]
    elif not row_tokens:
        row_tokens = [col["as"] for col in columns]

    tokens_copy["row_tokens"] = row_tokens
    return {
        "tokens": tokens_copy,
        "mapping": {},
        "join": {"parent_table": "batches", "parent_key": "id", "child_table": "lines", "child_key": "batch_id"},
        "date_columns": {},
        "filters": {},
        "reshape_rules": [
            {
                "purpose": "rows",
                "strategy": "UNION_ALL",
                "columns": columns,
            }
        ],
        "row_computed": {},
        "totals_math": {},
        "formatters": {},
        "order_by": {"rows": []},
        "notes": "",
    }


class FakeResponse:
    def __init__(self, content: str):
        self.choices = [type("Choice", (), {"message": type("Msg", (), {"content": content})})()]


def test_validate_generator_sql_pack_schema():
    valid_payload = {
        "dialect": "duckdb",
        "script": "SELECT 1;",
        "entrypoints": {"header": "SELECT 1", "rows": "SELECT 1", "totals": "SELECT 1"},
        "params": {"required": ["from_date", "to_date"], "optional": []},
        "notes": "",
    }
    validate_generator_sql_pack(valid_payload)

    with pytest.raises(SchemaValidationError):
        validate_generator_sql_pack({"dialect": "duckdb"})

    with pytest.raises(SchemaValidationError) as excinfo:
        invalid = dict(valid_payload)
        invalid["dialect"] = "sqlite"
        validate_generator_sql_pack(invalid)
    assert "duckdb" in str(excinfo.value).lower()


def test_validate_generator_output_schemas_schema():
    validate_generator_output_schemas({"header": [], "rows": [], "totals": []})
    with pytest.raises(SchemaValidationError):
        validate_generator_output_schemas({"header": [], "rows": []})


def test_validate_contract_v2_rejects_blank_parent_key():
    contract = _make_contract({"scalars": [], "row_tokens": [], "totals": []})
    contract["join"]["parent_key"] = ""
    with pytest.raises(SchemaValidationError) as excinfo:
        validate_contract_v2(contract)
    assert "contract.join.parent_key" in str(excinfo.value)


def test_validate_contract_v2_requires_child_key_when_child_table_present():
    contract = _make_contract({"scalars": [], "row_tokens": [], "totals": []})
    contract["join"]["child_table"] = "child_tbl"
    contract["join"]["child_key"] = "   "
    with pytest.raises(SchemaValidationError) as excinfo:
        validate_contract_v2(contract)
    assert "contract.join.child_key" in str(excinfo.value)


def test_build_generator_assets_detects_column_mismatch(monkeypatch, tmp_path):
    template_dir = tmp_path / "tpl"
    template_dir.mkdir()
    _write_png(template_dir / "reference_p1.png")

    tokens = {"scalars": ["h1"], "row_tokens": ["r1"], "totals": ["t1"]}
    contract_blueprint = _make_contract(tokens)
    step4_output = {
        "contract": contract_blueprint,
        "overview_md": "#",
        "step5_requirements": {},
    }

    def fake_response(*args, **kwargs):
        payload = {
            "contract": step4_output["contract"],
            "sql_pack": {
                "dialect": "duckdb",
                "script": "SELECT 1 AS h1;\nSELECT 1 AS r1;\nSELECT 1 AS t1;",
                "entrypoints": {
                    "header": "SELECT 1 AS wrong_alias",
                    "rows": "SELECT 1 AS r1",
                    "totals": "SELECT 1 AS t1",
                },
                "params": {"required": ["from_date", "to_date"], "optional": []},
                "notes": "",
            },
            "output_schemas": {"header": ["h1"], "rows": ["r1"], "totals": ["t1"]},
            "needs_user_fix": [],
            "dry_run": None,
            "summary": {},
        }
        return FakeResponse(json.dumps(payload, ensure_ascii=False))

    monkeypatch.setattr(generator_assets, "call_chat_completion", lambda *args, **kwargs: fake_response())
    monkeypatch.setattr(generator_assets, "get_openai_client", lambda: object())

    result = generator_assets.build_generator_assets_from_payload(
        template_dir=template_dir,
        step4_output=step4_output,
        final_template_html="<html></html>",
        reference_pdf_image=None,
        catalog_allowlist=None,
        params_spec=["from_date", "to_date"],
    )
    assert result["invalid"] is True
    assert any("schema_mismatch" in item for item in result["needs_user_fix"])


def test_build_generator_assets_accepts_legacy_sql_pack(monkeypatch, tmp_path):
    template_dir = tmp_path / "tpl"
    template_dir.mkdir()
    _write_png(template_dir / "report_final.png")

    tokens = {
        "scalars": ["plant_name"],
        "row_tokens": ["row_material_name"],
        "totals": ["total_set_wt"],
    }
    contract_blueprint = _make_contract(tokens)
    step4_output = {
        "contract": contract_blueprint,
        "overview_md": "#",
        "step5_requirements": {},
    }

    legacy_sql_pack = {
        "header": """SELECT
  :plant_name AS plant_name,
  :location AS location,
  DATE('now') AS print_date,
  :from_date AS from_date,
  :to_date AS to_date,
  :recipe_code AS recipe_code;""",
        "rows": """WITH filtered_recipes AS (
  SELECT *
  FROM recipes
  WHERE (:from_date IS NULL OR DATE(start_time) >= :from_date)
    AND (:to_date IS NULL OR DATE(start_time) <= :to_date)
    AND (:recipe_code IS NULL OR TRIM(:recipe_code) = '' OR recipe_name = :recipe_code)
),
agg AS (
  SELECT
    bin1_content AS row_material_name,
    COALESCE(bin1_sp, 0) AS row_set_wt,
    COALESCE(bin1_act, 0) AS row_ach_wt
  FROM filtered_recipes
  WHERE bin1_content IS NOT NULL AND TRIM(bin1_content) <> ''
)
SELECT
  ROW_NUMBER() OVER (ORDER BY row_material_name ASC) AS row_sl_no,
  row_material_name,
  row_set_wt,
  row_ach_wt,
  row_ach_wt - row_set_wt AS row_error_kg,
  CASE WHEN row_set_wt = 0 THEN NULL ELSE (row_ach_wt - row_set_wt) / row_set_wt END AS row_error_pct
FROM agg
ORDER BY row_material_name ASC;""",
        "totals": """WITH filtered_recipes AS (
  SELECT *
  FROM recipes
  WHERE (:from_date IS NULL OR DATE(start_time) >= :from_date)
    AND (:to_date IS NULL OR DATE(start_time) <= :to_date)
    AND (:recipe_code IS NULL OR TRIM(:recipe_code) = '' OR recipe_name = :recipe_code)
),
agg AS (
  SELECT
    COALESCE(bin1_sp, 0) AS row_set_wt,
    COALESCE(bin1_act, 0) AS row_ach_wt
  FROM filtered_recipes
)
SELECT
  SUM(row_set_wt) AS total_set_wt,
  SUM(row_ach_wt) AS total_ach_wt,
  SUM(row_ach_wt) - SUM(row_set_wt) AS total_error_kg,
  (SUM(row_ach_wt) - SUM(row_set_wt)) / NULLIF(SUM(row_set_wt), 0) AS total_error_pct
FROM agg;""",
        "params": ["from_date", "to_date", "plant_name", "location", "recipe_code"],
    }
    legacy_payload = {
        "contract": step4_output["contract"],
        "sql_pack": legacy_sql_pack,
        "output_schemas": {
            "header": ["plant_name", "location", "print_date", "from_date", "to_date", "recipe_code"],
            "rows": ["row_sl_no", "row_material_name", "row_set_wt", "row_ach_wt", "row_error_kg", "row_error_pct"],
            "totals": ["total_set_wt", "total_ach_wt", "total_error_kg", "total_error_pct"],
        },
        "needs_user_fix": [],
        "dry_run": None,
        "summary": {},
    }

    def fake_response(*args, **kwargs):
        return FakeResponse(json.dumps(legacy_payload, ensure_ascii=False))

    monkeypatch.setattr(generator_assets, "call_chat_completion", lambda *args, **kwargs: fake_response())
    monkeypatch.setattr(generator_assets, "get_openai_client", lambda: object())

    result = generator_assets.build_generator_assets_from_payload(
        template_dir=template_dir,
        step4_output=step4_output,
        final_template_html="<html></html>",
        reference_pdf_image=None,
        catalog_allowlist=None,
        params_spec=["from_date", "to_date", "plant_name", "location", "recipe_code"],
    )

    assert result["invalid"] is False
    assert result["needs_user_fix"] == []
    assert result["dialect"] == "duckdb"
    assert result["params"]["required"] == ["from_date", "to_date", "plant_name", "location", "recipe_code"]
    assert result["params"]["optional"] == []


def test_normalise_sql_pack_fills_missing_entrypoints(monkeypatch, tmp_path):
    template_dir = tmp_path / "tpl"
    template_dir.mkdir()
    _write_png(template_dir / "report_final.png")

    tokens = {"scalars": [], "row_tokens": [], "totals": []}
    contract_blueprint = _make_contract(tokens)
    step4_output = {
        "contract": contract_blueprint,
        "overview_md": "#",
        "step5_requirements": {},
    }

    payload_with_empty_entrypoints = {
        "contract": step4_output["contract"],
        "sql_pack": {
            "script": "SELECT 1 AS col;",
            "entrypoints": {},
            "params": {"required": [], "optional": []},
        },
        "output_schemas": {"header": [], "rows": [], "totals": []},
        "needs_user_fix": [],
        "dry_run": None,
        "summary": {},
    }

    def fake_response(*args, **kwargs):
        return FakeResponse(json.dumps(payload_with_empty_entrypoints, ensure_ascii=False))

    monkeypatch.setattr(generator_assets, "call_chat_completion", lambda *args, **kwargs: fake_response())
    monkeypatch.setattr(generator_assets, "get_openai_client", lambda: object())

    result = generator_assets.build_generator_assets_from_payload(
        template_dir=template_dir,
        step4_output=step4_output,
        final_template_html="<html></html>",
        reference_pdf_image=None,
        catalog_allowlist=None,
        params_spec=[],
    )

    assert result["invalid"] is False


def test_generator_assets_requires_step5_contract(monkeypatch, tmp_path):
    template_dir = tmp_path / "tpl"
    template_dir.mkdir()
    _write_png(template_dir / "report_final.png")

    step4_output = {
        "contract": _make_contract({"scalars": ["h1"], "row_tokens": ["r1"], "totals": ["t1"]}),
        "overview_md": "#",
        "step5_requirements": {},
    }

    payload_without_contract = {
        "sql_pack": {
            "script": "SELECT 1 AS h1;",
            "entrypoints": {"header": "SELECT 1 AS h1", "rows": "SELECT 1 AS r1", "totals": "SELECT 1 AS t1"},
            "params": {"required": [], "optional": []},
        },
        "output_schemas": {"header": ["h1"], "rows": ["r1"], "totals": ["t1"]},
        "needs_user_fix": [],
        "summary": {},
    }

    def fake_response(*args, **kwargs):
        return FakeResponse(json.dumps(payload_without_contract, ensure_ascii=False))

    monkeypatch.setattr(generator_assets, "call_chat_completion", lambda *args, **kwargs: fake_response())
    monkeypatch.setattr(generator_assets, "get_openai_client", lambda: object())

    with pytest.raises(generator_assets.GeneratorAssetsError) as excinfo:
        generator_assets.build_generator_assets_from_payload(
            template_dir=template_dir,
            step4_output=step4_output,
            final_template_html="<html></html>",
            reference_pdf_image=None,
            catalog_allowlist=None,
            params_spec=[],
        )
    assert "contract payload" in str(excinfo.value)


def test_generator_assets_validates_step5_contract(monkeypatch, tmp_path):
    template_dir = tmp_path / "tpl"
    template_dir.mkdir()
    _write_png(template_dir / "report_final.png")

    good_contract = _make_contract({"scalars": ["h1"], "row_tokens": ["r1"], "totals": ["t1"]})
    bad_contract = dict(good_contract)
    bad_contract["reshape_rules"] = [{"purpose": "rows", "strategy": "UNION_ALL", "columns": []}]

    step4_output = {
        "contract": good_contract,
        "overview_md": "#",
        "step5_requirements": {},
    }

    payload_with_bad_contract = {
        "contract": bad_contract,
        "sql_pack": {
            "script": "SELECT 1 AS h1;",
            "entrypoints": {"header": "SELECT 1 AS h1", "rows": "SELECT 1 AS r1", "totals": "SELECT 1 AS t1"},
            "params": {"required": [], "optional": []},
        },
        "output_schemas": {"header": ["h1"], "rows": ["r1"], "totals": ["t1"]},
        "needs_user_fix": [],
        "summary": {},
    }

    def fake_response(*args, **kwargs):
        return FakeResponse(json.dumps(payload_with_bad_contract, ensure_ascii=False))

    monkeypatch.setattr(generator_assets, "call_chat_completion", lambda *args, **kwargs: fake_response())
    monkeypatch.setattr(generator_assets, "get_openai_client", lambda: object())

    with pytest.raises(generator_assets.GeneratorAssetsError) as excinfo:
        generator_assets.build_generator_assets_from_payload(
            template_dir=template_dir,
            step4_output=step4_output,
            final_template_html="<html></html>",
            reference_pdf_image=None,
            catalog_allowlist=None,
            params_spec=[],
        )
    assert "Generator contract failed validation" in str(excinfo.value)


def test_generator_assets_backfills_row_order_and_purpose(monkeypatch, tmp_path):
    template_dir = tmp_path / "tpl"
    template_dir.mkdir()
    _write_png(template_dir / "report_final.png")

    tokens = {"scalars": [], "row_tokens": ["row_material_name"], "totals": []}
    contract_blueprint = _make_contract(tokens)
    contract_blueprint["order_by"] = {"rows": ["rows.row_material_name ASC"]}
    contract_blueprint["reshape_rules"][0].pop("purpose", None)

    step4_output = {
        "contract": contract_blueprint,
        "overview_md": "#",
        "step5_requirements": {},
    }

    response_payload = {
        "contract": json.loads(json.dumps(contract_blueprint)),
        "sql_pack": {
            "script": "-- HEADER SELECT --\nSELECT 1;\n-- ROWS SELECT --\nSELECT 1 AS row_material_name;\n-- TOTALS SELECT --\nSELECT 1;",
            "entrypoints": {
                "header": "SELECT 1",
                "rows": "SELECT 1 AS row_material_name",
                "totals": "SELECT 1",
            },
            "params": {"required": [], "optional": []},
        },
        "output_schemas": {"header": [], "rows": ["row_material_name"], "totals": []},
        "needs_user_fix": [],
        "summary": {},
    }

    def fake_response(*args, **kwargs):
        return FakeResponse(json.dumps(response_payload, ensure_ascii=False))

    monkeypatch.setattr(generator_assets, "call_chat_completion", lambda *args, **kwargs: fake_response())
    monkeypatch.setattr(generator_assets, "get_openai_client", lambda: object())

    result = generator_assets.build_generator_assets_from_payload(
        template_dir=template_dir,
        step4_output=step4_output,
        final_template_html="<html></html>",
        reference_pdf_image=None,
        catalog_allowlist=None,
        params_spec=[],
    )

    assert result["invalid"] is False

    written_contract = json.loads((template_dir / "contract.json").read_text(encoding="utf-8"))
    assert written_contract["row_order"] == ["rows.row_material_name ASC"]
    assert written_contract["reshape_rules"][0]["purpose"]
