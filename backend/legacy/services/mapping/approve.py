from __future__ import annotations

import importlib
import json
import logging
import os
import time
from typing import Any

from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse

from backend.app.repositories.connections.db_connection import verify_sqlite
from backend.app.services.contract.ContractBuilderV2 import ContractBuilderError, build_or_load_contract_v2
from backend.app.services.generator.GeneratorAssetsV1 import GeneratorAssetsError, build_generator_assets_from_payload
from backend.app.services.prompts.llm_prompts import PROMPT_VERSION, PROMPT_VERSION_3_5, PROMPT_VERSION_4
from backend.app.repositories.state import state_store
from backend.app.services.templates.TemplateVerify import render_html_to_png, render_panel_preview
from backend.app.services.utils import (
    TemplateLockError,
    acquire_template_lock,
    validate_mapping_schema,
    write_artifact_manifest,
    write_json_atomic,
    write_text_atomic,
)
from backend.app.services.utils.artifacts import load_manifest
from backend.legacy.utils.connection_utils import db_path_from_payload_or_default
from backend.legacy.utils.template_utils import artifact_url, manifest_endpoint, template_dir
from backend.legacy.utils.mapping_utils import mapping_keys_path, normalize_key_tokens, write_mapping_keys
from backend.legacy.services.mapping.helpers import (
    build_catalog_from_db as _build_catalog_from_db,
    compute_db_signature,
    http_error as _http_error,
    load_mapping_step3 as _load_mapping_step3,
    load_schema_ext as _load_schema_ext,
    normalize_artifact_map as _normalize_artifact_map,
    normalize_mapping_for_autofill as _normalize_mapping_for_autofill,
)

logger = logging.getLogger(__name__)

