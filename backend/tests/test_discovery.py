from __future__ import annotations

import sqlite3
from pathlib import Path

from backend.app.services.reports.discovery import discover_batches_and_counts


def _build_db(path: Path, schema_statements: list[str], data_statements: list[tuple[str, tuple]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(path)) as con:
        cur = con.cursor()
        for stmt in schema_statements:
            cur.execute(stmt)
        for stmt, params in data_statements:
            cur.execute(stmt, params)
        con.commit()


def test_discover_handles_contract_without_child_table(tmp_path: Path):
    db_path = tmp_path / "db.sqlite"
    _build_db(
        db_path,
        schema_statements=["CREATE TABLE recipes (id INTEGER PRIMARY KEY, start_time TEXT, plant TEXT)"],
        data_statements=[
            ("INSERT INTO recipes (id, start_time, plant) VALUES (?, ?, ?)", (1, "2025-01-05", "A")),
            ("INSERT INTO recipes (id, start_time, plant) VALUES (?, ?, ?)", (2, "2024-12-31", "B")),
        ],
    )

    contract = {
        "join": {
            "parent_table": "recipes",
            "child_table": "",
            "parent_key": "id",
            "child_key": "",
        },
        "date_columns": {
            "recipes": "start_time",
        },
    }

    summary = discover_batches_and_counts(
        db_path=db_path,
        contract=contract,
        start_date="2025-01-01",
        end_date="2025-12-31",
    )

    assert summary["batches_count"] == 1
    assert summary["rows_total"] == 1
    assert summary["batches"][0]["id"] == "1"
    assert summary["batches"][0]["parent"] == 1
    assert summary["batches"][0]["rows"] == 1


def test_discover_supports_list_keys_and_child_table(tmp_path: Path):
    db_path = tmp_path / "db.sqlite"
    _build_db(
        db_path,
        schema_statements=[
            "CREATE TABLE orders (plant_id INTEGER, batch_no TEXT, start_ts TEXT)",
            "CREATE TABLE order_items (plant_id INTEGER, batch_no TEXT, line_no INTEGER, start_ts TEXT)",
        ],
        data_statements=[
            ("INSERT INTO orders VALUES (?, ?, ?)", (101, "A", "2025-03-01")),
            ("INSERT INTO orders VALUES (?, ?, ?)", (101, "B", "2025-03-02")),
            ("INSERT INTO orders VALUES (?, ?, ?)", (101, "C", "2024-12-31")),
            ("INSERT INTO order_items VALUES (?, ?, ?, ?)", (101, "A", 1, "2025-03-01")),
            ("INSERT INTO order_items VALUES (?, ?, ?, ?)", (101, "A", 2, "2025-03-01")),
            ("INSERT INTO order_items VALUES (?, ?, ?, ?)", (101, "B", 1, "2025-03-02")),
            ("INSERT INTO order_items VALUES (?, ?, ?, ?)", (101, "C", 1, "2024-12-31")),
        ],
    )

    contract = {
        "join": {
            "parent_table": "orders",
            "child_table": "order_items",
            "parent_key": ["plant_id", "batch_no"],
            "child_key": ["plant_id", "batch_no"],
        },
        "date_columns": {
            "orders": "start_ts",
            "order_items": "start_ts",
        },
    }

    summary = discover_batches_and_counts(
        db_path=db_path,
        contract=contract,
        start_date="2025-03-01",
        end_date="2025-03-31",
    )

    # Only batches A and B fall inside the requested date range.
    ids = {batch["id"]: batch for batch in summary["batches"]}
    assert ids == {
        "101|A": {"id": "101|A", "parent": 1, "rows": 2},
        "101|B": {"id": "101|B", "parent": 1, "rows": 1},
    }
    assert summary["batches_count"] == 2
    assert summary["rows_total"] == 3
    metadata = summary["batch_metadata"]
    assert metadata["101|A"]["category"] == "101"
    assert metadata["101|A"]["plant_id"] == "101"
    assert metadata["101|A"]["batch_no"] == "A"
    assert str(metadata["101|A"]["time"]).startswith("2025-03-01")
    metric_map = {entry["batch_id"]: entry for entry in summary["batch_metrics"]}
    assert metric_map["101|A"]["plant_id"] == "101"
    assert metric_map["101|A"]["batch_no"] == "A"
    catalog = {field["name"]: field for field in summary["field_catalog"]}
    assert catalog["time"]["source"] == "orders.start_ts"
    assert catalog["plant_id"]["type"] == "categorical"
    assert catalog["plant_id"]["source"] == "orders.plant_id"
    assert "numeric_bins" in summary
    assert isinstance(summary["numeric_bins"].get("rows"), list)


def test_discover_infers_parent_key_from_child_when_missing(tmp_path: Path):
    db_path = tmp_path / "db.sqlite"
    _build_db(
        db_path,
        schema_statements=[
            "CREATE TABLE orders (order_id INTEGER PRIMARY KEY, start_ts TEXT)",
            "CREATE TABLE order_items (order_id INTEGER, line_no INTEGER, start_ts TEXT)",
        ],
        data_statements=[
            ("INSERT INTO orders VALUES (?, ?)", (1, "2025-04-01")),
            ("INSERT INTO orders VALUES (?, ?)", (2, "2025-04-02")),
            ("INSERT INTO orders VALUES (?, ?)", (3, "2024-12-31")),
            ("INSERT INTO order_items VALUES (?, ?, ?)", (1, 1, "2025-04-01")),
            ("INSERT INTO order_items VALUES (?, ?, ?)", (1, 2, "2025-04-01")),
            ("INSERT INTO order_items VALUES (?, ?, ?)", (2, 1, "2025-04-02")),
            ("INSERT INTO order_items VALUES (?, ?, ?)", (3, 1, "2024-12-31")),
        ],
    )

    contract = {
        "join": {
            "parent_table": "orders",
            "child_table": "order_items",
            "parent_key": "",
            "child_key": "order_id",
        },
        "date_columns": {
            "orders": "start_ts",
            "order_items": "start_ts",
        },
    }

    summary = discover_batches_and_counts(
        db_path=db_path,
        contract=contract,
        start_date="2025-04-01",
        end_date="2025-04-30",
    )

    ids = {batch["id"]: batch for batch in summary["batches"]}
    assert ids == {
        "1": {"id": "1", "parent": 1, "rows": 2},
        "2": {"id": "2", "parent": 1, "rows": 1},
    }
    assert summary["batches_count"] == 2
    assert summary["rows_total"] == 3


def test_discover_falls_back_to_rowid_when_no_keys(tmp_path: Path):
    db_path = tmp_path / "db.sqlite"
    _build_db(
        db_path,
        schema_statements=["CREATE TABLE readings (start_ts TEXT, metric REAL)"],
        data_statements=[
            ("INSERT INTO readings VALUES (?, ?)", ("2025-05-01", 1.1)),
            ("INSERT INTO readings VALUES (?, ?)", ("2025-05-15", 2.2)),
            ("INSERT INTO readings VALUES (?, ?)", ("2024-12-31", 3.3)),
        ],
    )

    contract = {
        "join": {
            "parent_table": "readings",
            "child_table": "",
            "parent_key": "",
            "child_key": "",
        },
        "date_columns": {
            "readings": "start_ts",
        },
    }

    summary = discover_batches_and_counts(
        db_path=db_path,
        contract=contract,
        start_date="2025-05-01",
        end_date="2025-05-31",
    )

    ids = {batch["id"]: batch for batch in summary["batches"]}
    # Row IDs start at 1 and increase with each insert.
    assert ids == {
        "1": {"id": "1", "parent": 1, "rows": 1},
        "2": {"id": "2", "parent": 1, "rows": 1},
    }
    assert summary["batches_count"] == 2
    assert summary["rows_total"] == 2


def test_discover_infers_parent_table_from_mapping_when_join_missing(tmp_path: Path):
    db_path = tmp_path / "db.sqlite"
    _build_db(
        db_path,
        schema_statements=["CREATE TABLE readings (start_ts TEXT, metric REAL)"],
        data_statements=[
            ("INSERT INTO readings VALUES (?, ?)", ("2025-05-01", 1.1)),
            ("INSERT INTO readings VALUES (?, ?)", ("2025-05-15", 2.2)),
        ],
    )

    contract = {
        "mapping": {"row_metric": "readings.metric"},
        "date_columns": {"readings": "start_ts"},
    }

    summary = discover_batches_and_counts(
        db_path=db_path,
        contract=contract,
        start_date="2025-05-01",
        end_date="2025-05-31",
    )

    assert summary["batches_count"] == 2
    assert summary["rows_total"] == 2
