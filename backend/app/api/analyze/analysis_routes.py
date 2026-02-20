# mypy: ignore-errors
"""API routes for document analysis."""
from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import StreamingResponse

from backend.app.services.config import get_settings
from backend.app.services.security import require_api_key
from backend.app.services.validation import validate_file_extension
from backend.app.schemas.analyze.analysis import AnalysisSuggestChartsPayload
from backend.app.services.analyze.document_analysis_service import (
    analyze_document_streaming,
    get_analysis,
    get_analysis_data,
    suggest_charts_for_analysis,
)
from backend.app.services.analyze.extraction_pipeline import extract_document_content
from backend.app.services.background_tasks import enqueue_background_job, run_event_stream_async

logger = logging.getLogger("neura.analyze.routes")

router = APIRouter(dependencies=[Depends(require_api_key)])

ALLOWED_EXTENSIONS = [".pdf", ".xlsx", ".xls", ".xlsm"]
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "application/vnd.ms-excel.sheet.macroEnabled.12",
    "application/octet-stream",
}
MAX_FILENAME_LENGTH = 255
READ_CHUNK_BYTES = 1024 * 1024
MAX_ANALYSIS_DATA_LIMIT = 2000


def _validate_upload(file: UploadFile) -> str:
    filename = Path(file.filename or "").name
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    if len(filename) > MAX_FILENAME_LENGTH:
        raise HTTPException(status_code=400, detail=f"Filename too long (max {MAX_FILENAME_LENGTH} characters)")
    is_valid, error = validate_file_extension(filename, ALLOWED_EXTENSIONS)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported content type '{file.content_type}'",
        )
    return filename


async def _persist_upload_with_limit(upload: UploadFile, max_bytes: int, suffix: str) -> tuple[Path, int]:
    size = 0
    tmp = tempfile.NamedTemporaryFile(prefix="nr-analysis-", suffix=suffix, delete=False)
    try:
        with tmp:
            while True:
                chunk = await upload.read(READ_CHUNK_BYTES)
                if not chunk:
                    break
                size += len(chunk)
                if size > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum size is {max_bytes} bytes.",
                    )
                tmp.write(chunk)
    finally:
        with contextlib.suppress(Exception):
            await upload.close()
    return Path(tmp.name), size


async def _streaming_generator(
    file_path: Path,
    file_name: str,
    template_id: Optional[str],
    connection_id: Optional[str],
    correlation_id: Optional[str],
):
    """Generate NDJSON streaming response."""
    try:
        async for event in analyze_document_streaming(
            file_path=file_path,
            file_name=file_name,
            template_id=template_id,
            connection_id=connection_id,
            correlation_id=correlation_id,
        ):
            yield json.dumps(event) + "\n"
    except Exception as exc:
        logger.exception(
            "analysis_stream_failed",
            extra={"event": "analysis_stream_failed", "error": str(exc), "correlation_id": correlation_id},
        )
        error_event = {
            "event": "error",
            "detail": "Analysis failed. Please try again.",
        }
        if correlation_id:
            error_event["correlation_id"] = correlation_id
        yield json.dumps(error_event) + "\n"
    finally:
        with contextlib.suppress(FileNotFoundError):
            file_path.unlink(missing_ok=True)


