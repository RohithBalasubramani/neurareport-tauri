from __future__ import annotations

import asyncio
import hashlib
import importlib
import json
import logging
from typing import Any, Iterator, Optional

from fastapi import HTTPException, Request

from backend.app.repositories.connections.db_connection import verify_sqlite
from backend.app.services.mapping.AutoMapInline import MappingInlineValidationError, run_llm_call_3
from backend.app.services.mapping.CorrectionsPreview import run_corrections_preview as corrections_preview_fn
from backend.app.services.mapping.HeaderMapping import approval_errors, get_parent_child_info
from backend.app.services.prompts.llm_prompts import PROMPT_VERSION
from backend.app.repositories.state import store as state_store_module
from backend.app.services.utils import TemplateLockError, acquire_template_lock, write_artifact_manifest, write_json_atomic, write_text_atomic
from backend.legacy.utils.connection_utils import db_path_from_payload_or_default
from backend.legacy.utils.mapping_utils import load_mapping_keys, mapping_keys_path
from backend.legacy.utils.template_utils import artifact_url, find_reference_pdf, find_reference_png, manifest_endpoint, template_dir

from .helpers import (
    build_catalog_from_db,
    build_rich_catalog_from_db,
    compute_db_signature,
    format_catalog_rich,
    http_error,
    load_mapping_step3,
    load_schema_ext,
    sha256_path,
    sha256_text,
)

logger = logging.getLogger(__name__)


