"""
Document Service - Core document editing operations.
"""

from __future__ import annotations

import json
import logging
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel

from backend.app.schemas.documents.document import DocumentContent as SchemaDocumentContent

from backend.app.services.config import get_settings

logger = logging.getLogger("neura.documents")


def _utcnow() -> datetime:
    """Get current UTC time with timezone info."""
    return datetime.now(timezone.utc)


DocumentContent = SchemaDocumentContent


class Document(BaseModel):
    """Document model."""

    id: str
    name: str
    content: DocumentContent | dict[str, Any]
    content_type: str = "tiptap"  # tiptap, html, markdown
    version: int = 1
    created_at: str
    updated_at: str
    owner_id: Optional[str] = None
    is_template: bool = False
    track_changes_enabled: bool = False
    collaboration_enabled: bool = False
    tags: list[str] = []
    metadata: dict[str, Any] = {}


class DocumentVersion(BaseModel):
    """Document version for history tracking."""

    id: str
    document_id: str
    version: int
    content: DocumentContent | dict[str, Any]
    created_at: str
    created_by: Optional[str] = None
    change_summary: Optional[str] = None


class DocumentComment(BaseModel):
    """Document comment model."""

    id: str
    document_id: str
    selection_start: int
    selection_end: int
    text: str
    author_id: Optional[str] = None
    author_name: Optional[str] = None
    created_at: str
    resolved: bool = False
    replies: list["DocumentComment"] = []


