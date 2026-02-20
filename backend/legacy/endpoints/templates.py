from __future__ import annotations

from typing import Optional

import contextlib
import tempfile
from pathlib import Path
from types import SimpleNamespace

from fastapi import APIRouter, File, Form, Query, Request, UploadFile

from backend.legacy.schemas.template_schema import (
    CorrectionsPreviewPayload,
    GeneratorAssetsPayload,
    LastUsedPayload,
    MappingPayload,
    TemplateAiEditPayload,
    TemplateChatPayload,
    TemplateManualEditPayload,
    TemplateRecommendPayload,
    TemplateRecommendResponse,
    TemplateUpdatePayload,
)
from backend.app.repositories.state import store as state_store_module
from backend.legacy.services.mapping.approve import run_mapping_approve
from backend.legacy.services.mapping.corrections import run_corrections_preview
from backend.legacy.services.mapping.key_options import mapping_key_options as mapping_key_options_service
from backend.legacy.services.mapping.preview import mapping_preview_internal, run_mapping_preview
from backend.legacy.services.template_service import (
    get_template_html,
    edit_template_ai,
    edit_template_manual,
    chat_template_edit,
    apply_chat_template_edit,
    export_template_zip as export_template_zip_service,
    import_template_zip as import_template_zip_service,
    undo_last_template_edit,
    verify_excel,
    verify_template,
    list_templates,
    templates_catalog,
    recommend_templates,
    bootstrap_state,
    delete_template,
    update_template_metadata,
    generator_assets,
)
from backend.app.services.background_tasks import (
    enqueue_background_job,
    iter_ndjson_events_async,
    run_event_stream_async,
)

router = APIRouter()


def _correlation(request: Request) -> str | None:
    return getattr(request.state, "correlation_id", None)


def _state_store():
    return state_store_module.state_store


def _request_with_correlation(correlation_id: str | None) -> SimpleNamespace:
    return SimpleNamespace(state=SimpleNamespace(correlation_id=correlation_id))


async def _persist_upload(file: UploadFile, suffix: str) -> tuple[Path, str]:
    filename = Path(file.filename or f"upload{suffix}").name
    tmp = tempfile.NamedTemporaryFile(prefix="nr-upload-", suffix=suffix, delete=False)
    try:
        with tmp:
            file.file.seek(0)
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break
                tmp.write(chunk)
    finally:
        with contextlib.suppress(Exception):
            await file.close()
    return Path(tmp.name), filename


@router.post("/templates/{template_id}/mapping/preview")
async def mapping_preview(template_id: str, connection_id: str, request: Request, force_refresh: bool = False):
    return await run_mapping_preview(template_id, connection_id, request, force_refresh, kind="pdf")


@router.post("/excel/{template_id}/mapping/preview")
async def mapping_preview_excel(template_id: str, connection_id: str, request: Request, force_refresh: bool = False):
    return await run_mapping_preview(template_id, connection_id, request, force_refresh, kind="excel")


@router.post("/templates/{template_id}/mapping/approve")
async def mapping_approve(template_id: str, payload: MappingPayload, request: Request):
    return await run_mapping_approve(template_id, payload, request, kind="pdf")


@router.post("/excel/{template_id}/mapping/approve")
async def mapping_approve_excel(template_id: str, payload: MappingPayload, request: Request):
    return await run_mapping_approve(template_id, payload, request, kind="excel")


@router.post("/templates/{template_id}/mapping/corrections-preview")
def mapping_corrections_preview(template_id: str, payload: CorrectionsPreviewPayload, request: Request):
    return run_corrections_preview(template_id, payload, request, kind="pdf")


@router.post("/excel/{template_id}/mapping/corrections-preview")
def mapping_corrections_preview_excel(template_id: str, payload: CorrectionsPreviewPayload, request: Request):
    return run_corrections_preview(template_id, payload, request, kind="excel")


@router.get("/templates/{template_id}/export.zip")
def export_template_zip_route(template_id: str, request: Request):
    return export_template_zip_service(template_id, request)


# Backwards-compatible alias to avoid naming regression in tests/clients.
export_template_zip = export_template_zip_route


@router.post("/templates/import-zip")
async def import_template_zip_route(
    request: Request,
    file: UploadFile = File(...),
    name: str | None = Form(None),
):
    return await import_template_zip_service(file=file, name=name, request=request)


@router.post("/templates/verify")
async def verify_template_route(
    request: Request,
    file: UploadFile = File(...),
    connection_id: str = Form(...),
    refine_iters: int = Form(0),
    background: bool = Query(False),
):
    if not background:
        return verify_template(file=file, connection_id=connection_id, refine_iters=refine_iters, request=request)

    upload_path, filename = await _persist_upload(file, suffix=".pdf")
    correlation_id = _correlation(request)
    template_name = Path(filename).stem or filename

    async def runner(job_id: str) -> None:
        upload = UploadFile(filename=filename, file=upload_path.open("rb"))
        try:
            response = verify_template(
                file=upload,
                connection_id=connection_id,
                refine_iters=refine_iters,
                request=_request_with_correlation(correlation_id),
            )
            await run_event_stream_async(
                job_id,
                iter_ndjson_events_async(response.body_iterator),
            )
        finally:
            with contextlib.suppress(Exception):
                await upload.close()
            with contextlib.suppress(FileNotFoundError):
                upload_path.unlink(missing_ok=True)

    job = await enqueue_background_job(
        job_type="verify_template",
        connection_id=connection_id,
        template_name=template_name,
        template_kind="pdf",
        meta={
            "filename": filename,
            "background": True,
            "refine_iters": refine_iters,
        },
        runner=runner,
    )

    return {"status": "queued", "job_id": job["id"], "correlation_id": correlation_id}


