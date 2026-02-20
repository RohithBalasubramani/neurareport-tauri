"""
Property-based tests for template domain models.

Uses hypothesis to test invariants that should always hold.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from hypothesis import given, strategies as st, settings, assume

from backend.engine.domain.templates import (
    Artifact,
    Template,
    TemplateKind,
    TemplateSchema,
    TemplateStatus,
)


# =============================================================================
# Strategies for generating test data
# =============================================================================

# Template ID strategy - alphanumeric with dashes
template_id_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789-_",
    min_size=1,
    max_size=64,
)

# Template name strategy - printable strings
template_name_strategy = st.text(min_size=1, max_size=100)

# Tag strategy - lowercase alphanumeric with dashes
tag_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789-_",
    min_size=1,
    max_size=50,
)

# Token strategy for schema
token_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789_{}_",
    min_size=1,
    max_size=50,
)


# =============================================================================
# Template Property Tests
# =============================================================================

class TestTemplateProperties:
    """Property-based tests for Template invariants."""

    @given(
        name=template_name_strategy,
        kind=st.sampled_from(list(TemplateKind)),
    )
    @settings(max_examples=50)
    def test_create_preserves_values(self, name: str, kind: TemplateKind):
        """Template.create() should preserve provided values."""
        assume(len(name.strip()) > 0)

        template = Template.create(name=name, kind=kind)

        assert template.name == name
        assert template.kind == kind
        assert template.status == TemplateStatus.DRAFT

    @given(
        template_id=template_id_strategy,
        name=template_name_strategy,
    )
    @settings(max_examples=50)
    def test_template_id_preserved(self, template_id: str, name: str):
        """Custom template ID should be preserved."""
        assume(len(template_id.strip()) > 0 and len(name.strip()) > 0)

        template = Template.create(name=name, template_id=template_id)

        assert template.template_id == template_id

    @given(tags=st.lists(tag_strategy, max_size=20))
    @settings(max_examples=30)
    def test_tags_preserved(self, tags: list[str]):
        """Tags should be preserved."""
        template = Template.create(name="Test", tags=tags)

        assert template.tags == tags

    @given(run_count=st.integers(min_value=0, max_value=1000))
    @settings(max_examples=30)
    def test_record_run_increments_correctly(self, run_count: int):
        """record_run() should always increment by 1."""
        template = Template.create(name="Test")
        template.run_count = run_count  # Set initial count

        template.record_run()

        assert template.run_count == run_count + 1

    @given(st.sampled_from(list(TemplateStatus)))
    @settings(max_examples=10)
    def test_transition_to_any_status(self, target_status: TemplateStatus):
        """Should be able to transition to any status."""
        template = Template.create(name="Test")

        template.transition_to(target_status)

        assert template.status == target_status


# =============================================================================
# Artifact Property Tests
# =============================================================================

class TestArtifactProperties:
    """Property-based tests for Artifact invariants."""

    @given(
        name=st.text(min_size=1, max_size=100),
        artifact_type=st.text(min_size=1, max_size=20),
        size_bytes=st.integers(min_value=0, max_value=10**12),
    )
    @settings(max_examples=50)
    def test_artifact_preserves_values(self, name: str, artifact_type: str, size_bytes: int):
        """Artifact should preserve all values."""
        assume(len(name.strip()) > 0 and len(artifact_type.strip()) > 0)

        artifact = Artifact(
            name=name,
            path=Path(f"/uploads/{name}"),
            artifact_type=artifact_type,
            size_bytes=size_bytes,
        )

        assert artifact.name == name
        assert artifact.artifact_type == artifact_type
        assert artifact.size_bytes == size_bytes

    @given(names=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10))
    @settings(max_examples=30)
    def test_add_artifact_deduplication(self, names: list[str]):
        """Adding artifacts with same name should replace."""
        assume(all(len(n.strip()) > 0 for n in names))

        template = Template.create(name="Test")

        for i, name in enumerate(names):
            artifact = Artifact(
                name=name,
                path=Path(f"/uploads/v{i}/{name}"),
                artifact_type="test",
            )
            template.add_artifact(artifact)

        # Unique names only
        unique_names = set(names)
        assert len(template.artifacts) == len(unique_names)

    @given(
        artifact_count=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=20)
    def test_many_unique_artifacts(self, artifact_count: int):
        """Should handle many unique artifacts."""
        template = Template.create(name="Test")

        for i in range(artifact_count):
            artifact = Artifact(
                name=f"artifact_{i}.html",
                path=Path(f"/uploads/artifact_{i}.html"),
                artifact_type="html",
            )
            template.add_artifact(artifact)

        assert len(template.artifacts) == artifact_count


# =============================================================================
# Schema Property Tests
# =============================================================================

class TestSchemaProperties:
    """Property-based tests for TemplateSchema."""

    @given(
        scalars=st.lists(token_strategy, max_size=20),
        row_tokens=st.lists(token_strategy, max_size=20),
        totals=st.lists(token_strategy, max_size=10),
    )
    @settings(max_examples=30)
    def test_schema_preserves_tokens(
        self, scalars: list[str], row_tokens: list[str], totals: list[str]
    ):
        """Schema should preserve all token lists."""
        schema = TemplateSchema(
            scalars=scalars,
            row_tokens=row_tokens,
            totals=totals,
        )

        assert schema.scalars == scalars
        assert schema.row_tokens == row_tokens
        assert schema.totals == totals

    @given(placeholder_count=st.integers(min_value=0, max_value=1000))
    @settings(max_examples=20)
    def test_placeholder_count_preserved(self, placeholder_count: int):
        """Placeholder count should be preserved."""
        schema = TemplateSchema(placeholders_found=placeholder_count)

        assert schema.placeholders_found == placeholder_count


# =============================================================================
# Serialization Property Tests
# =============================================================================

class TestSerializationProperties:
    """Property-based tests for serialization roundtrips."""

    @given(
        name=template_name_strategy,
        kind=st.sampled_from(list(TemplateKind)),
        status=st.sampled_from(list(TemplateStatus)),
        tags=st.lists(tag_strategy, max_size=10),
        run_count=st.integers(min_value=0, max_value=10000),
    )
    @settings(max_examples=50)
    def test_roundtrip_preserves_basic_fields(
        self,
        name: str,
        kind: TemplateKind,
        status: TemplateStatus,
        tags: list[str],
        run_count: int,
    ):
        """to_dict/from_dict should preserve basic fields."""
        assume(len(name.strip()) > 0)

        original = Template.create(name=name, kind=kind, tags=tags)
        original.transition_to(status)
        original.run_count = run_count

        # Roundtrip
        data = original.to_dict()
        restored = Template.from_dict(data)

        assert restored.name == original.name
        assert restored.kind == original.kind
        assert restored.status == original.status
        assert restored.tags == original.tags
        assert restored.run_count == original.run_count

    @given(
        scalars=st.lists(st.text(min_size=1, max_size=30), max_size=10),
        row_tokens=st.lists(st.text(min_size=1, max_size=30), max_size=10),
    )
    @settings(max_examples=30)
    def test_roundtrip_preserves_schema(self, scalars: list[str], row_tokens: list[str]):
        """Roundtrip should preserve schema."""
        assume(all(len(s.strip()) > 0 for s in scalars))
        assume(all(len(r.strip()) > 0 for r in row_tokens))

        schema = TemplateSchema(scalars=scalars, row_tokens=row_tokens)
        original = Template.create(name="Test", schema=schema)

        data = original.to_dict()
        restored = Template.from_dict(data)

        assert restored.schema is not None
        assert restored.schema.scalars == original.schema.scalars
        assert restored.schema.row_tokens == original.schema.row_tokens

    @given(
        name=template_name_strategy,
        description=st.text(max_size=500),
    )
    @settings(max_examples=30)
    def test_to_dict_is_json_serializable(self, name: str, description: str):
        """to_dict() result should always be JSON serializable."""
        assume(len(name.strip()) > 0)

        template = Template.create(name=name, description=description)
        template.add_artifact(Artifact(
            name="test.html",
            path=Path("/test.html"),
            artifact_type="html",
        ))

        data = template.to_dict()

        # Should not raise
        json_str = json.dumps(data)
        assert json_str is not None

        # Should be deserializable
        parsed = json.loads(json_str)
        assert parsed["name"] == name


# =============================================================================
# Status Transition Property Tests
# =============================================================================

class TestStatusTransitionProperties:
    """Property-based tests for status transitions."""

    @given(
        transitions=st.lists(
            st.sampled_from(list(TemplateStatus)),
            min_size=1,
            max_size=20,
        )
    )
    @settings(max_examples=30)
    def test_multiple_transitions(self, transitions: list[TemplateStatus]):
        """Should handle multiple transitions."""
        template = Template.create(name="Test")

        for status in transitions:
            template.transition_to(status)

        # Final status should be the last in the list
        assert template.status == transitions[-1]

    @given(
        transitions=st.lists(
            st.sampled_from(list(TemplateStatus)),
            min_size=1,
            max_size=50,
        )
    )
    @settings(max_examples=20)
    def test_transitions_update_timestamp(self, transitions: list[TemplateStatus]):
        """Each transition should update timestamp."""
        template = Template.create(name="Test")
        timestamps = [template.updated_at]

        import time
        for status in transitions:
            time.sleep(0.001)  # Tiny delay
            template.transition_to(status)
            timestamps.append(template.updated_at)

        # Timestamps should be non-decreasing
        for i in range(1, len(timestamps)):
            assert timestamps[i] >= timestamps[i - 1]


# =============================================================================
# Edge Case Property Tests
# =============================================================================

class TestEdgeCaseProperties:
    """Property-based tests for edge cases."""

    @given(st.text())
    @settings(max_examples=50)
    def test_any_string_as_name(self, name: str):
        """Should handle any string as name."""
        # Should not crash
        template = Template.create(name=name)
        assert template.name == name

    @given(st.text())
    @settings(max_examples=50)
    def test_any_string_as_description(self, description: str):
        """Should handle any string as description."""
        template = Template.create(name="Test", description=description)
        assert template.description == description

    @given(st.lists(st.text(), max_size=100))
    @settings(max_examples=30)
    def test_any_strings_as_tags(self, tags: list[str]):
        """Should handle any strings as tags."""
        template = Template.create(name="Test", tags=tags)
        assert template.tags == tags

    @given(
        empty_name=st.just(""),
        with_spaces=st.just("   "),
        with_newlines=st.just("line1\nline2"),
        with_tabs=st.just("col1\tcol2"),
    )
    @settings(max_examples=10)
    def test_special_string_values(
        self, empty_name, with_spaces, with_newlines, with_tabs
    ):
        """Should handle special string values."""
        # Empty name
        t1 = Template.create(name=empty_name)
        assert t1.name == ""

        # Whitespace name
        t2 = Template.create(name=with_spaces)
        assert t2.name == with_spaces

        # Newlines in name
        t3 = Template.create(name=with_newlines)
        assert "\n" in t3.name

        # Tabs in name
        t4 = Template.create(name=with_tabs)
        assert "\t" in t4.name


# =============================================================================
# Invariant Property Tests
# =============================================================================

class TestInvariantProperties:
    """Tests for invariants that should always hold."""

    @given(st.integers(min_value=0, max_value=100))
    @settings(max_examples=20)
    def test_run_count_never_decreases(self, initial_count: int):
        """Run count should never decrease via record_run()."""
        template = Template.create(name="Test")
        template.run_count = initial_count

        counts = [template.run_count]
        for _ in range(10):
            template.record_run()
            counts.append(template.run_count)

        # Should be strictly increasing
        for i in range(1, len(counts)):
            assert counts[i] > counts[i - 1]

    @given(
        artifact_names=st.lists(
            st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=20),
            min_size=1,
            max_size=20,
            unique=True,
        )
    )
    @settings(max_examples=30)
    def test_get_artifact_finds_added(self, artifact_names: list[str]):
        """get_artifact should find all added artifacts."""
        template = Template.create(name="Test")

        for name in artifact_names:
            artifact = Artifact(name=name, path=Path(f"/{name}"), artifact_type="test")
            template.add_artifact(artifact)

        for name in artifact_names:
            found = template.get_artifact(name)
            assert found is not None
            assert found.name == name

    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=20)
    def test_get_artifact_not_found_returns_none(self, search_name: str):
        """get_artifact should return None for missing artifacts."""
        template = Template.create(name="Test")
        # Add an artifact with a different name
        template.add_artifact(Artifact(
            name="existing.html",
            path=Path("/existing.html"),
            artifact_type="html",
        ))

        assume(search_name != "existing.html")

        result = template.get_artifact(search_name)
        assert result is None

    @given(
        kind=st.sampled_from(list(TemplateKind)),
        status=st.sampled_from(list(TemplateStatus)),
    )
    @settings(max_examples=20)
    def test_enum_values_serialized_correctly(
        self, kind: TemplateKind, status: TemplateStatus
    ):
        """Enum values should serialize to strings."""
        template = Template.create(name="Test", kind=kind)
        template.transition_to(status)

        data = template.to_dict()

        assert data["kind"] == kind.value
        assert data["status"] == status.value
        assert isinstance(data["kind"], str)
        assert isinstance(data["status"], str)


# =============================================================================
# Timestamps Property Tests
# =============================================================================

class TestTimestampProperties:
    """Property-based tests for timestamp behavior."""

    @given(st.integers(min_value=1, max_value=20))
    @settings(max_examples=10)
    def test_updated_at_monotonic_with_operations(self, operation_count: int):
        """updated_at should be monotonically non-decreasing."""
        template = Template.create(name="Test")
        timestamps = [template.updated_at]

        import time
        for i in range(operation_count):
            time.sleep(0.001)
            if i % 3 == 0:
                template.record_run()
            elif i % 3 == 1:
                template.transition_to(TemplateStatus.ANALYZING)
            else:
                template.add_artifact(Artifact(
                    name=f"artifact_{i}.html",
                    path=Path(f"/artifact_{i}.html"),
                    artifact_type="html",
                ))
            timestamps.append(template.updated_at)

        # All timestamps should be non-decreasing
        for i in range(1, len(timestamps)):
            assert timestamps[i] >= timestamps[i - 1]

    @given(st.datetimes(timezones=st.just(timezone.utc)))
    @settings(max_examples=20)
    def test_datetime_serialization(self, dt: datetime):
        """Datetime should serialize and deserialize correctly."""
        template = Template(
            template_id="test-123",
            name="Test",
            kind=TemplateKind.PDF,
            status=TemplateStatus.DRAFT,
            created_at=dt,
            updated_at=dt,
        )

        data = template.to_dict()

        # Should be ISO format
        assert "T" in data["created_at"]

        # Should roundtrip
        restored = Template.from_dict(data)
        # Allow small differences due to microsecond precision
        assert abs((restored.created_at - dt).total_seconds()) < 1
