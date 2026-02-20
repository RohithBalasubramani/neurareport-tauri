"""
Document Property-Based Tests - Using Hypothesis for validation.
"""

import os
import string
import uuid
from pathlib import Path

import pytest
from hypothesis import given, strategies as st, assume, settings


from backend.app.services.documents.service import (
    Document,
    DocumentService,
    DocumentVersion,
    DocumentComment,
    DocumentContent,
)
from backend.app.services.documents.pdf_operations import (
    PageInfo,
    WatermarkConfig,
    RedactionRegion,
    PDFMergeResult,
)
from backend.app.services.documents.collaboration import (
    CollaborationService,
    CollaboratorPresence,
)
from backend.app.schemas.documents.document import (
    CreateDocumentRequest,
    UpdateDocumentRequest,
    CommentRequest,
    PDFWatermarkRequest,
)


# Strategies for generating test data
document_name_strategy = st.text(
    alphabet=string.ascii_letters + string.digits + " _-",
    min_size=1,
    max_size=100,
)

content_text_strategy = st.text(
    alphabet=string.printable,
    min_size=0,
    max_size=1000,
)

tag_strategy = st.text(
    alphabet=string.ascii_lowercase + string.digits + "-",
    min_size=1,
    max_size=20,
)

user_id_strategy = st.text(
    alphabet=string.ascii_lowercase + string.digits + "-",
    min_size=1,
    max_size=36,
)

# Document content strategy
tiptap_content_strategy = st.fixed_dictionaries({
    "type": st.just("doc"),
    "content": st.lists(
        st.fixed_dictionaries({
            "type": st.sampled_from(["paragraph", "heading", "bulletList"]),
            "content": st.just([{"type": "text", "text": "test content"}]),
        }),
        min_size=0,
        max_size=10,
    ),
})


@pytest.fixture
def doc_service(tmp_path: Path) -> DocumentService:
    """Create a document service with temporary storage."""
    return DocumentService(uploads_root=tmp_path / "documents")


