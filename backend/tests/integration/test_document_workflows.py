"""
Document Management Integration Tests - Testing full document workflows.
"""

import json
import os
import uuid
from pathlib import Path
import time
from typing import Any

import pytest


from backend.app.services.documents.service import (
    Document,
    DocumentService,
    DocumentContent,
)
from backend.app.services.documents.collaboration import (
    CollaborationService,
)


def get_content_dict(content: Any) -> dict:
    """Helper to normalize content to dict regardless of type."""
    if isinstance(content, dict):
        return content
    return content.model_dump()

# Check if fitz is available for PDF tests
try:
    import fitz
    from backend.app.services.documents.pdf_operations import (
        PDFOperationsService,
        WatermarkConfig,
        RedactionRegion,
    )
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False


@pytest.fixture
def doc_service(tmp_path: Path) -> DocumentService:
    """Create document service with temporary storage."""
    return DocumentService(uploads_root=tmp_path / "documents")


@pytest.fixture
def collab_service() -> CollaborationService:
    """Create collaboration service."""
    return CollaborationService()


@pytest.fixture
def pdf_service(tmp_path: Path):
    """Create PDF operations service."""
    if not HAS_FITZ:
        pytest.skip("PyMuPDF not available")
    return PDFOperationsService(output_dir=tmp_path / "pdf_outputs")


def create_test_pdf(path: Path, num_pages: int = 1) -> Path:
    """Create a test PDF file."""
    if not HAS_FITZ:
        pytest.skip("PyMuPDF not available")
    doc = fitz.open()
    for i in range(num_pages):
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 50), f"Page {i + 1}")
    doc.save(str(path))
    doc.close()
    return path


class TestDocumentCRUDWorkflow:
    """Test complete document CRUD workflow."""

    def test_create_read_update_delete_workflow(self, doc_service: DocumentService):
        """Full CRUD workflow should work correctly."""
        # Create
        doc = doc_service.create(
            name="Workflow Test",
            owner_id="user-123",
            metadata={"category": "test"},
        )
        assert doc.id is not None
        assert doc.version == 1

        # Read
        retrieved = doc_service.get(doc.id)
        assert retrieved.name == "Workflow Test"
        assert retrieved.owner_id == "user-123"

        # Update
        updated = doc_service.update(
            doc.id,
            name="Updated Workflow Test",
            metadata={"status": "updated"},
        )
        assert updated.name == "Updated Workflow Test"
        assert updated.version == 2
        assert updated.metadata["category"] == "test"  # Preserved
        assert updated.metadata["status"] == "updated"  # Added

        # Delete
        result = doc_service.delete(doc.id)
        assert result is True

        # Verify deleted
        deleted = doc_service.get(doc.id)
        assert deleted is None

    def test_document_with_rich_content_workflow(self, doc_service: DocumentService):
        """Document with rich TipTap content should persist correctly."""
        rich_content = {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 1},
                    "content": [{"type": "text", "text": "Document Title"}],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "This is "},
                        {"type": "text", "marks": [{"type": "bold"}], "text": "bold"},
                        {"type": "text", "text": " and "},
                        {"type": "text", "marks": [{"type": "italic"}], "text": "italic"},
                        {"type": "text", "text": " text."},
                    ],
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {"type": "paragraph", "content": [{"type": "text", "text": "Item 1"}]}
                            ],
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {"type": "paragraph", "content": [{"type": "text", "text": "Item 2"}]}
                            ],
                        },
                    ],
                },
            ],
        }

        doc = doc_service.create(
            name="Rich Content Doc",
            content=DocumentContent(**rich_content),
        )

        retrieved = doc_service.get(doc.id)
        c = get_content_dict(retrieved.content)
        assert c["content"][0]["type"] == "heading"
        assert c["content"][1]["content"][1]["marks"][0]["type"] == "bold"
        assert len(c["content"][2]["content"]) == 2


