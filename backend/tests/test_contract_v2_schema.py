from __future__ import annotations

from copy import deepcopy

import pytest

from backend.app.services.utils.validation import (
    SchemaValidationError,
    validate_contract_v2,
    validate_step5_requirements,
)


def _sample_contract() -> dict:
    return {
        "tokens": {
            "scalars": ["report_title"],
            "row_tokens": ["material_name", "qty"],
            "totals": ["total_qty"],
        },
        "mapping": {
            "report_title": "batches.title",
            "material_name": "lines.material",
            "qty": "lines.qty",
            "total_qty": "lines.qty",
        },
        "unresolved": [],
        "join": {
            "parent_table": "batches",
            "parent_key": "batch_id",
            "child_table": "lines",
            "child_key": "batch_id",
        },
        "date_columns": {
            "batches": "batch_date",
            "lines": "line_date",
        },
        "reshape_rules": [
            {
                "purpose": "rows",
                "strategy": "NONE",
                "columns": [
                    {"as": "material_name", "from": ["lines.material"]},
                    {"as": "qty", "from": ["lines.qty"]},
                ],
            }
        ],
        "row_computed": {"qty_formatted": "ROUND(qty, 2)"},
        "totals_math": {"total_qty": "SUM(lines.qty)"},
        "formatters": {"qty": "number(2)"},
        "order_by": {"rows": ["material_name ASC"]},
        "filters": {},
        "assumptions": ["Totals exclude inactive batches."],
        "warnings": [],
        "validation": {
            "unknown_tokens": [],
            "unknown_columns": [],
            "token_coverage": {
                "scalars_mapped_pct": 100,
                "row_tokens_mapped_pct": 100,
                "totals_mapped_pct": 100,
            },
        },
    }


def _sample_step5_requirements() -> dict:
    return {
        "datasets": {
            "header": {
                "description": "Single-row header dataset",
                "columns": ["report_title"],
            },
            "rows": {
                "description": "Detail rows dataset",
                "columns": ["material_name", "qty"],
                "grouping": ["material_name"],
                "ordering": ["material_name ASC"],
            },
            "totals": {
                "description": "Aggregate totals dataset",
                "columns": ["total_qty"],
            },
        },
        "parameters": {
            "required": [{"name": "from_date", "type": "date"}],
            "optional": [{"name": "plant", "type": "string"}],
            "semantics": "Filter rows by provided date range and optional plant parameter.",
        },
        "transformations": [
            "Rows use raw values from lines table.",
        ],
        "edge_cases": [
            "Division by zero yields NULL.",
        ],
        "dialect_notes": [
            "Use sqlite-compatible syntax.",
        ],
        "artifact_expectations": {
            "output_schemas": "Rows output must include material_name and qty.",
            "sql_pack": "Provide SQL scripts zipped together.",
        },
    }


def test_contract_v2_schema_valid():
    validate_contract_v2(_sample_contract())


def test_contract_v2_schema_allows_base_filter_rule_without_columns():
    contract = _sample_contract()
    contract["reshape_rules"].insert(
        0,
        {
            "purpose": "Filter base recipes",
            "strategy": "BASE_FILTER",
            "where": ["recipes.start_time >= :from_date", "recipes.start_time <= :to_date"],
        },
    )
    validate_contract_v2(contract)


def test_contract_v2_schema_requires_column_rule():
    contract = _sample_contract()
    contract["reshape_rules"] = [
        {
            "purpose": "Filter base recipes",
            "strategy": "BASE_FILTER",
            "where": ["recipes.start_time >= :from_date"],
        }
    ]
    with pytest.raises(SchemaValidationError) as excinfo:
        validate_contract_v2(contract)
    assert "reshape_rules" in str(excinfo.value)


def test_step5_requirements_schema_valid():
    validate_step5_requirements(_sample_step5_requirements())


def test_contract_v2_schema_invalid_type():
    invalid = deepcopy(_sample_contract())
    invalid["tokens"]["scalars"] = "report_title"  # type: ignore[assignment]
    with pytest.raises(SchemaValidationError):
        validate_contract_v2(invalid)
