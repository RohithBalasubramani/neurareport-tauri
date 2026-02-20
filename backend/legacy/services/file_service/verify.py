from __future__ import annotations

import contextlib
import importlib
import logging
import os
import shutil
import tempfile
import time
import uuid
import json
from pathlib import Path
from typing import Any, Optional

from fastapi import HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse

from backend.app.services.excel.ExcelVerify import xlsx_to_html_preview
from backend.app.services.templates.TemplateVerify import (
    pdf_page_count,
    pdf_to_pngs,
    render_html_to_png,
    render_panel_preview,
    request_fix_html,
    request_initial_html,
    save_html,
)
from backend.app.services.templates.layout_hints import get_layout_hints
from backend.app.services.utils import (
    TemplateLockError,
    acquire_template_lock,
    get_correlation_id,
    write_artifact_manifest,
    write_json_atomic,
)
from backend.app.services.utils.artifacts import load_manifest
from backend.app.repositories.state import state_store
from backend.legacy.schemas.template_schema import GeneratorAssetsPayload
from backend.legacy.utils.template_utils import artifact_url, manifest_endpoint, template_dir

from .helpers import (
    MAX_VERIFY_PDF_BYTES,
    format_bytes,
    generate_template_id,
    http_error,
)

MAX_VERIFY_XLSX_BYTES: int = 50 * 1024 * 1024  # 50 MiB

logger = logging.getLogger(__name__)


