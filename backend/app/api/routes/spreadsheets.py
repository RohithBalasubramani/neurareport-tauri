"""
Spreadsheet API Routes - Spreadsheet editing and analysis endpoints.
"""

from __future__ import annotations

import logging
import threading
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import io

from ...schemas.spreadsheets import (
    CreateSpreadsheetRequest,
    UpdateSpreadsheetRequest,
    SpreadsheetResponse,
    SpreadsheetListResponse,
    CellUpdateRequest,
    SheetResponse,
    AddSheetRequest,
    ConditionalFormatRequest,
    DataValidationRequest,
    FreezePanesRequest,
    ExportRequest,
    PivotTableRequest,
    PivotTableResponse,
    AIFormulaRequest,
    AIFormulaResponse,
)
from ...services.spreadsheets import (
    SpreadsheetService,
    FormulaEngine,
    PivotService,
)
from ...services.ai.spreadsheet_ai_service import (
    spreadsheet_ai_service,
    SpreadsheetAIService,
)
from backend.app.services.security import require_api_key

logger = logging.getLogger("neura.api.spreadsheets")

router = APIRouter(tags=["spreadsheets"], dependencies=[Depends(require_api_key)])

# Service instances
_lock = threading.Lock()
_spreadsheet_service: Optional[SpreadsheetService] = None
_formula_engine: Optional[FormulaEngine] = None
_pivot_service: Optional[PivotService] = None


def get_spreadsheet_service() -> SpreadsheetService:
    global _spreadsheet_service
    if _spreadsheet_service is None:
        with _lock:
            if _spreadsheet_service is None:
                _spreadsheet_service = SpreadsheetService()
    return _spreadsheet_service


def get_formula_engine() -> FormulaEngine:
    global _formula_engine
    if _formula_engine is None:
        with _lock:
            if _formula_engine is None:
                _formula_engine = FormulaEngine()
    return _formula_engine


def get_pivot_service() -> PivotService:
    global _pivot_service
    if _pivot_service is None:
        with _lock:
            if _pivot_service is None:
                _pivot_service = PivotService()
    return _pivot_service


# ============================================
# Spreadsheet CRUD Endpoints
# ============================================