class TestDocumentModelProperties:
    """Property-based tests for Document model."""

    @given(
        name=document_name_strategy,
        version=st.integers(min_value=1, max_value=10000),
    )
    def test_document_preserves_name(self, name: str, version: int):
        """Document should preserve any valid name."""
        assume(len(name.strip()) > 0)
        doc = Document(
            id=str(uuid.uuid4()),
            name=name,
            content={"type": "doc", "content": []},
            version=version,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        assert doc.name == name
        assert doc.version == version

    @given(content=tiptap_content_strategy)
    def test_document_preserves_content(self, content: dict):
        """Document should preserve any valid content structure."""
        doc = Document(
            id=str(uuid.uuid4()),
            name="Test",
            content=content,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        # Content may be coerced to DocumentContent model
        c = doc.content if isinstance(doc.content, dict) else doc.content.model_dump()
        assert c == content

    @given(tags=st.lists(tag_strategy, min_size=0, max_size=10))
    def test_document_preserves_tags(self, tags: list):
        """Document should preserve any list of tags."""
        doc = Document(
            id=str(uuid.uuid4()),
            name="Test",
            content={"type": "doc", "content": []},
            tags=tags,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        assert doc.tags == tags

    @given(
        metadata=st.dictionaries(
            keys=st.text(alphabet=string.ascii_letters, min_size=1, max_size=20),
            values=st.one_of(st.integers(), st.text(max_size=50), st.booleans()),
            max_size=5,
        )
    )
    def test_document_preserves_metadata(self, metadata: dict):
        """Document should preserve any valid metadata."""
        doc = Document(
            id=str(uuid.uuid4()),
            name="Test",
            content={"type": "doc", "content": []},
            metadata=metadata,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        assert doc.metadata == metadata


class TestDocumentServiceProperties:
    """Property-based tests for DocumentService."""

    @given(name=document_name_strategy)
    @settings(max_examples=20)
    def test_create_get_roundtrip(self, name: str, tmp_path_factory):
        """Created document should be retrievable with same data."""
        assume(len(name.strip()) > 0)
        tmp_path = tmp_path_factory.mktemp("docs")
        doc_service = DocumentService(uploads_root=tmp_path / "documents")
        created = doc_service.create(name=name)
        retrieved = doc_service.get(created.id)
        assert retrieved is not None
        assert retrieved.name == name
        assert retrieved.id == created.id

    @given(
        name1=document_name_strategy,
        name2=document_name_strategy,
    )
    @settings(max_examples=20, deadline=None)
    def test_update_changes_only_specified_fields(
        self, name1: str, name2: str, tmp_path_factory
    ):
        """Update should only change specified fields."""
        assume(len(name1.strip()) > 0)
        assume(len(name2.strip()) > 0)
        assume(name1 != name2)
        tmp_path = tmp_path_factory.mktemp("docs")
        doc_service = DocumentService(uploads_root=tmp_path / "documents")

        created = doc_service.create(name=name1, owner_id="owner-1")
        updated = doc_service.update(created.id, name=name2)

        assert updated.name == name2
        assert updated.owner_id == "owner-1"  # Unchanged

    @given(num_updates=st.integers(min_value=1, max_value=10))
    @settings(max_examples=10, deadline=None)
    def test_version_increments_correctly(
        self, num_updates: int, tmp_path_factory
    ):
        """Version should increment by 1 for each update."""
        tmp_path = tmp_path_factory.mktemp("docs")
        doc_service = DocumentService(uploads_root=tmp_path / "documents")
        doc = doc_service.create(name="Test")
        assert doc.version == 1

        for i in range(num_updates):
            doc = doc_service.update(doc.id, name=f"Update {i}")

        assert doc.version == 1 + num_updates

    @given(num_updates=st.integers(min_value=1, max_value=10))
    @settings(max_examples=10, deadline=None)
    def test_versions_match_update_count(
        self, num_updates: int, tmp_path_factory
    ):
        """Number of versions should match number of updates."""
        tmp_path = tmp_path_factory.mktemp("docs")
        doc_service = DocumentService(uploads_root=tmp_path / "documents")
        doc = doc_service.create(name="Test")

        for i in range(num_updates):
            doc_service.update(doc.id, name=f"Update {i}")

        versions = doc_service.get_versions(doc.id)
        assert len(versions) == num_updates


class TestCommentProperties:
    """Property-based tests for comments."""

    @given(
        selection_start=st.integers(min_value=0, max_value=10000),
        selection_end=st.integers(min_value=0, max_value=10000),
        text=st.text(min_size=1, max_size=500),
    )
    @settings(max_examples=20)
    def test_comment_preserves_selection(
        self,
        selection_start: int,
        selection_end: int,
        text: str,
        tmp_path_factory,
    ):
        """Comment should preserve selection positions."""
        assume(len(text.strip()) > 0)
        tmp_path = tmp_path_factory.mktemp("docs")
        doc_service = DocumentService(uploads_root=tmp_path / "documents")
        doc = doc_service.create(name="Test")
        comment = doc_service.add_comment(
            doc.id,
            selection_start=selection_start,
            selection_end=selection_end,
            text=text,
        )
        assert comment.selection_start == selection_start
        assert comment.selection_end == selection_end
        assert comment.text == text

    @given(num_comments=st.integers(min_value=1, max_value=20))
    @settings(max_examples=10, deadline=None)
    def test_comment_count_matches(
        self, num_comments: int, tmp_path_factory
    ):
        """Number of comments should match additions."""
        tmp_path = tmp_path_factory.mktemp("docs")
        doc_service = DocumentService(uploads_root=tmp_path / "documents")
        doc = doc_service.create(name="Test")

        for i in range(num_comments):
            doc_service.add_comment(doc.id, i * 10, i * 10 + 5, f"Comment {i}")

        comments = doc_service.get_comments(doc.id)
        assert len(comments) == num_comments


class TestCollaborationProperties:
    """Property-based tests for collaboration service."""

    @given(num_users=st.integers(min_value=1, max_value=20))
    @settings(max_examples=10)
    def test_participant_count_matches_joins(self, num_users: int):
        """Participant count should match number of joins."""
        service = CollaborationService()
        session = service.start_session("doc-123")

        for i in range(num_users):
            service.join_session(session.id, f"user-{i}")

        updated = service.get_session(session.id)
        assert len(updated.participants) == num_users

    @given(user_id=user_id_strategy)
    @settings(max_examples=20)
    def test_join_leave_idempotent(self, user_id: str):
        """Join then leave should result in empty participants."""
        assume(len(user_id.strip()) > 0)
        service = CollaborationService()
        session = service.start_session("doc-123")

        service.join_session(session.id, user_id)
        service.leave_session(session.id, user_id)

        # Session may be ended if last user left
        updated = service.get_session(session.id)
        assert user_id not in updated.participants


class TestWatermarkConfigProperties:
    """Property-based tests for WatermarkConfig."""

    @given(
        text=st.text(min_size=1, max_size=50),
        font_size=st.integers(min_value=8, max_value=200),
        opacity=st.floats(min_value=0.1, max_value=1.0),
    )
    def test_watermark_config_accepts_valid_values(
        self, text: str, font_size: int, opacity: float
    ):
        """WatermarkConfig should accept valid values."""
        assume(len(text.strip()) > 0)
        config = WatermarkConfig(
            text=text,
            font_size=font_size,
            opacity=opacity,
        )
        assert config.text == text
        assert config.font_size == font_size
        assert config.opacity == opacity


class TestRedactionRegionProperties:
    """Property-based tests for RedactionRegion."""

    @given(
        page=st.integers(min_value=0, max_value=1000),
        x=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        y=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
        width=st.floats(min_value=1, max_value=1000, allow_nan=False, allow_infinity=False),
        height=st.floats(min_value=1, max_value=1000, allow_nan=False, allow_infinity=False),
    )
    def test_redaction_region_accepts_valid_coordinates(
        self, page: int, x: float, y: float, width: float, height: float
    ):
        """RedactionRegion should accept valid coordinates."""
        region = RedactionRegion(
            page=page,
            x=x,
            y=y,
            width=width,
            height=height,
        )
        assert region.page == page
        assert region.x == x
        assert region.y == y
        assert region.width == width
        assert region.height == height


class TestPageInfoProperties:
    """Property-based tests for PageInfo."""

    @given(
        page_number=st.integers(min_value=0, max_value=10000),
        width=st.floats(min_value=1, max_value=10000, allow_nan=False, allow_infinity=False),
        height=st.floats(min_value=1, max_value=10000, allow_nan=False, allow_infinity=False),
        rotation=st.sampled_from([0, 90, 180, 270]),
    )
    def test_page_info_accepts_valid_values(
        self, page_number: int, width: float, height: float, rotation: int
    ):
        """PageInfo should accept valid values."""
        info = PageInfo(
            page_number=page_number,
            width=width,
            height=height,
            rotation=rotation,
        )
        assert info.page_number == page_number
        assert info.width == width
        assert info.height == height
        assert info.rotation == rotation


class TestSchemaValidationProperties:
    """Property-based tests for schema validation."""

    @given(
        name=st.text(min_size=1, max_size=255, alphabet=string.printable.replace("\n", "").replace("\r", ""))
    )
    def test_create_document_request_accepts_valid_names(self, name: str):
        """CreateDocumentRequest should accept valid names."""
        assume(len(name.strip()) > 0)
        # Filter out control characters that may cause validation issues
        assume(all(ord(c) >= 32 for c in name))
        request = CreateDocumentRequest(name=name)
        assert request.name == name

    @given(
        selection_start=st.integers(min_value=0, max_value=100000),
        selection_end=st.integers(min_value=0, max_value=100000),
        text=st.text(min_size=1, max_size=4999),
    )
    def test_comment_request_accepts_valid_values(
        self, selection_start: int, selection_end: int, text: str
    ):
        """CommentRequest should accept valid values."""
        assume(len(text.strip()) > 0)
        # Filter out control characters
        assume(all(ord(c) >= 32 or c in "\n\r\t" for c in text))
        request = CommentRequest(
            selection_start=selection_start,
            selection_end=selection_end,
            text=text,
        )
        assert request.selection_start == selection_start
        assert request.selection_end == selection_end


class TestIdempotencyProperties:
    """Property-based tests for idempotent operations."""

    @given(name=document_name_strategy)
    @settings(max_examples=10, deadline=None)
    def test_get_is_idempotent(self, name: str, tmp_path_factory):
        """Multiple gets should return same result."""
        assume(len(name.strip()) > 0)
        tmp_path = tmp_path_factory.mktemp("docs")
        doc_service = DocumentService(uploads_root=tmp_path / "documents")
        doc = doc_service.create(name=name)

        result1 = doc_service.get(doc.id)
        result2 = doc_service.get(doc.id)
        result3 = doc_service.get(doc.id)

        assert result1.model_dump() == result2.model_dump() == result3.model_dump()

    @given(name=document_name_strategy)
    @settings(max_examples=10)
    def test_delete_twice_is_safe(self, name: str, tmp_path_factory):
        """Deleting twice should not raise error."""
        assume(len(name.strip()) > 0)
        tmp_path = tmp_path_factory.mktemp("docs")
        doc_service = DocumentService(uploads_root=tmp_path / "documents")
        doc = doc_service.create(name=name)

        result1 = doc_service.delete(doc.id)
        result2 = doc_service.delete(doc.id)

        assert result1 is True
        assert result2 is False  # Already deleted


class TestBoundaryProperties:
    """Property-based tests for boundary conditions."""

    @given(
        offset=st.integers(min_value=0, max_value=1000),
        limit=st.integers(min_value=1, max_value=100),
    )
    @settings(max_examples=20, deadline=None)
    def test_list_pagination_bounds(
        self, offset: int, limit: int, tmp_path_factory
    ):
        """List should handle pagination boundaries correctly."""
        tmp_path = tmp_path_factory.mktemp("docs")
        doc_service = DocumentService(uploads_root=tmp_path / "documents")
        # Create some documents
        for i in range(5):
            doc_service.create(name=f"Doc {i}")

        docs, total = doc_service.list_documents(offset=offset, limit=limit)
        assert len(docs) <= limit
        assert len(docs) <= max(0, 5 - offset)

    @given(num_docs=st.integers(min_value=0, max_value=20))
    @settings(max_examples=10, deadline=None)
    def test_list_count_correct(
        self, num_docs: int, tmp_path_factory
    ):
        """List should return correct number of documents."""
        tmp_path = tmp_path_factory.mktemp("docs")
        doc_service = DocumentService(uploads_root=tmp_path / "documents")
        for i in range(num_docs):
            doc_service.create(name=f"Doc {i}")

        docs, total = doc_service.list_documents(limit=100)
        assert len(docs) == num_docs
        assert total == num_docs