def verify_template(file: UploadFile, connection_id: str | None, request: Request, refine_iters: int = 0, page: int = 0):
    original_filename = getattr(file, "filename", "") or ""
    template_name_hint = Path(original_filename).stem if original_filename else ""
    tid = generate_template_id(template_name_hint, kind="pdf")
    tdir = template_dir(tid, must_exist=False, create=True)
    pdf_path = tdir / "source.pdf"
    html_path = tdir / "template_p1.html"

    request_state = getattr(request, "state", None)
    correlation_id = getattr(request_state, "correlation_id", None) or get_correlation_id()

    try:
        api_mod = importlib.import_module("backend.api")
    except Exception:
        api_mod = None
    pdf_page_count_fn = getattr(api_mod, "pdf_page_count", pdf_page_count)
    pdf_to_pngs_fn = getattr(api_mod, "pdf_to_pngs", pdf_to_pngs)
    request_initial_html_fn = getattr(api_mod, "request_initial_html", request_initial_html)
    save_html_fn = getattr(api_mod, "save_html", save_html)
    render_html_to_png_fn = getattr(api_mod, "render_html_to_png", render_html_to_png)
    render_panel_preview_fn = getattr(api_mod, "render_panel_preview", render_panel_preview)
    request_fix_html_fn = getattr(api_mod, "request_fix_html", request_fix_html)
    write_artifact_manifest_fn = getattr(api_mod, "write_artifact_manifest", write_artifact_manifest)
    get_layout_hints_fn = getattr(api_mod, "get_layout_hints", get_layout_hints)
    state_store_ref = getattr(api_mod, "state_store", state_store)

    def event_stream():
        pipeline_started = time.time()
        failed_error: str | None = None

        def emit(event: str, **payload):
            data = {"event": event, **payload}
            return (json.dumps(data, ensure_ascii=False) + "\n").encode("utf-8")

        stage_timings: dict[str, float] = {}

        def start_stage(stage_key: str, label: str, progress: int | float, **payload: Any) -> bytes:
            stage_timings[stage_key] = time.time()
            event_payload: dict[str, Any] = {
                "stage": stage_key,
                "label": label,
                "status": "started",
                "progress": progress,
                "template_id": tid,
            }
            if payload:
                event_payload.update(payload)
            return emit("stage", **event_payload)

        def finish_stage(
            stage_key: str,
            label: str,
            *,
            progress: int | float | None = None,
            status: str = "complete",
            **payload: Any,
        ) -> bytes:
            started = stage_timings.pop(stage_key, None)
            elapsed_ms = int((time.time() - started) * 1000) if started else None
            event_payload: dict[str, Any] = {
                "stage": stage_key,
                "label": label,
                "status": status,
                "template_id": tid,
            }
            if progress is not None:
                event_payload["progress"] = progress
            if elapsed_ms is not None:
                event_payload["elapsed_ms"] = elapsed_ms
            if payload:
                event_payload.update(payload)
            return emit("stage", **event_payload)

        try:
            stage_key = "verify.upload_pdf"
            stage_label = "Uploading your PDF"
            yield start_stage(stage_key, stage_label, progress=5)
            total_bytes = 0
            try:
                tmp = tempfile.NamedTemporaryFile(
                    dir=str(tdir),
                    prefix="source.",
                    suffix=".pdf.tmp",
                    delete=False,
                )
                try:
                    with tmp:
                        limit_bytes = MAX_VERIFY_PDF_BYTES
                        while True:
                            chunk = file.file.read(1024 * 1024)
                            if not chunk:
                                break
                            total_bytes += len(chunk)
                            if limit_bytes is not None and total_bytes > limit_bytes:
                                raise RuntimeError(f"Uploaded PDF exceeds {format_bytes(limit_bytes)} limit.")
                            tmp.write(chunk)
                        tmp.flush()
                        with contextlib.suppress(OSError):
                            os.fsync(tmp.fileno())
                    Path(tmp.name).replace(pdf_path)
                finally:
                    with contextlib.suppress(FileNotFoundError):
                        Path(tmp.name).unlink(missing_ok=True)
            except Exception as exc:
                logger.exception("verify_upload_pdf_failed")
                yield finish_stage(
                    stage_key,
                    stage_label,
                    progress=5,
                    status="error",
                    detail="File upload failed",
                    size_bytes=total_bytes or None,
                )
                raise
            else:
                # Detect page count and emit with the upload-complete event
                total_pages = 1
                try:
                    total_pages = pdf_page_count_fn(pdf_path)
                except Exception:
                    pass
                yield finish_stage(
                    stage_key, stage_label, progress=20,
                    size_bytes=total_bytes,
                    page_count=total_pages,
                    selected_page=page,
                )

            stage_key = "verify.render_reference_preview"
            stage_label = "Rendering a preview image"
            yield start_stage(stage_key, stage_label, progress=25, page=page, page_count=total_pages)
            png_path: Path | None = None
            layout_hints: dict[str, Any] | None = None
            try:
                ref_pngs = pdf_to_pngs_fn(pdf_path, tdir, dpi=int(os.getenv("PDF_DPI", "400")), page=page)
                if not ref_pngs:
                    raise RuntimeError("No pages rendered from PDF")
                png_path = ref_pngs[0]
                layout_hints = get_layout_hints_fn(pdf_path, page)
            except Exception as exc:
                logger.exception("verify_render_reference_preview_failed")
                yield finish_stage(stage_key, stage_label, progress=25, status="error", detail="Rendering preview failed")
                raise
            else:
                yield finish_stage(stage_key, stage_label, progress=60)

            stage_key = "verify.generate_html"
            stage_label = "Converting preview to HTML"
            yield start_stage(stage_key, stage_label, progress=70)
            try:
                initial_result = request_initial_html_fn(png_path, None, layout_hints=layout_hints)
                html_text = initial_result.html
                schema_payload = initial_result.schema or {}
                save_html_fn(html_path, html_text)
            except Exception as exc:
                logger.exception("verify_generate_html_failed")
                yield finish_stage(stage_key, stage_label, progress=70, status="error", detail="HTML generation failed")
                raise

            schema_path = tdir / "schema_ext.json"
            if schema_payload:
                try:
                    write_json_atomic(
                        schema_path,
                        schema_payload,
                        indent=2,
                        ensure_ascii=False,
                        step="verify_schema_ext",
                    )
                except Exception:
                    pass
            else:
                with contextlib.suppress(FileNotFoundError):
                    schema_path.unlink()

            yield finish_stage(stage_key, stage_label, progress=78)

            render_png_path = tdir / "render_p1.png"
            tight_render_png_path = render_png_path
            stage_key = "verify.render_html_preview"
            stage_label = "Rendering the HTML preview"
            yield start_stage(stage_key, stage_label, progress=80)
            try:
                render_html_to_png_fn(html_path, render_png_path)
                panel_png_path = render_png_path.with_name("render_p1_llm.png")
                render_panel_preview_fn(html_path, panel_png_path, fallback_png=render_png_path)
                tight_render_png_path = panel_png_path if panel_png_path.exists() else render_png_path
                yield finish_stage(stage_key, stage_label, progress=88)
            except Exception as exc:
                logger.exception("verify_render_html_preview_failed")
                yield finish_stage(stage_key, stage_label, progress=80, status="error", detail="HTML preview rendering failed")
                raise

            stage_key = "verify.refine_html_layout"
            stage_label = "Refining HTML layout fidelity..."
            max_fix_passes = int(os.getenv("MAX_FIX_PASSES", "1"))
            fix_enabled = os.getenv("VERIFY_FIX_HTML_ENABLED", "true").lower() not in {
                "false",
                "0",
            }

            yield start_stage(
                stage_key,
                stage_label,
                progress=90,
                max_fix_passes=max_fix_passes,
                fix_enabled=fix_enabled,
            )

            fix_result: Optional[dict[str, Any]] = None
            render_after_path: Optional[Path] = None
            render_after_full_path: Optional[Path] = None
            metrics_path: Optional[Path] = None
            fix_attempted = fix_enabled and max_fix_passes > 0

            if fix_attempted:
                try:
                    fix_result = request_fix_html_fn(
                        tdir,
                        html_path,
                        schema_path if schema_payload else None,
                        png_path,
                        tight_render_png_path,
                        0.0,
                    )
                except Exception:
                    pass
                else:
                    render_after_path = fix_result.get("render_after_path")
                    render_after_full_path = fix_result.get("render_after_full_path")
                    metrics_path = fix_result.get("metrics_path")

            yield finish_stage(
                stage_key,
                stage_label,
                progress=96,
                skipped=not fix_attempted,
                fix_attempted=fix_attempted,
                fix_accepted=bool(fix_result and fix_result.get("accepted")),
                render_after=artifact_url(render_after_path) if render_after_path else None,
                render_after_full=artifact_url(render_after_full_path) if render_after_full_path else None,
                metrics=artifact_url(metrics_path) if metrics_path else None,
            )

            schema_url = artifact_url(schema_path) if schema_payload else None
            render_url = artifact_url(tight_render_png_path)
            render_after_url = artifact_url(render_after_path) if render_after_path else None
            render_after_full_url = artifact_url(render_after_full_path) if render_after_full_path else None
            metrics_url = artifact_url(metrics_path) if metrics_path else None

            manifest_files: dict[str, Path] = {
                "source.pdf": pdf_path,
                "reference_p1.png": png_path,
                "template_p1.html": html_path,
                "render_p1.png": render_png_path,
            }
            if tight_render_png_path and tight_render_png_path.exists():
                manifest_files["render_p1_llm.png"] = tight_render_png_path
            if schema_payload:
                manifest_files["schema_ext.json"] = schema_path
            if render_after_path:
                manifest_files["render_p1_after.png"] = render_after_path
            if render_after_full_path:
                manifest_files["render_p1_after_full.png"] = render_after_full_path
            if metrics_path:
                manifest_files["fix_metrics.json"] = metrics_path

            stage_key = "verify.save_artifacts"
            stage_label = "Saving verification artifacts"
            yield start_stage(stage_key, stage_label, progress=97)
            try:
                write_artifact_manifest_fn(
                    tdir,
                    step="templates_verify",
                    files=manifest_files,
                    inputs=[str(pdf_path)],
                    correlation_id=correlation_id,
                )
            except Exception as exc:
                logger.exception("verify_save_artifacts_failed")
                yield finish_stage(stage_key, stage_label, progress=97, status="error", detail="Saving artifacts failed")
            else:
                yield finish_stage(
                    stage_key,
                    stage_label,
                    progress=99,
                    manifest_files=len(manifest_files),
                    schema_url=schema_url,
                    render_url=render_url,
                    render_after_url=render_after_url,
                    render_after_full_url=render_after_full_url,
                    metrics_url=metrics_url,
                )

            template_name = template_name_hint or f"Template {tid[:8]}"
            artifacts_for_state = {
                "template_html_url": artifact_url(html_path),
                "thumbnail_url": artifact_url(png_path),
                "pdf_url": artifact_url(pdf_path),
                "manifest_url": manifest_endpoint(tid, kind="pdf"),
            }
            if schema_url:
                artifacts_for_state["schema_ext_url"] = schema_url
            if render_url:
                artifacts_for_state["render_png_url"] = render_url
            if render_after_url:
                artifacts_for_state["render_after_png_url"] = render_after_url
            if render_after_full_url:
                artifacts_for_state["render_after_full_png_url"] = render_after_full_url
            if metrics_url:
                artifacts_for_state["fix_metrics_url"] = metrics_url

            state_store_ref.upsert_template(
                tid,
                name=template_name,
                status="draft",
                artifacts=artifacts_for_state,
                connection_id=connection_id or None,
                template_type="pdf",
            )
            state_store_ref.set_last_used(connection_id or None, tid)

            total_elapsed_ms = int((time.time() - pipeline_started) * 1000)
            yield emit(
                "result",
                stage="Verification complete.",
                progress=100,
                template_id=tid,
                schema=schema_payload,
                elapsed_ms=total_elapsed_ms,
                artifacts=artifacts_for_state,
                page_count=total_pages,
                selected_page=page,
            )
        except Exception as e:
            logger.exception("verify_template_failed")
            failed_error = "Verification failed"
            yield emit(
                "error",
                stage="Verification failed.",
                detail="Verification failed",
                template_id=tid,
            )
        finally:
            with contextlib.suppress(Exception):
                file.file.close()
            if failed_error:
                try:
                    template_name = template_name_hint or f"Template {tid[:8]}"
                    state_store_ref.upsert_template(
                        tid,
                        name=template_name,
                        status="failed",
                        artifacts={},
                        connection_id=connection_id or None,
                        template_type="pdf",
                        description=failed_error,
                    )
                except Exception:
                    pass
                with contextlib.suppress(Exception):
                    shutil.rmtree(tdir, ignore_errors=True)

    headers = {"Content-Type": "application/x-ndjson"}
    return StreamingResponse(event_stream(), headers=headers, media_type="application/x-ndjson")


