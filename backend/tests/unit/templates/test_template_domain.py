"""
Unit tests for template domain models.

Tests the Template, TemplateSchema, Artifact, and related domain entities.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from backend.engine.domain.templates import (
    Artifact,
    Template,
    TemplateKind,
    TemplateSchema,
    TemplateStatus,
)


# =============================================================================
# TemplateKind Tests
# =============================================================================

class TestTemplateKind:
    """Tests for TemplateKind enum."""

    def test_pdf_kind_value(self):
        """PDF kind should have value 'pdf'."""
        assert TemplateKind.PDF.value == "pdf"

    def test_excel_kind_value(self):
        """EXCEL kind should have value 'excel'."""
        assert TemplateKind.EXCEL.value == "excel"

    def test_kind_is_string_enum(self):
        """TemplateKind should be a string enum."""
        assert isinstance(TemplateKind.PDF, str)
        assert TemplateKind.PDF == "pdf"

    def test_kind_from_string(self):
        """Should create kind from string value."""
        assert TemplateKind("pdf") == TemplateKind.PDF
        assert TemplateKind("excel") == TemplateKind.EXCEL

    def test_invalid_kind_raises(self):
        """Invalid kind value should raise ValueError."""
        with pytest.raises(ValueError):
            TemplateKind("invalid")


# =============================================================================
# TemplateStatus Tests
# =============================================================================

class TestTemplateStatus:
    """Tests for TemplateStatus enum."""

    def test_status_values(self):
        """All status values should be correct."""
        assert TemplateStatus.DRAFT.value == "draft"
        assert TemplateStatus.ANALYZING.value == "analyzing"
        assert TemplateStatus.MAPPED.value == "mapped"
        assert TemplateStatus.APPROVED.value == "approved"
        assert TemplateStatus.FAILED.value == "failed"

    def test_status_is_string_enum(self):
        """TemplateStatus should be a string enum."""
        assert isinstance(TemplateStatus.DRAFT, str)
        assert TemplateStatus.DRAFT == "draft"

    def test_status_from_string(self):
        """Should create status from string value."""
        assert TemplateStatus("draft") == TemplateStatus.DRAFT
        assert TemplateStatus("approved") == TemplateStatus.APPROVED

    def test_invalid_status_raises(self):
        """Invalid status value should raise ValueError."""
        with pytest.raises(ValueError):
            TemplateStatus("invalid")

    def test_all_statuses_defined(self):
        """All expected statuses should be defined."""
        statuses = {s.value for s in TemplateStatus}
        expected = {"draft", "analyzing", "mapped", "approved", "failed"}
        assert statuses == expected


# =============================================================================
# Artifact Tests
# =============================================================================

class TestArtifact:
    """Tests for Artifact dataclass."""

    def test_create_artifact(self):
        """Should create artifact with required fields."""
        artifact = Artifact(
            name="template.html",
            path=Path("/uploads/tpl-123/template.html"),
            artifact_type="html",
        )
        assert artifact.name == "template.html"
        assert artifact.path == Path("/uploads/tpl-123/template.html")
        assert artifact.artifact_type == "html"

    def test_artifact_with_optional_fields(self):
        """Should create artifact with optional fields."""
        created = datetime.now(timezone.utc)
        artifact = Artifact(
            name="source.pdf",
            path=Path("/uploads/tpl-123/source.pdf"),
            artifact_type="pdf",
            size_bytes=1024,
            checksum="abc123",
            created_at=created,
        )
        assert artifact.size_bytes == 1024
        assert artifact.checksum == "abc123"
        assert artifact.created_at == created

    def test_artifact_is_frozen(self):
        """Artifact should be immutable (frozen)."""
        artifact = Artifact(
            name="template.html",
            path=Path("/uploads/tpl-123/template.html"),
            artifact_type="html",
        )
        with pytest.raises(AttributeError):
            artifact.name = "other.html"

    def test_artifact_defaults(self):
        """Optional fields should default to None."""
        artifact = Artifact(
            name="test.html",
            path=Path("/test"),
            artifact_type="html",
        )
        assert artifact.size_bytes is None
        assert artifact.checksum is None
        assert artifact.created_at is None

    def test_artifact_equality(self):
        """Artifacts with same values should be equal."""
        a1 = Artifact(name="test.html", path=Path("/test"), artifact_type="html")
        a2 = Artifact(name="test.html", path=Path("/test"), artifact_type="html")
        assert a1 == a2

    def test_artifact_hashable(self):
        """Frozen artifacts should be hashable."""
        artifact = Artifact(name="test.html", path=Path("/test"), artifact_type="html")
        # Should not raise
        hash(artifact)
        # Can be added to set
        s = {artifact}
        assert artifact in s


# =============================================================================
# TemplateSchema Tests
# =============================================================================

class TestTemplateSchema:
    """Tests for TemplateSchema dataclass."""

    def test_create_empty_schema(self):
        """Should create schema with defaults."""
        schema = TemplateSchema()
        assert schema.scalars == []
        assert schema.row_tokens == []
        assert schema.totals == []
        assert schema.tables_detected == []
        assert schema.placeholders_found == 0

    def test_create_schema_with_values(self):
        """Should create schema with provided values."""
        schema = TemplateSchema(
            scalars=["report_title", "report_date"],
            row_tokens=["line_amount", "line_desc"],
            totals=["grand_total"],
            tables_detected=["items", "summary"],
            placeholders_found=5,
        )
        assert schema.scalars == ["report_title", "report_date"]
        assert schema.row_tokens == ["line_amount", "line_desc"]
        assert schema.totals == ["grand_total"]
        assert schema.tables_detected == ["items", "summary"]
        assert schema.placeholders_found == 5

    def test_schema_is_mutable(self):
        """Schema should be mutable (not frozen)."""
        schema = TemplateSchema()
        schema.scalars.append("new_token")
        assert "new_token" in schema.scalars


# =============================================================================
# Template Tests - Creation
# =============================================================================

class TestTemplateCreation:
    """Tests for Template creation."""

    def test_create_minimal_template(self):
        """Should create template with minimal required fields."""
        template = Template(
            template_id="tpl-123",
            name="Test Template",
            kind=TemplateKind.PDF,
            status=TemplateStatus.DRAFT,
        )
        assert template.template_id == "tpl-123"
        assert template.name == "Test Template"
        assert template.kind == TemplateKind.PDF
        assert template.status == TemplateStatus.DRAFT

    def test_create_factory_method(self):
        """Template.create() should set defaults correctly."""
        template = Template.create(name="My Template")
        assert template.name == "My Template"
        assert template.kind == TemplateKind.PDF
        assert template.status == TemplateStatus.DRAFT
        assert template.template_id is not None
        assert len(template.template_id) > 0

    def test_create_with_custom_id(self):
        """Template.create() should accept custom ID."""
        template = Template.create(
            name="Custom",
            template_id="custom-id-123",
        )
        assert template.template_id == "custom-id-123"

    def test_create_with_kind(self):
        """Template.create() should accept kind parameter."""
        template = Template.create(
            name="Excel Template",
            kind=TemplateKind.EXCEL,
        )
        assert template.kind == TemplateKind.EXCEL

    def test_template_defaults(self):
        """Template should have sensible defaults."""
        template = Template.create(name="Test")
        assert template.schema is None
        assert template.contract_id is None
        assert template.artifacts == []
        assert template.source_file is None
        assert template.description is None
        assert template.last_run_at is None
        assert template.run_count == 0
        assert template.tags == []

    def test_template_timestamps(self):
        """Template should have created_at and updated_at."""
        before = datetime.now(timezone.utc)
        template = Template.create(name="Test")
        after = datetime.now(timezone.utc)

        assert before <= template.created_at <= after
        assert before <= template.updated_at <= after


# =============================================================================
# Template Tests - State Transitions
# =============================================================================

class TestTemplateStateTransitions:
    """Tests for Template state machine transitions."""

    def test_transition_to_analyzing(self):
        """Should transition from draft to analyzing."""
        template = Template.create(name="Test")
        assert template.status == TemplateStatus.DRAFT

        template.transition_to(TemplateStatus.ANALYZING)
        assert template.status == TemplateStatus.ANALYZING

    def test_transition_to_mapped(self):
        """Should transition to mapped."""
        template = Template.create(name="Test")
        template.transition_to(TemplateStatus.MAPPED)
        assert template.status == TemplateStatus.MAPPED

    def test_transition_to_approved(self):
        """Should transition to approved."""
        template = Template.create(name="Test")
        template.transition_to(TemplateStatus.APPROVED)
        assert template.status == TemplateStatus.APPROVED

    def test_transition_to_failed(self):
        """Should transition to failed."""
        template = Template.create(name="Test")
        template.transition_to(TemplateStatus.FAILED)
        assert template.status == TemplateStatus.FAILED

    def test_transition_updates_timestamp(self):
        """Transition should update updated_at timestamp."""
        template = Template.create(name="Test")
        original_updated = template.updated_at

        import time
        time.sleep(0.01)  # Small delay to ensure timestamp difference

        template.transition_to(TemplateStatus.ANALYZING)
        assert template.updated_at >= original_updated

    def test_transition_back_to_draft(self):
        """Should allow transitioning back to draft."""
        template = Template.create(name="Test")
        template.transition_to(TemplateStatus.ANALYZING)
        template.transition_to(TemplateStatus.DRAFT)
        assert template.status == TemplateStatus.DRAFT


# =============================================================================
# Template Tests - Run Tracking
# =============================================================================

class TestTemplateRunTracking:
    """Tests for Template run tracking."""

    def test_record_run_increments_count(self):
        """record_run() should increment run_count."""
        template = Template.create(name="Test")
        assert template.run_count == 0

        template.record_run()
        assert template.run_count == 1

        template.record_run()
        assert template.run_count == 2

    def test_record_run_sets_last_run_at(self):
        """record_run() should set last_run_at."""
        template = Template.create(name="Test")
        assert template.last_run_at is None

        before = datetime.now(timezone.utc)
        template.record_run()
        after = datetime.now(timezone.utc)

        assert template.last_run_at is not None
        assert before <= template.last_run_at <= after

    def test_record_run_updates_timestamp(self):
        """record_run() should update updated_at."""
        template = Template.create(name="Test")
        original_updated = template.updated_at

        import time
        time.sleep(0.01)

        template.record_run()
        assert template.updated_at >= original_updated


# =============================================================================
# Template Tests - Artifact Management
# =============================================================================

class TestTemplateArtifactManagement:
    """Tests for Template artifact management."""

    def test_add_artifact(self):
        """Should add artifact to template."""
        template = Template.create(name="Test")
        artifact = Artifact(
            name="template.html",
            path=Path("/uploads/template.html"),
            artifact_type="html",
        )

        template.add_artifact(artifact)
        assert len(template.artifacts) == 1
        assert template.artifacts[0] == artifact

    def test_add_artifact_replaces_same_name(self):
        """Adding artifact with same name should replace existing."""
        template = Template.create(name="Test")
        artifact1 = Artifact(
            name="template.html",
            path=Path("/uploads/v1/template.html"),
            artifact_type="html",
        )
        artifact2 = Artifact(
            name="template.html",
            path=Path("/uploads/v2/template.html"),
            artifact_type="html",
        )

        template.add_artifact(artifact1)
        template.add_artifact(artifact2)

        assert len(template.artifacts) == 1
        assert template.artifacts[0].path == Path("/uploads/v2/template.html")

    def test_add_multiple_artifacts(self):
        """Should add multiple artifacts with different names."""
        template = Template.create(name="Test")
        artifact1 = Artifact(name="source.pdf", path=Path("/source.pdf"), artifact_type="pdf")
        artifact2 = Artifact(name="template.html", path=Path("/template.html"), artifact_type="html")

        template.add_artifact(artifact1)
        template.add_artifact(artifact2)

        assert len(template.artifacts) == 2

    def test_get_artifact_found(self):
        """get_artifact() should return artifact when found."""
        template = Template.create(name="Test")
        artifact = Artifact(name="template.html", path=Path("/template.html"), artifact_type="html")
        template.add_artifact(artifact)

        result = template.get_artifact("template.html")
        assert result == artifact

    def test_get_artifact_not_found(self):
        """get_artifact() should return None when not found."""
        template = Template.create(name="Test")
        result = template.get_artifact("nonexistent.html")
        assert result is None

    def test_add_artifact_updates_timestamp(self):
        """add_artifact() should update updated_at."""
        template = Template.create(name="Test")
        original_updated = template.updated_at

        import time
        time.sleep(0.01)

        artifact = Artifact(name="test.html", path=Path("/test.html"), artifact_type="html")
        template.add_artifact(artifact)

        assert template.updated_at >= original_updated


# =============================================================================
# Template Tests - Serialization
# =============================================================================

class TestTemplateSerialization:
    """Tests for Template serialization."""

    def test_to_dict_minimal(self):
        """to_dict() should serialize minimal template."""
        template = Template(
            template_id="tpl-123",
            name="Test",
            kind=TemplateKind.PDF,
            status=TemplateStatus.DRAFT,
        )

        data = template.to_dict()
        assert data["template_id"] == "tpl-123"
        assert data["name"] == "Test"
        assert data["kind"] == "pdf"
        assert data["status"] == "draft"
        assert data["schema"] is None
        assert data["artifacts"] == []

    def test_to_dict_with_schema(self):
        """to_dict() should serialize schema correctly."""
        schema = TemplateSchema(
            scalars=["title"],
            row_tokens=["amount"],
            totals=["total"],
            tables_detected=["items"],
            placeholders_found=3,
        )
        template = Template.create(name="Test", schema=schema)

        data = template.to_dict()
        assert data["schema"]["scalars"] == ["title"]
        assert data["schema"]["row_tokens"] == ["amount"]
        assert data["schema"]["totals"] == ["total"]
        assert data["schema"]["tables_detected"] == ["items"]
        assert data["schema"]["placeholders_found"] == 3

    def test_to_dict_with_artifacts(self):
        """to_dict() should serialize artifacts."""
        template = Template.create(name="Test")
        artifact = Artifact(
            name="test.html",
            path=Path("/uploads/test.html"),
            artifact_type="html",
            size_bytes=1024,
        )
        template.add_artifact(artifact)

        data = template.to_dict()
        assert len(data["artifacts"]) == 1
        assert data["artifacts"][0]["name"] == "test.html"
        # Path may use OS-specific separators
        assert "test.html" in data["artifacts"][0]["path"]
        assert data["artifacts"][0]["artifact_type"] == "html"
        assert data["artifacts"][0]["size_bytes"] == 1024

    def test_to_dict_datetime_format(self):
        """to_dict() should serialize datetimes as ISO format."""
        template = Template.create(name="Test")
        data = template.to_dict()

        # Should be valid ISO format
        datetime.fromisoformat(data["created_at"])
        datetime.fromisoformat(data["updated_at"])

    def test_from_dict_minimal(self):
        """from_dict() should deserialize minimal data."""
        data = {
            "template_id": "tpl-123",
            "name": "Test",
            "kind": "pdf",
            "status": "draft",
        }

        template = Template.from_dict(data)
        assert template.template_id == "tpl-123"
        assert template.name == "Test"
        assert template.kind == TemplateKind.PDF
        assert template.status == TemplateStatus.DRAFT

    def test_from_dict_with_schema(self):
        """from_dict() should deserialize schema."""
        data = {
            "template_id": "tpl-123",
            "name": "Test",
            "kind": "pdf",
            "status": "draft",
            "schema": {
                "scalars": ["title"],
                "row_tokens": ["amount"],
                "totals": ["total"],
                "tables_detected": ["items"],
                "placeholders_found": 3,
            },
        }

        template = Template.from_dict(data)
        assert template.schema is not None
        assert template.schema.scalars == ["title"]
        assert template.schema.row_tokens == ["amount"]

    def test_from_dict_with_artifacts(self):
        """from_dict() should deserialize artifacts."""
        data = {
            "template_id": "tpl-123",
            "name": "Test",
            "kind": "pdf",
            "status": "draft",
            "artifacts": [
                {
                    "name": "test.html",
                    "path": "/uploads/test.html",
                    "artifact_type": "html",
                    "size_bytes": 1024,
                }
            ],
        }

        template = Template.from_dict(data)
        assert len(template.artifacts) == 1
        assert template.artifacts[0].name == "test.html"
        assert template.artifacts[0].path == Path("/uploads/test.html")

    def test_from_dict_with_datetime_strings(self):
        """from_dict() should parse datetime strings."""
        data = {
            "template_id": "tpl-123",
            "name": "Test",
            "kind": "pdf",
            "status": "draft",
            "created_at": "2025-01-15T10:30:00+00:00",
            "updated_at": "2025-01-15T11:00:00+00:00",
            "last_run_at": "2025-01-15T12:00:00+00:00",
        }

        template = Template.from_dict(data)
        assert template.created_at.year == 2025
        assert template.last_run_at is not None
        assert template.last_run_at.hour == 12

    def test_roundtrip_serialization(self):
        """to_dict/from_dict should roundtrip correctly."""
        original = Template.create(
            name="Test Template",
            kind=TemplateKind.EXCEL,
            template_id="roundtrip-123",
            description="Test description",
            tags=["finance", "monthly"],
        )
        original.transition_to(TemplateStatus.APPROVED)
        original.record_run()
        original.add_artifact(Artifact(
            name="source.xlsx",
            path=Path("/uploads/source.xlsx"),
            artifact_type="excel",
            size_bytes=2048,
        ))

        # Serialize and deserialize
        data = original.to_dict()
        restored = Template.from_dict(data)

        # Verify all fields match
        assert restored.template_id == original.template_id
        assert restored.name == original.name
        assert restored.kind == original.kind
        assert restored.status == original.status
        assert restored.description == original.description
        assert restored.tags == original.tags
        assert restored.run_count == original.run_count
        assert len(restored.artifacts) == len(original.artifacts)

    def test_to_dict_json_serializable(self):
        """to_dict() result should be JSON serializable."""
        template = Template.create(name="Test")
        template.add_artifact(Artifact(
            name="test.html",
            path=Path("/test.html"),
            artifact_type="html",
        ))

        data = template.to_dict()
        # Should not raise
        json_str = json.dumps(data)
        assert json_str is not None


# =============================================================================
# Template Tests - Edge Cases
# =============================================================================

class TestTemplateEdgeCases:
    """Tests for Template edge cases."""

    def test_empty_name(self):
        """Template with empty name should still work."""
        template = Template(
            template_id="tpl-123",
            name="",
            kind=TemplateKind.PDF,
            status=TemplateStatus.DRAFT,
        )
        assert template.name == ""

    def test_unicode_name(self):
        """Template should handle unicode names."""
        template = Template.create(name="Rapport financier")
        assert template.name == "Rapport financier"

        data = template.to_dict()
        restored = Template.from_dict(data)
        assert restored.name == "Rapport financier"

    def test_special_characters_in_tags(self):
        """Tags should handle special characters."""
        tags = ["tag-with-dash", "tag_with_underscore", "CamelCase"]
        template = Template.create(name="Test", tags=tags)
        assert template.tags == tags

    def test_long_description(self):
        """Should handle long descriptions."""
        description = "A" * 10000
        template = Template.create(name="Test", description=description)
        assert len(template.description) == 10000

    def test_many_artifacts(self):
        """Should handle many artifacts."""
        template = Template.create(name="Test")
        for i in range(100):
            artifact = Artifact(
                name=f"file_{i}.html",
                path=Path(f"/uploads/file_{i}.html"),
                artifact_type="html",
            )
            template.add_artifact(artifact)

        assert len(template.artifacts) == 100

    def test_status_defaults_on_missing(self):
        """from_dict should default to draft status if missing."""
        data = {
            "template_id": "tpl-123",
            "name": "Test",
        }
        template = Template.from_dict(data)
        assert template.status == TemplateStatus.DRAFT

    def test_kind_defaults_on_missing(self):
        """from_dict should default to pdf kind if missing."""
        data = {
            "template_id": "tpl-123",
            "name": "Test",
        }
        template = Template.from_dict(data)
        assert template.kind == TemplateKind.PDF
