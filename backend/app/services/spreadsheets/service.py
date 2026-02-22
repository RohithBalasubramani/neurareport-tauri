"""
Spreadsheet Service - Core spreadsheet operations.
"""

from __future__ import annotations

import json
import logging
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel

from backend.app.services.config import get_settings

logger = logging.getLogger("neura.spreadsheets")


class CellValue(BaseModel):
    """Cell value with type information."""

    value: Any
    formula: Optional[str] = None
    formatted_value: Optional[str] = None
    cell_type: str = "string"  # string, number, boolean, date, formula, error


class CellFormat(BaseModel):
    """Cell formatting options."""

    bold: bool = False
    italic: bool = False
    underline: bool = False
    font_size: int = 11
    font_color: str = "#000000"
    background_color: Optional[str] = None
    horizontal_align: str = "left"  # left, center, right
    vertical_align: str = "middle"  # top, middle, bottom
    number_format: Optional[str] = None
    border: Optional[dict[str, Any]] = None


class ConditionalFormat(BaseModel):
    """Conditional formatting rule."""

    id: str
    range: str  # e.g., "A1:B10"
    type: str  # greaterThan, lessThan, equals, between, text, custom
    value: Any
    value2: Optional[Any] = None  # For "between" type
    format: CellFormat


class DataValidation(BaseModel):
    """Data validation rule."""

    id: str
    range: str
    type: str  # list, number, date, text, custom
    criteria: str  # equals, between, greaterThan, etc.
    value: Any
    value2: Optional[Any] = None
    allow_blank: bool = True
    show_dropdown: bool = True
    error_message: Optional[str] = None


class Sheet(BaseModel):
    """Single sheet in a spreadsheet."""

    id: str
    name: str
    index: int
    data: list[list[Any]]  # 2D array of cell values
    formats: dict[str, CellFormat] = {}  # cell address -> format
    column_widths: dict[int, int] = {}
    row_heights: dict[int, int] = {}
    frozen_rows: int = 0
    frozen_cols: int = 0
    conditional_formats: list[ConditionalFormat] = []
    data_validations: list[DataValidation] = []


class Spreadsheet(BaseModel):
    """Spreadsheet model."""

    id: str
    name: str
    sheets: list[Sheet]
    created_at: str
    updated_at: str
    owner_id: Optional[str] = None
    metadata: dict[str, Any] = {}


class PivotTableConfig(BaseModel):
    """Pivot table configuration."""

    id: str
    spreadsheet_id: str
    sheet_id: str
    source_range: str
    rows: list[str]  # Field names for rows
    columns: list[str]  # Field names for columns
    values: list[dict[str, str]]  # [{"field": "Amount", "aggregation": "SUM"}]
    filters: list[dict[str, Any]] = []
    name: str = "PivotTable1"