class TestVersionHistoryWorkflow:
    """Test version history workflow."""

    def test_version_history_tracks_changes(self, doc_service: DocumentService):
        """Version history should track all changes."""
        doc = doc_service.create(name="Version Test")

        # Make several updates
        contents = [
            {"type": "doc", "content": [{"type": "text", "text": f"Version {i}"}]}
            for i in range(1, 6)
        ]

        for i, content in enumerate(contents):
            doc_service.update(
                doc.id,
                content=DocumentContent(**content),
            )

        # Check versions
        versions = doc_service.get_versions(doc.id)
        assert len(versions) == 5
        # Versions sorted descending
        assert versions[0].version == 5
        assert versions[4].version == 1

    def test_version_content_preserved(self, doc_service: DocumentService):
        """Each version should preserve its content."""
        doc = doc_service.create(
            name="Version Content Test",
            content=DocumentContent(type="doc", content=[{"type": "text", "text": "Original"}]),
        )

        doc_service.update(
            doc.id,
            content=DocumentContent(type="doc", content=[{"type": "text", "text": "Updated"}]),
        )

        versions = doc_service.get_versions(doc.id)
        # Version 1 should have original content
        vc = get_content_dict(versions[0].content)
        assert vc["content"][0]["text"] == "Original"

        # Current document should have updated content
        current = doc_service.get(doc.id)
        cc = get_content_dict(current.content)
        assert cc["content"][0]["text"] == "Updated"


class TestCommentWorkflow:
    """Test comment workflow."""

    def test_add_review_resolve_comment_workflow(self, doc_service: DocumentService):
        """Complete comment review workflow."""
        doc = doc_service.create(name="Comment Test")

        # Add comments
        comment1 = doc_service.add_comment(
            doc.id, 0, 50, "Please review this section",
            author_id="reviewer-1", author_name="Alice",
        )
        comment2 = doc_service.add_comment(
            doc.id, 100, 150, "Typo here",
            author_id="reviewer-2", author_name="Bob",
        )

        # Get all comments
        comments = doc_service.get_comments(doc.id)
        assert len(comments) == 2
        assert all(not c.resolved for c in comments)

        # Resolve first comment
        doc_service.resolve_comment(doc.id, comment1.id)

        # Check status
        comments = doc_service.get_comments(doc.id)
        resolved = [c for c in comments if c.resolved]
        unresolved = [c for c in comments if not c.resolved]
        assert len(resolved) == 1
        assert len(unresolved) == 1

    def test_comments_preserved_across_updates(self, doc_service: DocumentService):
        """Comments should persist across document updates."""
        doc = doc_service.create(name="Comment Persistence Test")
        doc_service.add_comment(doc.id, 0, 10, "Initial comment")

        # Update document several times
        for i in range(5):
            doc_service.update(doc.id, name=f"Update {i}")

        # Comments should still exist
        comments = doc_service.get_comments(doc.id)
        assert len(comments) == 1
        assert comments[0].text == "Initial comment"


class TestTemplateWorkflow:
    """Test document template workflow."""

    def test_create_document_from_template(self, doc_service: DocumentService):
        """Create new document based on template."""
        # Create template
        template_content = {
            "type": "doc",
            "content": [
                {"type": "heading", "content": [{"type": "text", "text": "Template Header"}]},
                {"type": "paragraph", "content": [{"type": "text", "text": "Template body..."}]},
            ],
        }
        template = doc_service.create(
            name="Report Template",
            content=DocumentContent(**template_content),
            is_template=True,
        )

        # Create new document from template
        new_doc = doc_service.create(
            name="My Report",
            content=DocumentContent(**template_content),  # Copy template content
            owner_id="user-123",
        )

        assert new_doc.is_template is False
        assert new_doc.content == template.content
        assert new_doc.id != template.id

    def test_list_only_templates(self, doc_service: DocumentService):
        """Should be able to list only templates."""
        # Create mix of documents and templates
        doc_service.create(name="Regular Doc 1")
        doc_service.create(name="Template 1", is_template=True)
        doc_service.create(name="Regular Doc 2")
        doc_service.create(name="Template 2", is_template=True)

        templates, templates_total = doc_service.list_documents(is_template=True)
        regular, regular_total = doc_service.list_documents(is_template=False)

        assert len(templates) == 2
        assert len(regular) == 2
        assert all(t.is_template for t in templates)
        assert all(not d.is_template for d in regular)