@router.post("", response_model=SpreadsheetResponse)
async def create_spreadsheet(
    request: CreateSpreadsheetRequest,
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Create a new spreadsheet."""
    spreadsheet = svc.create(
        name=request.name,
        initial_data=request.initial_data,
    )
    return _to_spreadsheet_response(spreadsheet)


@router.get("", response_model=SpreadsheetListResponse)
async def list_spreadsheets(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """List all spreadsheets."""
    spreadsheets = svc.list_spreadsheets(limit=limit, offset=offset)
    return SpreadsheetListResponse(
        spreadsheets=[_to_spreadsheet_response(s) for s in spreadsheets],
        total=len(spreadsheets),
        offset=offset,
        limit=limit,
    )


@router.get("/{spreadsheet_id}")
async def get_spreadsheet(
    spreadsheet_id: str,
    sheet_index: int = Query(0, ge=0),
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Get a spreadsheet with data."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    if sheet_index >= len(spreadsheet.sheets):
        raise HTTPException(status_code=400, detail="Sheet index out of range")

    sheet = spreadsheet.sheets[sheet_index]
    return {
        "id": spreadsheet.id,
        "name": spreadsheet.name,
        "sheet_id": sheet.id,
        "sheet_name": sheet.name,
        "data": sheet.data,
        "formats": sheet.formats,
        "column_widths": sheet.column_widths,
        "row_heights": sheet.row_heights,
        "frozen_rows": sheet.frozen_rows,
        "frozen_cols": sheet.frozen_cols,
        "conditional_formats": [cf.model_dump() for cf in sheet.conditional_formats],
        "data_validations": [dv.model_dump() for dv in sheet.data_validations],
    }


@router.put("/{spreadsheet_id}", response_model=SpreadsheetResponse)
async def update_spreadsheet(
    spreadsheet_id: str,
    request: UpdateSpreadsheetRequest,
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Update spreadsheet metadata."""
    spreadsheet = svc.update(
        spreadsheet_id=spreadsheet_id,
        name=request.name,
        metadata=request.metadata,
    )
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")
    return _to_spreadsheet_response(spreadsheet)


@router.delete("/{spreadsheet_id}")
async def delete_spreadsheet(
    spreadsheet_id: str,
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Delete a spreadsheet."""
    success = svc.delete(spreadsheet_id)
    if not success:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")
    return {"status": "ok", "message": "Spreadsheet deleted"}


# ============================================
# Cell Operations
# ============================================

@router.put("/{spreadsheet_id}/cells")
async def update_cells(
    spreadsheet_id: str,
    request: CellUpdateRequest,
    sheet_index: int = Query(0, ge=0),
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Update cell values."""
    updates = [{"row": u.row, "col": u.col, "value": u.value} for u in request.updates]
    spreadsheet = svc.update_cells(spreadsheet_id, sheet_index, updates)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")
    return {"status": "ok", "updated_count": len(updates)}


@router.get("/{spreadsheet_id}/cells")
async def get_cell_range(
    spreadsheet_id: str,
    sheet_index: int = Query(0, ge=0),
    start_row: int = Query(0, ge=0),
    start_col: int = Query(0, ge=0),
    end_row: int = Query(99, ge=0),
    end_col: int = Query(25, ge=0),
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Get cell range from a spreadsheet sheet."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    if sheet_index >= len(spreadsheet.sheets):
        raise HTTPException(status_code=400, detail="Sheet index out of range")

    sheet = spreadsheet.sheets[sheet_index]
    data = sheet.data

    # Clamp end bounds to actual data dimensions
    actual_end_row = min(end_row, len(data) - 1)
    actual_end_col = min(end_col, (len(data[0]) - 1) if data else 0)

    if start_row > actual_end_row or start_col > actual_end_col:
        return {
            "spreadsheet_id": spreadsheet_id,
            "sheet_index": sheet_index,
            "start_row": start_row,
            "start_col": start_col,
            "end_row": end_row,
            "end_col": end_col,
            "data": [],
        }

    sliced = []
    for r in range(start_row, actual_end_row + 1):
        row = data[r][start_col:actual_end_col + 1] if r < len(data) else []
        sliced.append(row)

    return {
        "spreadsheet_id": spreadsheet_id,
        "sheet_index": sheet_index,
        "start_row": start_row,
        "start_col": start_col,
        "end_row": actual_end_row,
        "end_col": actual_end_col,
        "data": sliced,
    }


# ============================================
# Sheet Operations
# ============================================

@router.post("/{spreadsheet_id}/sheets", response_model=SheetResponse)
async def add_sheet(
    spreadsheet_id: str,
    request: AddSheetRequest,
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Add a new sheet to the spreadsheet."""
    sheet = svc.add_sheet(spreadsheet_id, request.name)
    if not sheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")
    return SheetResponse(
        id=sheet.id,
        name=sheet.name,
        index=sheet.index,
        row_count=len(sheet.data),
        col_count=len(sheet.data[0]) if sheet.data else 0,
        frozen_rows=sheet.frozen_rows,
        frozen_cols=sheet.frozen_cols,
    )


@router.delete("/{spreadsheet_id}/sheets/{sheet_id}")
async def delete_sheet(
    spreadsheet_id: str,
    sheet_id: str,
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Delete a sheet from the spreadsheet."""
    success = svc.delete_sheet(spreadsheet_id, sheet_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot delete sheet (not found or last sheet)")
    return {"status": "ok", "message": "Sheet deleted"}


@router.put("/{spreadsheet_id}/sheets/{sheet_id}/rename")
async def rename_sheet(
    spreadsheet_id: str,
    sheet_id: str,
    name: str = Query(..., min_length=1, max_length=100),
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Rename a sheet."""
    success = svc.rename_sheet(spreadsheet_id, sheet_id, name)
    if not success:
        raise HTTPException(status_code=404, detail="Sheet not found")
    return {"status": "ok", "message": "Sheet renamed"}


@router.put("/{spreadsheet_id}/sheets/{sheet_id}/freeze")
async def freeze_panes(
    spreadsheet_id: str,
    sheet_id: str,
    request: FreezePanesRequest,
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Set frozen rows and columns."""
    success = svc.freeze_panes(spreadsheet_id, sheet_id, request.rows, request.cols)
    if not success:
        raise HTTPException(status_code=404, detail="Sheet not found")
    return {"status": "ok", "frozen_rows": request.rows, "frozen_cols": request.cols}


# ============================================
# Conditional Formatting
# ============================================

@router.post("/{spreadsheet_id}/sheets/{sheet_id}/conditional-format")
async def add_conditional_format(
    spreadsheet_id: str,
    sheet_id: str,
    request: ConditionalFormatRequest,
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Add conditional formatting rules."""
    import uuid
    from ...services.spreadsheets.service import ConditionalFormat, CellFormat

    for rule in request.rules:
        cf = ConditionalFormat(
            id=str(uuid.uuid4()),
            range=request.range,
            type=rule.type,
            value=rule.value,
            value2=rule.value2,
            format=CellFormat(**rule.format.model_dump()),
        )
        success = svc.set_conditional_format(spreadsheet_id, sheet_id, cf)
        if not success:
            raise HTTPException(status_code=404, detail="Sheet not found")

    return {"status": "ok", "message": "Conditional formatting applied"}


@router.delete("/{spreadsheet_id}/sheets/{sheet_id}/conditional-formats/{format_id}")
async def remove_conditional_format(
    spreadsheet_id: str,
    sheet_id: str,
    format_id: str,
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Remove a conditional format by ID from a sheet."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    for sheet in spreadsheet.sheets:
        if sheet.id == sheet_id:
            original_count = len(sheet.conditional_formats)
            sheet.conditional_formats = [
                cf for cf in sheet.conditional_formats if cf.id != format_id
            ]
            if len(sheet.conditional_formats) == original_count:
                raise HTTPException(status_code=404, detail="Conditional format not found")

            from datetime import datetime, timezone
            spreadsheet.updated_at = datetime.now(timezone.utc).isoformat()
            svc._save_spreadsheet(spreadsheet)
            return {"status": "ok", "message": "Conditional format removed"}

    raise HTTPException(status_code=404, detail="Sheet not found")


# ============================================
# Data Validation
# ============================================

@router.post("/{spreadsheet_id}/sheets/{sheet_id}/validation")
async def add_data_validation(
    spreadsheet_id: str,
    sheet_id: str,
    request: DataValidationRequest,
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Add data validation rules."""
    import uuid
    from ...services.spreadsheets.service import DataValidation

    dv = DataValidation(
        id=str(uuid.uuid4()),
        range=request.range,
        type=request.type,
        criteria=request.criteria,
        value=request.value,
        value2=request.value2,
        allow_blank=request.allow_blank,
        show_dropdown=request.show_dropdown,
        error_message=request.error_message,
    )
    success = svc.set_data_validation(spreadsheet_id, sheet_id, dv)
    if not success:
        raise HTTPException(status_code=404, detail="Sheet not found")

    return {"status": "ok", "message": "Data validation applied"}


# ============================================
# Import/Export
# ============================================

@router.post("/import")
async def import_spreadsheet(
    file: UploadFile = File(...),
    name: Optional[str] = Query(None),
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Import a spreadsheet from CSV or Excel file."""
    content = await file.read()
    filename = file.filename or "import"

    if filename.endswith(".csv"):
        spreadsheet = svc.import_csv(
            content.decode("utf-8"),
            name=name or filename.replace(".csv", ""),
        )
    elif filename.endswith((".xlsx", ".xls")):
        spreadsheet = svc.import_xlsx(
            content,
            name=name or filename.rsplit(".", 1)[0],
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or XLSX.")

    return _to_spreadsheet_response(spreadsheet)


# ============================================
# Formula Utilities (static paths - must be before /{spreadsheet_id})
# ============================================

class FormulaValidateRequest(BaseModel):
    formula: str = Field(..., min_length=1)


@router.post("/formula/validate")
async def validate_formula(
    request: FormulaValidateRequest,
    engine: FormulaEngine = Depends(get_formula_engine),
):
    """Validate a formula syntax."""
    formula = request.formula
    if not formula.startswith("="):
        formula = f"={formula}"

    # Use engine to check syntax by evaluating against empty data
    result = engine.evaluate(formula, [[]])
    is_valid = result.error is None
    return {
        "formula": request.formula,
        "valid": is_valid,
        "error": result.error,
    }


@router.get("/formula/functions")
async def list_formula_functions(
    engine: FormulaEngine = Depends(get_formula_engine),
):
    """List available formula functions."""
    functions = []
    for name, func in engine.FUNCTIONS.items():
        doc = getattr(func, "__doc__", None) or f"{name} function"
        functions.append({
            "name": name,
            "description": doc.strip(),
        })
    return {"functions": functions, "total": len(functions)}


@router.get("/{spreadsheet_id}/export")
async def export_spreadsheet(
    spreadsheet_id: str,
    format: str = Query("csv", pattern="^(csv|tsv|xlsx)$"),
    sheet_index: int = Query(0, ge=0),
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Export a spreadsheet to CSV, TSV, or Excel format."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    filename = f"{spreadsheet.name}.{format}"

    if format == "xlsx":
        xlsx_bytes = svc.export_xlsx(spreadsheet_id, sheet_index)
        if xlsx_bytes is None:
            raise HTTPException(status_code=404, detail="Spreadsheet not found")
        return StreamingResponse(
            io.BytesIO(xlsx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    delimiter = "\t" if format == "tsv" else ","
    content = svc.export_csv(spreadsheet_id, sheet_index, delimiter)
    if content is None:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    return StreamingResponse(
        io.StringIO(content),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ============================================
# Pivot Tables
# ============================================

@router.post("/{spreadsheet_id}/pivot", response_model=PivotTableResponse)
async def create_pivot_table(
    spreadsheet_id: str,
    request: PivotTableRequest,
    sheet_index: int = Query(0, ge=0),
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
    pivot_svc: PivotService = Depends(get_pivot_service),
):
    """Create a pivot table from spreadsheet data."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    if sheet_index >= len(spreadsheet.sheets):
        raise HTTPException(status_code=400, detail="Sheet index out of range")

    sheet = spreadsheet.sheets[sheet_index]

    # Convert sheet data to records
    records = pivot_svc.data_to_records(sheet.data)

    # Create pivot config
    from ...services.spreadsheets.pivot_service import PivotTableConfig, PivotValue, PivotFilter
    config = PivotTableConfig(
        id="",
        name=request.name,
        source_sheet_id=sheet.id,
        source_range=request.source_range,
        row_fields=request.row_fields,
        column_fields=request.column_fields,
        value_fields=[
            PivotValue(
                field=v.field,
                aggregation=v.aggregation,
                alias=v.alias,
            )
            for v in request.value_fields
        ],
        filters=[
            PivotFilter(
                field=f.field,
                values=f.values,
                exclude=f.exclude,
            )
            for f in request.filters
        ],
        show_grand_totals=request.show_grand_totals,
        show_row_totals=request.show_row_totals,
        show_col_totals=request.show_col_totals,
    )

    result = pivot_svc.compute_pivot(records, config)

    return PivotTableResponse(
        id=config.id,
        name=config.name,
        headers=result.headers,
        rows=result.rows,
        column_totals=result.column_totals,
        grand_total=result.grand_total,
    )


@router.put("/{spreadsheet_id}/pivot/{pivot_id}", response_model=PivotTableResponse)
async def update_pivot_table(
    spreadsheet_id: str,
    pivot_id: str,
    request: PivotTableRequest,
    sheet_index: int = Query(0, ge=0),
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
    pivot_svc: PivotService = Depends(get_pivot_service),
):
    """Update a pivot table and recompute with updated config."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    if sheet_index >= len(spreadsheet.sheets):
        raise HTTPException(status_code=400, detail="Sheet index out of range")

    sheet = spreadsheet.sheets[sheet_index]

    # Convert sheet data to records
    records = pivot_svc.data_to_records(sheet.data)

    # Create updated pivot config with existing ID
    from ...services.spreadsheets.pivot_service import PivotTableConfig, PivotValue, PivotFilter
    config = PivotTableConfig(
        id=pivot_id,
        name=request.name,
        source_sheet_id=sheet.id,
        source_range=request.source_range,
        row_fields=request.row_fields,
        column_fields=request.column_fields,
        value_fields=[
            PivotValue(
                field=v.field,
                aggregation=v.aggregation,
                alias=v.alias,
            )
            for v in request.value_fields
        ],
        filters=[
            PivotFilter(
                field=f.field,
                values=f.values,
                exclude=f.exclude,
            )
            for f in request.filters
        ],
        show_grand_totals=request.show_grand_totals,
        show_row_totals=request.show_row_totals,
        show_col_totals=request.show_col_totals,
    )

    result = pivot_svc.compute_pivot(records, config)

    return PivotTableResponse(
        id=config.id,
        name=config.name,
        headers=result.headers,
        rows=result.rows,
        column_totals=result.column_totals,
        grand_total=result.grand_total,
    )


@router.delete("/{spreadsheet_id}/pivot/{pivot_id}")
async def delete_pivot_table(
    spreadsheet_id: str,
    pivot_id: str,
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Delete a pivot table."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    # Remove pivot table metadata from spreadsheet
    pivots = spreadsheet.metadata.get("pivot_tables", {})
    if pivot_id not in pivots:
        raise HTTPException(status_code=404, detail="Pivot table not found")

    del pivots[pivot_id]
    spreadsheet.metadata["pivot_tables"] = pivots

    from datetime import datetime, timezone
    spreadsheet.updated_at = datetime.now(timezone.utc).isoformat()
    svc._save_spreadsheet(spreadsheet)

    return {"status": "ok", "message": "Pivot table deleted"}


@router.post("/{spreadsheet_id}/pivot/{pivot_id}/refresh", response_model=PivotTableResponse)
async def refresh_pivot_table(
    spreadsheet_id: str,
    pivot_id: str,
    sheet_index: int = Query(0, ge=0),
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
    pivot_svc: PivotService = Depends(get_pivot_service),
):
    """Refresh/recompute a pivot table using its existing config."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    # Retrieve pivot config from metadata
    pivots = spreadsheet.metadata.get("pivot_tables", {})
    pivot_config_data = pivots.get(pivot_id)
    if not pivot_config_data:
        raise HTTPException(status_code=404, detail="Pivot table not found")

    if sheet_index >= len(spreadsheet.sheets):
        raise HTTPException(status_code=400, detail="Sheet index out of range")

    sheet = spreadsheet.sheets[sheet_index]
    records = pivot_svc.data_to_records(sheet.data)

    from ...services.spreadsheets.pivot_service import PivotTableConfig
    config = PivotTableConfig(**pivot_config_data)

    result = pivot_svc.compute_pivot(records, config)

    return PivotTableResponse(
        id=config.id,
        name=config.name,
        headers=result.headers,
        rows=result.rows,
        column_totals=result.column_totals,
        grand_total=result.grand_total,
    )


# ============================================
# Formula Evaluation
# ============================================

@router.post("/{spreadsheet_id}/evaluate")
async def evaluate_formula(
    spreadsheet_id: str,
    formula: str = Query(..., min_length=1),
    sheet_index: int = Query(0, ge=0),
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
    engine: FormulaEngine = Depends(get_formula_engine),
):
    """Evaluate a formula against spreadsheet data."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    if sheet_index >= len(spreadsheet.sheets):
        raise HTTPException(status_code=400, detail="Sheet index out of range")

    sheet = spreadsheet.sheets[sheet_index]
    result = engine.evaluate(formula, sheet.data)

    return {
        "formula": formula,
        "value": result.value,
        "formatted_value": result.formatted_value,
        "error": result.error,
    }


# ============================================
# AI Features
# ============================================

@router.post("/{spreadsheet_id}/ai/formula", response_model=AIFormulaResponse)
async def generate_formula(
    spreadsheet_id: str,
    request: AIFormulaRequest,
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Generate a formula from natural language description."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    try:
        # Get context from spreadsheet data
        context = None
        if spreadsheet.sheets:
            sheet = spreadsheet.sheets[0]
            if sheet.data and len(sheet.data) > 0:
                # Extract column headers for context
                headers = sheet.data[0] if sheet.data[0] else []
                context = f"Columns: {', '.join(str(h) for h in headers if h)}"

        result = await spreadsheet_ai_service.natural_language_to_formula(
            description=request.description,
            context=context,
            spreadsheet_type=request.spreadsheet_type if hasattr(request, 'spreadsheet_type') else "excel",
        )

        return AIFormulaResponse(
            formula=result.formula,
            explanation=result.explanation,
            example_result=result.examples[0] if result.examples else "",
            confidence=0.9,
            alternatives=result.alternative_formulas,
        )
    except Exception as e:
        logger.error(f"Formula generation failed: {e}")
        raise HTTPException(status_code=500, detail="Formula generation failed")


@router.post("/{spreadsheet_id}/ai/explain")
async def explain_formula_endpoint(
    spreadsheet_id: str,
    formula: str = Query(..., min_length=2),
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Explain what a formula does in plain language."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    try:
        result = await spreadsheet_ai_service.explain_formula(formula)

        return {
            "formula": result.formula,
            "explanation": result.summary,
            "step_by_step": result.step_by_step,
            "components": result.components,
            "potential_issues": result.potential_issues,
        }
    except Exception as e:
        logger.error(f"Formula explanation failed: {e}")
        raise HTTPException(status_code=500, detail="Formula explanation failed")


@router.post("/{spreadsheet_id}/ai/clean")
async def suggest_data_cleaning(
    spreadsheet_id: str,
    sheet_index: int = Query(0, ge=0),
    column: Optional[str] = Query(None),
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Get AI suggestions for cleaning data."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    if sheet_index >= len(spreadsheet.sheets):
        raise HTTPException(status_code=400, detail="Sheet index out of range")

    try:
        sheet = spreadsheet.sheets[sheet_index]

        # Convert sheet data to list of dicts
        if not sheet.data or len(sheet.data) < 2:
            return {
                "suggestions": [],
                "quality_score": 100.0,
                "summary": "Not enough data for analysis",
            }

        headers = sheet.data[0]
        data_sample = []
        for row in sheet.data[1:21]:  # Sample first 20 rows
            row_dict = {}
            for i, val in enumerate(row):
                if i < len(headers) and headers[i]:
                    row_dict[str(headers[i])] = val
            data_sample.append(row_dict)

        result = await spreadsheet_ai_service.analyze_data_quality(data_sample)

        return {
            "suggestions": [s.model_dump() for s in result.suggestions],
            "quality_score": result.quality_score,
            "summary": result.summary,
        }
    except Exception as e:
        logger.error(f"Data cleaning analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Data cleaning analysis failed")


@router.post("/{spreadsheet_id}/ai/anomalies")
async def detect_anomalies_endpoint(
    spreadsheet_id: str,
    sheet_index: int = Query(0, ge=0),
    column: str = Query(...),
    sensitivity: str = Query("medium", pattern="^(low|medium|high)$"),
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Detect anomalies in a column."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    if sheet_index >= len(spreadsheet.sheets):
        raise HTTPException(status_code=400, detail="Sheet index out of range")

    try:
        sheet = spreadsheet.sheets[sheet_index]

        # Convert sheet data to list of dicts
        if not sheet.data or len(sheet.data) < 2:
            return {
                "anomalies": [],
                "total_rows_analyzed": 0,
                "anomaly_count": 0,
                "summary": "Not enough data for analysis",
            }

        headers = sheet.data[0]
        data_sample = []
        for row in sheet.data[1:]:
            row_dict = {}
            for i, val in enumerate(row):
                if i < len(headers) and headers[i]:
                    row_dict[str(headers[i])] = val
            data_sample.append(row_dict)

        result = await spreadsheet_ai_service.detect_anomalies(
            data=data_sample,
            columns_to_analyze=[column] if column else None,
            sensitivity=sensitivity,
        )

        return {
            "anomalies": [a.model_dump() for a in result.anomalies],
            "total_rows_analyzed": result.total_rows_analyzed,
            "anomaly_count": result.anomaly_count,
            "summary": result.summary,
        }
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        raise HTTPException(status_code=500, detail="Anomaly detection failed")


@router.post("/{spreadsheet_id}/ai/predict")
async def generate_predictions(
    spreadsheet_id: str,
    target_description: str = Query(..., min_length=1),
    based_on_columns: str = Query(..., min_length=1),
    sheet_index: int = Query(0, ge=0),
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Generate predictive column based on existing data patterns."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    if sheet_index >= len(spreadsheet.sheets):
        raise HTTPException(status_code=400, detail="Sheet index out of range")

    try:
        sheet = spreadsheet.sheets[sheet_index]

        # Convert sheet data to list of dicts
        if not sheet.data or len(sheet.data) < 2:
            return {
                "column_name": "",
                "predictions": [],
                "confidence_scores": [],
                "methodology": "Insufficient data",
                "accuracy_estimate": 0,
            }

        headers = sheet.data[0]
        data_sample = []
        for row in sheet.data[1:]:
            row_dict = {}
            for i, val in enumerate(row):
                if i < len(headers) and headers[i]:
                    row_dict[str(headers[i])] = val
            data_sample.append(row_dict)

        # Parse columns
        columns = [c.strip() for c in based_on_columns.split(",")]

        result = await spreadsheet_ai_service.generate_predictive_column(
            data=data_sample,
            target_description=target_description,
            based_on_columns=columns,
        )

        return {
            "column_name": result.column_name,
            "predictions": result.predictions,
            "confidence_scores": result.confidence_scores,
            "methodology": result.methodology,
            "accuracy_estimate": result.accuracy_estimate,
        }
    except Exception as e:
        logger.error(f"Prediction generation failed: {e}")
        raise HTTPException(status_code=500, detail="Prediction generation failed")


@router.post("/{spreadsheet_id}/ai/suggest")
async def suggest_formulas_endpoint(
    spreadsheet_id: str,
    sheet_index: int = Query(0, ge=0),
    analysis_goals: Optional[str] = Query(None),
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Get AI-suggested formulas based on data structure."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    if sheet_index >= len(spreadsheet.sheets):
        raise HTTPException(status_code=400, detail="Sheet index out of range")

    try:
        sheet = spreadsheet.sheets[sheet_index]

        # Convert sheet data to list of dicts
        if not sheet.data or len(sheet.data) < 2:
            return {"suggestions": []}

        headers = sheet.data[0]
        data_sample = []
        for row in sheet.data[1:11]:  # Sample first 10 rows
            row_dict = {}
            for i, val in enumerate(row):
                if i < len(headers) and headers[i]:
                    row_dict[str(headers[i])] = val
            data_sample.append(row_dict)

        results = await spreadsheet_ai_service.suggest_formulas(
            data_sample=data_sample,
            analysis_goals=analysis_goals,
        )

        return {
            "suggestions": [
                {
                    "formula": r.formula,
                    "explanation": r.explanation,
                    "examples": r.examples,
                    "alternatives": r.alternative_formulas,
                }
                for r in results
            ]
        }
    except Exception as e:
        logger.error(f"Formula suggestion failed: {e}")
        raise HTTPException(status_code=500, detail="Formula suggestion failed")


# ============================================
# Collaboration
# ============================================

@router.post("/{spreadsheet_id}/collaborate")
async def start_collaboration(
    spreadsheet_id: str,
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Start a spreadsheet collaboration session."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    session_id = str(uuid.uuid4())
    session_info = {
        "session_id": session_id,
        "spreadsheet_id": spreadsheet_id,
        "spreadsheet_name": spreadsheet.name,
        "status": "active",
        "created_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat(),
        "collaborators": [],
    }
    return session_info


@router.get("/{spreadsheet_id}/collaborators")
async def get_collaborators(
    spreadsheet_id: str,
    svc: SpreadsheetService = Depends(get_spreadsheet_service),
):
    """Get current collaborators for a spreadsheet."""
    spreadsheet = svc.get(spreadsheet_id)
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")

    collaborators = spreadsheet.metadata.get("collaborators", [])
    return {
        "spreadsheet_id": spreadsheet_id,
        "collaborators": collaborators,
        "total": len(collaborators),
    }


# ============================================
# Helper Functions
# ============================================

def _to_spreadsheet_response(spreadsheet) -> SpreadsheetResponse:
    """Convert Spreadsheet model to response."""
    return SpreadsheetResponse(
        id=spreadsheet.id,
        name=spreadsheet.name,
        sheets=[
            SheetResponse(
                id=s.id,
                name=s.name,
                index=s.index,
                row_count=len(s.data),
                col_count=len(s.data[0]) if s.data else 0,
                frozen_rows=s.frozen_rows,
                frozen_cols=s.frozen_cols,
            )
            for s in spreadsheet.sheets
        ],
        created_at=spreadsheet.created_at,
        updated_at=spreadsheet.updated_at,
        owner_id=spreadsheet.owner_id,
        metadata=spreadsheet.metadata,
    )