@router.post("/excel/verify")
async def verify_excel_route(
    request: Request,
    file: UploadFile = File(...),
    connection_id: str | None = Form(None),
    background: bool = Query(False),
):
    if not background:
        return verify_excel(file=file, request=request, connection_id=connection_id)

    upload_path, filename = await _persist_upload(file, suffix=".xlsx")
    correlation_id = _correlation(request)
    template_name = Path(filename).stem or filename

    async def runner(job_id: str) -> None:
        upload = UploadFile(filename=filename, file=upload_path.open("rb"))
        try:
            response = verify_excel(
                file=upload,
                request=_request_with_correlation(correlation_id),
                connection_id=connection_id,
            )
            await run_event_stream_async(
                job_id,
                iter_ndjson_events_async(response.body_iterator),
            )
        finally:
            with contextlib.suppress(Exception):
                await upload.close()
            with contextlib.suppress(FileNotFoundError):
                upload_path.unlink(missing_ok=True)

    job = await enqueue_background_job(
        job_type="verify_excel",
        connection_id=connection_id,
        template_name=template_name,
        template_kind="excel",
        meta={
            "filename": filename,
            "background": True,
        },
        runner=runner,
    )

    return {"status": "queued", "job_id": job["id"], "correlation_id": correlation_id}


@router.get("/templates/{template_id}/html")
def get_template_html_route(template_id: str, request: Request):
    return get_template_html(template_id, request)


@router.post("/templates/{template_id}/edit-manual")
def edit_template_manual_route(template_id: str, payload: TemplateManualEditPayload, request: Request):
    return edit_template_manual(template_id, payload, request)


@router.post("/templates/{template_id}/edit-ai")
def edit_template_ai_route(template_id: str, payload: TemplateAiEditPayload, request: Request):
    return edit_template_ai(template_id, payload, request)


@router.post("/templates/{template_id}/undo-last-edit")
def undo_last_edit_route(template_id: str, request: Request):
    return undo_last_template_edit(template_id, request)


@router.post("/templates/{template_id}/chat")
def chat_template_edit_route(template_id: str, payload: TemplateChatPayload, request: Request):
    """
    Conversational template editing endpoint.

    Send a conversation history to have an interactive chat session with the AI
    to gather requirements and make template edits. The AI will ask clarifying
    questions if needed before proposing changes.
    """
    return chat_template_edit(template_id, payload, request)


@router.post("/templates/{template_id}/chat/apply")
def apply_chat_template_edit_route(template_id: str, payload: TemplateManualEditPayload, request: Request):
    """
    Apply the HTML changes from a chat conversation.

    Call this endpoint after the user confirms they want to apply the proposed
    changes from the chat conversation.
    """
    return apply_chat_template_edit(template_id, payload.html, request)


@router.get("/state/bootstrap")
def bootstrap_state_route(request: Request):
    return bootstrap_state(request)


@router.post("/state/last-used")
def set_last_used_route(payload: LastUsedPayload, request: Request):
    """Record the last-used connection and template IDs for session persistence."""
    last_used = _state_store().set_last_used(
        connection_id=payload.connection_id,
        template_id=payload.template_id,
    )
    return {
        "status": "ok",
        "last_used": last_used,
        "correlation_id": _correlation(request),
    }


@router.get("/templates/catalog")
def templates_catalog_route(request: Request):
    return templates_catalog(request)


@router.get("/templates")
def list_templates_route(request: Request, status: Optional[str] = None):
    return list_templates(status, request)


@router.post("/templates/recommend", response_model=TemplateRecommendResponse)
def recommend_templates_route(payload: TemplateRecommendPayload, request: Request):
    return recommend_templates(payload, request)


@router.delete("/templates/{template_id}")
def delete_template_route(template_id: str, request: Request):
    return delete_template(template_id, request)


@router.patch("/templates/{template_id}")
def update_template_metadata_route(template_id: str, payload: TemplateUpdatePayload, request: Request):
    return update_template_metadata(template_id, payload, request)


@router.post("/templates/{template_id}/generator-assets/v1")
def generator_assets_route(template_id: str, payload: GeneratorAssetsPayload, request: Request):
    return generator_assets(template_id, payload, request, kind="pdf")


@router.post("/excel/{template_id}/generator-assets/v1")
def generator_assets_excel_route(template_id: str, payload: GeneratorAssetsPayload, request: Request):
    return generator_assets(template_id, payload, request, kind="excel")


@router.get("/templates/{template_id}/keys/options")
def mapping_key_options(
    template_id: str,
    request: Request,
    connection_id: str | None = None,
    tokens: str | None = None,
    limit: int = 500,
    start_date: str | None = None,
    end_date: str | None = None,
    debug: bool = False,
):
    return mapping_key_options_service(
        template_id=template_id,
        request=request,
        connection_id=connection_id,
        tokens=tokens,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        kind="pdf",
        debug=debug,
    )


@router.get("/excel/{template_id}/keys/options")
def mapping_key_options_excel(
    template_id: str,
    request: Request,
    connection_id: str | None = None,
    tokens: str | None = None,
    limit: int = 500,
    start_date: str | None = None,
    end_date: str | None = None,
    debug: bool = False,
):
    return mapping_key_options_service(
        template_id=template_id,
        request=request,
        connection_id=connection_id,
        tokens=tokens,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        kind="excel",
        debug=debug,
    )