class TestCollaborationWorkflow:
    """Test real-time collaboration workflow."""

    def test_multi_user_collaboration_session(
        self, doc_service: DocumentService, collab_service: CollaborationService
    ):
        """Multiple users collaborating on same document."""
        doc = doc_service.create(name="Collab Doc")

        # Start collaboration session
        session = collab_service.start_session(doc.id, user_id="user-1")

        # Other users join
        collab_service.join_session(session.id, "user-2", "Alice")
        collab_service.join_session(session.id, "user-3", "Bob")

        # Check participants
        updated_session = collab_service.get_session(session.id)
        assert len(updated_session.participants) == 3

        # Users update presence
        collab_service.update_presence(session.id, "user-1", cursor_position=100)
        collab_service.update_presence(session.id, "user-2", cursor_position=200)
        collab_service.update_presence(
            session.id, "user-3",
            selection_start=50, selection_end=75,
        )

        # Get presence info
        presence = collab_service.get_presence(session.id)
        assert len(presence) == 3

        # Users leave
        collab_service.leave_session(session.id, "user-2")
        collab_service.leave_session(session.id, "user-3")

        # Check remaining
        updated_session = collab_service.get_session(session.id)
        assert len(updated_session.participants) == 1
        assert "user-1" in updated_session.participants

        # Last user leaves
        collab_service.leave_session(session.id, "user-1")

        # Session should be ended
        final_session = collab_service.get_session(session.id)
        assert final_session.is_active is False


class TestFilterAndSearchWorkflow:
    """Test document filtering and search workflow."""

    def test_filter_by_owner(self, doc_service: DocumentService):
        """Filter documents by owner."""
        doc_service.create(name="User1 Doc 1", owner_id="user-1")
        doc_service.create(name="User1 Doc 2", owner_id="user-1")
        doc_service.create(name="User2 Doc", owner_id="user-2")

        user1_docs, user1_total = doc_service.list_documents(owner_id="user-1")
        user2_docs, user2_total = doc_service.list_documents(owner_id="user-2")

        assert len(user1_docs) == 2
        assert len(user2_docs) == 1

    def test_paginated_listing(self, doc_service: DocumentService):
        """Test paginated document listing."""
        for i in range(25):
            doc_service.create(name=f"Doc {i:02d}")

        # First page
        page1, total1 = doc_service.list_documents(limit=10, offset=0)
        assert len(page1) == 10
        assert total1 == 25

        # Second page
        page2, total2 = doc_service.list_documents(limit=10, offset=10)
        assert len(page2) == 10

        # Third page (partial)
        page3, total3 = doc_service.list_documents(limit=10, offset=20)
        assert len(page3) == 5

        # No overlap between pages
        page1_ids = {d.id for d in page1}
        page2_ids = {d.id for d in page2}
        page3_ids = {d.id for d in page3}
        assert not page1_ids.intersection(page2_ids)
        assert not page2_ids.intersection(page3_ids)


@pytest.mark.skipif(not HAS_FITZ, reason="PyMuPDF not available")
class TestPDFWorkflow:
    """Test PDF operations workflow."""

    def test_pdf_merge_workflow(self, pdf_service, tmp_path: Path):
        """Merge multiple PDFs workflow."""
        # Create source PDFs
        pdf1 = create_test_pdf(tmp_path / "doc1.pdf", num_pages=2)
        pdf2 = create_test_pdf(tmp_path / "doc2.pdf", num_pages=3)
        pdf3 = create_test_pdf(tmp_path / "doc3.pdf", num_pages=1)

        # Merge
        result = pdf_service.merge_pdfs([pdf1, pdf2, pdf3])

        assert result.page_count == 6
        assert len(result.source_files) == 3
        assert Path(result.output_path).exists()

    def test_pdf_watermark_workflow(self, pdf_service, tmp_path: Path):
        """Add watermark to PDF workflow."""
        source_pdf = create_test_pdf(tmp_path / "source.pdf", num_pages=5)

        # Add watermark
        config = WatermarkConfig(
            text="CONFIDENTIAL",
            position="diagonal",
            opacity=0.3,
        )
        output = pdf_service.add_watermark(source_pdf, config)

        assert output.exists()
        pages = pdf_service.get_page_info(output)
        assert len(pages) == 5

    def test_pdf_redaction_workflow(self, pdf_service, tmp_path: Path):
        """Redact sensitive information workflow."""
        source_pdf = create_test_pdf(tmp_path / "sensitive.pdf", num_pages=3)

        # Define redaction regions (e.g., social security numbers, addresses)
        regions = [
            RedactionRegion(page=0, x=50, y=50, width=200, height=20),
            RedactionRegion(page=1, x=100, y=100, width=150, height=30),
            RedactionRegion(page=2, x=50, y=200, width=300, height=25),
        ]

        output = pdf_service.redact_regions(source_pdf, regions)

        assert output.exists()

    def test_pdf_split_and_extract_workflow(self, pdf_service, tmp_path: Path):
        """Split PDF and extract pages workflow."""
        source_pdf = create_test_pdf(tmp_path / "large.pdf", num_pages=10)

        # Split into sections
        ranges = [(0, 2), (3, 5), (6, 9)]
        split_files = pdf_service.split_pdf(source_pdf, ranges)

        assert len(split_files) == 3
        assert pdf_service.get_page_info(split_files[0]).__len__() == 3
        assert pdf_service.get_page_info(split_files[1]).__len__() == 3
        assert pdf_service.get_page_info(split_files[2]).__len__() == 4

        # Extract specific pages
        extracted = pdf_service.extract_pages(source_pdf, [0, 4, 9])
        assert pdf_service.get_page_info(extracted).__len__() == 3

    def test_pdf_rotate_workflow(self, pdf_service, tmp_path: Path):
        """Rotate PDF pages workflow."""
        source_pdf = create_test_pdf(tmp_path / "rotate.pdf", num_pages=4)

        # Rotate all pages 90 degrees
        output = pdf_service.rotate_pages(source_pdf, 90)
        pages = pdf_service.get_page_info(output)
        assert all(p.rotation == 90 for p in pages)

        # Rotate only specific pages
        output2 = pdf_service.rotate_pages(source_pdf, 180, pages=[1, 3])
        pages2 = pdf_service.get_page_info(output2)
        assert pages2[0].rotation == 0
        assert pages2[1].rotation == 180
        assert pages2[2].rotation == 0
        assert pages2[3].rotation == 180