def verify_excel(file: UploadFile, request: Request, connection_id: str | None = None):
    template_kind = "excel"
    original_filename = getattr(file, "filename", "") or ""
    template_name_hint = Path(original_filename).stem if original_filename else ""
    tid = generate_template_id(template_name_hint or "Workbook", kind=template_kind)
    tdir = template_dir(tid, must_exist=False, create=True, kind=template_kind)
    xlsx_path = tdir / "source.xlsx"

    request_state = getattr(request, "state", None)
    correlation_id = getattr(request_state, "correlation_id", None) or get_correlation_id()

    try:
        api_mod = importlib.import_module("backend.api")
    except Exception:
        api_mod = None
    write_artifact_manifest_fn = getattr(api_mod, "write_artifact_manifest", write_artifact_manifest)
    state_store_ref = getattr(api_mod, "state_store", state_store)

    def event_stream():
        pipeline_started = time.time()
        failed_error: str | None = None

        def emit(event: str, **payload):
            data = {"event": event, **payload}
            return (json.dumps(data, ensure_ascii=False) + "\n").encode("utf-8")

        stage_timings: dict[str, float] = {}

        def start_stage(stage_key: str, label: str, progress: int | float, **payload: Any) -> bytes:
            stage_timings[stage_key] = time.time()
            event_payload = {
                "stage": stage_key,
                "label": label,
                "status": "started",
                "progress": progress,
                "template_id": tid,
                "kind": template_kind,
            }
            if payload:
                event_payload.update(payload)
            return emit("stage", **event_payload)

        def finish_stage(
            stage_key: str,
            label: str,
            *,
            progress: int | float | None = None,
            status: str = "complete",
            **payload: Any,
        ) -> bytes:
            started = stage_timings.pop(stage_key, None)
            elapsed_ms = int((time.time() - started) * 1000) if started else None
            event_payload = {
                "stage": stage_key,
                "label": label,
                "status": status,
                "template_id": tid,
                "kind": template_kind,
            }
            if progress is not None:
                event_payload["progress"] = progress
            if elapsed_ms is not None:
                event_payload["elapsed_ms"] = elapsed_ms
            if payload:
                event_payload.update(payload)
            return emit("stage", **event_payload)

        try:
            stage_key = "excel.upload_file"
            stage_label = "Uploading your workbook"
            yield start_stage(stage_key, stage_label, progress=5)
            total_bytes = 0
            try:
                tmp = tempfile.NamedTemporaryFile(
                    dir=str(tdir),
                    prefix="source.",
                    suffix=".xlsx.tmp",
                    delete=False,
                )
                try:
                    with tmp:
                        while True:
                            chunk = file.file.read(1024 * 1024)
                            if not chunk:
                                break
                            total_bytes += len(chunk)
                            if total_bytes > MAX_VERIFY_XLSX_BYTES:
                                raise RuntimeError(f"Uploaded Excel file exceeds {format_bytes(MAX_VERIFY_XLSX_BYTES)} limit.")
                            tmp.write(chunk)
                        tmp.flush()
                        with contextlib.suppress(OSError):
                            os.fsync(tmp.fileno())
                    Path(tmp.name).replace(xlsx_path)
                finally:
                    with contextlib.suppress(FileNotFoundError):
                        Path(tmp.name).unlink(missing_ok=True)
            except Exception as exc:
                logger.exception("excel_upload_file_failed")
                yield finish_stage(stage_key, stage_label, progress=5, status="error", detail="File upload failed")
                raise
            else:
                yield finish_stage(stage_key, stage_label, progress=25, size_bytes=total_bytes)

            stage_key = "excel.generate_html"
            stage_label = "Building preview HTML"
            yield start_stage(stage_key, stage_label, progress=45)
            try:
                preview = xlsx_to_html_preview(xlsx_path, tdir)
                html_path = preview.html_path
                png_path = preview.png_path
            except Exception as exc:
                logger.exception("excel_generate_html_failed")
                yield finish_stage(stage_key, stage_label, progress=45, status="error", detail="HTML generation failed")
                raise
            else:
                yield finish_stage(stage_key, stage_label, progress=80)

            schema_path = tdir / "schema_ext.json"
            sample_rows_path = tdir / "sample_rows.json"
            reference_html_path = tdir / "reference_p1.html"
            reference_png_path = tdir / "reference_p1.png"
            manifest_files: dict[str, Path] = {"source.xlsx": xlsx_path, "template_p1.html": html_path}
            if png_path and png_path.exists():
                manifest_files[png_path.name] = png_path
            if reference_png_path.exists():
                manifest_files[reference_png_path.name] = reference_png_path
            if sample_rows_path.exists():
                manifest_files[sample_rows_path.name] = sample_rows_path
            if reference_html_path.exists():
                manifest_files[reference_html_path.name] = reference_html_path
            if schema_path.exists():
                manifest_files[schema_path.name] = schema_path

            stage_key = "excel.save_artifacts"
            stage_label = "Saving verification artifacts"
            yield start_stage(stage_key, stage_label, progress=90)
            try:
                write_artifact_manifest_fn(
                    tdir,
                    step="excel_verify",
                    files=manifest_files,
                    inputs=[str(xlsx_path)],
                    correlation_id=correlation_id,
                )
            except Exception as exc:
                logger.exception("excel_save_artifacts_failed")
                yield finish_stage(stage_key, stage_label, progress=90, status="error", detail="Saving artifacts failed")
                raise
            else:
                yield finish_stage(stage_key, stage_label, progress=96, manifest_files=len(manifest_files))

            manifest_url = manifest_endpoint(tid, kind=template_kind)
            html_url = artifact_url(html_path)
            png_url = artifact_url(png_path)
            xlsx_url = artifact_url(xlsx_path)
            sample_rows_url = artifact_url(sample_rows_path) if sample_rows_path.exists() else None
            reference_html_url = artifact_url(reference_html_path) if reference_html_path.exists() else None
            reference_png_url = artifact_url(reference_png_path) if reference_png_path.exists() else None
            schema_url = artifact_url(schema_path) if schema_path.exists() else None

            template_display_name = template_name_hint or "Workbook"
            state_store_ref.upsert_template(
                tid,
                name=template_display_name,
                status="draft",
                artifacts={
                    "template_html_url": html_url,
                    "thumbnail_url": png_url,
                    "xlsx_url": xlsx_url,
                    "manifest_url": manifest_url,
                    **({"sample_rows_url": sample_rows_url} if sample_rows_url else {}),
                    **({"reference_html_url": reference_html_url} if reference_html_url else {}),
                    **({"reference_png_url": reference_png_url} if reference_png_url else {}),
                    **({"schema_ext_url": schema_url} if schema_url else {}),
                },
                connection_id=connection_id or None,
                template_type=template_kind,
            )
            state_store_ref.set_last_used(connection_id or None, tid)

            total_elapsed_ms = int((time.time() - pipeline_started) * 1000)
            yield emit(
                "result",
                stage="Excel verification complete.",
                progress=100,
                template_id=tid,
                kind=template_kind,
                schema=None,
                elapsed_ms=total_elapsed_ms,
                artifacts={
                    "xlsx_url": xlsx_url,
                    "png_url": png_url,
                    "html_url": html_url,
                    "manifest_url": manifest_url,
                    **({"sample_rows_url": sample_rows_url} if sample_rows_url else {}),
                    **({"reference_html_url": reference_html_url} if reference_html_url else {}),
                    **({"reference_png_url": reference_png_url} if reference_png_url else {}),
                    **({"schema_ext_url": schema_url} if schema_url else {}),
                },
            )
        except Exception as exc:
            logger.exception("excel_verify_failed")
            failed_error = "Excel verification failed"
            yield emit(
                "error",
                stage="Excel verification failed.",
                detail="Excel verification failed",
                template_id=tid,
                kind=template_kind,
            )
        finally:
            file.file.close()
            if failed_error:
                try:
                    template_display_name = template_name_hint or "Workbook"
                    state_store_ref.upsert_template(
                        tid,
                        name=template_display_name,
                        status="failed",
                        artifacts={},
                        connection_id=connection_id or None,
                        template_type=template_kind,
                        description=failed_error,
                    )
                except Exception:
                    pass
                with contextlib.suppress(Exception):
                    shutil.rmtree(tdir, ignore_errors=True)

    headers = {"Content-Type": "application/x-ndjson"}
    return StreamingResponse(event_stream(), headers=headers, media_type="application/x-ndjson")