@router.post("/upload")
async def upload_and_analyze(
    request: Request,
    file: UploadFile = File(...),
    template_id: Optional[str] = Form(None),
    connection_id: Optional[str] = Form(None),
    background: bool = Query(False),
):
    """
    Upload a document (PDF or Excel) and analyze it with AI.

    Returns a streaming NDJSON response with progress updates and final results.
    Use background=true to queue the analysis as a job.

    Events:
    - stage: Progress update with stage name and percentage
    - error: Error occurred, includes detail message
    - result: Final analysis result
    """
    settings = get_settings()
    file_name = _validate_upload(file)
    correlation_id = getattr(request.state, "correlation_id", None)

    if background:
        suffix = Path(file_name).suffix or ".bin"
        upload_path, size_bytes = await _persist_upload_with_limit(file, settings.max_upload_bytes, suffix=suffix)

        async def runner(job_id: str) -> None:
            try:
                async def _events():
                    async for event in analyze_document_streaming(
                        file_path=upload_path,
                        file_name=file_name,
                        template_id=template_id,
                        connection_id=connection_id,
                        correlation_id=correlation_id,
                    ):
                        yield event

                def _result_builder(event: dict) -> dict:
                    if event.get("event") != "result":
                        return {}
                    tables = event.get("tables") or []
                    charts = event.get("chart_suggestions") or []
                    return {
                        "analysis_id": event.get("analysis_id"),
                        "document_name": event.get("document_name"),
                        "summary": event.get("summary"),
                        "table_count": len(tables),
                        "chart_count": len(charts),
                        "warnings": event.get("warnings") or [],
                    }

                await run_event_stream_async(job_id, _events(), result_builder=_result_builder)
            finally:
                with contextlib.suppress(FileNotFoundError):
                    upload_path.unlink(missing_ok=True)

        job = await enqueue_background_job(
            job_type="analyze_document",
            template_id=template_id,
            connection_id=connection_id,
            template_name=file_name,
            meta={
                "filename": file_name,
                "size_bytes": size_bytes,
                "background": True,
            },
            runner=runner,
        )

        return {"status": "queued", "job_id": job["id"], "correlation_id": correlation_id}

    try:
        suffix = Path(file_name).suffix or ".bin"
        upload_path, _ = await _persist_upload_with_limit(file, settings.max_upload_bytes, suffix=suffix)
    finally:
        await file.close()

    return StreamingResponse(
        _streaming_generator(
            upload_path,
            file_name,
            template_id,
            connection_id,
            correlation_id,
        ),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/extract")
async def extract_document(
    request: Request,
    file: UploadFile = File(...),
    table_limit: int = Query(50, ge=1, le=200),
    table_offset: int = Query(0, ge=0),
    text_limit: int = Query(50000, ge=0, le=200000),
    include_text: bool = Query(True),
):
    """Quickly extract raw tables and text without full AI analysis."""
    settings = get_settings()
    file_name = _validate_upload(file)
    correlation_id = getattr(request.state, "correlation_id", None)

    try:
        suffix = Path(file_name).suffix or ".bin"
        upload_path, _ = await _persist_upload_with_limit(file, settings.max_upload_bytes, suffix=suffix)
    finally:
        await file.close()

    extracted = await asyncio.to_thread(
        extract_document_content,
        file_path=upload_path,
        file_name=file_name,
    )
    with contextlib.suppress(FileNotFoundError):
        upload_path.unlink(missing_ok=True)

    total_tables = len(extracted.tables_raw or [])
    table_slice = extracted.tables_raw[table_offset:table_offset + table_limit]
    text_content = extracted.text_content or ""
    original_text_len = len(text_content)
    if not include_text:
        text_content = ""
    elif text_limit and original_text_len > text_limit:
        text_content = text_content[:text_limit]

    return {
        "status": "ok",
        "file_name": extracted.file_name,
        "document_type": extracted.document_type,
        "page_count": extracted.page_count,
        "tables": table_slice,
        "tables_total": total_tables,
        "tables_offset": table_offset,
        "tables_limit": table_limit,
        "sheets": extracted.sheets,
        "text": text_content,
        "text_length": original_text_len,
        "text_truncated": include_text and text_limit > 0 and original_text_len > text_limit,
        "errors": extracted.errors,
        "correlation_id": correlation_id,
    }


@router.get("/{analysis_id}")
async def get_analysis_result(analysis_id: str, request: Request):
    """Get a previously computed analysis result."""
    result = get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "status": "ok",
        **result.model_dump(),
        "correlation_id": getattr(request.state, "correlation_id", None),
    }


@router.get("/{analysis_id}/data")
async def get_analysis_raw_data(
    analysis_id: str,
    request: Request,
    limit: int = Query(500, ge=1, le=MAX_ANALYSIS_DATA_LIMIT),
    offset: int = Query(0, ge=0),
):
    """Get raw data from an analysis for charting."""
    data = get_analysis_data(analysis_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    paginated = data[offset:offset + limit]

    return {
        "status": "ok",
        "analysis_id": analysis_id,
        "data": paginated,
        "total": len(data),
        "offset": offset,
        "limit": limit,
        "correlation_id": getattr(request.state, "correlation_id", None),
    }


@router.post("/{analysis_id}/charts/suggest")
async def suggest_charts(
    analysis_id: str,
    payload: AnalysisSuggestChartsPayload,
    request: Request,
):
    """Generate additional chart suggestions for an existing analysis."""
    result = get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    charts = await asyncio.to_thread(suggest_charts_for_analysis, analysis_id, payload)

    sample_data = result.raw_data[:100] if payload.include_sample_data else None

    return {
        "status": "ok",
        "analysis_id": analysis_id,
        "charts": [c.model_dump() for c in charts],
        "sample_data": sample_data,
        "correlation_id": getattr(request.state, "correlation_id", None),
    }


__all__ = ["router"]