class TestErrorRecoveryWorkflow:
    """Test error recovery workflows."""

    def test_recover_from_failed_update(self, doc_service: DocumentService):
        """System should recover gracefully from failed updates."""
        doc = doc_service.create(name="Recovery Test")
        original_content = doc.content

        # Simulate getting document, making changes, but not saving
        retrieved = doc_service.get(doc.id)
        assert retrieved.content == original_content

    def test_document_isolation(self, doc_service: DocumentService):
        """Operations on one document shouldn't affect others."""
        doc1 = doc_service.create(name="Doc 1")
        doc2 = doc_service.create(name="Doc 2")

        # Update doc1 many times
        for i in range(10):
            doc_service.update(doc1.id, name=f"Doc 1 - Update {i}")

        # Delete doc1
        doc_service.delete(doc1.id)

        # Doc2 should be unaffected
        retrieved = doc_service.get(doc2.id)
        assert retrieved.name == "Doc 2"
        assert retrieved.version == 1


class TestDataIntegrityWorkflow:
    """Test data integrity workflows."""

    def test_content_not_corrupted_through_updates(self, doc_service: DocumentService):
        """Content should remain intact through multiple updates."""
        complex_content = {
            "type": "doc",
            "content": [
                {"type": "heading", "attrs": {"level": 1}, "content": [{"type": "text", "text": "Title"}]},
                {"type": "paragraph", "content": [
                    {"type": "text", "text": "Special chars: <>&\"' and unicode: 日本語 🎉"},
                ]},
            ],
        }

        doc = doc_service.create(
            name="Integrity Test",
            content=DocumentContent(**complex_content),
        )

        # Update metadata only (content should stay same)
        for i in range(10):
            doc_service.update(doc.id, metadata={f"key_{i}": f"value_{i}"})

        # Verify content unchanged
        final = doc_service.get(doc.id)
        fc = get_content_dict(final.content)
        content_str = json.dumps(fc, ensure_ascii=False)
        assert "日本語" in content_str
        assert "🎉" in content_str
        assert "<>&" in content_str

    def test_versions_maintain_integrity(self, doc_service: DocumentService):
        """Versions should maintain content integrity."""
        contents = [
            {"type": "doc", "content": [{"type": "text", "text": f"Content {i}"}]}
            for i in range(5)
        ]

        doc = doc_service.create(
            name="Version Integrity",
            content=DocumentContent(**contents[0]),
        )

        for content in contents[1:]:
            doc_service.update(doc.id, content=DocumentContent(**content))

        versions = doc_service.get_versions(doc.id)

        # Each version should have correct content
        for i, version in enumerate(reversed(versions)):
            expected = f"Content {i}"
            vc = get_content_dict(version.content)
            assert vc["content"][0]["text"] == expected
