from __future__ import annotations

import importlib
import json
import time
from pathlib import Path
from typing import Any

from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse

from backend.app.services.generator.GeneratorAssetsV1 import GeneratorAssetsError, build_generator_assets_from_payload
from backend.app.repositories.state import store as state_store_module
from backend.app.services.utils import TemplateLockError, acquire_template_lock, get_correlation_id
from backend.app.services.utils.artifacts import load_manifest
from backend.legacy.schemas.template_schema import GeneratorAssetsPayload
from backend.legacy.utils.template_utils import manifest_endpoint, template_dir

from .helpers import http_error, normalize_artifact_map, resolve_template_kind

import logging

logger = logging.getLogger(__name__)


def _state_store():
    return state_store_module.state_store


def generator_assets(template_id: str, payload: GeneratorAssetsPayload, request: Request, *, kind: str = "pdf"):
    correlation_id = getattr(request.state, "correlation_id", None) or get_correlation_id()
    logger.info(
        "generator_assets_v1_start",
        extra={
            "event": "generator_assets_v1_start",
            "template_id": template_id,
            "correlation_id": correlation_id,
            "force_rebuild": bool(payload.force_rebuild),
            "template_kind": kind,
        },
    )

    resolved_kind = resolve_template_kind(template_id) if kind == "pdf" else kind
    template_dir_path = template_dir(template_id, kind=resolved_kind)
    require_contract_join = (resolved_kind or "pdf").lower() != "excel"
    base_template_path = template_dir_path / "template_p1.html"
    final_template_path = template_dir_path / "report_final.html"
    contract_path = template_dir_path / "contract.json"
    overview_path = template_dir_path / "overview.md"
    step5_path = template_dir_path / "step5_requirements.json"

    def _load_step4_payload() -> dict[str, Any]:
        contract_payload = payload.step4_output.get("contract") if payload.step4_output else None
        overview_md = payload.step4_output.get("overview_md") if payload.step4_output else None
        step5_requirements = payload.step4_output.get("step5_requirements") if payload.step4_output else None

        if contract_payload is None:
            if payload.contract is not None:
                contract_payload = payload.contract
            elif contract_path.exists():
                contract_payload = json.loads(contract_path.read_text(encoding="utf-8"))
        if contract_payload is None:
            raise HTTPException(status_code=422, detail="Contract payload is required to build generator assets.")

        if overview_md is None:
            if payload.overview_md is not None:
                overview_md = payload.overview_md
            elif overview_path.exists():
                overview_md = overview_path.read_text(encoding="utf-8")

        if step5_requirements is None:
            if step5_path.exists():
                try:
                    step5_requirements = json.loads(step5_path.read_text(encoding="utf-8"))
                except Exception:
                    step5_requirements = {}
            else:
                step5_requirements = {}

        return {
            "contract": contract_payload,
            "overview_md": overview_md,
            "step5_requirements": step5_requirements or {},
        }

    step4_output = payload.step4_output or _load_step4_payload()

    if payload.final_template_html is not None:
        final_template_html = payload.final_template_html
    else:
        source_path = final_template_path if final_template_path.exists() else base_template_path
        if not source_path.exists():
            raise HTTPException(status_code=422, detail="Template HTML not found. Run mapping approval first.")
        final_template_html = source_path.read_text(encoding="utf-8", errors="ignore")

    catalog_allowlist = payload.catalog or None
    params_spec = payload.params or None
    sample_params = payload.sample_params or None
    dialect = payload.dialect or payload.dialect_hint or "duckdb"
    incoming_key_tokens = payload.key_tokens

    try:
        lock_ctx = acquire_template_lock(template_dir_path, "generator_assets_v1", correlation_id)
    except TemplateLockError:
        raise http_error(status_code=409, code="template_locked", message="Template is currently processing another request.")

    try:
        api_mod = importlib.import_module("backend.api")
    except Exception:
        api_mod = None
    builder = getattr(api_mod, "build_generator_assets_from_payload", build_generator_assets_from_payload)

    def event_stream():
        started = time.time()

        def emit(event: str, **data: Any) -> bytes:
            return (json.dumps({"event": event, **data}, ensure_ascii=False) + "\n").encode("utf-8")

        with lock_ctx:
            yield emit(
                "stage",
                stage="generator_assets_v1",
                status="start",
                progress=10,
                template_id=template_id,
                correlation_id=correlation_id,
            )
            try:
                result = builder(
                    template_dir=template_dir_path,
                    step4_output=step4_output,
                    final_template_html=final_template_html,
                    reference_pdf_image=payload.reference_pdf_image,
                    catalog_allowlist=catalog_allowlist,
                    dialect=dialect,
                    params_spec=params_spec,
                    sample_params=sample_params,
                    force_rebuild=payload.force_rebuild,
                    key_tokens=incoming_key_tokens,
                    require_contract_join=require_contract_join,
                )
            except GeneratorAssetsError as exc:
                logger.warning(
                    "generator_assets_v1_failed",
                    extra={"event": "generator_assets_v1_failed", "template_id": template_id, "correlation_id": correlation_id},
                )
                yield emit("error", stage="generator_assets_v1", detail="Generator assets failed", template_id=template_id)
                return
            except Exception as exc:
                logger.exception(
                    "generator_assets_v1_unexpected",
                    extra={"event": "generator_assets_v1_unexpected", "template_id": template_id, "correlation_id": correlation_id},
                )
                yield emit("error", stage="generator_assets_v1", detail="Generator assets failed", template_id=template_id)
                return

            artifacts_urls = normalize_artifact_map(result.get("artifacts"))
            yield emit(
                "stage",
                stage="generator_assets_v1",
                status="done",
                progress=90,
                template_id=template_id,
                correlation_id=correlation_id,
                invalid=result.get("invalid"),
                needs_user_fix=result.get("needs_user_fix") or [],
                dialect=result.get("dialect"),
                params=result.get("params"),
                summary=result.get("summary"),
                dry_run=result.get("dry_run"),
                cached=result.get("cached"),
                artifacts=artifacts_urls,
            )

            manifest = load_manifest(template_dir_path) or {}
            manifest_url = manifest_endpoint(template_id, kind=resolved_kind)

            existing_tpl = _state_store().get_template_record(template_id) or {}
            artifacts_payload = {
                "contract_url": artifacts_urls.get("contract"),
                "generator_sql_pack_url": artifacts_urls.get("sql_pack"),
                "generator_output_schemas_url": artifacts_urls.get("output_schemas"),
                "generator_assets_url": artifacts_urls.get("generator_assets"),
                "manifest_url": manifest_url,
            }
            _state_store().upsert_template(
                template_id,
                name=existing_tpl.get("name") or f"Template {template_id[:8]}",
                status=existing_tpl.get("status") or "approved",
                artifacts={k: v for k, v in artifacts_payload.items() if v},
                connection_id=existing_tpl.get("last_connection_id"),
                template_type=resolved_kind,
            )
            _state_store().update_template_generator(
                template_id,
                dialect=result.get("dialect"),
                params=result.get("params"),
                invalid=bool(result.get("invalid")),
                needs_user_fix=result.get("needs_user_fix") or [],
                summary=result.get("summary"),
                dry_run=result.get("dry_run"),
            )

            yield emit(
                "result",
                template_id=template_id,
                invalid=result.get("invalid"),
                needs_user_fix=result.get("needs_user_fix") or [],
                dialect=result.get("dialect"),
                params=result.get("params"),
                summary=result.get("summary"),
                dry_run=result.get("dry_run"),
                cached=result.get("cached"),
                artifacts=artifacts_urls,
                manifest=manifest,
                manifest_url=manifest_url,
            )

            logger.info(
                "generator_assets_v1_complete",
                extra={
                    "event": "generator_assets_v1_complete",
                    "template_id": template_id,
                    "invalid": result.get("invalid"),
                    "needs_user_fix": len(result.get("needs_user_fix") or []),
                    "correlation_id": correlation_id,
                    "elapsed_ms": int((time.time() - started) * 1000),
                },
            )

    headers = {"Content-Type": "application/x-ndjson"}
    return StreamingResponse(event_stream(), headers=headers, media_type="application/x-ndjson")
