"""
Document Ingestion API Routes
Endpoints for importing documents from various sources.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile, status
from pydantic import BaseModel, Field

from backend.app.api.middleware import limiter, RATE_LIMIT_STRICT

from backend.app.services.ingestion import (
    ingestion_service,
    email_ingestion_service,
    web_clipper_service,
    folder_watcher_service,
    transcription_service,
)
from backend.app.services.ingestion.folder_watcher import WatcherConfig
from backend.app.services.ingestion.transcription import TranscriptionLanguage
from backend.app.services.security import require_api_key
import backend.app.services.state_access as state_access

import ipaddress
from urllib.parse import urlparse
from pathlib import Path

logger = logging.getLogger(__name__)


def _validate_external_url(url: str) -> str:
    """Validate URL to prevent SSRF. Raises HTTPException if URL is unsafe."""
    try:
        parsed = urlparse(url)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid URL")

    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only HTTP/HTTPS URLs are allowed")

    if not parsed.hostname:
        raise HTTPException(status_code=400, detail="Invalid URL: no hostname")

    hostname = parsed.hostname.lower()

    # Block localhost and common internal hostnames
    blocked_hosts = {"localhost", "127.0.0.1", "0.0.0.0", "::1", "[::1]", "metadata.google.internal"}
    if hostname in blocked_hosts:
        raise HTTPException(status_code=400, detail="URL points to a restricted address")

    # Resolve hostname and check for private IPs
    try:
        import socket
        resolved = socket.getaddrinfo(hostname, None)
        for _, _, _, _, addr in resolved:
            ip = ipaddress.ip_address(addr[0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                raise HTTPException(status_code=400, detail="URL points to a restricted address")
    except socket.gaierror:
        raise HTTPException(status_code=400, detail="Could not resolve URL hostname")
    except HTTPException:
        raise
    except Exception:
        logger.warning("URL validation failed unexpectedly")
        raise HTTPException(status_code=400, detail="URL validation failed")

    return url


router = APIRouter(dependencies=[Depends(require_api_key)])

# Maximum upload sizes
MAX_SINGLE_FILE_BYTES = 200 * 1024 * 1024  # 200 MB
MAX_BULK_TOTAL_BYTES = 500 * 1024 * 1024   # 500 MB total for bulk


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class IngestUrlRequest(BaseModel):
    url: str = Field(..., description="URL to download and ingest")
    filename: Optional[str] = Field(default=None, description="Override filename")


class IngestStructuredDataRequest(BaseModel):
    filename: str = Field(..., description="File name with extension")
    content: str = Field(..., description="File content (JSON/XML/YAML)")
    format_hint: Optional[str] = Field(default=None, description="Format hint")


class ClipUrlRequest(BaseModel):
    url: str = Field(..., description="URL to clip")
    include_images: bool = Field(default=True, description="Include images")
    clean_content: bool = Field(default=True, description="Clean HTML")
    output_format: str = Field(default="html", description="Output format")


class ClipSelectionRequest(BaseModel):
    url: str = Field(..., description="Source URL")
    selected_html: str = Field(..., description="Selected HTML content")
    page_title: Optional[str] = Field(default=None, description="Page title")


class CreateWatcherRequest(BaseModel):
    path: str = Field(..., description="Folder path to watch")
    recursive: bool = Field(default=True, description="Watch subdirectories")
    patterns: List[str] = Field(default=["*"], description="File patterns to match")
    ignore_patterns: List[str] = Field(default_factory=list, description="Patterns to ignore")
    auto_import: bool = Field(default=True, description="Auto-import files")
    delete_after_import: bool = Field(default=False, description="Delete after import")
    target_collection: Optional[str] = Field(default=None, description="Target collection")
    tags: List[str] = Field(default_factory=list, description="Tags to apply")


class TranscribeRequest(BaseModel):
    language: str = Field(default="auto", description="Language code or 'auto'")
    include_timestamps: bool = Field(default=True, description="Include timestamps")
    diarize_speakers: bool = Field(default=False, description="Identify speakers")


class ImapConnectRequest(BaseModel):
    host: str = Field(..., description="IMAP server hostname")
    port: int = Field(default=993, description="IMAP server port")
    username: str = Field(..., description="Account username")
    password: str = Field(..., description="Account password")
    use_ssl: bool = Field(default=True, description="Use SSL/TLS")
    folder: str = Field(default="INBOX", description="Mailbox folder to monitor")


class EmailIngestRequest(BaseModel):
    include_attachments: bool = Field(default=True, description="Process attachments")


class GenerateInboxRequest(BaseModel):
    purpose: str = Field(default="default", description="Inbox purpose label")


# =============================================================================
# FILE INGESTION ENDPOINTS
# =============================================================================

@router.post("/upload")
@limiter.limit(RATE_LIMIT_STRICT)
async def upload_file(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    auto_ocr: bool = Form(default=True),
    generate_preview: bool = Form(default=True),
    tags: str = Form(default=""),
    collection: str = Form(default=""),
):
    """
    Upload and ingest a file with auto-detection.

    Returns:
        IngestionResult with document details
    """
    try:
        content = await file.read()
        if len(content) > MAX_SINGLE_FILE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum size of {MAX_SINGLE_FILE_BYTES // (1024*1024)} MB",
            )
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty",
            )

        metadata = {}
        if tags:
            metadata["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
        if collection:
            metadata["collection"] = collection

        result = await ingestion_service.ingest_file(
            filename=file.filename or "upload",
            content=content,
            metadata=metadata,
            auto_ocr=auto_ocr,
            generate_preview=generate_preview,
        )
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Upload failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Upload failed",
        )


@router.post("/upload/bulk")
@limiter.limit(RATE_LIMIT_STRICT)
async def upload_bulk(
    request: Request,
    response: Response,
    files: List[UploadFile] = File(...),
    tags: str = Form(default=""),
    collection: str = Form(default=""),
):
    """
    Upload multiple files at once.

    Returns:
        List of IngestionResults
    """
    results = []
    errors = []
    cumulative_bytes = 0

    metadata = {}
    if tags:
        metadata["tags"] = [t.strip() for t in tags.split(",")]
    if collection:
        metadata["collection"] = collection

    for file in files:
        try:
            content = await file.read()
            cumulative_bytes += len(content)
            if cumulative_bytes > MAX_BULK_TOTAL_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Bulk upload exceeds maximum total size of {MAX_BULK_TOTAL_BYTES // (1024*1024)} MB",
                )
            result = await ingestion_service.ingest_file(
                filename=file.filename or "upload",
                content=content,
                metadata=metadata,
            )
            results.append(result.model_dump())
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Bulk upload processing failed for %s: %s", file.filename, e)
            errors.append({"filename": file.filename, "error": "Processing failed"})

    return {
        "total": len(files),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
    }


@router.post("/upload/zip")
@limiter.limit(RATE_LIMIT_STRICT)
async def upload_zip(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    preserve_structure: bool = Form(default=True),
    flatten: bool = Form(default=False),
):
    """
    Upload and extract a ZIP archive.

    Returns:
        BulkIngestionResult with all extracted documents
    """
    try:
        content = await file.read()
        if len(content) > MAX_SINGLE_FILE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"ZIP file exceeds maximum size of {MAX_SINGLE_FILE_BYTES // (1024*1024)} MB",
            )
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded ZIP file is empty",
            )
        result = await ingestion_service.ingest_zip_archive(
            filename=file.filename or "archive.zip",
            content=content,
            preserve_structure=preserve_structure,
            flatten=flatten,
        )
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("ZIP upload failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ZIP upload failed",
        )


@router.post("/url")
async def ingest_from_url(request: IngestUrlRequest):
    """
    Download and ingest a file from a URL.

    Returns:
        IngestionResult with document details
    """
    try:
        _validate_external_url(request.url)
        result = await ingestion_service.ingest_from_url(
            url=request.url,
            filename=request.filename,
        )
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("URL ingestion failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="URL ingestion failed",
        )


@router.post("/structured")
async def ingest_structured_data(request: IngestStructuredDataRequest):
    """
    Import structured data (JSON/XML/YAML) as an editable table.

    Returns:
        StructuredDataImport with table details
    """
    try:
        result = await ingestion_service.import_structured_data(
            filename=request.filename,
            content=request.content.encode("utf-8"),
            format_hint=request.format_hint,
        )
        return result.model_dump()
    except Exception as e:
        logger.exception("Structured data import failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Structured data import failed",
        )


# =============================================================================
# WEB CLIPPER ENDPOINTS
# =============================================================================

@router.post("/clip/url")
async def clip_web_page(request: ClipUrlRequest):
    """
    Clip content from a web page.

    Returns:
        ClippedContent with extracted content
    """
    try:
        _validate_external_url(request.url)
        clipped = await web_clipper_service.clip_url(
            url=request.url,
            include_images=request.include_images,
            clean_content=request.clean_content,
        )

        # Save as document
        doc_id = await web_clipper_service.save_as_document(
            clipped=clipped,
            format=request.output_format,
        )

        result = clipped.model_dump()
        result["document_id"] = doc_id
        return result
    except Exception as e:
        logger.exception("Web clip failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Web clip failed",
        )


@router.post("/clip/selection")
async def clip_selection(request: ClipSelectionRequest):
    """
    Clip a user-selected portion of a page.

    Returns:
        ClippedContent with selected content
    """
    try:
        _validate_external_url(request.url)
        clipped = await web_clipper_service.clip_selection(
            url=request.url,
            selected_html=request.selected_html,
            page_title=request.page_title,
        )

        doc_id = await web_clipper_service.save_as_document(clipped)

        result = clipped.model_dump()
        result["document_id"] = doc_id
        return result
    except Exception as e:
        logger.exception("Selection clip failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Selection clip failed",
        )


# =============================================================================
# FOLDER WATCHER ENDPOINTS
# =============================================================================

@router.post("/watchers")
async def create_folder_watcher(request: CreateWatcherRequest):
    """
    Create a new folder watcher.

    Returns:
        WatcherStatus
    """
    import hashlib
    from datetime import datetime, timezone

    watcher_path = Path(request.path).resolve()
    if not str(watcher_path).startswith(str(Path.cwd())):
        raise HTTPException(status_code=400, detail="Watcher path must be within the application directory")

    watcher_id = hashlib.sha256(f"{request.path}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:12]

    config = WatcherConfig(
        watcher_id=watcher_id,
        path=request.path,
        recursive=request.recursive,
        patterns=request.patterns,
        ignore_patterns=request.ignore_patterns,
        auto_import=request.auto_import,
        delete_after_import=request.delete_after_import,
        target_collection=request.target_collection,
        tags=request.tags,
    )

    try:
        watcher_status = await folder_watcher_service.create_watcher(config)
        return watcher_status.model_dump()
    except Exception as e:
        logger.exception("Failed to create watcher: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create watcher",
        )


@router.get("/watchers")
async def list_folder_watchers():
    """
    List all folder watchers.

    Returns:
        List of WatcherStatus
    """
    watchers = folder_watcher_service.list_watchers()
    return [w.model_dump() for w in watchers]


@router.get("/watchers/{watcher_id}")
async def get_watcher_status(watcher_id: str):
    """
    Get status of a folder watcher.

    Returns:
        WatcherStatus
    """
    try:
        watcher_info = folder_watcher_service.get_status(watcher_id)
        return watcher_info.model_dump()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watcher not found")


@router.post("/watchers/{watcher_id}/start")
async def start_watcher(watcher_id: str):
    """Start a folder watcher."""
    try:
        success = await folder_watcher_service.start_watcher(watcher_id)
        return {"success": success}
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watcher not found")


@router.post("/watchers/{watcher_id}/stop")
async def stop_watcher(watcher_id: str):
    """Stop a folder watcher."""
    success = await folder_watcher_service.stop_watcher(watcher_id)
    return {"success": success}


@router.post("/watchers/{watcher_id}/scan")
async def scan_watched_folder(watcher_id: str):
    """
    Manually scan a watched folder for existing files.

    Returns:
        List of FileEvents
    """
    try:
        events = await folder_watcher_service.scan_folder(watcher_id)
        return [e.model_dump() for e in events]
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watcher not found")


@router.delete("/watchers/{watcher_id}")
async def delete_watcher(watcher_id: str):
    """Delete a folder watcher."""
    success = await folder_watcher_service.delete_watcher(watcher_id)
    return {"success": success}


# =============================================================================
# TRANSCRIPTION ENDPOINTS
# =============================================================================

@router.post("/transcribe")
@limiter.limit(RATE_LIMIT_STRICT)
async def transcribe_file(
    request: Request,
    file: UploadFile = File(...),
    language: str = Form(default="auto"),
    include_timestamps: bool = Form(default=True),
    diarize_speakers: bool = Form(default=False),
    output_format: str = Form(default="html"),
):
    """
    Transcribe an audio or video file.

    Returns:
        TranscriptionResult with full transcript
    """
    try:
        content = await file.read()

        lang = TranscriptionLanguage(language) if language in [l.value for l in TranscriptionLanguage] else TranscriptionLanguage.AUTO

        result = await transcription_service.transcribe_file(
            filename=file.filename or "recording",
            content=content,
            language=lang,
            include_timestamps=include_timestamps,
            diarize_speakers=diarize_speakers,
        )

        # Create document
        doc_id = await transcription_service.create_document_from_transcription(
            result=result,
            format=output_format,
            include_timestamps=include_timestamps,
        )

        response = result.model_dump()
        response["document_id"] = doc_id
        return response
    except Exception as e:
        logger.exception("Transcription failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transcription failed",
        )


@router.post("/transcribe/voice-memo")
async def transcribe_voice_memo(
    file: UploadFile = File(...),
    extract_action_items: bool = Form(default=True),
    extract_key_points: bool = Form(default=True),
):
    """
    Transcribe a voice memo with intelligent extraction.

    Returns:
        VoiceMemoResult with transcript and extracted items
    """
    try:
        content = await file.read()

        result = await transcription_service.transcribe_voice_memo(
            filename=file.filename or "voice_memo",
            content=content,
            extract_action_items=extract_action_items,
            extract_key_points=extract_key_points,
        )
        return result.model_dump()
    except Exception as e:
        logger.exception("Voice memo transcription failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Voice memo transcription failed",
        )


@router.get("/transcribe/{job_id}")
async def get_transcription_status(job_id: str):
    """
    Get the status of a transcription job.

    Returns:
        Job status, progress, and result when complete
    """
    job = state_access.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcription job not found",
        )
    return {
        "job_id": job_id,
        "status": job.get("status"),
        "progress": job.get("progress"),
        "result": job.get("result"),
    }


# =============================================================================
# EMAIL IMAP ENDPOINTS
# =============================================================================

@router.post("/email/imap/connect")
async def connect_imap_account(request: ImapConnectRequest):
    """
    Connect an IMAP email account.

    Tests the connection and stores the account configuration.

    Returns:
        Connection result with account ID
    """
    try:
        result = await email_ingestion_service.connect_imap(
            host=request.host,
            port=request.port,
            username=request.username,
            password=request.password,
            use_ssl=request.use_ssl,
            folder=request.folder,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("IMAP connection failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="IMAP connection failed",
        )


@router.get("/email/imap/accounts")
async def list_imap_accounts():
    """
    List connected IMAP email accounts.

    Returns:
        List of connected IMAP accounts
    """
    try:
        accounts = email_ingestion_service.list_imap_accounts()
        return [a if isinstance(a, dict) else a.model_dump() for a in accounts]
    except Exception as e:
        logger.exception("Failed to list IMAP accounts: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list IMAP accounts",
        )


@router.post("/email/imap/accounts/{account_id}/sync")
async def sync_imap_account(account_id: str):
    """
    Sync emails from an IMAP account.

    Triggers email synchronisation for the specified account.

    Returns:
        Sync job status
    """
    try:
        result = await email_ingestion_service.sync_imap_account(account_id)
        return result
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IMAP account not found",
        )
    except Exception as e:
        logger.exception("IMAP sync failed for account %s: %s", account_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="IMAP sync failed",
        )


# =============================================================================
# EMAIL INGESTION ENDPOINTS
# =============================================================================

@router.post("/email/inbox")
async def generate_inbox_address(request: GenerateInboxRequest, user_id: str = "default"):
    """
    Generate a unique email inbox address for forwarding.

    Returns:
        Email address for forwarding
    """
    address = email_ingestion_service.generate_inbox_address(
        user_id=user_id,
        purpose=request.purpose,
    )
    return {"inbox_address": address}


@router.post("/email/ingest")
async def ingest_email(
    file: UploadFile = File(...),
    include_attachments: bool = Form(default=True),
):
    """
    Ingest a raw email file (.eml).

    Returns:
        EmailDocumentResult with created document
    """
    try:
        content = await file.read()

        result = await email_ingestion_service.convert_email_to_document(
            raw_email=content,
            include_attachments=include_attachments,
        )
        return result.model_dump()
    except Exception as e:
        logger.exception("Email ingestion failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email ingestion failed",
        )


@router.post("/email/parse")
async def parse_email(
    file: UploadFile = File(...),
    extract_action_items: bool = Form(default=True),
):
    """
    Parse an email and extract structured data.

    Returns:
        Parsed email with action items and links
    """
    try:
        content = await file.read()

        result = await email_ingestion_service.parse_incoming_email(
            raw_email=content,
            extract_action_items=extract_action_items,
        )
        return result
    except Exception as e:
        logger.exception("Email parsing failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email parsing failed",
        )


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@router.post("/detect-type")
async def detect_file_type(file: UploadFile = File(...)):
    """
    Detect the type of an uploaded file.

    Returns:
        Detected file type and metadata
    """
    content = await file.read()
    file_type = ingestion_service.detect_file_type(
        filename=file.filename or "unknown",
        content=content,
    )
    return {
        "filename": file.filename,
        "detected_type": file_type.value,
        "size_bytes": len(content),
    }


@router.get("/supported-types")
async def list_supported_types():
    """
    List all supported file types for ingestion.

    Returns:
        List of supported file types
    """
    from backend.app.services.ingestion.service import FileType

    return {
        "file_types": [t.value for t in FileType if t != FileType.UNKNOWN],
        "transcription_languages": [l.value for l in TranscriptionLanguage],
    }
