"""
Visualization & Diagrams API Routes
Endpoints for generating charts, diagrams, and visual representations.
"""
from __future__ import annotations

import logging
import re
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.app.services.security import require_api_key

from backend.app.services.visualization import visualization_service
from backend.app.services.visualization.service import (
    DiagramType, ChartType, TimelineEvent, GanttTask,
)

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(require_api_key)])


# =============================================================================
# REQUEST MODELS
# =============================================================================

class FlowchartRequest(BaseModel):
    description: str = Field(..., description="Process description")
    title: Optional[str] = Field(default=None, description="Flowchart title")


class MindmapRequest(BaseModel):
    content: str = Field(..., description="Document content")
    title: Optional[str] = Field(default=None, description="Central topic")
    max_depth: int = Field(default=3, ge=1, le=5, description="Max depth")


class OrgChartRequest(BaseModel):
    org_data: List[Dict[str, Any]] = Field(..., description="Organization data")
    title: Optional[str] = Field(default=None, description="Chart title")


class TimelineRequest(BaseModel):
    events: List[Dict[str, Any]] = Field(..., description="Timeline events")
    title: Optional[str] = Field(default=None, description="Timeline title")


class GanttRequest(BaseModel):
    tasks: List[Dict[str, Any]] = Field(..., description="Project tasks")
    title: Optional[str] = Field(default=None, description="Chart title")


class NetworkGraphRequest(BaseModel):
    relationships: List[Dict[str, Any]] = Field(..., description="Relationships")
    title: Optional[str] = Field(default=None, description="Graph title")


class KanbanRequest(BaseModel):
    items: List[Dict[str, Any]] = Field(..., description="Kanban items")
    columns: Optional[List[str]] = Field(default=None, description="Column names")
    title: Optional[str] = Field(default=None, description="Board title")


class SequenceDiagramRequest(BaseModel):
    interactions: List[Dict[str, Any]] = Field(..., description="Interactions")
    title: Optional[str] = Field(default=None, description="Diagram title")


class WordcloudRequest(BaseModel):
    text: str = Field(..., description="Source text")
    max_words: int = Field(default=100, ge=10, le=500, description="Max words")
    title: Optional[str] = Field(default=None, description="Title")


class TableToChartRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="Table data")
    chart_type: str = Field(default="bar", description="Chart type")
    x_column: Optional[str] = Field(default=None, description="X axis column")
    y_columns: Optional[List[str]] = Field(default=None, description="Y axis columns")
    title: Optional[str] = Field(default=None, description="Chart title")


class SparklineRequest(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="Data rows")
    value_columns: List[str] = Field(..., description="Columns for sparklines")


# =============================================================================
# DIAGRAM ENDPOINTS
# =============================================================================

@router.post("/diagrams/flowchart")
async def generate_flowchart(request: FlowchartRequest):
    """
    Generate a flowchart from a process description.

    Returns:
        DiagramSpec for the flowchart
    """
    try:
        result = await visualization_service.generate_flowchart(
            description=request.description,
            title=request.title,
        )
        return result.model_dump()
    except Exception as e:
        logger.error(f"Flowchart generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Visualization generation failed")


@router.post("/diagrams/mindmap")
async def generate_mindmap(request: MindmapRequest):
    """
    Generate a mind map from document content.

    Returns:
        DiagramSpec for the mind map
    """
    try:
        result = await visualization_service.generate_mindmap(
            document_content=request.content,
            title=request.title,
            max_depth=request.max_depth,
        )
        return result.model_dump()
    except Exception as e:
        logger.error(f"Mindmap generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Visualization generation failed")


@router.post("/diagrams/org-chart")
async def generate_org_chart(request: OrgChartRequest):
    """
    Generate an organization chart.

    Returns:
        DiagramSpec for the org chart
    """
    try:
        result = await visualization_service.generate_org_chart(
            org_data=request.org_data,
            title=request.title,
        )
        return result.model_dump()
    except Exception as e:
        logger.error(f"Org chart generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Visualization generation failed")


