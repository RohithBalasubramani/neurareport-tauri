"""Export Schemas.

Pydantic models for document export and distribution.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from backend.app.utils.validation import is_safe_external_url


class ExportFormat(str, Enum):
    """Supported export formats."""
    PDF = "pdf"
    PDFA = "pdfa"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    EPUB = "epub"
    LATEX = "latex"
    MARKDOWN = "markdown"
    HTML = "html"
    PNG = "png"
    JPG = "jpg"
    TEXT = "text"


class DistributionChannel(str, Enum):
    """Distribution channels."""
    EMAIL = "email"
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    PORTAL = "portal"
    EMBED = "embed"


class ExportStatus(str, Enum):
    """Export job status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExportOptions(BaseModel):
    """Common export options."""
    quality: str = "high"  # low, medium, high
    include_metadata: bool = True
    include_toc: bool = False
    password: Optional[str] = None


class PDFExportOptions(ExportOptions):
    """PDF-specific export options."""
    pdfa_compliant: bool = False
    watermark: Optional[str] = None
    header: Optional[str] = None
    footer: Optional[str] = None
    page_numbers: bool = True
    compress_images: bool = True


class DocxExportOptions(ExportOptions):
    """Word document export options."""
    track_changes: bool = False
    template_path: Optional[str] = None


class PptxExportOptions(ExportOptions):
    """PowerPoint export options."""
    slide_layout: str = "title_and_content"
    include_speaker_notes: bool = False


class EpubExportOptions(ExportOptions):
    """ePub export options."""
    cover_image: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None


class LatexExportOptions(ExportOptions):
    """LaTeX export options."""
    document_class: str = "article"
    packages: list[str] = Field(default_factory=list)
    bibliography_style: Optional[str] = None


class MarkdownExportOptions(ExportOptions):
    """Markdown export options."""
    flavor: str = "gfm"  # gfm, commonmark, pandoc
    include_frontmatter: bool = True
    image_handling: str = "embed"  # embed, link, download


class ExportRequest(BaseModel):
    """Request to export a document."""
    document_id: str
    format: ExportFormat
    options: dict[str, Any] = Field(default_factory=dict)
    filename: Optional[str] = None


class BulkExportRequest(BaseModel):
    """Request to export multiple documents."""
    document_ids: list[str] = Field(..., min_length=1, max_length=100)
    format: ExportFormat
    options: dict[str, Any] = Field(default_factory=dict)
    zip_filename: Optional[str] = None


class ExportResponse(BaseModel):
    """Export response."""
    job_id: str
    status: ExportStatus
    format: ExportFormat
    document_id: str
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class DistributionRequest(BaseModel):
    """Request to distribute a document."""
    document_id: str
    channel: DistributionChannel
    recipients: list[str] = Field(default_factory=list)
    message: Optional[str] = None
    subject: Optional[str] = None
    schedule_at: Optional[datetime] = None
    options: dict[str, Any] = Field(default_factory=dict)


class EmailCampaignRequest(BaseModel):
    """Request for bulk email distribution."""
    document_ids: list[str] = Field(..., min_length=1, max_length=50)
    recipients: list[str] = Field(..., min_length=1, max_length=500)
    subject: str = Field(..., min_length=1, max_length=500)
    message: str = Field(..., max_length=10_000)
    from_name: Optional[str] = None
    reply_to: Optional[str] = None
    attach_documents: bool = True
    track_opens: bool = True


class PortalPublishRequest(BaseModel):
    """Request to publish document to portal."""
    document_id: str
    portal_path: str
    title: Optional[str] = None
    description: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    public: bool = False
    password: Optional[str] = None
    expires_at: Optional[datetime] = None


class EmbedGenerateRequest(BaseModel):
    """Request to generate embed code."""
    document_id: str
    width: int = 800
    height: int = 600
    allow_download: bool = False
    allow_print: bool = False
    show_toolbar: bool = True
    theme: str = "light"


class EmbedResponse(BaseModel):
    """Embed code response."""
    embed_code: str
    embed_url: str
    token: str
    expires_at: Optional[datetime] = None


class WebhookDeliveryRequest(BaseModel):
    """Request to deliver via webhook."""
    document_id: str
    webhook_url: str
    method: str = "POST"
    headers: dict[str, str] = Field(default_factory=dict)
    include_content: bool = True
    payload_template: Optional[str] = None

    @field_validator("webhook_url")
    @classmethod
    def validate_webhook_url(cls, v: str) -> str:
        is_safe, error = is_safe_external_url(v)
        if not is_safe:
            raise ValueError(f"Unsafe webhook URL: {error}")
        return v


class SlackMessageRequest(BaseModel):
    """Request to send to Slack."""
    document_id: str
    channel: str
    message: Optional[str] = None
    thread_ts: Optional[str] = None
    upload_file: bool = True


class TeamsMessageRequest(BaseModel):
    """Request to send to Microsoft Teams."""
    document_id: str
    webhook_url: str
    title: Optional[str] = None
    message: Optional[str] = None
    mention_users: list[str] = Field(default_factory=list)

    @field_validator("webhook_url")
    @classmethod
    def validate_webhook_url(cls, v: str) -> str:
        is_safe, error = is_safe_external_url(v)
        if not is_safe:
            raise ValueError(f"Unsafe webhook URL: {error}")
        return v


class DistributionResponse(BaseModel):
    """Distribution response."""
    job_id: str
    channel: DistributionChannel
    status: str
    recipients_count: int
    sent_at: Optional[datetime] = None
    error: Optional[str] = None
