from __future__ import annotations

import contextlib
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Optional

from fastapi import HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from backend.app.services.config import get_settings as get_api_settings
from backend.app.services.templates.errors import TemplateImportError
from backend.app.services.templates.service import TemplateService
from backend.app.services.utils import TemplateLockError, acquire_template_lock
from backend.app.services.templates.catalog import build_unified_template_catalog
from backend.app.services.utils import get_correlation_id
from backend.app.repositories.state import store as state_store_module
from backend.app.services.prompts.llm_prompts_templates import recommend_templates_from_catalog
from backend.app.services.utils.zip_tools import create_zip_from_dir
from backend.app.utils.validation import is_safe_name
from backend.legacy.services.file_service import (
    apply_chat_template_edit as apply_chat_template_edit_service,
    chat_template_create as chat_template_create_service,
    chat_template_edit as chat_template_edit_service,
    create_template_from_chat as create_template_from_chat_service,
    edit_template_ai as edit_template_ai_service,
    edit_template_manual as edit_template_manual_service,
    generator_assets as generator_assets_service,
    get_template_html as get_template_html_service,
    undo_last_template_edit as undo_last_template_edit_service,
    verify_excel as verify_excel_service,
    verify_template as verify_template_service,
)
from backend.legacy.services.file_service.helpers import (
    load_template_generator_summary as _load_template_generator_summary,
    resolve_template_kind as _resolve_template_kind,
    update_template_generator_summary_for_edit as _update_template_generator_summary_for_edit,
)
from backend.legacy.schemas.template_schema import (
    GeneratorAssetsPayload,
    TemplateAiEditPayload,
    TemplateChatPayload,
    TemplateManualEditPayload,
    TemplateRecommendPayload,
    TemplateRecommendResponse,
    TemplateRecommendation,
    TemplateUpdatePayload,
)
from backend.legacy.utils.schedule_utils import utcnow_iso
from backend.legacy.utils.template_utils import template_dir
from backend.legacy.utils.mapping_utils import load_mapping_keys

_TEMPLATE_SERVICE: TemplateService | None = None


def _get_template_service() -> TemplateService:
    global _TEMPLATE_SERVICE
    if _TEMPLATE_SERVICE is None:
        settings = get_api_settings()
        _TEMPLATE_SERVICE = TemplateService(
            uploads_root=settings.uploads_dir,
            excel_uploads_root=settings.excel_uploads_dir,
            max_bytes=settings.max_upload_bytes,
            max_zip_entries=settings.max_zip_entries,
            max_zip_uncompressed_bytes=settings.max_zip_uncompressed_bytes,
            max_concurrency=settings.template_import_max_concurrency,
        )
    return _TEMPLATE_SERVICE


def _http_error(status_code: int, code: str, message: str, details: str | None = None) -> HTTPException:
    payload = {"status": "error", "code": code, "message": message}
    if details:
        payload["details"] = details
    return HTTPException(status_code=status_code, detail=payload)


def _state_store():
    return state_store_module.state_store


def _normalize_tags(values: Optional[list[str]]) -> list[str]:
    if not values:
        return []
    seen: set[str] = set()
    normalized: list[str] = []
    for raw in values:
        text = re.sub(r"[^A-Za-z0-9 _-]", "", str(raw or "")).strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(text[:32])
        if len(normalized) >= 12:
            break
    return normalized


def export_template_zip(template_id: str, request: Request):
    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
    kind = _resolve_template_kind(template_id)
    tdir = template_dir(template_id, must_exist=True, create=False, kind=kind)
    try:
        lock_ctx = acquire_template_lock(tdir, "template_export", correlation_id)
    except TemplateLockError:
        raise _http_error(
            409,
            "template_locked",
            "Template is currently processing another request.",
        )

    fd, tmp_name = tempfile.mkstemp(prefix=f"{template_id}-", suffix=".zip")
    os.close(fd)
    zip_path = Path(tmp_name)

    def _cleanup(path: Path = zip_path) -> None:
        with contextlib.suppress(FileNotFoundError):
            path.unlink(missing_ok=True)

    with lock_ctx:
        create_zip_from_dir(tdir, zip_path, include_root=True)

    headers = {"X-Correlation-ID": correlation_id} if correlation_id else None
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"{template_id}.zip",
        background=BackgroundTask(_cleanup),
        headers=headers,
    )


async def import_template_zip(file: UploadFile, request: Request, name: str | None = None):
    if not file:
        raise _http_error(400, "file_missing", "No file provided for import.")

    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
    service = _get_template_service()
    try:
        result = await service.import_zip(file, name, correlation_id)
    except TemplateImportError as exc:
        detail = {"status": "error", "code": exc.code, "message": exc.message}
        if exc.detail:
            detail["detail"] = exc.detail
        if correlation_id:
            detail["correlation_id"] = correlation_id
        raise HTTPException(status_code=exc.status_code, detail=detail)

    normalized = dict(result or {})
    normalized.setdefault("status", "ok")
    normalized.setdefault("correlation_id", correlation_id)
    return normalized