def _mapping_preview_pipeline(
    template_id: str,
    connection_id: Optional[str],
    request: Optional[Request],
    *,
    correlation_id: Optional[str] = None,
    force_refresh: bool = False,
    kind: str = "pdf",
) -> Iterator[dict[str, Any]]:
    try:
        api_mod = importlib.import_module("backend.api")
    except Exception:
        api_mod = None
    verify_sqlite_fn = getattr(api_mod, "verify_sqlite", verify_sqlite)
    run_llm_call_3_fn = getattr(api_mod, "run_llm_call_3", run_llm_call_3)
    build_catalog_fn = getattr(api_mod, "_build_catalog_from_db", build_catalog_from_db)
    get_parent_child_info_fn = getattr(api_mod, "get_parent_child_info", get_parent_child_info)
    state_store_ref = getattr(api_mod, "state_store", state_store_module.state_store)

    correlation_id = correlation_id or (getattr(request.state, "correlation_id", None) if request else None)
    yield {
        "event": "stage",
        "stage": "mapping_preview",
        "status": "start",
        "template_id": template_id,
        "correlation_id": correlation_id,
        "prompt_version": PROMPT_VERSION,
    }

    template_dir_path = template_dir(template_id, kind=kind)
    mapping_keys_file = mapping_keys_path(template_dir_path)
    html_path = template_dir_path / "template_p1.html"
    if not html_path.exists():
        html_path = template_dir_path / "report_final.html"
    if not html_path.exists():
        raise http_error(404, "template_not_ready", "Run /templates/verify first")
    template_html = html_path.read_text(encoding="utf-8", errors="ignore")

    schema_ext = load_schema_ext(template_dir_path) or {}
    db_path = db_path_from_payload_or_default(connection_id)
    verify_sqlite_fn(db_path)

    catalog = list(dict.fromkeys(build_catalog_fn(db_path)))

    # Build rich catalog with types + sample values for LLM mapping
    _rich_catalog_text: str | None = None
    try:
        _rich_catalog_text = format_catalog_rich(build_rich_catalog_from_db(db_path))
    except Exception:
        logger.warning("rich_catalog_build_degraded", extra={"template_id": template_id})

    try:
        schema_info = get_parent_child_info_fn(db_path)
    except Exception as exc:
        logger.warning(
            "mapping_preview_schema_probe_degraded",
            extra={
                "event": "mapping_preview_schema_probe_degraded",
                "template_id": template_id,
                "error": str(exc),
            },
        )
        # Additive fallback: build minimal schema_info from catalog so the
        # LLM mapping call can still proceed with available table/column info.
        tables_from_catalog: dict[str, list[str]] = {}
        for entry in catalog:
            if "." in entry:
                tbl, col = entry.split(".", 1)
                tables_from_catalog.setdefault(tbl, []).append(col)
        if tables_from_catalog:
            all_tables = sorted(tables_from_catalog.keys())
            first_table = all_tables[0]
            first_cols = tables_from_catalog[first_table]
            schema_info = {
                "child table": first_table,
                "parent table": first_table,
                "child_columns": first_cols,
                "parent_columns": first_cols,
                "common_names": first_cols,
            }
        else:
            schema_info = {
                "child table": "",
                "parent table": "",
                "child_columns": [],
                "parent_columns": [],
                "common_names": [],
            }
    pdf_sha = sha256_path(find_reference_pdf(template_dir_path)) or ""
    png_path = find_reference_png(template_dir_path)
    db_sig = compute_db_signature(db_path) or ""
    html_pre_sha = sha256_text(template_html)
    catalog_sha = hashlib.sha256(json.dumps(catalog, sort_keys=True).encode("utf-8")).hexdigest()
    schema_sha = hashlib.sha256(json.dumps(schema_ext, sort_keys=True).encode("utf-8")).hexdigest() if schema_ext else ""
    saved_keys = load_mapping_keys(template_dir_path)

    cache_payload = {
        "pdf_sha": pdf_sha,
        "db_signature": db_sig,
        "html_sha": html_pre_sha,
        "prompt_version": PROMPT_VERSION,
        "catalog_sha": catalog_sha,
        "schema_sha": schema_sha,
    }
    cache_key = hashlib.sha256(json.dumps(cache_payload, sort_keys=True).encode("utf-8")).hexdigest()

    cached_doc, mapping_path = load_mapping_step3(template_dir_path)
    constants_path = template_dir_path / "constant_replacements.json"
    if not force_refresh and cached_doc:
        prompt_meta = cached_doc.get("prompt_meta") or {}
        post_sha = prompt_meta.get("post_html_sha256")
        pre_sha_cached = prompt_meta.get("pre_html_sha256")
        cache_key_stored = prompt_meta.get("cache_key")
        html_matches_pre = pre_sha_cached == html_pre_sha
        html_matches_post = bool(post_sha and post_sha == html_pre_sha)
        cache_key_matches = cache_key_stored == cache_key
        cache_match = (cache_key_matches and (html_matches_pre or html_matches_post)) or (
            html_matches_post and cache_key_stored and not cache_key_matches
        )
        if cache_match:
            effective_cache_key = cache_key if cache_key_matches else (cache_key_stored or cache_key)
            mapping = cached_doc.get("mapping") or {}
            constant_replacements = cached_doc.get("constant_replacements") or {}
            if not constant_replacements and isinstance(cached_doc.get("raw_payload"), dict):
                constant_replacements = cached_doc["raw_payload"].get("constant_replacements") or {}
            errors = approval_errors(mapping)
            cached_prompt_version = prompt_meta.get("prompt_version") or PROMPT_VERSION
            yield {
                "event": "stage",
                "stage": "mapping_preview",
                "status": "cached",
                "template_id": template_id,
                "cache_key": effective_cache_key,
                "correlation_id": correlation_id,
                "prompt_version": cached_prompt_version,
            }
            return {
                "mapping": mapping,
                "errors": errors,
                "schema_info": schema_info,
                "catalog": catalog,
                "cache_key": effective_cache_key,
                "cached": True,
                "constant_replacements": constant_replacements,
                "constant_replacements_count": len(constant_replacements),
                "prompt_version": cached_prompt_version,
                "keys": saved_keys,
            }

    try:
        lock_ctx = acquire_template_lock(template_dir_path, "mapping_preview", correlation_id)
    except TemplateLockError:
        raise http_error(409, "template_locked", "Template is currently processing another request.")

    with lock_ctx:
        try:
            result = run_llm_call_3_fn(
                template_html,
                catalog,
                schema_ext,
                PROMPT_VERSION,
                str(png_path) if png_path else "",
                cache_key,
                rich_catalog_text=_rich_catalog_text,
            )
        except MappingInlineValidationError as exc:
            logger.exception("mapping_llm_validation_error")
            raise http_error(422, "mapping_llm_invalid", "Mapping LLM validation failed")
        except Exception as exc:
            logger.exception(
                "mapping_preview_llm_failed",
                extra={"event": "mapping_preview_llm_failed", "template_id": template_id},
            )
            raise http_error(500, "mapping_llm_failed", "Mapping LLM call failed")

        html_applied = result.html_constants_applied
        write_text_atomic(html_path, html_applied, encoding="utf-8", step="mapping_preview_html")
        html_post_sha = sha256_text(html_applied)

        mapping_doc = {
            "mapping": result.mapping,
            "meta": result.meta,
            "prompt_meta": {
                **(result.prompt_meta or {}),
                "cache_key": cache_key,
                "pre_html_sha256": html_pre_sha,
                "post_html_sha256": html_post_sha,
                "prompt_version": PROMPT_VERSION,
                "catalog_sha256": cache_payload.get("catalog_sha"),
                "schema_sha256": cache_payload.get("schema_sha"),
                "pdf_sha256": pdf_sha,
                "db_signature": db_sig,
            },
            "raw_payload": result.raw_payload,
            "constant_replacements": result.constant_replacements,
            "token_samples": result.token_samples,
        }
        write_json_atomic(mapping_path, mapping_doc, ensure_ascii=False, indent=2, step="mapping_preview_mapping")
        write_json_atomic(
            constants_path,
            result.constant_replacements,
            ensure_ascii=False,
            indent=2,
            step="mapping_preview_constants",
        )
        files_payload = {html_path.name: html_path, mapping_path.name: mapping_path, constants_path.name: constants_path}
        if mapping_keys_file.exists():
            files_payload[mapping_keys_file.name] = mapping_keys_file
        write_artifact_manifest(
            template_dir_path,
            step="mapping_inline_llm_call_3",
            files=files_payload,
            inputs=[
                f"cache_key={cache_key}",
                f"catalog_sha256={cache_payload.get('catalog_sha')}",
                f"schema_sha256={cache_payload.get('schema_sha')}",
                f"html_pre_sha256={html_pre_sha}",
                f"html_post_sha256={html_post_sha}",
            ],
            correlation_id=correlation_id,
        )

    errors = approval_errors(result.mapping)
    constant_replacements = result.constant_replacements

    record = state_store_ref.get_template_record(template_id) or {}
    template_name = record.get("name") or f"Template {template_id[:8]}"
    artifacts = {
        "template_html_url": artifact_url(html_path),
        "mapping_step3_url": artifact_url(mapping_path),
    }
    constants_url = artifact_url(constants_path)
    if constants_url:
        artifacts["constants_inlined_url"] = constants_url
    if mapping_keys_file.exists():
        artifacts["mapping_keys_url"] = artifact_url(mapping_keys_file)
    schema_path = template_dir_path / "schema_ext.json"
    schema_url = artifact_url(schema_path) if schema_path.exists() else None
    if schema_url:
        artifacts["schema_ext_url"] = schema_url
    state_store_ref.upsert_template(
        template_id,
        name=template_name,
        status="mapping_previewed",
        artifacts={k: v for k, v in artifacts.items() if v},
        connection_id=connection_id or record.get("last_connection_id"),
        mapping_keys=saved_keys,
        template_type=kind,
    )

    yield {
        "event": "stage",
        "stage": "mapping_preview",
        "status": "ok",
        "template_id": template_id,
        "cache_key": cache_key,
        "correlation_id": correlation_id,
        "prompt_version": PROMPT_VERSION,
    }

    return {
        "mapping": result.mapping,
        "errors": errors,
        "schema_info": schema_info,
        "catalog": catalog,
        "cache_key": cache_key,
        "cached": False,
        "constant_replacements": constant_replacements,
        "constant_replacements_count": len(constant_replacements),
        "prompt_version": PROMPT_VERSION,
        "keys": saved_keys,
    }


