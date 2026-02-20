from __future__ import annotations

from backend.app.services.reports.contract_adapter import ContractAdapter


def _base_contract(filters: dict) -> dict:
    return {
        "mapping": {},
        "join": {
            "parent_table": "orders",
            "parent_key": "order_id",
            "child_table": "",
            "child_key": "",
        },
        "date_columns": {},
        "filters": filters,
    }


def test_optional_filters_auto_bind_param_when_missing_param_tokens():
    contract = _base_contract({"optional": {"order_number": "orders.order_number"}})
    adapter = ContractAdapter(contract)

    predicates, params = adapter.build_base_where_clauses(include_date_range=False)

    assert predicates == [
        "(:order_number IS NULL OR TRIM(:order_number) = '' OR orders.order_number = :order_number)"
    ]
    assert params == ["order_number"]