class SpreadsheetService:
    """Service for spreadsheet CRUD operations."""

    def __init__(self, storage_path: Optional[Path] = None):
        base_root = get_settings().uploads_root
        self._storage_path = storage_path or (base_root / "spreadsheets")
        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def create(
        self,
        name: str,
        owner_id: Optional[str] = None,
        initial_data: Optional[list[list[Any]]] = None,
    ) -> Spreadsheet:
        """Create a new spreadsheet."""
        now = datetime.now(timezone.utc).isoformat()

        # Create initial sheet
        initial_sheet = Sheet(
            id=str(uuid.uuid4()),
            name="Sheet1",
            index=0,
            data=initial_data or [["" for _ in range(26)] for _ in range(100)],
        )

        spreadsheet = Spreadsheet(
            id=str(uuid.uuid4()),
            name=name,
            sheets=[initial_sheet],
            created_at=now,
            updated_at=now,
            owner_id=owner_id,
        )

        self._save_spreadsheet(spreadsheet)
        logger.info(f"Created spreadsheet: {spreadsheet.id}")
        return spreadsheet

    def get(self, spreadsheet_id: str) -> Optional[Spreadsheet]:
        """Get a spreadsheet by ID."""
        file_path = self._get_spreadsheet_path(spreadsheet_id)
        if not file_path or not file_path.exists():
            return None
        with open(file_path) as f:
            data = json.load(f)
        return Spreadsheet(**data)

    def update(
        self,
        spreadsheet_id: str,
        name: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Optional[Spreadsheet]:
        """Update spreadsheet metadata."""
        with self._lock:
            spreadsheet = self.get(spreadsheet_id)
            if not spreadsheet:
                return None

            if name:
                spreadsheet.name = name
            if metadata:
                spreadsheet.metadata.update(metadata)

            spreadsheet.updated_at = datetime.now(timezone.utc).isoformat()
            self._save_spreadsheet(spreadsheet)
            return spreadsheet

    def delete(self, spreadsheet_id: str) -> bool:
        """Delete a spreadsheet."""
        file_path = self._get_spreadsheet_path(spreadsheet_id)
        if not file_path or not file_path.exists():
            return False
        file_path.unlink()
        logger.info(f"Deleted spreadsheet: {spreadsheet_id}")
        return True

    def update_cells(
        self,
        spreadsheet_id: str,
        sheet_index: int,
        updates: list[dict[str, Any]],
    ) -> Optional[Spreadsheet]:
        """Update cell values. updates = [{"row": 0, "col": 0, "value": "Hello"}]"""
        with self._lock:
            spreadsheet = self.get(spreadsheet_id)
            if not spreadsheet:
                return None

            if sheet_index < 0 or sheet_index >= len(spreadsheet.sheets):
                return None

            sheet = spreadsheet.sheets[sheet_index]

            for update in updates:
                row = update.get("row", 0)
                col = update.get("col", 0)
                value = update.get("value", "")

                # Expand data array if needed
                while row >= len(sheet.data):
                    sheet.data.append(["" for _ in range(len(sheet.data[0]) if sheet.data else 26)])
                while col >= len(sheet.data[row]):
                    sheet.data[row].append("")

                sheet.data[row][col] = value

            spreadsheet.updated_at = datetime.now(timezone.utc).isoformat()
            self._save_spreadsheet(spreadsheet)
            return spreadsheet

    def add_sheet(
        self,
        spreadsheet_id: str,
        name: Optional[str] = None,
    ) -> Optional[Sheet]:
        """Add a new sheet to the spreadsheet."""
        with self._lock:
            spreadsheet = self.get(spreadsheet_id)
            if not spreadsheet:
                return None

            new_index = len(spreadsheet.sheets)
            sheet_name = name or f"Sheet{new_index + 1}"

            sheet = Sheet(
                id=str(uuid.uuid4()),
                name=sheet_name,
                index=new_index,
                data=[["" for _ in range(26)] for _ in range(100)],
            )

            spreadsheet.sheets.append(sheet)
            spreadsheet.updated_at = datetime.now(timezone.utc).isoformat()
            self._save_spreadsheet(spreadsheet)

            logger.info(f"Added sheet {sheet_name} to spreadsheet {spreadsheet_id}")
            return sheet

    def delete_sheet(self, spreadsheet_id: str, sheet_id: str) -> bool:
        """Delete a sheet from the spreadsheet."""
        with self._lock:
            spreadsheet = self.get(spreadsheet_id)
            if not spreadsheet:
                return False

            # Don't delete last sheet
            if len(spreadsheet.sheets) <= 1:
                return False

            spreadsheet.sheets = [s for s in spreadsheet.sheets if s.id != sheet_id]

            # Reindex sheets
            for i, sheet in enumerate(spreadsheet.sheets):
                sheet.index = i

            spreadsheet.updated_at = datetime.now(timezone.utc).isoformat()
            self._save_spreadsheet(spreadsheet)
            return True

    def rename_sheet(
        self,
        spreadsheet_id: str,
        sheet_id: str,
        new_name: str,
    ) -> bool:
        """Rename a sheet."""
        with self._lock:
            spreadsheet = self.get(spreadsheet_id)
            if not spreadsheet:
                return False

            for sheet in spreadsheet.sheets:
                if sheet.id == sheet_id:
                    sheet.name = new_name
                    spreadsheet.updated_at = datetime.now(timezone.utc).isoformat()
                    self._save_spreadsheet(spreadsheet)
                    return True

            return False

    def set_conditional_format(
        self,
        spreadsheet_id: str,
        sheet_id: str,
        conditional_format: ConditionalFormat,
    ) -> bool:
        """Add or update a conditional format rule."""
        with self._lock:
            spreadsheet = self.get(spreadsheet_id)
            if not spreadsheet:
                return False

            for sheet in spreadsheet.sheets:
                if sheet.id == sheet_id:
                    # Update existing or add new
                    updated = False
                    for i, cf in enumerate(sheet.conditional_formats):
                        if cf.id == conditional_format.id:
                            sheet.conditional_formats[i] = conditional_format
                            updated = True
                            break

                    if not updated:
                        sheet.conditional_formats.append(conditional_format)

                    spreadsheet.updated_at = datetime.now(timezone.utc).isoformat()
                    self._save_spreadsheet(spreadsheet)
                    return True

            return False

    def set_data_validation(
        self,
        spreadsheet_id: str,
        sheet_id: str,
        validation: DataValidation,
    ) -> bool:
        """Add or update a data validation rule."""
        with self._lock:
            spreadsheet = self.get(spreadsheet_id)
            if not spreadsheet:
                return False

            for sheet in spreadsheet.sheets:
                if sheet.id == sheet_id:
                    # Update existing or add new
                    updated = False
                    for i, dv in enumerate(sheet.data_validations):
                        if dv.id == validation.id:
                            sheet.data_validations[i] = validation
                            updated = True
                            break

                    if not updated:
                        sheet.data_validations.append(validation)

                    spreadsheet.updated_at = datetime.now(timezone.utc).isoformat()
                    self._save_spreadsheet(spreadsheet)
                    return True

            return False

    def freeze_panes(
        self,
        spreadsheet_id: str,
        sheet_id: str,
        rows: int = 0,
        cols: int = 0,
    ) -> bool:
        """Set frozen rows and columns for a sheet."""
        with self._lock:
            spreadsheet = self.get(spreadsheet_id)
            if not spreadsheet:
                return False

            for sheet in spreadsheet.sheets:
                if sheet.id == sheet_id:
                    sheet.frozen_rows = rows
                    sheet.frozen_cols = cols
                    spreadsheet.updated_at = datetime.now(timezone.utc).isoformat()
                    self._save_spreadsheet(spreadsheet)
                    return True

            return False

    def import_csv(
        self,
        csv_content: str,
        name: str = "Imported Spreadsheet",
        delimiter: str = ",",
        owner_id: Optional[str] = None,
    ) -> Spreadsheet:
        """Import a CSV file as a new spreadsheet."""
        import csv
        from io import StringIO

        reader = csv.reader(StringIO(csv_content), delimiter=delimiter)
        data = list(reader)

        # Pad rows to equal length
        max_cols = max(len(row) for row in data) if data else 26
        for row in data:
            while len(row) < max_cols:
                row.append("")

        return self.create(name=name, owner_id=owner_id, initial_data=data)

    def import_xlsx(
        self,
        xlsx_content: bytes,
        name: str = "Imported Spreadsheet",
        owner_id: Optional[str] = None,
    ) -> Spreadsheet:
        """Import an XLSX file as a new spreadsheet."""
        import openpyxl
        from io import BytesIO

        wb = openpyxl.load_workbook(BytesIO(xlsx_content), data_only=True)
        sheets: list[Sheet] = []
        for idx, ws in enumerate(wb.worksheets):
            data: list[list[Any]] = []
            for row in ws.iter_rows(values_only=True):
                data.append([("" if v is None else v) for v in row])
            if not data:
                data = [["" for _ in range(26)] for _ in range(100)]
            # Pad rows to equal length
            max_cols = max(len(r) for r in data) if data else 26
            for r in data:
                while len(r) < max_cols:
                    r.append("")
            sheets.append(Sheet(
                id=str(uuid.uuid4()),
                name=ws.title or f"Sheet{idx + 1}",
                index=idx,
                data=data,
            ))

        if not sheets:
            sheets = [Sheet(
                id=str(uuid.uuid4()),
                name="Sheet1",
                index=0,
                data=[["" for _ in range(26)] for _ in range(100)],
            )]

        now = datetime.now(timezone.utc).isoformat()
        spreadsheet = Spreadsheet(
            id=str(uuid.uuid4()),
            name=name,
            sheets=sheets,
            created_at=now,
            updated_at=now,
            owner_id=owner_id,
        )
        self._save_spreadsheet(spreadsheet)
        logger.info(f"Imported XLSX spreadsheet: {spreadsheet.id} ({len(sheets)} sheets)")
        return spreadsheet

    def export_csv(
        self,
        spreadsheet_id: str,
        sheet_index: int = 0,
        delimiter: str = ",",
    ) -> Optional[str]:
        """Export a sheet as CSV."""
        import csv
        from io import StringIO

        spreadsheet = self.get(spreadsheet_id)
        if not spreadsheet:
            return None

        if sheet_index < 0 or sheet_index >= len(spreadsheet.sheets):
            return None

        sheet = spreadsheet.sheets[sheet_index]
        output = StringIO()
        writer = csv.writer(output, delimiter=delimiter)

        for row in sheet.data:
            writer.writerow(row)

        return output.getvalue()

    def export_xlsx(
        self,
        spreadsheet_id: str,
        sheet_index: int = 0,
    ) -> Optional[bytes]:
        """Export a sheet as XLSX binary."""
        import openpyxl
        from io import BytesIO

        spreadsheet = self.get(spreadsheet_id)
        if not spreadsheet:
            return None

        if sheet_index < 0 or sheet_index >= len(spreadsheet.sheets):
            return None

        sheet = spreadsheet.sheets[sheet_index]
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = sheet.name

        for row in sheet.data:
            ws.append(row)

        buf = BytesIO()
        wb.save(buf)
        return buf.getvalue()

    def list_spreadsheets(
        self,
        owner_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Spreadsheet]:
        """List all spreadsheets."""
        spreadsheets = []

        for file_path in self._storage_path.glob("*.json"):
            try:
                with open(file_path) as f:
                    data = json.load(f)
                spreadsheet = Spreadsheet(**data)

                if owner_id and spreadsheet.owner_id != owner_id:
                    continue

                spreadsheets.append(spreadsheet)
            except Exception as e:
                logger.warning(f"Error loading spreadsheet from {file_path}: {e}")

        # Sort by updated_at descending
        spreadsheets.sort(key=lambda s: s.updated_at, reverse=True)
        return spreadsheets[offset:offset + limit]

    def _normalize_id(self, spreadsheet_id: str) -> Optional[str]:
        try:
            return str(uuid.UUID(str(spreadsheet_id)))
        except (ValueError, TypeError):
            return None

    def _get_spreadsheet_path(self, spreadsheet_id: str) -> Optional[Path]:
        """Get path to spreadsheet JSON file."""
        normalized = self._normalize_id(spreadsheet_id)
        if not normalized:
            return None
        return self._storage_path / f"{normalized}.json"

    def _save_spreadsheet(self, spreadsheet: Spreadsheet) -> None:
        """Save spreadsheet to disk."""
        file_path = self._get_spreadsheet_path(spreadsheet.id)
        if not file_path:
            raise ValueError(f"Invalid spreadsheet ID: {spreadsheet.id}")
        with open(file_path, "w") as f:
            json.dump(spreadsheet.model_dump(), f, indent=2)
