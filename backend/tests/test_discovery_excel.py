from __future__ import annotations

import sqlite3
from pathlib import Path

from backend.app.services.reports.discovery_excel import discover_batches_and_counts


def _build_db(path: Path, schema_statements: list[str], data_statements: list[tuple[str, tuple]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(path)) as con:
        cur = con.cursor()
        for stmt in schema_statements:
            cur.execute(stmt)
        for stmt, params in data_statements:
            cur.execute(stmt, params)
        con.commit()


def test_excel_discovery_infers_parent_table_from_mapping(tmp_path: Path):
    db_path = tmp_path / "excel.db"
    _build_db(
        db_path,
        schema_statements=["CREATE TABLE flowmeters (timestamp_utc TEXT, value REAL)"],
        data_statements=[
            ("INSERT INTO flowmeters VALUES (?, ?)", ("2025-06-01", 10.0)),
            ("INSERT INTO flowmeters VALUES (?, ?)", ("2025-06-02", 20.0)),
        ],
    )

    contract = {
        "mapping": {"row_value": "flowmeters.value"},
        "date_columns": {"flowmeters": "timestamp_utc"},
    }

    summary = discover_batches_and_counts(
        db_path=db_path,
        contract=contract,
        start_date="2025-06-01",
        end_date="2025-06-30",
    )

    assert summary["batches_count"] == 2
    assert summary["rows_total"] == 2
