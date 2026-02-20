from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

from fastapi import Request
from fastapi.responses import StreamingResponse

from backend.app.services.mapping.CorrectionsPreview import CorrectionsPreviewError, run_corrections_preview as corrections_preview_fn
from backend.app.services.prompts.llm_prompts import PROMPT_VERSION_3_5
from backend.app.repositories.state import state_store
from backend.app.services.utils import TemplateLockError, acquire_template_lock
from backend.legacy.services.mapping.helpers import http_error as _http_error
from backend.legacy.utils.template_utils import artifact_url, template_dir

logger = logging.getLogger(__name__)

def run_corrections_preview(
    template_id: str,
    payload: Any,
    request: Request,
    *,
    kind: str = "pdf",
):
    correlation_id = getattr(request.state, "correlation_id", None)
    logger.info(
        "corrections_preview_start",
        extra={
            "event": "corrections_preview_start",
            "template_id": template_id,
            "correlation_id": correlation_id,
            "template_kind": kind,
        },
    )

    template_dir_path = template_dir(template_id, kind=kind)
    template_html_path = template_dir_path / "template_p1.html"
    mapping_step3_path = template_dir_path / "mapping_step3.json"
    schema_ext_path = template_dir_path / "schema_ext.json"

    page_index = max(1, int(payload.page or 1))
    reference_png = template_dir_path / f"reference_p{page_index}.png"
    page_png_path = reference_png if reference_png.exists() else None

    def event_stream():
        started = time.time()

        def emit(event: str, **data: Any) -> bytes:
            return (json.dumps({"event": event, **data}, ensure_ascii=False) + "\n").encode("utf-8")

        yield emit(
            "stage",
            stage="corrections_preview",
            status="start",
            progress=10,
            template_id=template_id,
            correlation_id=correlation_id,
            prompt_version=PROMPT_VERSION_3_5,
        )
        try:
            try:
                lock_ctx = acquire_template_lock(
                    template_dir_path,
                    "mapping_corrections_preview",
                    correlation_id,
                )
            except TemplateLockError:
                yield emit(
                    "error",
                    stage="corrections_preview",
                    detail="Template is currently processing another request.",
                    template_id=template_id,
                )
                return
            with lock_ctx:
                result = corrections_preview_fn(
                    upload_dir=template_dir_path,
                    template_html_path=template_html_path,
                    mapping_step3_path=mapping_step3_path,
                    schema_ext_path=schema_ext_path,
                    user_input=payload.user_input or "",
                    page_png_path=page_png_path,
                    model_selector=payload.model_selector,
                    mapping_override=payload.mapping_override,
                    sample_tokens=payload.sample_tokens,
                )
        except CorrectionsPreviewError as exc:
            logger.warning(
                "corrections_preview_failed",
                extra={"event": "corrections_preview_failed", "template_id": template_id, "correlation_id": correlation_id},
            )
            yield emit("error", stage="corrections_preview", detail="Corrections preview failed", template_id=template_id)
            return
        except Exception as exc:
            logger.exception(
                "corrections_preview_unexpected",
                extra={
                    "event": "corrections_preview_unexpected",
                    "template_id": template_id,
                    "correlation_id": correlation_id,
                },
            )
            yield emit("error", stage="corrections_preview", detail="Corrections preview failed", template_id=template_id)
            return

        artifacts_raw = result.get("artifacts") or {}
        artifacts: dict[str, str] = {}
        for name, value in artifacts_raw.items():
            resolved: Optional[Path]
            if isinstance(value, Path):
                resolved = value
            else:
                try:
                    resolved = Path(value)
                except Exception:
                    resolved = None
            url = artifact_url(resolved)
            if url:
                artifacts[str(name)] = url

        template_html_url = artifacts.get("template_html")
        page_summary_url = artifacts.get("page_summary")
        if template_html_url or page_summary_url:
            existing_tpl = state_store.get_template_record(template_id) or {}
            artifacts_for_state: dict[str, str] = {}
            if template_html_url:
                artifacts_for_state["template_html_url"] = template_html_url
            if page_summary_url:
                artifacts_for_state["page_summary_url"] = page_summary_url
            if artifacts_for_state:
                existing_status = (existing_tpl.get("status") or "").lower()
                next_status = existing_tpl.get("status") or "mapping_corrections_previewed"
                if existing_status != "approved":
                    next_status = "mapping_corrections_previewed"
                state_store.upsert_template(
                    template_id,
                    name=existing_tpl.get("name") or f"Template {template_id[:8]}",
                    status=next_status,
                    artifacts=artifacts_for_state,
                    connection_id=existing_tpl.get("last_connection_id"),
                    template_type=kind,
                )

        yield emit(
            "stage",
            stage="corrections_preview",
            status="done",
            progress=90,
            template_id=template_id,
            correlation_id=correlation_id,
            cache_hit=bool(result.get("cache_hit")),
            prompt_version=PROMPT_VERSION_3_5,
        )

        yield emit(
            "result",
            template_id=template_id,
            summary=result.get("summary") or {},
            processed=result.get("processed") or {},
            artifacts=artifacts,
            cache_key=result.get("cache_key"),
            cache_hit=bool(result.get("cache_hit")),
            prompt_version=PROMPT_VERSION_3_5,
        )

        logger.info(
            "corrections_preview_complete",
            extra={
                "event": "corrections_preview_complete",
                "template_id": template_id,
                "elapsed_ms": int((time.time() - started) * 1000),
                "correlation_id": correlation_id,
            },
        )

    headers = {"Content-Type": "application/x-ndjson"}
    return StreamingResponse(event_stream(), headers=headers, media_type="application/x-ndjson")
