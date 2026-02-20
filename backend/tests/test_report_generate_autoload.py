from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, cast

from backend.app.services.reports.ReportGenerate import fill_and_print


def _write_generator_bundle(
    template_dir: Path,
    use_page_total: bool = False,
    include_page_fields: bool = True,
) -> None:
    generator_dir = template_dir / "generator"
    generator_dir.mkdir(parents=True, exist_ok=True)

    page_total_col = "page_total" if use_page_total else "page_count"

    header_select_parts = [
        "'PlantX' AS plant_name",
        "'LocY' AS location",
        "date('2024-01-01') AS print_date",
        ":from_date AS from_date",
        ":to_date AS to_date",
        "COALESCE(:recipe_code, '') AS recipe_code",
    ]
    if include_page_fields:
        header_select_parts.extend(
            [
                "1 AS page_no",
                f"1 AS {page_total_col}",
            ]
        )

    entrypoints = {
        "header": ("SELECT " + ", ".join(header_select_parts) + ";"),
        "rows": (
            "SELECT "
            "ROW_NUMBER() OVER (ORDER BY material_name) AS sl_no, "
            "material_name, "
            "set_wt, "
            "ach_wt, "
            "(ach_wt - set_wt) AS error_kg, "
            "CASE WHEN set_wt = 0 THEN NULL ELSE 100.0 * (ach_wt - set_wt) / set_wt END AS error_percent "
            "FROM recipes "
            "WHERE date(start_time) BETWEEN date(:from_date) AND date(:to_date) "
            "ORDER BY material_name;"
        ),
        "totals": (
            "SELECT "
            "SUM(set_wt) AS total_set_wt, "
            "SUM(ach_wt) AS total_ach_wt, "
            "SUM(ach_wt - set_wt) AS total_error_kg, "
            "CASE WHEN SUM(set_wt) = 0 THEN NULL ELSE 100.0 * SUM(ach_wt - set_wt) / SUM(set_wt) END AS total_error_percent "
            "FROM recipes "
            "WHERE date(start_time) BETWEEN date(:from_date) AND date(:to_date);"
        ),
    }

    meta = {
        "entrypoints": entrypoints,
        "params": {"required": ["from_date", "to_date"], "optional": ["recipe_code"]},
        "dialect": "duckdb",
        "needs_user_fix": [],
        "invalid": False,
        "summary": {},
    }
    (generator_dir / "generator_assets.json").write_text(json.dumps(meta), encoding="utf-8")
    header_fields = [
        "plant_name",
        "location",
        "print_date",
        "from_date",
        "to_date",
        "recipe_code",
    ]
    if include_page_fields:
        header_fields.extend(["page_no", page_total_col])

    (generator_dir / "output_schemas.json").write_text(
        json.dumps(
            {
                "header": header_fields,
                "rows": ["sl_no", "material_name", "set_wt", "ach_wt", "error_kg", "error_percent"],
                "totals": ["total_set_wt", "total_ach_wt", "total_error_kg", "total_error_percent"],
            }
        ),
        encoding="utf-8",
    )
    (generator_dir / "sql_pack.sql").write_text("-- generated sql", encoding="utf-8")


def _write_contract(
    template_dir: Path,
    use_page_total: bool = False,
    include_page_fields: bool = True,
) -> dict:
    page_total_col = "page_total" if use_page_total else "page_count"

    contract = {
        "mapping": {
            "plant_name": "PARAM:plant_name",
            "location": "PARAM:location",
            "print_date": "PARAM:print_date",
            "from_date": "PARAM:from_date",
            "to_date": "PARAM:to_date",
            "recipe_code": "PARAM:recipe_code",
            "sl_no": "rows.sl_no",
            "material_name": "rows.material_name",
            "set_wt": "rows.set_wt",
            "ach_wt": "rows.ach_wt",
            "error_kg": "rows.error_kg",
            "error_percent": "rows.error_percent",
            "total_set_wt": "totals.total_set_wt",
            "total_ach_wt": "totals.total_ach_wt",
            "total_error_kg": "totals.total_error_kg",
            "total_error_percent": "totals.total_error_percent",
        },
        "join": {
            "parent_table": "recipes",
            "parent_key": "id",
            "child_table": "",
            "child_key": "",
        },
        "date_columns": {"recipes": "start_time"},
        "header_tokens": [
            "plant_name",
            "location",
            "print_date",
            "from_date",
            "to_date",
            "recipe_code",
        ],
        "row_tokens": ["sl_no", "material_name", "set_wt", "ach_wt", "error_kg", "error_percent"],
        "totals": {
            "total_set_wt": "totals.total_set_wt",
            "total_ach_wt": "totals.total_ach_wt",
            "total_error_kg": "totals.total_error_kg",
            "total_error_percent": "totals.total_error_percent",
        },
        "row_order": ["ROWID"],
        "literals": {},
        "filters": {"required": {}, "optional": {}},
        "row_computed": {},
        "totals_math": {},
        "formatters": {},
        "order_by": {"rows": ["material_name ASC"]},
        "unresolved": [],
        "tokens": {
            "scalars": [
                "plant_name",
                "location",
                "print_date",
                "from_date",
                "to_date",
                "recipe_code",
            ],
            "row_tokens": ["sl_no", "material_name", "set_wt", "ach_wt", "error_kg", "error_percent"],
            "totals": ["total_set_wt", "total_ach_wt", "total_error_kg", "total_error_percent"],
        },
    }
    if include_page_fields:
        mapping = cast(dict[str, Any], contract["mapping"])
        mapping["page_no"] = "PARAM:page_no"
        mapping[page_total_col] = f"PARAM:{page_total_col}"

        header_tokens = cast(list[str], contract["header_tokens"])
        header_tokens.extend(["page_no", page_total_col])

        tokens = cast(dict[str, Any], contract["tokens"])
        scalars = cast(list[str], tokens.get("scalars") or [])
        scalars.extend(["page_no", page_total_col])
        tokens["scalars"] = scalars
    return contract