def verify_template(file: UploadFile, connection_id: str | None, request: Request, refine_iters: int = 0):
    return verify_template_service(
        file=file,
        connection_id=connection_id,
        request=request,
        refine_iters=refine_iters,
    )


def verify_excel(file: UploadFile, request: Request, connection_id: str | None = None):
    return verify_excel_service(file=file, request=request, connection_id=connection_id)


def get_template_html(template_id: str, request: Request):
    return get_template_html_service(template_id, request)


def edit_template_manual(template_id: str, payload: TemplateManualEditPayload, request: Request):
    return edit_template_manual_service(template_id, payload, request)


def edit_template_ai(template_id: str, payload: TemplateAiEditPayload, request: Request):
    return edit_template_ai_service(template_id, payload, request)


def undo_last_template_edit(template_id: str, request: Request):
    return undo_last_template_edit_service(template_id, request)


def chat_template_edit(template_id: str, payload: TemplateChatPayload, request: Request):
    return chat_template_edit_service(template_id, payload, request)


def apply_chat_template_edit(template_id: str, html: str, request: Request):
    return apply_chat_template_edit_service(template_id, html, request)


def chat_template_create(payload: TemplateChatPayload, request: Request, sample_pdf_bytes: bytes | None = None):
    return chat_template_create_service(payload, request, sample_pdf_bytes=sample_pdf_bytes)


def create_template_from_chat(payload, request: Request):
    return create_template_from_chat_service(payload, request)


def generator_assets(template_id: str, payload: GeneratorAssetsPayload, request: Request, *, kind: str = "pdf"):
    return generator_assets_service(template_id, payload, request, kind=kind)


def bootstrap_state(request: Request):
    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
    templates = _state_store().list_templates()
    hydrated_templates = _ensure_template_mapping_keys(templates)

    # Get connections with optional limit for performance
    all_connections = _state_store().list_connections()
    # Sort by lastConnected (most recent first), then by createdAt
    sorted_connections = sorted(
        all_connections,
        key=lambda c: (c.get("lastConnected") or c.get("createdAt") or ""),
        reverse=True
    )
    # Limit to 20 most recent to reduce payload size
    limited_connections = sorted_connections[:20]

    return {
        "status": "ok",
        "connections": limited_connections,
        "templates": hydrated_templates,
        "last_used": _state_store().get_last_used(),
        "correlation_id": correlation_id,
    }


def templates_catalog(request: Request):
    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
    catalog = build_unified_template_catalog()
    return {"status": "ok", "templates": catalog, "correlation_id": correlation_id}


def list_templates(status: Optional[str], request: Request):
    templates = _state_store().list_templates()
    if status:
        status_lower = status.lower()
        # Compatibility: legacy records may store schedulable templates as
        # "active" instead of "approved".
        if status_lower == "approved":
            templates = [t for t in templates if (t.get("status") or "").lower() in {"approved", "active"}]
        else:
            templates = [t for t in templates if (t.get("status") or "").lower() == status_lower]
    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
    hydrated = _ensure_template_mapping_keys(templates)
    return {"status": "ok", "templates": hydrated, "correlation_id": correlation_id}


def recommend_templates(payload: TemplateRecommendPayload, request: Request):
    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
    catalog = build_unified_template_catalog()

    def _dedupe_str_list(values: list[str] | None) -> list[str]:
        if not values:
            return []
        seen: set[str] = set()
        cleaned: list[str] = []
        for raw in values:
            text = str(raw or "").strip()
            if not text or text in seen:
                continue
            seen.add(text)
            cleaned.append(text)
        return cleaned

    hints: dict[str, Any] = {}

    kind_values: list[str] = []
    if payload.kind:
        kind_values.append(payload.kind)
    if getattr(payload, "kinds", None):
        kind_values.extend(payload.kinds or [])
    kinds = _dedupe_str_list(kind_values)
    if payload.kind:
        kind = str(payload.kind or "").strip()
        if kind:
            hints["kind"] = kind
    if kinds:
        hints["kinds"] = kinds

    domain_values: list[str] = []
    if payload.domain:
        domain_values.append(payload.domain)
    if getattr(payload, "domains", None):
        domain_values.extend(payload.domains or [])
    domains = _dedupe_str_list(domain_values)
    if payload.domain:
        domain = str(payload.domain or "").strip()
        if domain:
            hints["domain"] = domain
    if domains:
        hints["domains"] = domains

    if payload.schema_snapshot is not None:
        hints["schema_snapshot"] = payload.schema_snapshot
    tables = _dedupe_str_list(payload.tables)
    if tables:
        hints["tables"] = tables

    raw_recs = recommend_templates_from_catalog(
        catalog,
        requirement=payload.requirement,
        hints=hints,
        max_results=6,
    )

    catalog_by_id: dict[str, dict[str, Any]] = {}
    for item in catalog:
        if isinstance(item, dict):
            tid = str(item.get("id") or "").strip()
            if tid and tid not in catalog_by_id:
                catalog_by_id[tid] = item

    recommendations: list[TemplateRecommendation] = []
    for rec in raw_recs:
        tid = str(rec.get("id") or "").strip()
        if not tid:
            continue
        template = catalog_by_id.get(tid)
        if not template:
            continue
        explanation = str(rec.get("explanation") or "").strip()
        try:
            score = float(rec.get("score") or 0.0)
        except Exception:
            score = 0.0
        recommendations.append(
            TemplateRecommendation(
                template=template,
                explanation=explanation,
                score=score,
            )
        )

    return TemplateRecommendResponse(recommendations=recommendations)


