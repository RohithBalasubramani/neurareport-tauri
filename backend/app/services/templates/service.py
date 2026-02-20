from __future__ import annotations

import asyncio
import contextlib
import logging
import tempfile
import zipfile
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from backend.app.utils.event_bus import Event, EventBus, logging_middleware, metrics_middleware
from backend.app.utils.pipeline import PipelineRunner, PipelineStep
from backend.app.utils.result import Result, err, ok
from backend.app.utils.strategies import StrategyRegistry
from backend.app.services.templates.errors import (
    TemplateExtractionError,
    TemplateImportError,
    TemplateLockedError,
    TemplateTooLargeError,
    TemplateZipInvalidError,
)
from backend.app.services.templates.strategies import TemplateKindStrategy, build_template_kind_registry
from backend.app.utils.validation import sanitize_filename
from backend.app.repositories.state import state_store
from backend.app.services.utils import TemplateLockError, acquire_template_lock
from backend.app.services.utils.artifacts import load_manifest
from backend.app.services.utils.zip_tools import detect_zip_root, extract_zip_to_dir


@dataclass
class TemplateImportContext:
    upload: UploadFile
    display_name: Optional[str]
    correlation_id: Optional[str]
    tmp_path: Optional[Path] = None
    root: Optional[str] = None
    contains_excel: bool = False
    kind: Optional[str] = None
    template_id: Optional[str] = None
    template_dir: Optional[Path] = None
    name: Optional[str] = None
    artifacts: dict = field(default_factory=dict)
    manifest: dict = field(default_factory=dict)


def _create_temp_path(*, suffix: str) -> Path:
    handle = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tmp_path = Path(handle.name)
    handle.close()
    return tmp_path


