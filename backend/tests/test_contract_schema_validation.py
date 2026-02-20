from __future__ import annotations

import pytest

from backend.app.services.utils.validation import (
    SchemaValidationError,
    validate_contract_schema,
)


def _base_contract() -> dict:
    return {
        "mapping": {},
        "join": {
            "parent_table": "recipes",
            "parent_key": "id",
            "child_table": "",
            "child_key": "",
        },
        "date_columns": {},
        "header_tokens": [],
        "row_tokens": [],
        "totals": {},
        "row_order": [],
        "literals": {},
    }


def test_contract_schema_allows_empty_child_join():
    payload = _base_contract()
    validate_contract_schema(payload)


def test_contract_schema_allows_null_child_join():
    payload = _base_contract()
    payload["join"]["child_table"] = None
    payload["join"]["child_key"] = None
    validate_contract_schema(payload)


def test_contract_schema_rejects_non_string_child_join():
    payload = _base_contract()
    payload["join"]["child_table"] = 123  # type: ignore[assignment]
    with pytest.raises(SchemaValidationError):
        validate_contract_schema(payload)


def test_contract_schema_requires_child_key_when_table_present():
    payload = _base_contract()
    payload["join"]["child_table"] = "line_items"
    payload["join"]["child_key"] = ""
    with pytest.raises(SchemaValidationError):
        validate_contract_schema(payload)


def test_contract_schema_infers_join_from_mapping_when_missing():
    payload = _base_contract()
    payload.pop("join")
    payload["mapping"] = {"row_value": "flowmeters.value"}
    validate_contract_schema(payload)
    join = payload.get("join") or {}
    assert join.get("parent_table") == "flowmeters"
    assert join.get("parent_key") == "__rowid__"