def _write_template(template_path: Path) -> None:
    template_path.write_text(
        """<html><body>
<section class="batch-block">
  <div>{{plant_name}} - {{location}}</div>
  <div>From {{from_date}} to {{to_date}}</div>
  <table>
    <tbody>
      <tr>
        <td>{{sl_no}}</td>
        <td>{{material_name}}</td>
        <td>{{set_wt}}</td>
        <td>{{ach_wt}}</td>
        <td>{{error_kg}}</td>
        <td>{{error_percent}}</td>
      </tr>
    </tbody>
  </table>
  <footer>
    Totals: {{total_set_wt}} / {{total_ach_wt}} / {{total_error_kg}} / {{total_error_percent}}
    Page {{page_no}} of {{page_count}}
  </footer>
</section>
</body></html>""",
        encoding="utf-8",
    )


def _write_db(db_path: Path) -> None:
    con = sqlite3.connect(str(db_path))
    try:
        con.execute(
            "CREATE TABLE recipes (id INTEGER PRIMARY KEY, start_time TEXT, material_name TEXT, set_wt REAL, ach_wt REAL)"
        )
        con.executemany(
            "INSERT INTO recipes (id, start_time, material_name, set_wt, ach_wt) VALUES (?, ?, ?, ?, ?)",
            [
                (1, "2024-05-01", "MaterialA", 10.0, 11.5),
                (2, "2024-05-02", "MaterialB", 20.0, 19.0),
            ],
        )
        con.commit()
    finally:
        con.close()


def test_fill_and_print_autoloads_generator_bundle(tmp_path):
    template_dir = tmp_path / "template"
    template_dir.mkdir()
    template_path = template_dir / "report_final.html"
    _write_template(template_path)
    _write_generator_bundle(template_dir, include_page_fields=False)

    contract = _write_contract(template_dir, include_page_fields=False)
    db_path = tmp_path / "recipes.db"
    _write_db(db_path)

    out_html = tmp_path / "out.html"
    out_pdf = tmp_path / "out.pdf"

    fill_and_print(
        OBJ=contract,
        TEMPLATE_PATH=template_path,
        DB_PATH=db_path,
        OUT_HTML=out_html,
        OUT_PDF=out_pdf,
        START_DATE="2024-01-01",
        END_DATE="2024-12-31",
        batch_ids=None,
    )

    output = out_html.read_text(encoding="utf-8")
    assert "MaterialA" in output
    assert "MaterialB" in output
    assert "Totals" in output
    assert 'class="nr-page-number"' in output
    assert 'class="nr-page-count"' in output


def test_fill_and_print_supports_page_total_token(tmp_path):
    template_dir = tmp_path / "template_total"
    template_dir.mkdir()
    template_path = template_dir / "report_final.html"
    _write_template(template_path)

    template_html = template_path.read_text(encoding="utf-8")
    template_html = template_html.replace("{{page_count}}", "{{page_total}}")
    template_path.write_text(template_html, encoding="utf-8")

    _write_generator_bundle(template_dir, use_page_total=True, include_page_fields=False)
    contract = _write_contract(template_dir, use_page_total=True, include_page_fields=False)

    db_path = tmp_path / "recipes_total.db"
    _write_db(db_path)

    out_html = tmp_path / "out_total.html"
    out_pdf = tmp_path / "out_total.pdf"

    fill_and_print(
        OBJ=contract,
        TEMPLATE_PATH=template_path,
        DB_PATH=db_path,
        OUT_HTML=out_html,
        OUT_PDF=out_pdf,
        START_DATE="2024-01-01",
        END_DATE="2024-12-31",
        batch_ids=None,
    )

    output = out_html.read_text(encoding="utf-8")
    assert 'class="nr-page-number"' in output
    assert 'class="nr-page-count"' in output
    assert 'Page <span class="nr-page-number"' in output
    assert 'of <span class="nr-page-count"' in output