async def run_mapping_preview(
    template_id: str,
    connection_id: str,
    request: Request,
    force_refresh: bool = False,
    *,
    kind: str = "pdf",
) -> dict:
    correlation_id = getattr(request.state, "correlation_id", None)
    logger.info(
        "mapping_preview_start",
        extra={
            "event": "mapping_preview_start",
            "template_id": template_id,
            "connection_id": connection_id,
            "force_refresh": force_refresh,
            "template_kind": kind,
            "correlation_id": correlation_id,
        },
    )
    pipeline = _mapping_preview_pipeline(
        template_id,
        connection_id,
        request,
        correlation_id=correlation_id,
        force_refresh=force_refresh,
        kind=kind,
    )
    try:
        while True:
            next(pipeline)
    except StopIteration as stop:
        payload = stop.value or {}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "mapping_preview_failed",
            extra={"event": "mapping_preview_failed", "template_id": template_id, "correlation_id": correlation_id},
        )
        raise http_error(500, "mapping_preview_failed", "Mapping preview failed")

    logger.info(
        "mapping_preview_complete",
        extra={
            "event": "mapping_preview_complete",
            "template_id": template_id,
            "connection_id": connection_id,
            "cache_key": payload.get("cache_key"),
            "cached": payload.get("cached", False),
            "template_kind": kind,
            "correlation_id": correlation_id,
        },
    )
    return payload


def mapping_preview_internal(
    template_id: str,
    connection_id: str,
    request: Request,
    force_refresh: bool = False,
    *,
    kind: str = "pdf",
) -> dict:
    coro = run_mapping_preview(template_id, connection_id, request, force_refresh, kind=kind)
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    raise RuntimeError("mapping_preview_internal cannot be called from a running event loop; use run_mapping_preview instead.")