class DocumentService:
    """Service for document CRUD operations."""

    def __init__(self, state_store=None, uploads_root: Optional[Path] = None):
        self._state_store = state_store
        base_root = get_settings().uploads_root
        self._uploads_root = uploads_root or (base_root / "documents")
        self._uploads_root.mkdir(parents=True, exist_ok=True)
        # Lock for file operations to prevent race conditions
        self._lock = threading.Lock()

    def _normalize_content(self, content: Optional[Any]) -> dict[str, Any]:
        """Normalize incoming content payloads to a plain dict."""
        if content is None:
            return {"type": "doc", "content": []}
        if isinstance(content, DocumentContent):
            return content.model_dump()
        if hasattr(content, "model_dump"):
            return content.model_dump()
        if isinstance(content, dict):
            return content
        return {"type": "doc", "content": []}

    def create(
        self,
        name: str,
        content: Optional[DocumentContent] = None,
        owner_id: Optional[str] = None,
        is_template: bool = False,
        metadata: Optional[dict] = None,
    ) -> Document:
        """Create a new document."""
        now = _utcnow().isoformat()
        doc = Document(
            id=str(uuid.uuid4()),
            name=name,
            content=self._normalize_content(content),
            created_at=now,
            updated_at=now,
            owner_id=owner_id,
            is_template=is_template,
            metadata=metadata or {},
        )
        with self._lock:
            self._save_document(doc)
        logger.info(f"Created document: {doc.id}")
        return doc

    def get(self, document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        doc_path = self._get_document_path(document_id)
        if not doc_path:
            return None
        with self._lock:
            if not doc_path.exists():
                return None
            try:
                with open(doc_path, encoding="utf-8") as f:
                    data = json.load(f)
            except FileNotFoundError:
                return None
        return Document(**data)

    def update(
        self,
        document_id: str,
        name: Optional[str] = None,
        content: Optional[DocumentContent] = None,
        metadata: Optional[dict] = None,
        create_version: bool = True,
    ) -> Optional[Document]:
        """Update an existing document."""
        with self._lock:
            doc = self._get_unlocked(document_id)
            if not doc:
                return None

            # Create version snapshot before update
            if create_version:
                self._create_version(doc)

            # Update fields
            if name is not None:
                doc.name = name
            if content is not None:
                doc.content = DocumentContent(**self._normalize_content(content))
            if metadata is not None:
                doc.metadata.update(metadata)

            doc.updated_at = _utcnow().isoformat()
            doc.version += 1

            self._save_document(doc)
            logger.info(f"Updated document: {doc.id} to version {doc.version}")
            return doc

    def _get_unlocked(self, document_id: str) -> Optional[Document]:
        """Get document without acquiring lock (for internal use when lock is held)."""
        doc_path = self._get_document_path(document_id)
        if not doc_path or not doc_path.exists():
            return None
        with open(doc_path, encoding="utf-8") as f:
            data = json.load(f)
        return Document(**data)

    def delete(self, document_id: str) -> bool:
        """Delete a document."""
        with self._lock:
            doc_path = self._get_document_path(document_id)
            if not doc_path or not doc_path.exists():
                return False
            doc_path.unlink()
            # Also delete versions and comments
            doc_dir = self._get_document_dir(document_id)
            if doc_dir and doc_dir.exists():
                import shutil
                # Delete versions subdirectory
                versions_dir = doc_dir / "versions"
                if versions_dir.exists():
                    shutil.rmtree(versions_dir)
                # Delete comments subdirectory
                comments_dir = doc_dir / "comments"
                if comments_dir.exists():
                    shutil.rmtree(comments_dir)
            logger.info(f"Deleted document: {document_id}")
            return True

    def list_documents(
        self,
        owner_id: Optional[str] = None,
        is_template: Optional[bool] = None,
        tags: Optional[list[str]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Document], int]:
        """List documents with optional filters."""
        documents = []
        # Collect file paths first under lock to avoid concurrent modification issues
        with self._lock:
            doc_files = list(self._uploads_root.glob("**/document.json"))

        for doc_file in doc_files:
            try:
                with open(doc_file, encoding="utf-8") as f:
                    data = json.load(f)
                doc = Document(**data)

                # Apply filters
                if owner_id and doc.owner_id != owner_id:
                    continue
                if is_template is not None and doc.is_template != is_template:
                    continue
                if tags and not any(t in doc.tags for t in tags):
                    continue

                documents.append(doc)
            except FileNotFoundError:
                # File was deleted between glob and read - skip it
                continue
            except Exception as e:
                logger.warning(f"Error loading document from {doc_file}: {e}")

        # Sort by updated_at descending
        documents.sort(key=lambda d: d.updated_at, reverse=True)
        return documents[offset:offset + limit], len(documents)

    def get_versions(self, document_id: str) -> list[DocumentVersion]:
        """Get all versions of a document."""
        versions_root = self._get_document_dir(document_id)
        if not versions_root:
            return []
        versions_dir = versions_root / "versions"
        if not versions_dir.exists():
            return []

        versions = []
        for version_file in versions_dir.glob("*.json"):
            try:
                with open(version_file, encoding="utf-8") as f:
                    data = json.load(f)
                versions.append(DocumentVersion(**data))
            except Exception as e:
                logger.warning(f"Error loading version from {version_file}: {e}")

        versions.sort(key=lambda v: v.version, reverse=True)
        return versions

    def add_comment(
        self,
        document_id: str,
        selection_start: int,
        selection_end: int,
        text: str,
        author_id: Optional[str] = None,
        author_name: Optional[str] = None,
    ) -> Optional[DocumentComment]:
        """Add a comment to a document."""
        with self._lock:
            doc = self._get_unlocked(document_id)
            if not doc:
                return None

            comment = DocumentComment(
                id=str(uuid.uuid4()),
                document_id=document_id,
                selection_start=selection_start,
                selection_end=selection_end,
                text=text,
                author_id=author_id,
                author_name=author_name,
                created_at=_utcnow().isoformat(),
            )

            self._save_comment(comment)
            logger.info(f"Added comment {comment.id} to document {document_id}")
            return comment

    def get_comments(self, document_id: str) -> list[DocumentComment]:
        """Get all comments for a document."""
        comments_root = self._get_document_dir(document_id)
        if not comments_root:
            return []
        comments_dir = comments_root / "comments"
        if not comments_dir.exists():
            return []

        comments = []
        for comment_file in comments_dir.glob("*.json"):
            try:
                with open(comment_file, encoding="utf-8") as f:
                    data = json.load(f)
                comments.append(DocumentComment(**data))
            except Exception as e:
                logger.warning(f"Error loading comment from {comment_file}: {e}")

        comments.sort(key=lambda c: c.created_at)
        return comments

    def resolve_comment(self, document_id: str, comment_id: str) -> bool:
        """Mark a comment as resolved."""
        comments = self.get_comments(document_id)
        for comment in comments:
            if comment.id == comment_id:
                comment.resolved = True
                self._save_comment(comment)
                return True
        return False

    def delete_comment(self, document_id: str, comment_id: str) -> bool:
        """Delete a comment from a document."""
        with self._lock:
            comments_dir = self._uploads_root / document_id / "comments"
            if not comments_dir.exists():
                return False
            comment_path = comments_dir / f"{comment_id}.json"
            if not comment_path.exists():
                return False
            comment_path.unlink()
            logger.info(f"Deleted comment {comment_id} from document {document_id}")
            return True

    def _get_document_path(self, document_id: str) -> Optional[Path]:
        """Get path to document JSON file."""
        doc_dir = self._get_document_dir(document_id)
        if not doc_dir:
            return None
        return doc_dir / "document.json"

    def _get_document_dir(self, document_id: str) -> Optional[Path]:
        normalized = self._normalize_id(document_id)
        if not normalized:
            return None
        return self._uploads_root / normalized

    def _normalize_id(self, document_id: str) -> Optional[str]:
        try:
            return str(uuid.UUID(str(document_id)))
        except (ValueError, TypeError):
            return None

    def _save_document(self, doc: Document) -> None:
        """Save document to disk."""
        doc_dir = self._uploads_root / doc.id
        doc_dir.mkdir(parents=True, exist_ok=True)
        doc_path = doc_dir / "document.json"
        with open(doc_path, "w", encoding="utf-8") as f:
            json.dump(doc.model_dump(), f, indent=2, ensure_ascii=False)

    def _create_version(self, doc: Document) -> DocumentVersion:
        """Create a version snapshot of a document."""
        version = DocumentVersion(
            id=str(uuid.uuid4()),
            document_id=doc.id,
            version=doc.version,
            content=doc.content,
            created_at=_utcnow().isoformat(),
        )

        versions_dir = self._uploads_root / doc.id / "versions"
        versions_dir.mkdir(parents=True, exist_ok=True)
        version_path = versions_dir / f"v{doc.version}.json"
        with open(version_path, "w", encoding="utf-8") as f:
            json.dump(version.model_dump(), f, indent=2, ensure_ascii=False)

        return version

    def _save_comment(self, comment: DocumentComment) -> None:
        """Save comment to disk."""
        comments_dir = self._uploads_root / comment.document_id / "comments"
        comments_dir.mkdir(parents=True, exist_ok=True)
        comment_path = comments_dir / f"{comment.id}.json"
        with open(comment_path, "w", encoding="utf-8") as f:
            json.dump(comment.model_dump(), f, indent=2, ensure_ascii=False)
