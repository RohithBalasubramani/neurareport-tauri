#!/usr/bin/env python3
"""
Create a NeuraReport invoice-style report testkit with:
1) Five web-sourced invoice PDF fixtures
2) Five corresponding SQLite fixture databases
3) Optional registration as NeuraReport connections
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import sqlite3
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "samples" / "report_generation_testkit"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.repositories.state import state_store


PDF_FIXTURES = [
    {
        "id": "01_onlineinvoices_sample_invoice",
        "report_type": "Invoice Template",
        "pdf_url": "https://create.onlineinvoices.com/img/uploads/business-template-files/Sample%20Invoice%20Template%20-%20Sheet1.pdf",
        "pdf_name": "01_onlineinvoices_sample_invoice.pdf",
        "db_name": "01_onlineinvoices_sample_invoice.sqlite3",
        "connection_name": "Fixture 01 - OnlineInvoices Sample Invoice",
        "seed": 101,
        "vendor_name": "Nova Office Supplies",
        "currency": "USD",
    },
    {
        "id": "02_zoho_standard_invoice",
        "report_type": "Invoice Template",
        "pdf_url": "https://www.zoho.com/invoice/invoice-templates/sample/zoho-invoice-standard-template.pdf",
        "pdf_name": "02_zoho_standard_invoice.pdf",
        "db_name": "02_zoho_standard_invoice.sqlite3",
        "connection_name": "Fixture 02 - Zoho Standard Invoice",
        "seed": 202,
        "vendor_name": "BluePeak Consulting",
        "currency": "USD",
    },
    {
        "id": "03_smartsheet_basic_invoice",
        "report_type": "Invoice Template",
        "pdf_url": "https://www.smartsheet.com/sites/default/files/2020-03/IC-Basic-Invoice-Template-10768_PDF.pdf",
        "pdf_name": "03_smartsheet_basic_invoice.pdf",
        "db_name": "03_smartsheet_basic_invoice.sqlite3",
        "connection_name": "Fixture 03 - Smartsheet Basic Invoice",
        "seed": 303,
        "vendor_name": "Apex Facilities Services",
        "currency": "USD",
    },
    {
        "id": "04_invoicesimple_pdf_template",
        "report_type": "Invoice Template",
        "pdf_url": "https://www.invoicesimple.com/wp-content/uploads/2022/12/InvoiceSimple-PDF-Template.pdf",
        "pdf_name": "04_invoicesimple_pdf_template.pdf",
        "db_name": "04_invoicesimple_pdf_template.sqlite3",
        "connection_name": "Fixture 04 - InvoiceSimple PDF Template",
        "seed": 404,
        "vendor_name": "Riverbend Mechanical",
        "currency": "USD",
    },
    {
        "id": "05_intuit_property_management_invoice",
        "report_type": "Invoice Template",
        "pdf_url": "https://digitalasset.intuit.com/render/content/dam/intuit/sbseg/en_us/quickbooks-online/web/content/editable-PDF-property-management-invoice-template.pdf",
        "pdf_name": "05_intuit_property_management_invoice.pdf",
        "db_name": "05_intuit_property_management_invoice.sqlite3",
        "connection_name": "Fixture 05 - Intuit Property Management Invoice",
        "seed": 505,
        "vendor_name": "Summit Property Management",
        "currency": "USD",
    },
]


LEGACY_FIXTURE_CONNECTION_IDS = [
    "fixture-01_bis_annual_report_2024",
    "fixture-02_bis_annual_report_2023",
    "fixture-03_bis_annual_report_2022",
    "fixture-04_bis_annual_report_2021",
    "fixture-05_bis_annual_report_2020",
    "fixture-01_gsa_motor_vehicle_accident_report",
    "fixture-02_nyc_vehicle_inspection_report",
    "fixture-03_dol_labor_inspection_report",
    "fixture-04_hawaii_osha_301_incident_report",
    "fixture-05_nj_driver_vehicle_inspection_report",
]


def _download_pdf(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    request = Request(
        url=url,
        headers={
            "User-Agent": "Mozilla/5.0 (NeuraReport Fixture Builder)",
            "Accept": "application/pdf,*/*",
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            data = response.read()
            content_type = (response.headers.get("Content-Type") or "").lower()
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"Failed to download PDF from {url}: {exc}") from exc

    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"Downloaded file from {url} is not a PDF")
    if content_type and "pdf" not in content_type and "octet-stream" not in content_type:
        raise RuntimeError(f"Unexpected content type for {url}: {content_type}")
    dst.write_bytes(data)


def _create_invoice_db(db_path: Path, *, seed: int, vendor_name: str, currency: str) -> dict[str, Any]:
    rng = random.Random(seed)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            billing_address TEXT,
            city TEXT,
            state TEXT,
            postal_code TEXT,
            country TEXT,
            email TEXT,
            phone TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE invoices (
            invoice_number TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            vendor_name TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            currency TEXT NOT NULL,
            status TEXT NOT NULL,
            subtotal REAL NOT NULL,
            tax_amount REAL NOT NULL,
            discount_amount REAL NOT NULL,
            total_amount REAL NOT NULL,
            notes TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT NOT NULL,
            line_no INTEGER NOT NULL,
            item_code TEXT,
            description TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit_price REAL NOT NULL,
            line_total REAL NOT NULL,
            category TEXT,
            FOREIGN KEY(invoice_number) REFERENCES invoices(invoice_number)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT NOT NULL,
            payment_date TEXT NOT NULL,
            method TEXT NOT NULL,
            transaction_ref TEXT,
            amount_paid REAL NOT NULL,
            FOREIGN KEY(invoice_number) REFERENCES invoices(invoice_number)
        )
        """
    )

    cities = [
        ("New York", "NY"),
        ("Austin", "TX"),
        ("Seattle", "WA"),
        ("Chicago", "IL"),
        ("Denver", "CO"),
        ("Atlanta", "GA"),
        ("Miami", "FL"),
    ]
    categories = ["Services", "Maintenance", "Supplies", "Labor", "Consulting"]
    payment_methods = ["Bank Transfer", "Credit Card", "ACH", "Check"]

    customers: list[tuple[Any, ...]] = []
    for i in range(1, 11):
        city, st = cities[(seed + i) % len(cities)]
        customers.append(
            (
                f"CUST-{seed}-{i:03d}",
                f"Customer {i} {vendor_name.split()[0]}",
                f"{100 + i} Market Street",
                city,
                st,
                f"{10000 + i}",
                "US",
                f"customer{i}@example.com",
                f"+1-555-01{i:03d}",
            )
        )
    cur.executemany(
        """
        INSERT INTO customers (
            customer_id, customer_name, billing_address, city, state,
            postal_code, country, email, phone
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        customers,
    )

    invoice_rows: list[tuple[Any, ...]] = []
    item_rows: list[tuple[Any, ...]] = []
    payment_rows: list[tuple[Any, ...]] = []

    base_issue = date(2025, 8, 1)
    invoice_count = 20
    for idx in range(1, invoice_count + 1):
        inv_no = f"INV-{seed}-{idx:05d}"
        cust_id = customers[(seed + idx) % len(customers)][0]
        issue_date = base_issue + timedelta(days=idx * 3)
        due_date = issue_date + timedelta(days=30)

        line_count = rng.randint(2, 6)
        subtotal = 0.0
        for line_no in range(1, line_count + 1):
            qty = round(rng.uniform(1.0, 12.0), 2)
            unit_price = round(rng.uniform(45.0, 900.0), 2)
            line_total = round(qty * unit_price, 2)
            subtotal += line_total
            item_rows.append(
                (
                    inv_no,
                    line_no,
                    f"ITM-{(seed + idx + line_no) % 999:03d}",
                    f"Line item {line_no} for invoice {idx}",
                    qty,
                    unit_price,
                    line_total,
                    categories[(seed + line_no + idx) % len(categories)],
                )
            )

        subtotal = round(subtotal, 2)
        discount = round(subtotal * rng.choice([0.0, 0.02, 0.05]), 2)
        taxable = max(0.0, subtotal - discount)
        tax = round(taxable * 0.0825, 2)
        total = round(taxable + tax, 2)
        status = "Paid" if idx % 4 != 0 else "Open"
        notes = "Thank you for your business."

        invoice_rows.append(
            (
                inv_no,
                cust_id,
                vendor_name,
                issue_date.isoformat(),
                due_date.isoformat(),
                currency,
                status,
                subtotal,
                tax,
                discount,
                total,
                notes,
            )
        )

        if status == "Paid":
            paid_dt = issue_date + timedelta(days=rng.randint(3, 18))
            payment_rows.append(
                (
                    inv_no,
                    paid_dt.isoformat(),
                    payment_methods[(seed + idx) % len(payment_methods)],
                    f"TXN-{seed}-{idx:06d}",
                    total,
                )
            )

    cur.executemany(
        """
        INSERT INTO invoices (
            invoice_number, customer_id, vendor_name, issue_date, due_date,
            currency, status, subtotal, tax_amount, discount_amount, total_amount, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        invoice_rows,
    )
    cur.executemany(
        """
        INSERT INTO invoice_items (
            invoice_number, line_no, item_code, description, quantity,
            unit_price, line_total, category
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        item_rows,
    )
    cur.executemany(
        """
        INSERT INTO payments (
            invoice_number, payment_date, method, transaction_ref, amount_paid
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        payment_rows,
    )

    conn.commit()
    conn.close()
    return {
        "tables": ["customers", "invoices", "invoice_items", "payments"],
        "row_counts": {
            "customers": len(customers),
            "invoices": len(invoice_rows),
            "invoice_items": len(item_rows),
            "payments": len(payment_rows),
        },
    }


def _register_connection(connection_id: str, name: str, db_path: Path, tags: list[str]) -> None:
    db_abs = str(db_path.resolve())
    db_url = f"sqlite:///{db_abs}"
    state_store.upsert_connection(
        conn_id=connection_id,
        name=name,
        db_type="sqlite",
        database_path=db_abs,
        secret_payload={"database": db_abs, "db_url": db_url},
        status="connected",
        latency_ms=0.0,
        tags=tags,
    )
    state_store.record_connection_ping(
        connection_id,
        status="connected",
        detail="Fixture connection prepared",
        latency_ms=0.0,
    )


def _remove_known_fixture_connections() -> None:
    ids = [f"fixture-{fixture['id']}" for fixture in PDF_FIXTURES] + LEGACY_FIXTURE_CONNECTION_IDS
    for conn_id in ids:
        try:
            state_store.delete_connection(conn_id)
        except Exception:
            continue


def _reset_output_dirs(output_root: Path) -> None:
    for sub in ("pdf_reports", "databases"):
        path = output_root / sub
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)


def _build_fixture(output_root: Path, fixture: dict[str, Any], register_connections: bool) -> dict[str, Any]:
    pdf_path = output_root / "pdf_reports" / fixture["pdf_name"]
    db_path = output_root / "databases" / fixture["db_name"]
    connection_id = f"fixture-{fixture['id']}"

    _download_pdf(fixture["pdf_url"], pdf_path)
    db_meta = _create_invoice_db(
        db_path,
        seed=fixture["seed"],
        vendor_name=fixture["vendor_name"],
        currency=fixture["currency"],
    )

    if register_connections:
        _register_connection(
            connection_id=connection_id,
            name=fixture["connection_name"],
            db_path=db_path,
            tags=["fixture", "report-testkit", "report-generation", "invoice", "web-pdf"],
        )

    return {
        "id": fixture["id"],
        "report_type": fixture["report_type"],
        "pdf": {
            "path": str(pdf_path.relative_to(ROOT)),
            "source_url": fixture["pdf_url"],
            "size_bytes": pdf_path.stat().st_size,
        },
        "database": {
            "path": str(db_path.relative_to(ROOT)),
            "size_bytes": db_path.stat().st_size,
            "kind": "invoice",
            **db_meta,
        },
        "connection": {
            "id": connection_id,
            "name": fixture["connection_name"],
            "registered": register_connections,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create 5 invoice-style PDF + SQLite fixtures for NeuraReport")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Output folder for fixtures (default: samples/report_generation_testkit)",
    )
    parser.add_argument(
        "--skip-register-connections",
        action="store_true",
        help="Create files only; do not register connections in state store",
    )
    args = parser.parse_args()

    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    _reset_output_dirs(output_root)

    if not args.skip_register_connections:
        _remove_known_fixture_connections()

    fixtures_output: list[dict[str, Any]] = []
    for fixture in PDF_FIXTURES:
        fixtures_output.append(
            _build_fixture(
                output_root=output_root,
                fixture=fixture,
                register_connections=not args.skip_register_connections,
            )
        )

    manifest = {
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "project_root": str(ROOT),
        "output_root": str(output_root),
        "registered_connections": not args.skip_register_connections,
        "fixtures": fixtures_output,
    }
    manifest_path = output_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("Created report-generation testkit:")
    print(f"  manifest: {manifest_path}")
    for item in fixtures_output:
        print(
            f"  - {item['id']}: {item['pdf']['path']} | {item['database']['path']} | {item['connection']['id']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