async def run_mapping_approve(
    template_id: str,
    payload: Any,
    request: Request,
    *,
    kind: str = "pdf",
):
    correlation_id = getattr(request.state, "correlation_id", None)
    try:
        api_mod = importlib.import_module("backend.api")
    except Exception:
        api_mod = None
    contract_builder = getattr(api_mod, "build_or_load_contract_v2", build_or_load_contract_v2)
    generator_builder = getattr(api_mod, "build_generator_assets_from_payload", build_generator_assets_from_payload)
    render_html_fn = getattr(api_mod, "render_html_to_png", render_html_to_png)
    render_panel_fn = getattr(api_mod, "render_panel_preview", render_panel_preview)
    logger.info(
        "mapping_approve_start",
        extra={
            "event": "mapping_approve_start",
            "template_id": template_id,
            "connection_id": payload.connection_id,
            "mapping_size": len(payload.mapping or {}),
            "template_kind": kind,
            "correlation_id": correlation_id,
        },
    )

    template_dir_path = template_dir(template_id, kind=kind)
    require_contract_join = (kind or "pdf").lower() != "excel"
    base_template_path = template_dir_path / "template_p1.html"
    final_html_path = template_dir_path / "report_final.html"
    mapping_path = template_dir_path / "mapping_pdf_labels.json"
    mapping_keys_file = mapping_keys_path(template_dir_path)
    incoming_keys = normalize_key_tokens(payload.keys)
    mapping_dict = payload.mapping or {}
    keys_clean = [key for key in incoming_keys if key in mapping_dict]

    try:
        db_path = db_path_from_payload_or_default(payload.connection_id)
        verify_sqlite(db_path)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("approve_db_validation_failed")
        raise _http_error(400, "db_invalid", "Invalid database reference")

    schema_ext = _load_schema_ext(template_dir_path) or {}
    auto_mapping_doc, _ = _load_mapping_step3(template_dir_path)
    auto_mapping_proposal = auto_mapping_doc or {}
    catalog = list(dict.fromkeys(_build_catalog_from_db(db_path)))
    db_sig = compute_db_signature(db_path)

    try:
        lock_ctx = acquire_template_lock(template_dir_path, "mapping_approve", correlation_id)
    except TemplateLockError:
        raise _http_error(
            status_code=409,
            code="template_locked",
            message="Template is currently processing another request.",
        )

    def event_stream():
        pipeline_started = time.time()
        nonlocal keys_clean

        def log_stage(stage_name: str, status: str, started: float) -> None:
            logger.info(
                "mapping_approve_stage",
                extra={
                    "event": "mapping_approve_stage",
                    "template_id": template_id,
                    "stage": stage_name,
                    "status": status,
                    "elapsed_ms": int((time.time() - started) * 1000),
                    "correlation_id": correlation_id,
                },
            )

        def emit(event: str, **payload_data: Any) -> bytes:
            data = {"event": event, **payload_data}
            return (json.dumps(data, ensure_ascii=False) + "\n").encode("utf-8")

        stage_timings: dict[str, float] = {}

        def start_stage(stage_key: str, label: str, progress: int | float, **payload_data: Any) -> bytes:
            stage_timings[stage_key] = time.time()
            payload = {"stage": stage_key, "label": label, "status": "started", "progress": progress, "template_id": template_id}
            payload.update(payload_data)
            return emit("stage", **payload)

        def finish_stage(
            stage_key: str,
            label: str,
            *,
            progress: int | float | None = None,
            status: str = "complete",
            **payload_data: Any,
        ) -> bytes:
            started = stage_timings.pop(stage_key, None)
            elapsed_ms = int((time.time() - started) * 1000) if started else None
            payload: dict[str, Any] = {"stage": stage_key, "label": label, "status": status, "template_id": template_id}
            if progress is not None:
                payload["progress"] = progress
            if elapsed_ms is not None:
                payload["elapsed_ms"] = elapsed_ms
            payload.update(payload_data)
            return emit("stage", **payload)

        contract_ready = False
        contract_stage_summary: dict[str, Any] | None = None
        generator_stage_summary: dict[str, Any] | None = None
        contract_result: dict[str, Any] = {}
        generator_result: dict[str, Any] | None = None
        generator_artifacts_urls: dict[str, str] = {}

        with lock_ctx:
            stage_key = "mapping.save"
            stage_label = "Saving mapping changes"
            stage_started = time.time()
            try:
                yield start_stage(stage_key, stage_label, progress=5)
                normalized_list = _normalize_mapping_for_autofill(payload.mapping)
                normalized_headers = {entry["header"] for entry in normalized_list}
                keys_clean = [key for key in keys_clean if key in normalized_headers]
                validate_mapping_schema(normalized_list)
                write_json_atomic(mapping_path, normalized_list, indent=2, ensure_ascii=False, step="mapping_save")
                keys_clean = write_mapping_keys(template_dir_path, keys_clean)
                manifest_files = {mapping_path.name: mapping_path}
                if mapping_keys_file.exists():
                    manifest_files[mapping_keys_file.name] = mapping_keys_file
                write_artifact_manifest(
                    template_dir_path,
                    step="mapping_save",
                    files=manifest_files,
                    inputs=[f"mapping_tokens={len(normalized_list)}", f"mapping_keys={len(keys_clean)}"],
                    correlation_id=correlation_id,
                )
                log_stage(stage_label, "ok", stage_started)
                yield finish_stage(stage_key, stage_label, progress=20, mapping_tokens=len(normalized_list))
            except Exception as exc:
                log_stage(stage_label, "error", stage_started)
                logger.exception(
                    "mapping_save_failed",
                    extra={"event": "mapping_save_failed", "template_id": template_id, "correlation_id": correlation_id},
                )
                yield finish_stage(stage_key, stage_label, progress=5, status="error", detail="Mapping save failed")
                yield emit("error", stage=stage_key, label=stage_label, detail="Mapping save failed", template_id=template_id)
                return

            stage_key = "mapping.prepare_template"
            stage_label = "Preparing template shell"
            stage_started = time.time()
            try:
                yield start_stage(stage_key, stage_label, progress=25)
                if not base_template_path.exists() and not final_html_path.exists():
                    raise FileNotFoundError("No template HTML found. Run /templates/verify or create via chat first.")
                if not final_html_path.exists():
                    from backend.app.services.utils.html import _fix_fixed_footers
                    final_html_path.write_text(
                        _fix_fixed_footers(base_template_path.read_text(encoding="utf-8", errors="ignore")),
                        encoding="utf-8",
                    )
                log_stage(stage_label, "ok", stage_started)
                yield finish_stage(stage_key, stage_label, progress=50)
            except Exception as exc:
                log_stage(stage_label, "error", stage_started)
                logger.exception(
                    "mapping_prepare_final_html_failed",
                    extra={
                        "event": "mapping_prepare_final_html_failed",
                        "template_id": template_id,
                        "correlation_id": correlation_id,
                    },
                )
                yield finish_stage(stage_key, stage_label, progress=25, status="error", detail="Template preparation failed")
                yield emit("error", stage=stage_key, label=stage_label, detail="Template preparation failed", template_id=template_id)
                return

            final_html_url = artifact_url(final_html_path)
            template_html_url = final_html_url or artifact_url(base_template_path)
            tokens_mapped = len(payload.mapping or {})

            stage_key = "contract_build_v2"
            stage_label = "Drafting contract package"
            stage_started = time.time()
            yield start_stage(
                stage_key,
                stage_label,
                progress=55,
                contract_ready=False,
                blueprint_ready=bool(auto_mapping_proposal),
                overview_md=None,
                cached=False,
                warnings=[],
                assumptions=[],
                validation={},
                prompt_version=PROMPT_VERSION_4,
            )
            try:
                final_html_text = final_html_path.read_text(encoding="utf-8", errors="ignore")
                contract_result = contract_builder(
                    template_dir=template_dir_path,
                    catalog=catalog,
                    final_template_html=final_html_text,
                    schema=schema_ext,
                    auto_mapping_proposal=auto_mapping_proposal,
                    mapping_override=payload.mapping,
                    user_instructions=payload.user_instructions or "",
                    dialect_hint=payload.dialect_hint,
                    db_signature=db_sig,
                    key_tokens=keys_clean,
                )
                contract_ready = True
                contract_artifacts_urls = _normalize_artifact_map(contract_result.get("artifacts"))
                contract_stage_summary = {
                    "stage": stage_key,
                    "status": "done",
                    "contract_ready": True,
                    "overview_md": contract_result.get("overview_md"),
                    "cached": contract_result.get("cached"),
                    "warnings": contract_result.get("warnings"),
                    "assumptions": contract_result.get("assumptions"),
                    "validation": contract_result.get("validation"),
                    "artifacts": contract_artifacts_urls,
                    "prompt_version": PROMPT_VERSION_4,
                }
                log_stage(stage_label, "ok", stage_started)
                yield finish_stage(
                    stage_key,
                    stage_label,
                    progress=75,
                    contract_ready=True,
                    overview_md=contract_result.get("overview_md"),
                    cached=contract_result.get("cached"),
                    warnings=contract_result.get("warnings"),
                    assumptions=contract_result.get("assumptions"),
                    validation=contract_result.get("validation"),
                    artifacts=contract_artifacts_urls,
                    prompt_version=PROMPT_VERSION_4,
                )
            except ContractBuilderError as exc:
                log_stage(stage_label, "error", stage_started)
                logger.exception(
                    "contract_build_failed",
                    extra={"event": "contract_build_failed", "template_id": template_id, "correlation_id": correlation_id},
                )
                yield finish_stage(
                    stage_key,
                    stage_label,
                    progress=55,
                    status="error",
                    detail="Contract build failed",
                    prompt_version=PROMPT_VERSION_4,
                )
                yield emit(
                    "error",
                    stage=stage_key,
                    label=stage_label,
                    detail="Contract build failed",
                    template_id=template_id,
                    prompt_version=PROMPT_VERSION_4,
                )
                return
            except Exception as exc:
                log_stage(stage_label, "error", stage_started)
                logger.exception(
                    "contract_build_failed",
                    extra={"event": "contract_build_failed", "template_id": template_id, "correlation_id": correlation_id},
                )
                yield finish_stage(
                    stage_key,
                    stage_label,
                    progress=55,
                    status="error",
                    detail="Contract build failed",
                    prompt_version=PROMPT_VERSION_4,
                )
                yield emit(
                    "error",
                    stage=stage_key,
                    label=stage_label,
                    detail="Contract build failed",
                    template_id=template_id,
                    prompt_version=PROMPT_VERSION_4,
                )
                return

            stage_key = "generator_assets_v1"
            stage_label = "Creating generator assets"
            stage_started = time.time()
            generator_dialect = payload.generator_dialect or payload.dialect_hint or "duckdb"

            # DataFrame pipeline resolves data directly from the contract —
            # skip SQL-based generator assets entirely (Call 5 SQL removed).
            logger.info("df_mode_skip_generator_assets", extra={"event": "df_mode_skip_generator_assets", "template_id": template_id})
            generator_stage_summary = {"stage": stage_key, "status": "skipped", "detail": "Skipped — DataFrame pipeline"}
            generator_artifacts_urls = {}
            yield finish_stage(stage_key, stage_label, progress=92, status="skipped", detail="Skipped — DataFrame pipeline")

            stage_key = "mapping.thumbnail"
            stage_label = "Capturing template thumbnail"
            stage_started = time.time()
            thumbnail_url = None
            try:
                yield start_stage(stage_key, stage_label, progress=95)
                thumb_path = final_html_path.parent / "report_final.png"
                render_html_fn(final_html_path, thumb_path)
                thumbnail_url = artifact_url(thumb_path)
                write_artifact_manifest(
                    template_dir_path,
                    step="mapping_thumbnail",
                    files={
                        "report_final.html": final_html_path,
                        "template_p1.html": base_template_path,
                        "report_final.png": thumb_path,
                    },
                    inputs=[str(mapping_path)],
                    correlation_id=correlation_id,
                )
                log_stage(stage_label, "ok", stage_started)
                yield finish_stage(stage_key, stage_label, progress=98, thumbnail_url=thumbnail_url)
            except Exception:
                log_stage(stage_label, "error", stage_started)
                yield finish_stage(stage_key, stage_label, progress=95, status="error")

            manifest_data = load_manifest(template_dir_path) or {}
            manifest_url = manifest_endpoint(template_id, kind=kind)
            page_summary_path = template_dir_path / "page_summary.txt"
            page_summary_url = artifact_url(page_summary_path)

            contract_artifacts = (
                contract_stage_summary.get("artifacts") if isinstance(contract_stage_summary, dict) else {}
            )
            generator_artifacts = (
                generator_stage_summary.get("artifacts") if isinstance(generator_stage_summary, dict) else {}
            )
            if not isinstance(generator_artifacts, dict):
                generator_artifacts = {}

            generator_contract_url = generator_artifacts.get("contract") or generator_artifacts.get("contract.json")
            contract_url = generator_contract_url or contract_artifacts.get("contract") or contract_artifacts.get("contract.json")

            # Fallback: if stage artifacts didn't report a contract URL but
            # contract.json exists on disk (e.g. fresh build path), derive the URL.
            if not contract_url:
                disk_contract = template_dir_path / "contract.json"
                if disk_contract.exists():
                    contract_url = artifact_url(disk_contract)

            # Also derive overview/step5 URLs from disk when stages didn't report them
            overview_url = contract_artifacts.get("overview")
            if not overview_url:
                disk_overview = template_dir_path / "overview.md"
                if disk_overview.exists():
                    overview_url = artifact_url(disk_overview)

            step5_url = contract_artifacts.get("step5_requirements")
            if not step5_url:
                disk_step5 = template_dir_path / "step5_requirements.json"
                if disk_step5.exists():
                    step5_url = artifact_url(disk_step5)

            artifacts_payload = {
                "template_html_url": template_html_url,
                "final_html_url": final_html_url,
                "thumbnail_url": thumbnail_url,
                "manifest_url": manifest_url,
                "page_summary_url": page_summary_url,
                "contract_url": contract_url,
                "overview_url": overview_url,
                "step5_requirements_url": step5_url,
                "generator_sql_pack_url": generator_artifacts.get("sql_pack"),
                "generator_output_schemas_url": generator_artifacts.get("output_schemas"),
                "generator_assets_url": generator_artifacts.get("generator_assets"),
                "mapping_keys_url": artifact_url(mapping_keys_file) if mapping_keys_file.exists() else None,
            }

            final_contract_ready = bool(contract_url)

            existing_tpl = state_store.get_template_record(template_id) or {}
            state_store.upsert_template(
                template_id,
                name=existing_tpl.get("name") or f"Template {template_id[:8]}",
                status="approved" if final_contract_ready else "pending",
                artifacts={k: v for k, v in artifacts_payload.items() if v},
                connection_id=payload.connection_id or existing_tpl.get("last_connection_id"),
                mapping_keys=keys_clean,
                template_type=kind,
            )

            if generator_result:
                state_store.update_template_generator(
                    template_id,
                    dialect=generator_result.get("dialect"),
                    params=generator_result.get("params"),
                    invalid=bool(generator_result.get("invalid")),
                    needs_user_fix=generator_result.get("needs_user_fix") or [],
                    summary=generator_result.get("summary"),
                    dry_run=generator_result.get("dry_run"),
                )

            state_store.set_last_used(payload.connection_id or existing_tpl.get("last_connection_id"), template_id)

            total_elapsed_ms = int((time.time() - pipeline_started) * 1000)
            contract_ready = final_contract_ready
            result_payload = {
                "stage": "Approval complete.",
                "progress": 100,
                "template_id": template_id,
                "saved": artifact_url(mapping_path),
                "final_html_path": str(final_html_path),
                "final_html_url": final_html_url,
                "template_html_url": template_html_url,
                "thumbnail_url": thumbnail_url,
                "contract_ready": contract_ready,
                "token_map_size": tokens_mapped,
                "user_values_supplied": bool((payload.user_values_text or "").strip()),
                "manifest": manifest_data,
                "manifest_url": manifest_url,
                "artifacts": {k: v for k, v in artifacts_payload.items() if v},
                "contract_stage": contract_stage_summary,
                "generator_stage": generator_stage_summary,
                "prompt_versions": {
                    "mapping": PROMPT_VERSION,
                    "corrections": PROMPT_VERSION_3_5,
                    "contract": PROMPT_VERSION_4,
                },
                "elapsed_ms": total_elapsed_ms,
                "keys": keys_clean,
                "keys_count": len(keys_clean),
            }
            yield emit("result", **result_payload)

            logger.info(
                "mapping_approve_complete",
                extra={
                    "event": "mapping_approve_complete",
                    "template_id": template_id,
                    "contract_ready": contract_ready,
                    "thumbnail_url": thumbnail_url,
                    "correlation_id": correlation_id,
                    "elapsed_ms": total_elapsed_ms,
                },
            )

    headers = {"Content-Type": "application/x-ndjson"}
    return StreamingResponse(event_stream(), headers=headers, media_type="application/x-ndjson")