def delete_template(template_id: str, request: Request):
    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
    existing_record = _state_store().get_template_record(template_id)
    template_kind = _resolve_template_kind(template_id)
    tdir = template_dir(template_id, must_exist=False, create=False, kind=template_kind)

    lock_ctx: contextlib.AbstractContextManager[Any] = contextlib.nullcontext()
    if tdir.exists():
        try:
            lock_ctx = acquire_template_lock(tdir, "template_delete", correlation_id)
        except TemplateLockError:
            raise _http_error(
                409,
                "template_locked",
                "Template is currently processing another request.",
            )

    removed_dir = False
    with lock_ctx:
        if tdir.exists():
            try:
                shutil.rmtree(tdir)
                removed_dir = True
            except FileNotFoundError:
                removed_dir = False
            except Exception as exc:
                raise _http_error(
                    500,
                    "template_delete_failed",
                    f"Failed to remove template files: {exc}",
                )

        removed_state = _state_store().delete_template(template_id)

    if not removed_state and not removed_dir and existing_record is None:
        raise _http_error(404, "template_not_found", "template_id not found")

    return {
        "status": "ok",
        "template_id": template_id,
        "correlation_id": correlation_id,
    }


def update_template_metadata(template_id: str, payload: TemplateUpdatePayload, request: Request):
    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
    record = _state_store().get_template_record(template_id)
    if not record:
        raise _http_error(404, "template_not_found", "template_id not found")

    name = payload.name if payload.name is not None else record.get("name") or template_id
    if payload.name is not None and not is_safe_name(name):
        raise _http_error(400, "invalid_name", "Template name contains invalid characters")

    description = payload.description if payload.description is not None else record.get("description")
    if description is not None:
        description = str(description).strip()
        if len(description) > 280:
            raise _http_error(400, "description_too_long", "Description is limited to 280 characters")

    tags = _normalize_tags(payload.tags) if payload.tags is not None else list(record.get("tags") or [])
    status = payload.status if payload.status is not None else record.get("status") or "draft"
    status_norm = str(status or "").strip().lower()
    if status_norm not in {"draft", "pending", "approved", "archived"}:
        raise _http_error(400, "invalid_status", "Status must be draft, pending, approved, or archived")

    updated = _state_store().upsert_template(
        template_id,
        name=name,
        status=status_norm,
        description=description,
        artifacts=record.get("artifacts") or {},
        tags=tags,
        connection_id=record.get("last_connection_id"),
        mapping_keys=record.get("mapping_keys"),
        template_type=record.get("kind") or "pdf",
    )

    return {
        "status": "ok",
        "template": updated,
        "correlation_id": correlation_id,
    }


def _ensure_template_mapping_keys(records: list[dict]) -> list[dict]:
    hydrated: list[dict] = []
    for record in records:
        mapping_keys = record.get("mappingKeys") or []
        if mapping_keys:
            hydrated.append(record)
            continue
        template_id = record.get("id")
        if not template_id:
            hydrated.append(record)
            continue

        kind = record.get("kind") or "pdf"
        try:
            tdir = template_dir(template_id, must_exist=False, create=False, kind=kind)
        except HTTPException:
            hydrated.append(record)
            continue

        keys = load_mapping_keys(tdir)
        if not keys:
            hydrated.append(record)
            continue

        new_record = dict(record)
        new_record["mappingKeys"] = keys
        hydrated.append(new_record)

        try:
            _state_store().upsert_template(
                template_id,
                name=record.get("name") or f"Template {template_id[:8]}",
                status=record.get("status") or "unknown",
                artifacts=record.get("artifacts") or {},
                tags=record.get("tags") or [],
                connection_id=record.get("lastConnectionId"),
                mapping_keys=keys,
                template_type=kind,
            )
        except Exception:
            pass
    return hydrated