@router.post("/diagrams/timeline")
async def generate_timeline(request: TimelineRequest):
    """
    Generate a timeline visualization.

    Returns:
        DiagramSpec for the timeline
    """
    try:
        parsed_events = []
        _DATE_RE = re.compile(r"\b(\d{4}[-/]\d{2}(?:[-/]\d{2})?)\b")
        for i, e in enumerate(request.events):
            if "id" not in e:
                e["id"] = str(uuid.uuid4())[:8]
            if "title" not in e or "date" not in e:
                desc = e.get("description", "")
                m = _DATE_RE.search(desc)
                if "date" not in e:
                    e["date"] = m.group(1) if m else f"event-{i + 1}"
                if "title" not in e:
                    # Strip the date prefix (e.g. "2023-01: ") to get the title
                    title = _DATE_RE.sub("", desc).strip().lstrip(":").strip()
                    e["title"] = title or desc or f"Event {i + 1}"
            parsed_events.append(TimelineEvent(**e))
        result = await visualization_service.generate_timeline(
            events=parsed_events,
            title=request.title,
        )
        return result.model_dump()
    except Exception as e:
        logger.error(f"Timeline generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Visualization generation failed")


@router.post("/diagrams/gantt")
async def generate_gantt(request: GanttRequest):
    """
    Generate a Gantt chart.

    Returns:
        DiagramSpec for the Gantt chart
    """
    try:
        tasks = [GanttTask(**t) for t in request.tasks]
        result = await visualization_service.generate_gantt(
            tasks=tasks,
            title=request.title,
        )
        return result.model_dump()
    except Exception as e:
        logger.error(f"Gantt generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Visualization generation failed")


@router.post("/diagrams/network")
async def generate_network_graph(request: NetworkGraphRequest):
    """
    Generate a network/relationship graph.

    Returns:
        DiagramSpec for the network graph
    """
    try:
        result = await visualization_service.generate_network_graph(
            relationships=request.relationships,
            title=request.title,
        )
        return result.model_dump()
    except Exception as e:
        logger.error(f"Network graph generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Visualization generation failed")


@router.post("/diagrams/kanban")
async def generate_kanban(request: KanbanRequest):
    """
    Generate a Kanban board visualization.

    Returns:
        DiagramSpec for the Kanban board
    """
    try:
        result = await visualization_service.generate_kanban(
            items=request.items,
            columns=request.columns,
            title=request.title,
        )
        return result.model_dump()
    except Exception as e:
        logger.error(f"Kanban generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Visualization generation failed")


@router.post("/diagrams/sequence")
async def generate_sequence_diagram(request: SequenceDiagramRequest):
    """
    Generate a sequence diagram.

    Returns:
        DiagramSpec for the sequence diagram
    """
    try:
        result = await visualization_service.generate_sequence_diagram(
            interactions=request.interactions,
            title=request.title,
        )
        return result.model_dump()
    except Exception as e:
        logger.error(f"Sequence diagram generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Visualization generation failed")


@router.post("/diagrams/wordcloud")
async def generate_wordcloud(request: WordcloudRequest):
    """
    Generate a word cloud from text.

    Returns:
        DiagramSpec for the word cloud
    """
    try:
        result = await visualization_service.generate_wordcloud(
            text=request.text,
            max_words=request.max_words,
            title=request.title,
        )
        return result.model_dump()
    except Exception as e:
        logger.error(f"Wordcloud generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Visualization generation failed")


# =============================================================================
# CHART ENDPOINTS
# =============================================================================

@router.post("/charts/from-table")
async def table_to_chart(request: TableToChartRequest):
    """
    Convert table data to a chart.

    Returns:
        ChartSpec for the chart
    """
    try:
        chart_type = ChartType(request.chart_type) if request.chart_type in [t.value for t in ChartType] else ChartType.BAR

        result = await visualization_service.table_to_chart(
            data=request.data,
            chart_type=chart_type,
            x_column=request.x_column,
            y_columns=request.y_columns,
            title=request.title,
        )
        return result.model_dump()
    except Exception as e:
        logger.error(f"Chart generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Visualization generation failed")


