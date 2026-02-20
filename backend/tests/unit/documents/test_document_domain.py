"""
Document Domain Tests - Testing Document, DocumentVersion, DocumentComment models.
"""

import os
import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError


from backend.app.services.documents.service import (
    Document,
    DocumentVersion,
    DocumentComment,
)
from backend.app.services.documents.pdf_operations import (
    PageInfo,
    WatermarkConfig,
    RedactionRegion,
    PDFMergeResult,
)
from backend.app.services.documents.collaboration import (
    CollaborationSession,
    CollaboratorPresence,
)
from backend.app.schemas.documents.document import (
    DocumentContent,
    CreateDocumentRequest,
    UpdateDocumentRequest,
    CommentRequest,
    PDFReorderRequest,
    PDFWatermarkRequest,
    RedactionRegion as SchemaRedactionRegion,
    PDFRedactRequest,
)


class TestDocumentModel:
    """Test Document model validation and behavior."""

    def test_create_document_with_required_fields(self):
        """Document should be created with required fields."""
        doc = Document(
            id=str(uuid.uuid4()),
            name="Test Document",
            content={"type": "doc", "content": []},
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        assert doc.name == "Test Document"
        assert doc.version == 1
        assert doc.content_type == "tiptap"
        assert doc.is_template is False
        assert doc.tags == []

    def test_document_default_values(self):
        """Document should have correct default values."""
        doc = Document(
            id=str(uuid.uuid4()),
            name="Test",
            content={"type": "doc", "content": []},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        assert doc.version == 1
        assert doc.content_type == "tiptap"
        assert doc.owner_id is None
        assert doc.is_template is False
        assert doc.track_changes_enabled is False
        assert doc.collaboration_enabled is False
        assert doc.tags == []
        assert doc.metadata == {}

    def test_document_with_all_fields(self):
        """Document should accept all optional fields."""
        doc = Document(
            id=str(uuid.uuid4()),
            name="Full Document",
            content={"type": "doc", "content": [{"type": "paragraph"}]},
            content_type="markdown",
            version=5,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-02T00:00:00Z",
            owner_id="user-123",
            is_template=True,
            track_changes_enabled=True,
            collaboration_enabled=True,
            tags=["tag1", "tag2"],
            metadata={"key": "value"},
        )
        assert doc.content_type == "markdown"
        assert doc.version == 5
        assert doc.owner_id == "user-123"
        assert doc.is_template is True
        assert doc.track_changes_enabled is True
        assert doc.collaboration_enabled is True
        assert "tag1" in doc.tags
        assert doc.metadata["key"] == "value"

    def test_document_model_dump(self):
        """Document model_dump should serialize correctly."""
        doc = Document(
            id="doc-123",
            name="Test",
            content={"type": "doc", "content": []},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        data = doc.model_dump()
        assert data["id"] == "doc-123"
        assert data["name"] == "Test"
        assert isinstance(data["content"], dict)

    def test_document_content_with_nested_structure(self):
        """Document should handle nested content structure."""
        content = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [{"type": "text", "text": "Title"}],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Hello "},
                        {"type": "text", "marks": [{"type": "bold"}], "text": "world"},
                    ],
                },
            ],
        }
        doc = Document(
            id=str(uuid.uuid4()),
            name="Rich Content",
            content=content,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        # Content may be DocumentContent model or dict
        c = doc.content if isinstance(doc.content, dict) else doc.content.model_dump()
        assert c["content"][0]["type"] == "heading"
        assert c["content"][1]["content"][1]["marks"][0]["type"] == "bold"

    def test_document_empty_name_rejected(self):
        """Document with empty name should be rejected by schema validation."""
        # Note: Document model itself doesn't validate min_length,
        # but CreateDocumentRequest schema does
        request = CreateDocumentRequest
        with pytest.raises(ValidationError):
            request(name="")

    def test_document_preserves_unicode_content(self):
        """Document should preserve unicode characters."""
        doc = Document(
            id=str(uuid.uuid4()),
            name="日本語ドキュメント",
            content={"type": "doc", "content": [{"type": "text", "text": "こんにちは世界"}]},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        assert "日本語" in doc.name
        assert "こんにちは" in str(doc.content)


class TestDocumentVersionModel:
    """Test DocumentVersion model."""

    def test_create_version_with_required_fields(self):
        """Version should be created with required fields."""
        version = DocumentVersion(
            id=str(uuid.uuid4()),
            document_id="doc-123",
            version=1,
            content={"type": "doc", "content": []},
            created_at="2024-01-01T00:00:00Z",
        )
        assert version.document_id == "doc-123"
        assert version.version == 1
        assert version.created_by is None
        assert version.change_summary is None

    def test_version_with_optional_fields(self):
        """Version should accept optional fields."""
        version = DocumentVersion(
            id=str(uuid.uuid4()),
            document_id="doc-123",
            version=2,
            content={"type": "doc", "content": []},
            created_at="2024-01-01T00:00:00Z",
            created_by="user-456",
            change_summary="Updated formatting",
        )
        assert version.created_by == "user-456"
        assert version.change_summary == "Updated formatting"

    def test_version_preserves_content(self):
        """Version should preserve complete content."""
        content = {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Original"}]}]}
        version = DocumentVersion(
            id=str(uuid.uuid4()),
            document_id="doc-123",
            version=1,
            content=content,
            created_at="2024-01-01T00:00:00Z",
        )
        # Content may be coerced to DocumentContent model
        c = version.content if isinstance(version.content, dict) else version.content.model_dump()
        assert c == content


class TestDocumentCommentModel:
    """Test DocumentComment model."""

    def test_create_comment_with_required_fields(self):
        """Comment should be created with required fields."""
        comment = DocumentComment(
            id=str(uuid.uuid4()),
            document_id="doc-123",
            selection_start=0,
            selection_end=10,
            text="This is a comment",
            created_at="2024-01-01T00:00:00Z",
        )
        assert comment.selection_start == 0
        assert comment.selection_end == 10
        assert comment.text == "This is a comment"
        assert comment.resolved is False
        assert comment.replies == []

    def test_comment_with_author_info(self):
        """Comment should accept author information."""
        comment = DocumentComment(
            id=str(uuid.uuid4()),
            document_id="doc-123",
            selection_start=5,
            selection_end=15,
            text="Review this section",
            author_id="user-123",
            author_name="John Doe",
            created_at="2024-01-01T00:00:00Z",
        )
        assert comment.author_id == "user-123"
        assert comment.author_name == "John Doe"

    def test_comment_with_replies(self):
        """Comment should support nested replies."""
        reply = DocumentComment(
            id=str(uuid.uuid4()),
            document_id="doc-123",
            selection_start=5,
            selection_end=15,
            text="Good point",
            created_at="2024-01-01T01:00:00Z",
        )
        comment = DocumentComment(
            id=str(uuid.uuid4()),
            document_id="doc-123",
            selection_start=5,
            selection_end=15,
            text="Original comment",
            created_at="2024-01-01T00:00:00Z",
            replies=[reply],
        )
        assert len(comment.replies) == 1
        assert comment.replies[0].text == "Good point"

    def test_comment_resolved_state(self):
        """Comment resolved state should be settable."""
        comment = DocumentComment(
            id=str(uuid.uuid4()),
            document_id="doc-123",
            selection_start=0,
            selection_end=10,
            text="Fix typo",
            created_at="2024-01-01T00:00:00Z",
            resolved=True,
        )
        assert comment.resolved is True


class TestPageInfoModel:
    """Test PageInfo model for PDF operations."""

    def test_create_page_info(self):
        """PageInfo should be created with all fields."""
        info = PageInfo(
            page_number=0,
            width=612.0,
            height=792.0,
            rotation=0,
        )
        assert info.page_number == 0
        assert info.width == 612.0
        assert info.height == 792.0
        assert info.rotation == 0

    def test_page_info_with_rotation(self):
        """PageInfo should support rotation values."""
        info = PageInfo(
            page_number=1,
            width=792.0,
            height=612.0,
            rotation=90,
        )
        assert info.rotation == 90


class TestWatermarkConfigModel:
    """Test WatermarkConfig model."""

    def test_watermark_defaults(self):
        """WatermarkConfig should have sensible defaults."""
        config = WatermarkConfig(text="CONFIDENTIAL")
        assert config.text == "CONFIDENTIAL"
        assert config.position == "center"
        assert config.font_size == 48
        assert config.opacity == 0.3
        assert config.color == "#808080"
        assert config.rotation == -45

    def test_watermark_custom_values(self):
        """WatermarkConfig should accept custom values."""
        config = WatermarkConfig(
            text="DRAFT",
            position="diagonal",
            font_size=72,
            opacity=0.5,
            color="#FF0000",
            rotation=-30,
        )
        assert config.text == "DRAFT"
        assert config.position == "diagonal"
        assert config.font_size == 72
        assert config.opacity == 0.5
        assert config.color == "#FF0000"
        assert config.rotation == -30


class TestRedactionRegionModel:
    """Test RedactionRegion model."""

    def test_create_redaction_region(self):
        """RedactionRegion should be created with coordinates."""
        region = RedactionRegion(
            page=0,
            x=100,
            y=200,
            width=150,
            height=50,
        )
        assert region.page == 0
        assert region.x == 100
        assert region.y == 200
        assert region.width == 150
        assert region.height == 50
        assert region.color == "#000000"

    def test_redaction_custom_color(self):
        """RedactionRegion should accept custom color."""
        region = RedactionRegion(
            page=1,
            x=50,
            y=100,
            width=200,
            height=30,
            color="#FFFFFF",
        )
        assert region.color == "#FFFFFF"


class TestPDFMergeResultModel:
    """Test PDFMergeResult model."""

    def test_merge_result(self):
        """PDFMergeResult should contain merge information."""
        result = PDFMergeResult(
            output_path="/path/to/merged.pdf",
            page_count=10,
            source_files=["/path/to/file1.pdf", "/path/to/file2.pdf"],
        )
        assert result.output_path == "/path/to/merged.pdf"
        assert result.page_count == 10
        assert len(result.source_files) == 2


class TestCollaborationSessionModel:
    """Test CollaborationSession model."""

    def test_create_session(self):
        """CollaborationSession should be created correctly."""
        session = CollaborationSession(
            id=str(uuid.uuid4()),
            document_id="doc-123",
            created_at="2024-01-01T00:00:00Z",
        )
        assert session.document_id == "doc-123"
        assert session.participants == []
        assert session.is_active is True

    def test_session_with_participants(self):
        """Session should track participants."""
        session = CollaborationSession(
            id=str(uuid.uuid4()),
            document_id="doc-123",
            created_at="2024-01-01T00:00:00Z",
            participants=["user-1", "user-2"],
            websocket_url="ws://localhost:8000/ws/collab/doc-123",
        )
        assert len(session.participants) == 2
        assert session.websocket_url is not None


class TestCollaboratorPresenceModel:
    """Test CollaboratorPresence model."""

    def test_create_presence(self):
        """CollaboratorPresence should be created correctly."""
        presence = CollaboratorPresence(
            user_id="user-123",
            user_name="John",
            last_seen="2024-01-01T00:00:00Z",
        )
        assert presence.user_id == "user-123"
        assert presence.user_name == "John"
        assert presence.cursor_position is None
        assert presence.color == "#3B82F6"

    def test_presence_with_selection(self):
        """Presence should track cursor and selection."""
        presence = CollaboratorPresence(
            user_id="user-123",
            user_name="John",
            cursor_position=50,
            selection_start=40,
            selection_end=60,
            color="#10B981",
            last_seen="2024-01-01T00:00:00Z",
        )
        assert presence.cursor_position == 50
        assert presence.selection_start == 40
        assert presence.selection_end == 60


class TestDocumentSchemas:
    """Test document request/response schemas."""

    def test_create_document_request_validation(self):
        """CreateDocumentRequest should validate fields."""
        request = CreateDocumentRequest(name="My Document")
        assert request.name == "My Document"
        assert request.content is None
        assert request.is_template is False
        assert request.tags == []

    def test_create_document_request_name_too_long(self):
        """CreateDocumentRequest should reject names over 255 chars."""
        with pytest.raises(ValidationError):
            CreateDocumentRequest(name="x" * 256)

    def test_create_document_request_with_content(self):
        """CreateDocumentRequest should accept content."""
        content = DocumentContent(type="doc", content=[])
        request = CreateDocumentRequest(
            name="Doc with Content",
            content=content,
            is_template=True,
            tags=["draft", "important"],
        )
        assert request.content.type == "doc"
        assert request.is_template is True
        assert "draft" in request.tags

    def test_update_document_request(self):
        """UpdateDocumentRequest should allow partial updates."""
        request = UpdateDocumentRequest(name="New Name")
        assert request.name == "New Name"
        assert request.content is None
        assert request.tags is None

    def test_comment_request_validation(self):
        """CommentRequest should validate selection bounds."""
        request = CommentRequest(
            selection_start=0,
            selection_end=10,
            text="Good point",
        )
        assert request.selection_start == 0
        assert request.selection_end == 10

    def test_comment_request_negative_selection_rejected(self):
        """CommentRequest should reject negative selection values."""
        with pytest.raises(ValidationError):
            CommentRequest(selection_start=-1, selection_end=10, text="Bad")

    def test_comment_request_empty_text_rejected(self):
        """CommentRequest should reject empty text."""
        with pytest.raises(ValidationError):
            CommentRequest(selection_start=0, selection_end=10, text="")

    def test_comment_request_text_too_long_rejected(self):
        """CommentRequest should reject text over 5000 chars."""
        with pytest.raises(ValidationError):
            CommentRequest(selection_start=0, selection_end=10, text="x" * 5001)


class TestPDFSchemas:
    """Test PDF operation schemas."""

    def test_pdf_reorder_request(self):
        """PDFReorderRequest should validate page order."""
        request = PDFReorderRequest(page_order=[2, 0, 1])
        assert request.page_order == [2, 0, 1]

    def test_pdf_reorder_request_empty_rejected(self):
        """PDFReorderRequest should reject empty page order."""
        with pytest.raises(ValidationError):
            PDFReorderRequest(page_order=[])

    def test_pdf_watermark_request_defaults(self):
        """PDFWatermarkRequest should have defaults."""
        request = PDFWatermarkRequest(text="DRAFT")
        assert request.text == "DRAFT"
        assert request.position == "center"
        assert request.font_size == 48
        assert request.opacity == 0.3
        assert request.color == "#808080"

    def test_pdf_watermark_request_validation(self):
        """PDFWatermarkRequest should validate fields."""
        with pytest.raises(ValidationError):
            PDFWatermarkRequest(text="")  # Empty text

    def test_pdf_watermark_request_invalid_position(self):
        """PDFWatermarkRequest should reject invalid position."""
        with pytest.raises(ValidationError):
            PDFWatermarkRequest(text="Test", position="invalid")

    def test_pdf_watermark_request_invalid_color(self):
        """PDFWatermarkRequest should reject invalid color format."""
        with pytest.raises(ValidationError):
            PDFWatermarkRequest(text="Test", color="red")

    def test_pdf_watermark_request_font_size_bounds(self):
        """PDFWatermarkRequest should enforce font size bounds."""
        with pytest.raises(ValidationError):
            PDFWatermarkRequest(text="Test", font_size=5)  # Too small
        with pytest.raises(ValidationError):
            PDFWatermarkRequest(text="Test", font_size=250)  # Too large

    def test_pdf_watermark_request_opacity_bounds(self):
        """PDFWatermarkRequest should enforce opacity bounds."""
        with pytest.raises(ValidationError):
            PDFWatermarkRequest(text="Test", opacity=0.05)  # Too low
        with pytest.raises(ValidationError):
            PDFWatermarkRequest(text="Test", opacity=1.5)  # Too high

    def test_schema_redaction_region(self):
        """SchemaRedactionRegion should validate coordinates."""
        region = SchemaRedactionRegion(
            page=0,
            x=10.0,
            y=20.0,
            width=100.0,
            height=50.0,
        )
        assert region.page == 0
        assert region.width == 100.0

    def test_schema_redaction_region_negative_rejected(self):
        """SchemaRedactionRegion should reject negative page."""
        with pytest.raises(ValidationError):
            SchemaRedactionRegion(page=-1, x=10, y=20, width=100, height=50)

    def test_schema_redaction_region_zero_dimensions_rejected(self):
        """SchemaRedactionRegion should reject zero dimensions."""
        with pytest.raises(ValidationError):
            SchemaRedactionRegion(page=0, x=10, y=20, width=0, height=50)

    def test_pdf_redact_request(self):
        """PDFRedactRequest should require at least one region."""
        region = SchemaRedactionRegion(page=0, x=10, y=20, width=100, height=50)
        request = PDFRedactRequest(regions=[region])
        assert len(request.regions) == 1

    def test_pdf_redact_request_empty_rejected(self):
        """PDFRedactRequest should reject empty regions."""
        with pytest.raises(ValidationError):
            PDFRedactRequest(regions=[])
