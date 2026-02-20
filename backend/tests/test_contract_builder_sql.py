import pytest

from backend.app.services.contract.ContractBuilderV2 import (
    ContractBuilderError,
    _normalize_sql_mapping_sections,
)


def test_normalize_sql_mapping_sections_rejects_legacy_prefix():
    contract = {
        "mapping": {"total_set": "DERIVED:SUM(recipes.bin1_sp)"},
        "totals": {"total_set": "DERIVED:SUM(recipes.bin1_sp)"},
    }
    with pytest.raises(ContractBuilderError):
        _normalize_sql_mapping_sections(contract, allow_list=["recipes.bin1_sp"])


def test_normalize_sql_mapping_sections_keeps_sql_fragment():
    contract = {
        "mapping": {"total_error": "SUM(recipes.bin1_act) - SUM(recipes.bin1_sp)"},
    }
    _normalize_sql_mapping_sections(contract, allow_list=["recipes.bin1_act", "recipes.bin1_sp"])
    assert contract["mapping"]["total_error"] == "SUM(recipes.bin1_act) - SUM(recipes.bin1_sp)"


def test_normalize_sql_mapping_sections_rejects_unknown_columns():
    contract = {"mapping": {"bad": "SUM(recipes.missing_col)"}}  # unknown column on known table
    with pytest.raises(ContractBuilderError):
        _normalize_sql_mapping_sections(contract, allow_list=["recipes.bin1_sp"])


def test_normalize_sql_mapping_sections_rejects_subqueries():
    contract = {"mapping": {"bad": "SELECT * FROM recipes"}}
    with pytest.raises(ContractBuilderError):
        _normalize_sql_mapping_sections(contract, allow_list=["recipes.bin1_sp"])