@router.post("/charts/sparklines")
async def generate_sparklines(request: SparklineRequest):
    """
    Generate inline sparkline charts.

    Returns:
        List of ChartSpecs for sparklines
    """
    try:
        results = await visualization_service.generate_sparklines(
            data=request.data,
            value_columns=request.value_columns,
        )
        return [r.model_dump() for r in results]
    except Exception as e:
        logger.error(f"Sparkline generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Visualization generation failed")


# =============================================================================
# EXPORT ENDPOINTS
# =============================================================================

@router.get("/diagrams/{diagram_id}/mermaid")
async def export_as_mermaid(diagram_id: str):
    """
    Export diagram as Mermaid.js syntax.

    Returns:
        Mermaid.js code
    """
    try:
        code = await visualization_service.export_diagram_as_mermaid(diagram_id)
        return {"mermaid_code": code}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visualization not found")
    except Exception as e:
        logger.error(f"Mermaid export failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Visualization generation failed")


@router.get("/diagrams/{diagram_id}/svg")
async def export_as_svg(diagram_id: str):
    """
    Export diagram as SVG.

    Returns:
        SVG content
    """
    try:
        svg_content = await visualization_service.export_diagram_as_svg(diagram_id)
        return {"svg": svg_content, "diagram_id": diagram_id}
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visualization not found")
    except Exception as e:
        logger.error(f"SVG export failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Visualization generation failed")


@router.get("/diagrams/{diagram_id}/png")
async def export_as_png(diagram_id: str):
    """
    Export diagram as PNG.

    Returns:
        PNG image as streaming response
    """
    try:
        png_bytes = await visualization_service.export_diagram_as_png(diagram_id)
        return StreamingResponse(
            png_bytes,
            media_type="image/png",
            headers={"Content-Disposition": f'attachment; filename="{diagram_id}.png"'},
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visualization not found")
    except Exception as e:
        logger.error(f"PNG export failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Visualization generation failed")


# =============================================================================
# EXCEL EXTRACTION ENDPOINT
# =============================================================================

@router.post("/extract-excel")
async def extract_excel(file: UploadFile = File(...)):
    """
    Extract table data from an Excel (.xlsx/.xls) or CSV file.

    Returns sheets with headers + rows, ready for chart generation.
    """
    import io
    import pandas as pd

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("xlsx", "xls", "csv"):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: .{ext}. Use .xlsx, .xls, or .csv")

    try:
        content = await file.read()
        buf = io.BytesIO(content)

        if ext == "csv":
            df = pd.read_csv(buf)
            sheets = [{"name": file.filename, "headers": list(df.columns), "rows": df.fillna("").values.tolist(), "row_count": len(df), "column_count": len(df.columns)}]
        else:
            xls = pd.ExcelFile(buf, engine="openpyxl")
            sheets = []
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                if df.empty:
                    continue
                # Convert all values to JSON-safe types
                rows = []
                for _, row in df.iterrows():
                    rows.append([str(v) if pd.notna(v) else "" for v in row])
                sheets.append({
                    "name": sheet_name,
                    "headers": [str(c) for c in df.columns],
                    "rows": rows,
                    "row_count": len(df),
                    "column_count": len(df.columns),
                })

        # Also provide the first sheet as a flat JSON array (ready for charts)
        data_preview = []
        if sheets:
            s = sheets[0]
            for row in s["rows"][:200]:  # cap at 200 rows for preview
                data_preview.append(dict(zip(s["headers"], row)))

        return {
            "filename": file.filename,
            "sheets": sheets,
            "total_sheets": len(sheets),
            "data": data_preview,
        }
    except Exception as e:
        logger.error(f"Excel extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract data: {str(e)}")


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@router.get("/types/diagrams")
async def list_diagram_types():
    """List available diagram types."""
    return {"types": [t.value for t in DiagramType]}


@router.get("/types/charts")
async def list_chart_types():
    """List available chart types."""
    return {"types": [t.value for t in ChartType]}
