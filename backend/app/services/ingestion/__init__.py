"""
Document Ingestion Service Module
Handles various document import methods including drag-drop, email, web clipper, etc.
"""
from .service import (
    IngestionService,
    ingestion_service,
)
from .email_ingestion import EmailIngestionService, email_ingestion_service
from .web_clipper import WebClipperService, web_clipper_service
from .folder_watcher import FolderWatcherService, folder_watcher_service
from .transcription import TranscriptionService, transcription_service

__all__ = [
    "IngestionService",
    "ingestion_service",
    "EmailIngestionService",
    "email_ingestion_service",
    "WebClipperService",
    "web_clipper_service",
    "FolderWatcherService",
    "folder_watcher_service",
    "TranscriptionService",
    "transcription_service",
]