class TemplateService:
    def __init__(
        self,
        uploads_root: Path,
        excel_uploads_root: Path,
        max_bytes: int,
        *,
        max_zip_entries: int | None = None,
        max_zip_uncompressed_bytes: int | None = None,
        max_concurrency: int = 4,
        event_bus: Optional[EventBus] = None,
        kind_registry: Optional[StrategyRegistry[TemplateKindStrategy] | dict[str, TemplateKindStrategy]] = None,
    ) -> None:
        self.uploads_root = uploads_root
        self.excel_uploads_root = excel_uploads_root
        self.max_bytes = max_bytes
        self.max_zip_entries = max_zip_entries
        self.max_zip_uncompressed_bytes = max_zip_uncompressed_bytes
        self._semaphore = asyncio.Semaphore(max(1, int(max_concurrency or 1)))
        self.logger = logging.getLogger("neura.templates")
        self.event_bus = event_bus or EventBus(
            middlewares=[logging_middleware(logging.getLogger("neura.events")), metrics_middleware(logging.getLogger("neura.events"))]
        )
        if isinstance(kind_registry, StrategyRegistry):
            self.kind_registry = kind_registry
        else:
            self.kind_registry = build_template_kind_registry(self.uploads_root, self.excel_uploads_root)
            if kind_registry:
                for key, strategy in kind_registry.items():
                    self.kind_registry.register(key, strategy)

    def _normalize_display_name(
        self,
        display_name: Optional[str],
        root_name: Optional[str],
        upload_name: Optional[str],
    ) -> str:
        raw = (display_name or "").strip() or (root_name or "").strip() or (upload_name or "").strip() or "template"
        base = Path(raw).name
        base = Path(base).stem or base
        safe = sanitize_filename(base)
        if len(safe) > 100:
            safe = safe[:100].rstrip()
        return safe or "template"

    async def _write_upload(self, upload, dest: Path) -> int:
        size = 0
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            with dest.open("wb") as fh:
                while True:
                    chunk = await upload.read(1024 * 1024)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > self.max_bytes:
                        raise TemplateTooLargeError(self.max_bytes)
                    fh.write(chunk)
        except Exception:
            with contextlib.suppress(Exception):
                dest.unlink(missing_ok=True)
            raise
        finally:
            with contextlib.suppress(Exception):
                await upload.seek(0)
        return size

    async def import_zip(
        self,
        upload: UploadFile,
        display_name: Optional[str],
        correlation_id: Optional[str],
    ):
        ctx = TemplateImportContext(upload=upload, display_name=display_name, correlation_id=correlation_id)
        tmp_paths: list[Path] = []

        async def _write(ctx: TemplateImportContext) -> Result[TemplateImportContext, TemplateImportError | Exception]:
            tmp_path = _create_temp_path(suffix=".zip")
            try:
                await self._write_upload(ctx.upload, tmp_path)
            except TemplateImportError as exc:
                return err(exc)
            except Exception as exc:
                logger.exception("Template upload failed")
                return err(TemplateImportError(code="upload_failed", message="Upload failed"))
            tmp_paths.append(tmp_path)
            return ok(replace(ctx, tmp_path=tmp_path))

        def _inspect(ctx: TemplateImportContext) -> Result[TemplateImportContext, TemplateImportError]:
            if not ctx.tmp_path:
                return err(TemplateImportError(code="upload_missing", message="Temporary upload path missing"))
            try:
                with zipfile.ZipFile(ctx.tmp_path, "r") as zf:
                    members = list(zf.infolist())
                    file_members = [member for member in members if not member.is_dir()]
                    if self.max_zip_entries is not None and len(file_members) > self.max_zip_entries:
                        return err(
                            TemplateImportError(
                                code="zip_too_many_files",
                                message="Zip contains too many files",
                                detail=f"max_entries={self.max_zip_entries}",
                            )
                        )
                    if self.max_zip_uncompressed_bytes is not None:
                        total_uncompressed = sum(member.file_size for member in file_members)
                        if total_uncompressed > self.max_zip_uncompressed_bytes:
                            return err(
                                TemplateImportError(
                                    code="zip_too_large",
                                    message="Zip expands beyond allowed size",
                                    detail=f"max_uncompressed_bytes={self.max_zip_uncompressed_bytes}",
                                )
                            )
                    root = detect_zip_root(m.filename for m in members)
                    contains_excel = any(Path(m.filename).name.lower() == "source.xlsx" for m in members)
            except Exception as exc:
                logger.exception("Invalid template ZIP")
                return err(TemplateZipInvalidError(detail="Invalid ZIP archive"))
            kind = "excel" if contains_excel else "pdf"
            name = self._normalize_display_name(display_name, root, upload.filename)
            return ok(
                replace(
                    ctx,
                    root=root,
                    contains_excel=contains_excel,
                    kind=kind,
                    name=name,
                )
            )

        def _allocate(ctx: TemplateImportContext) -> Result[TemplateImportContext, TemplateImportError]:
            if not ctx.kind:
                return err(TemplateImportError(code="kind_missing", message="Unable to infer template kind"))
            strategy = self.kind_registry.resolve(ctx.kind)
            template_id = strategy.generate_id(ctx.name)
            tdir = strategy.ensure_target_dir(template_id)
            return ok(replace(ctx, template_id=template_id, template_dir=tdir))

        def _extract(ctx: TemplateImportContext) -> Result[TemplateImportContext, TemplateImportError]:
            if not ctx.template_dir or not ctx.template_id or not ctx.tmp_path:
                return err(TemplateImportError(code="missing_context", message="Template import context incomplete"))
            try:
                lock_ctx = acquire_template_lock(ctx.template_dir, "import_zip", ctx.correlation_id)
            except TemplateLockError:
                return err(TemplateLockedError())

            with lock_ctx:
                try:
                    extract_zip_to_dir(
                        ctx.tmp_path,
                        ctx.template_dir,
                        strip_root=True,
                        max_entries=self.max_zip_entries,
                        max_uncompressed_bytes=self.max_zip_uncompressed_bytes,
                    )
                except Exception as exc:
                    with contextlib.suppress(Exception):
                        for path in ctx.template_dir.rglob("*"):
                            if path.is_file():
                                path.unlink()
                    logger.exception("Template extraction failed")
                    return err(TemplateExtractionError(detail="Extraction failed"))

                manifest = load_manifest(ctx.template_dir) or {}
                artifacts = manifest.get("artifacts") or {}
                template_name = ctx.name or f"Template {ctx.template_id[:6]}"
                status = "approved" if (ctx.template_dir / "contract.json").exists() else "draft"
                state_store.upsert_template(
                    ctx.template_id,
                    name=template_name,
                    status=status,
                    artifacts=artifacts,
                    connection_id=None,
                    mapping_keys=[],
                    template_type=ctx.kind,
                )

            return ok(
                replace(
                    ctx,
                    artifacts=artifacts,
                    manifest=manifest,
                    name=template_name,
                )
            )

        async def _emit_complete(
            ctx: TemplateImportContext,
        ) -> Result[TemplateImportContext, TemplateImportError]:
            await self.event_bus.publish(
                Event(
                    name="template.imported",
                    payload={
                        "template_id": ctx.template_id,
                        "kind": ctx.kind,
                        "artifacts": list((ctx.artifacts or {}).keys()),
                    },
                    correlation_id=ctx.correlation_id,
                )
            )
            return ok(ctx)

        steps = [
            PipelineStep("write_upload", _write),
            PipelineStep("inspect_zip", _inspect),
            PipelineStep("allocate_id", _allocate),
            PipelineStep("extract_and_persist", _extract),
            PipelineStep("emit_complete", _emit_complete),
        ]

        async with self._semaphore:
            runner = PipelineRunner(
                steps,
                bus=self.event_bus,
                logger=self.logger,
                correlation_id=correlation_id,
            )
            try:
                result = await runner.run(ctx)
            finally:
                with contextlib.suppress(Exception):
                    for path in tmp_paths:
                        path.unlink(missing_ok=True)

        if result.is_err:
            error = result.unwrap_err()
            if isinstance(error, TemplateImportError):
                raise error
            logger.exception("Template import failed")
            raise TemplateImportError(code="import_failed", message="Template import failed")

        final_ctx = result.unwrap()
        return {
            "template_id": final_ctx.template_id,
            "name": final_ctx.name,
            "kind": final_ctx.kind,
            "artifacts": final_ctx.artifacts,
            "correlation_id": correlation_id,
        }

    async def export_zip(
        self,
        template_id: str,
        correlation_id: Optional[str],
    ) -> dict:
        """Export a template directory as a zip file."""
        from fastapi import HTTPException

        # Find the template in state
        template_record = state_store.get_template_record(template_id)
        if not template_record:
            raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")

        template_kind = template_record.get("kind") or template_record.get("template_type") or "pdf"
        template_name = template_record.get("name") or template_id

        # Resolve template directory
        if template_kind == "excel":
            template_dir = self.excel_uploads_root / template_id
        else:
            template_dir = self.uploads_root / template_id

        if not template_dir.exists():
            raise HTTPException(status_code=404, detail=f"Template directory not found for '{template_id}'")

        # Create a temporary zip file
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in template_name)
        zip_filename = f"{safe_name}-{template_id[:8]}.zip"
        tmp_zip_path = _create_temp_path(suffix=".zip")

        try:
            with zipfile.ZipFile(tmp_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for file_path in template_dir.rglob("*"):
                    if file_path.is_file():
                        # Skip lock files and temp files
                        if file_path.name.startswith(".") or file_path.suffix == ".lock":
                            continue
                        arcname = file_path.relative_to(template_dir)
                        zf.write(file_path, arcname)
        except Exception as exc:
            with contextlib.suppress(Exception):
                tmp_zip_path.unlink(missing_ok=True)
            self.logger.exception("template_export_zip_failed")
            raise HTTPException(status_code=500, detail="Failed to create export zip")

        self.logger.info(
            "template_exported",
            extra={
                "event": "template_exported",
                "template_id": template_id,
                "kind": template_kind,
                "zip_path": str(tmp_zip_path),
                "correlation_id": correlation_id,
            },
        )

        return {
            "zip_path": str(tmp_zip_path),
            "filename": zip_filename,
            "template_id": template_id,
            "kind": template_kind,
        }

    async def duplicate(
        self,
        template_id: str,
        new_name: Optional[str],
        correlation_id: Optional[str],
    ) -> dict:
        """Duplicate a template by copying its directory to a new ID."""
        import shutil
        from fastapi import HTTPException

        # Find the source template
        template_record = state_store.get_template_record(template_id)
        if not template_record:
            raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")

        template_kind = template_record.get("kind") or template_record.get("template_type") or "pdf"
        original_name = template_record.get("name") or template_id

        # Determine source directory
        if template_kind == "excel":
            source_dir = self.excel_uploads_root / template_id
        else:
            source_dir = self.uploads_root / template_id

        if not source_dir.exists():
            raise HTTPException(status_code=404, detail=f"Template directory not found for '{template_id}'")

        # Generate new template info
        strategy = self.kind_registry.resolve(template_kind)
        display_name = new_name or f"{original_name} (Copy)"
        new_template_id = strategy.generate_id(display_name)
        target_dir = strategy.ensure_target_dir(new_template_id)

        try:
            # Copy all files from source to target
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    # Skip lock files and temp files
                    if file_path.name.startswith(".") or file_path.suffix == ".lock":
                        continue
                    rel_path = file_path.relative_to(source_dir)
                    dest_path = target_dir / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)

            # Load manifest and artifacts
            manifest = load_manifest(target_dir) or {}
            artifacts = manifest.get("artifacts") or {}
            status = "approved" if (target_dir / "contract.json").exists() else "draft"

            # Register the new template in state
            state_store.upsert_template(
                new_template_id,
                name=display_name,
                status=status,
                artifacts=artifacts,
                connection_id=None,
                mapping_keys=[],
                template_type=template_kind,
            )

            self.logger.info(
                "template_duplicated",
                extra={
                    "event": "template_duplicated",
                    "source_id": template_id,
                    "new_id": new_template_id,
                    "kind": template_kind,
                    "correlation_id": correlation_id,
                },
            )

            return {
                "template_id": new_template_id,
                "name": display_name,
                "kind": template_kind,
                "status": status,
                "artifacts": artifacts,
                "source_id": template_id,
            }
        except Exception as exc:
            # Clean up on failure
            with contextlib.suppress(Exception):
                if target_dir.exists():
                    shutil.rmtree(target_dir)
            self.logger.exception("template_duplicate_failed")
            raise HTTPException(status_code=500, detail="Failed to duplicate template")

    async def update_tags(
        self,
        template_id: str,
        tags: list[str],
    ) -> dict:
        """Update tags for a template."""
        from fastapi import HTTPException

        template_record = state_store.get_template_record(template_id)
        if not template_record:
            raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")

        # Clean and normalize tags
        cleaned_tags = sorted(set(tag.strip().lower() for tag in tags if tag.strip()))

        # Update the template
        state_store.upsert_template(
            template_id,
            name=template_record.get("name") or template_id,
            status=template_record.get("status") or "draft",
            artifacts=template_record.get("artifacts"),
            tags=cleaned_tags,
            connection_id=template_record.get("last_connection_id"),
            mapping_keys=template_record.get("mapping_keys"),
            template_type=template_record.get("kind"),
            description=template_record.get("description"),
        )

        return {
            "template_id": template_id,
            "tags": cleaned_tags,
        }

    async def get_all_tags(self) -> dict:
        """Get all unique tags across all templates."""
        templates = state_store.list_templates()
        all_tags = set()
        tag_counts = {}

        for template in templates:
            tags = template.get("tags") or []
            for tag in tags:
                all_tags.add(tag)
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Sort tags by count (most used first), then alphabetically
        sorted_tags = sorted(all_tags, key=lambda t: (-tag_counts.get(t, 0), t))

        return {
            "tags": sorted_tags,
            "tagCounts": tag_counts,
            "total": len(sorted_tags),
        }
