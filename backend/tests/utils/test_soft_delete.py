"""Comprehensive tests for backend.app.utils.soft_delete.

Coverage layers:
  1. Unit tests — DeletionStatus enum, SoftDeleteMetadata, SoftDeletable defaults/methods
  2. Integration tests — SoftDeleteManager filters/batch ops, soft_deletable_dict, full lifecycle
  3. Property-based — Hypothesis: random retention_days, deleted_by, round-trip invariants
  4. Failure injection — double soft_delete, restore on permanently deleted, empty cleanup
  5. Concurrency — thread-safety of status transitions
  6. Security / abuse — long strings, Unicode, XSS payloads, negative retention_days
  7. Usability — realistic session soft-delete scenario, batch operations
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from unittest.mock import patch

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from backend.app.utils.soft_delete import (
    DEFAULT_RETENTION_DAYS,
    DeletionStatus,
    SoftDeleteMetadata,
    SoftDeletable,
    SoftDeleteManager,
    soft_deletable_dict,
)


# ---------------------------------------------------------------------------
# Test fixture: concrete subclass of SoftDeletable
# ---------------------------------------------------------------------------

@dataclass
class SampleSession(SoftDeletable):
    id: str = ""
    name: str = ""


@dataclass
class SampleDocument(SoftDeletable):
    doc_id: int = 0
    title: str = ""
    content: str = ""


# ---------------------------------------------------------------------------
# Helper: frozen datetime for deterministic tests
# ---------------------------------------------------------------------------

FROZEN_NOW = datetime(2025, 6, 15, 12, 0, 0)


def _frozen_utcnow():
    return FROZEN_NOW


# ==========================================================================
# 1. UNIT TESTS
# ==========================================================================


class TestDeletionStatusEnum:
    """Verify enum values and membership."""

    def test_active_value(self):
        assert DeletionStatus.ACTIVE == "active"
        assert DeletionStatus.ACTIVE.value == "active"

    def test_soft_deleted_value(self):
        assert DeletionStatus.SOFT_DELETED == "soft_deleted"
        assert DeletionStatus.SOFT_DELETED.value == "soft_deleted"

    def test_permanently_deleted_value(self):
        assert DeletionStatus.PERMANENTLY_DELETED == "permanently_deleted"
        assert DeletionStatus.PERMANENTLY_DELETED.value == "permanently_deleted"

    def test_enum_is_str(self):
        """DeletionStatus inherits from str."""
        assert isinstance(DeletionStatus.ACTIVE, str)

    def test_enum_members_count(self):
        assert len(DeletionStatus) == 3


class TestSoftDeleteMetadata:
    """Construction, is_expired, days_until_expiry."""

    def test_construction_minimal(self):
        meta = SoftDeleteMetadata(deleted_at=FROZEN_NOW)
        assert meta.deleted_at == FROZEN_NOW
        assert meta.deleted_by is None
        assert meta.reason is None
        assert meta.expires_at is None
        assert meta.original_data is None

    def test_construction_full(self):
        expires = FROZEN_NOW + timedelta(days=30)
        meta = SoftDeleteMetadata(
            deleted_at=FROZEN_NOW,
            deleted_by="admin@test.com",
            reason="cleanup",
            expires_at=expires,
            original_data={"key": "val"},
        )
        assert meta.deleted_by == "admin@test.com"
        assert meta.reason == "cleanup"
        assert meta.expires_at == expires
        assert meta.original_data == {"key": "val"}

    def test_is_expired_no_expiry(self):
        """No expires_at means never expired."""
        meta = SoftDeleteMetadata(deleted_at=FROZEN_NOW, expires_at=None)
        assert meta.is_expired() is False

    @patch("backend.app.utils.soft_delete.datetime")
    def test_is_expired_true(self, mock_dt):
        """When utcnow() is past expires_at, item is expired."""
        expires = FROZEN_NOW + timedelta(days=30)
        mock_dt.utcnow.return_value = expires + timedelta(seconds=1)
        meta = SoftDeleteMetadata(deleted_at=FROZEN_NOW, expires_at=expires)
        assert meta.is_expired() is True

    @patch("backend.app.utils.soft_delete.datetime")
    def test_is_expired_false(self, mock_dt):
        """When utcnow() is before expires_at, item is not expired."""
        expires = FROZEN_NOW + timedelta(days=30)
        mock_dt.utcnow.return_value = FROZEN_NOW + timedelta(days=15)
        meta = SoftDeleteMetadata(deleted_at=FROZEN_NOW, expires_at=expires)
        assert meta.is_expired() is False

    def test_days_until_expiry_no_expiry(self):
        meta = SoftDeleteMetadata(deleted_at=FROZEN_NOW, expires_at=None)
        assert meta.days_until_expiry() is None

    @patch("backend.app.utils.soft_delete.datetime")
    def test_days_until_expiry_positive(self, mock_dt):
        expires = FROZEN_NOW + timedelta(days=30)
        mock_dt.utcnow.return_value = FROZEN_NOW + timedelta(days=10)
        meta = SoftDeleteMetadata(deleted_at=FROZEN_NOW, expires_at=expires)
        assert meta.days_until_expiry() == 20

    @patch("backend.app.utils.soft_delete.datetime")
    def test_days_until_expiry_zero_when_past(self, mock_dt):
        """days_until_expiry returns 0 (not negative) when past expiry."""
        expires = FROZEN_NOW + timedelta(days=30)
        mock_dt.utcnow.return_value = expires + timedelta(days=5)
        meta = SoftDeleteMetadata(deleted_at=FROZEN_NOW, expires_at=expires)
        assert meta.days_until_expiry() == 0

    @patch("backend.app.utils.soft_delete.datetime")
    def test_days_until_expiry_exact_boundary(self, mock_dt):
        """At exactly the expiry time, days=0."""
        expires = FROZEN_NOW + timedelta(days=30)
        mock_dt.utcnow.return_value = expires
        meta = SoftDeleteMetadata(deleted_at=FROZEN_NOW, expires_at=expires)
        assert meta.days_until_expiry() == 0


class TestSoftDeletableDefaults:
    """Default state is ACTIVE, properties work correctly."""

    def test_default_state_is_active(self):
        session = SampleSession(id="1", name="s1")
        assert session._deletion_status == DeletionStatus.ACTIVE
        assert session._deletion_metadata is None

    def test_is_active_property(self):
        session = SampleSession(id="1", name="s1")
        assert session.is_active is True

    def test_is_deleted_property_when_active(self):
        session = SampleSession(id="1", name="s1")
        assert session.is_deleted is False

    def test_deletion_metadata_returns_none_when_active(self):
        session = SampleSession(id="1", name="s1")
        assert session.deletion_metadata is None


class TestSoftDeletableSoftDelete:
    """soft_delete() method."""

    @patch("backend.app.utils.soft_delete.datetime")
    def test_soft_delete_returns_true_on_first_call(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        result = session.soft_delete(deleted_by="admin", reason="test")
        assert result is True

    @patch("backend.app.utils.soft_delete.datetime")
    def test_soft_delete_sets_status(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.soft_delete()
        assert session._deletion_status == DeletionStatus.SOFT_DELETED
        assert session.is_deleted is True
        assert session.is_active is False

    @patch("backend.app.utils.soft_delete.datetime")
    def test_soft_delete_sets_metadata(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.soft_delete(deleted_by="user@x.com", reason="no longer needed", retention_days=15)
        meta = session._deletion_metadata
        assert meta is not None
        assert meta.deleted_at == FROZEN_NOW
        assert meta.deleted_by == "user@x.com"
        assert meta.reason == "no longer needed"
        assert meta.expires_at == FROZEN_NOW + timedelta(days=15)

    @patch("backend.app.utils.soft_delete.datetime")
    def test_soft_delete_preserves_data_by_default(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="42", name="my_session")
        session.soft_delete()
        meta = session._deletion_metadata
        assert meta.original_data is not None
        assert meta.original_data["id"] == "42"
        assert meta.original_data["name"] == "my_session"

    @patch("backend.app.utils.soft_delete.datetime")
    def test_soft_delete_no_preserve(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.soft_delete(preserve_data=False)
        assert session._deletion_metadata.original_data is None

    @patch("backend.app.utils.soft_delete.datetime")
    def test_soft_delete_zero_retention_no_expiry(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.soft_delete(retention_days=0)
        assert session._deletion_metadata.expires_at is None

    @patch("backend.app.utils.soft_delete.datetime")
    def test_deletion_metadata_property_returns_metadata_when_deleted(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.soft_delete(reason="bye")
        assert session.deletion_metadata is not None
        assert session.deletion_metadata.reason == "bye"


class TestSoftDeletableRestore:
    """restore() method."""

    @patch("backend.app.utils.soft_delete.datetime")
    def test_restore_returns_true_when_soft_deleted(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.soft_delete()
        result = session.restore()
        assert result is True

    @patch("backend.app.utils.soft_delete.datetime")
    def test_restore_sets_active(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.soft_delete()
        session.restore()
        assert session.is_active is True
        assert session.is_deleted is False
        assert session._deletion_metadata is None

    def test_restore_returns_false_when_active(self):
        session = SampleSession(id="1", name="s1")
        assert session.restore() is False

    @patch("backend.app.utils.soft_delete.datetime")
    def test_restore_returns_false_when_permanently_deleted(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.permanently_delete()
        assert session.restore() is False


class TestSoftDeletablePermanentlyDelete:
    """permanently_delete() method."""

    def test_permanently_delete_from_active(self):
        session = SampleSession(id="1", name="s1")
        result = session.permanently_delete()
        assert result is True
        assert session._deletion_status == DeletionStatus.PERMANENTLY_DELETED

    @patch("backend.app.utils.soft_delete.datetime")
    def test_permanently_delete_from_soft_deleted(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.soft_delete()
        result = session.permanently_delete()
        assert result is True
        assert session._deletion_status == DeletionStatus.PERMANENTLY_DELETED

    def test_permanently_deleted_is_not_active(self):
        session = SampleSession(id="1", name="s1")
        session.permanently_delete()
        assert session.is_active is False

    def test_permanently_deleted_is_not_soft_deleted(self):
        session = SampleSession(id="1", name="s1")
        session.permanently_delete()
        assert session.is_deleted is False


class TestGetPreservableData:
    """_get_preservable_data returns only public attributes."""

    def test_only_public_attrs(self):
        session = SampleSession(id="abc", name="sess")
        data = session._get_preservable_data()
        assert "id" in data
        assert "name" in data
        # Private attrs should be excluded
        assert "_deletion_status" not in data
        assert "_deletion_metadata" not in data

    def test_subclass_with_more_fields(self):
        doc = SampleDocument(doc_id=99, title="Report", content="body text")
        data = doc._get_preservable_data()
        assert data["doc_id"] == 99
        assert data["title"] == "Report"
        assert data["content"] == "body text"
        assert "_deletion_status" not in data


# ==========================================================================
# 2. INTEGRATION TESTS
# ==========================================================================


class TestSoftDeleteManagerFilterActive:

    @patch("backend.app.utils.soft_delete.datetime")
    def test_filter_active(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        s1 = SampleSession(id="1", name="active")
        s2 = SampleSession(id="2", name="deleted")
        s2.soft_delete()
        s3 = SampleSession(id="3", name="also_active")

        manager = SoftDeleteManager()
        active = manager.filter_active([s1, s2, s3])
        assert len(active) == 2
        assert s1 in active
        assert s3 in active

    def test_filter_active_empty_list(self):
        manager = SoftDeleteManager()
        assert manager.filter_active([]) == []


class TestSoftDeleteManagerFilterDeleted:

    @patch("backend.app.utils.soft_delete.datetime")
    def test_filter_deleted(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        s1 = SampleSession(id="1", name="active")
        s2 = SampleSession(id="2", name="deleted")
        s2.soft_delete()

        manager = SoftDeleteManager()
        deleted = manager.filter_deleted([s1, s2])
        assert len(deleted) == 1
        assert s2 in deleted


class TestSoftDeleteManagerFilterExpired:

    @patch("backend.app.utils.soft_delete.datetime")
    def test_filter_expired(self, mock_dt):
        # Step 1: soft_delete with retention_days=1 at FROZEN_NOW
        mock_dt.utcnow.return_value = FROZEN_NOW
        mock_dt.side_effect = None
        s1 = SampleSession(id="1", name="expired_soon")
        s1.soft_delete(retention_days=1)
        s2 = SampleSession(id="2", name="not_expired")
        s2.soft_delete(retention_days=365)

        # Step 2: advance time to 2 days later for expiry check
        mock_dt.utcnow.return_value = FROZEN_NOW + timedelta(days=2)

        manager = SoftDeleteManager()
        expired = manager.filter_expired([s1, s2])
        assert len(expired) == 1
        assert s1 in expired


class TestSoftDeleteManagerCleanupExpired:

    @patch("backend.app.utils.soft_delete.datetime")
    def test_cleanup_expired(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        s1 = SampleSession(id="1", name="exp")
        s1.soft_delete(retention_days=1)
        s2 = SampleSession(id="2", name="keep")
        s2.soft_delete(retention_days=365)
        s3 = SampleSession(id="3", name="active")

        # Advance time past s1's expiry
        mock_dt.utcnow.return_value = FROZEN_NOW + timedelta(days=2)

        manager = SoftDeleteManager()
        count, remaining = manager.cleanup_expired([s1, s2, s3])
        assert count == 1
        assert s1 not in remaining
        assert s2 in remaining
        assert s3 in remaining
        assert s1._deletion_status == DeletionStatus.PERMANENTLY_DELETED


class TestSoftDeleteManagerRestoreAll:

    @patch("backend.app.utils.soft_delete.datetime")
    def test_restore_all(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        s1 = SampleSession(id="1", name="d1")
        s2 = SampleSession(id="2", name="d2")
        s3 = SampleSession(id="3", name="active")
        s1.soft_delete()
        s2.soft_delete()

        manager = SoftDeleteManager()
        restored = manager.restore_all([s1, s2, s3])
        assert restored == 2
        assert s1.is_active
        assert s2.is_active
        assert s3.is_active


class TestSoftDeleteManagerGetRecoveryInfo:

    @patch("backend.app.utils.soft_delete.datetime")
    def test_recovery_info_for_deleted_item(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.soft_delete(deleted_by="admin", reason="cleanup", retention_days=30)

        manager = SoftDeleteManager()
        info = manager.get_recovery_info(session)
        assert info is not None
        assert info["deleted_at"] == FROZEN_NOW.isoformat()
        assert info["deleted_by"] == "admin"
        assert info["reason"] == "cleanup"
        assert info["can_restore"] is True
        assert info["has_preserved_data"] is True
        assert isinstance(info["days_until_permanent_deletion"], int)

    def test_recovery_info_returns_none_for_active(self):
        session = SampleSession(id="1", name="s1")
        manager = SoftDeleteManager()
        assert manager.get_recovery_info(session) is None

    @patch("backend.app.utils.soft_delete.datetime")
    def test_recovery_info_expired_item(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.soft_delete(retention_days=1)

        # Advance past expiry
        mock_dt.utcnow.return_value = FROZEN_NOW + timedelta(days=5)
        manager = SoftDeleteManager()
        info = manager.get_recovery_info(session)
        assert info is not None
        assert info["can_restore"] is False
        assert info["days_until_permanent_deletion"] == 0


class TestSoftDeletableDict:

    def test_active_item(self):
        session = SampleSession(id="1", name="s1")
        d = soft_deletable_dict(session)
        assert d["id"] == "1"
        assert d["name"] == "s1"
        assert d["_is_deleted"] is False
        assert "_deletion_info" not in d

    @patch("backend.app.utils.soft_delete.datetime")
    def test_deleted_item(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="2", name="gone")
        session.soft_delete(deleted_by="user", reason="bye", retention_days=10)

        d = soft_deletable_dict(session)
        assert d["_is_deleted"] is True
        assert "_deletion_info" in d
        info = d["_deletion_info"]
        assert info["deleted_at"] == FROZEN_NOW.isoformat()
        assert info["deleted_by"] == "user"
        assert info["reason"] == "bye"
        assert isinstance(info["days_until_permanent_deletion"], int)


class TestFullLifecycle:
    """Integration: create -> soft_delete -> restore -> soft_delete -> permanently_delete."""

    @patch("backend.app.utils.soft_delete.datetime")
    def test_full_lifecycle(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW

        session = SampleSession(id="lifecycle", name="test")
        assert session.is_active is True
        assert session.is_deleted is False

        # Soft delete
        assert session.soft_delete(deleted_by="admin", reason="first delete") is True
        assert session.is_deleted is True
        assert session.is_active is False
        assert session.deletion_metadata is not None
        assert session.deletion_metadata.reason == "first delete"

        # Restore
        assert session.restore() is True
        assert session.is_active is True
        assert session.is_deleted is False
        assert session.deletion_metadata is None

        # Soft delete again
        assert session.soft_delete(deleted_by="admin", reason="second delete") is True
        assert session.is_deleted is True
        assert session.deletion_metadata.reason == "second delete"

        # Permanently delete
        assert session.permanently_delete() is True
        assert session._deletion_status == DeletionStatus.PERMANENTLY_DELETED
        assert session.is_active is False
        assert session.is_deleted is False

    @patch("backend.app.utils.soft_delete.datetime")
    def test_lifecycle_with_manager(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        manager = SoftDeleteManager(retention_days=7)

        items = [
            SampleSession(id="1", name="a"),
            SampleSession(id="2", name="b"),
            SampleSession(id="3", name="c"),
        ]

        # Delete two
        items[0].soft_delete(retention_days=1)
        items[1].soft_delete(retention_days=365)

        assert len(manager.filter_active(items)) == 1
        assert len(manager.filter_deleted(items)) == 2

        # Advance time: item 0 expires
        mock_dt.utcnow.return_value = FROZEN_NOW + timedelta(days=2)
        count, remaining = manager.cleanup_expired(items)
        assert count == 1
        assert len(remaining) == 2


# ==========================================================================
# 3. PROPERTY-BASED TESTS (Hypothesis)
# ==========================================================================


class TestPropertyBased:

    @given(retention_days=st.integers(min_value=1, max_value=365))
    @settings(max_examples=50)
    def test_soft_delete_restore_round_trip(self, retention_days):
        """soft_delete + restore always returns to active state."""
        session = SampleSession(id="prop", name="prop_test")
        assert session.is_active
        result = session.soft_delete(retention_days=retention_days)
        assert result is True
        assert session.is_deleted
        result = session.restore()
        assert result is True
        assert session.is_active

    @given(deleted_by=st.text(min_size=0, max_size=200))
    @settings(max_examples=50)
    def test_deleted_by_stored_verbatim(self, deleted_by):
        """Any string for deleted_by is stored as-is."""
        session = SampleSession(id="1", name="s1")
        session.soft_delete(deleted_by=deleted_by)
        assert session._deletion_metadata.deleted_by == deleted_by

    @given(
        reason=st.one_of(st.none(), st.text(min_size=0, max_size=500)),
        retention_days=st.integers(min_value=0, max_value=365),
    )
    @settings(max_examples=50)
    def test_soft_delete_never_crashes(self, reason, retention_days):
        """soft_delete with any valid combo of params should never raise."""
        session = SampleSession(id="safe", name="safe_test")
        result = session.soft_delete(reason=reason, retention_days=retention_days)
        assert result is True

    @given(retention_days=st.integers(min_value=1, max_value=365))
    @settings(max_examples=30)
    def test_expiry_set_correctly(self, retention_days):
        """expires_at = deleted_at + retention_days when retention_days > 0."""
        session = SampleSession(id="exp", name="exp_test")
        session.soft_delete(retention_days=retention_days)
        meta = session._deletion_metadata
        assert meta.expires_at is not None
        expected = meta.deleted_at + timedelta(days=retention_days)
        assert meta.expires_at == expected

    @given(retention_days=st.just(0))
    @settings(max_examples=5)
    def test_zero_retention_no_expiry(self, retention_days):
        """retention_days=0 means no auto-expiry."""
        session = SampleSession(id="z", name="zero")
        session.soft_delete(retention_days=retention_days)
        assert session._deletion_metadata.expires_at is None


# ==========================================================================
# 4. FAILURE INJECTION
# ==========================================================================


class TestFailureInjection:

    @patch("backend.app.utils.soft_delete.datetime")
    def test_double_soft_delete_returns_false(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        assert session.soft_delete() is True
        assert session.soft_delete() is False

    @patch("backend.app.utils.soft_delete.datetime")
    def test_soft_delete_after_permanently_deleted_returns_false(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.permanently_delete()
        assert session.soft_delete() is False

    def test_restore_on_active_returns_false(self):
        session = SampleSession(id="1", name="s1")
        assert session.restore() is False

    def test_restore_on_permanently_deleted_returns_false(self):
        session = SampleSession(id="1", name="s1")
        session.permanently_delete()
        assert session.restore() is False

    @patch("backend.app.utils.soft_delete.datetime")
    def test_cleanup_with_no_expired_items(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        s1 = SampleSession(id="1", name="active")
        s2 = SampleSession(id="2", name="deleted_not_expired")
        s2.soft_delete(retention_days=365)

        manager = SoftDeleteManager()
        count, remaining = manager.cleanup_expired([s1, s2])
        assert count == 0
        assert len(remaining) == 2

    def test_cleanup_empty_list(self):
        manager = SoftDeleteManager()
        count, remaining = manager.cleanup_expired([])
        assert count == 0
        assert remaining == []

    @patch("backend.app.utils.soft_delete.datetime")
    def test_restore_all_with_no_deleted_items(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        items = [SampleSession(id="1", name="a"), SampleSession(id="2", name="b")]
        manager = SoftDeleteManager()
        assert manager.restore_all(items) == 0

    @patch("backend.app.utils.soft_delete.datetime")
    def test_get_recovery_info_permanently_deleted(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.permanently_delete()
        manager = SoftDeleteManager()
        assert manager.get_recovery_info(session) is None

    @patch("backend.app.utils.soft_delete.datetime")
    def test_deletion_metadata_property_returns_none_after_permanent_delete(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.soft_delete()
        session.permanently_delete()
        # is_deleted is False for PERMANENTLY_DELETED, so deletion_metadata returns None
        assert session.deletion_metadata is None


# ==========================================================================
# 5. CONCURRENCY
# ==========================================================================


class TestConcurrency:

    @patch("backend.app.utils.soft_delete.datetime")
    def test_concurrent_soft_delete_only_one_succeeds(self, mock_dt):
        """When multiple threads try to soft_delete, at most one succeeds."""
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="race", name="race_test")
        results = []
        barrier = threading.Barrier(10)

        def worker():
            barrier.wait()
            result = session.soft_delete(deleted_by=threading.current_thread().name)
            results.append(result)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Exactly one True (first to acquire), rest False
        # NOTE: due to CPython GIL this is deterministic, but we still verify invariant
        assert results.count(True) == 1
        assert results.count(False) == 9
        assert session.is_deleted is True

    @patch("backend.app.utils.soft_delete.datetime")
    def test_concurrent_restore_only_one_succeeds(self, mock_dt):
        """When multiple threads try to restore, at most one succeeds."""
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="race2", name="race_restore")
        session.soft_delete()
        results = []
        barrier = threading.Barrier(10)

        def worker():
            barrier.wait()
            result = session.restore()
            results.append(result)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert results.count(True) == 1
        assert results.count(False) == 9
        assert session.is_active is True

    @patch("backend.app.utils.soft_delete.datetime")
    def test_concurrent_mixed_operations(self, mock_dt):
        """Concurrent soft_delete and restore do not crash."""
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="mix", name="mixed")
        errors = []

        def delete_worker():
            try:
                session.soft_delete()
            except Exception as e:
                errors.append(e)

        def restore_worker():
            try:
                session.restore()
            except Exception as e:
                errors.append(e)

        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=delete_worker))
            threads.append(threading.Thread(target=restore_worker))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        # Final state is one of the valid states
        assert session._deletion_status in (
            DeletionStatus.ACTIVE,
            DeletionStatus.SOFT_DELETED,
        )


# ==========================================================================
# 6. SECURITY / ABUSE
# ==========================================================================


class TestSecurityAbuse:

    @patch("backend.app.utils.soft_delete.datetime")
    def test_very_long_reason_string(self, mock_dt):
        """Very long reason strings are stored without truncation (document as finding)."""
        mock_dt.utcnow.return_value = FROZEN_NOW
        long_reason = "x" * 100_000
        session = SampleSession(id="1", name="s1")
        session.soft_delete(reason=long_reason)
        assert session._deletion_metadata.reason == long_reason
        assert len(session._deletion_metadata.reason) == 100_000

    @patch("backend.app.utils.soft_delete.datetime")
    def test_unicode_deleted_by(self, mock_dt):
        """Unicode characters in deleted_by are preserved."""
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        unicode_user = "\u2603\u2764\U0001f600 admin@\u00fc\u00f6\u00e4.com"
        session.soft_delete(deleted_by=unicode_user)
        assert session._deletion_metadata.deleted_by == unicode_user

    @patch("backend.app.utils.soft_delete.datetime")
    def test_xss_in_reason_stored_literally(self, mock_dt):
        """
        XSS payload in reason is stored literally without sanitization.
        FINDING: The module does not sanitize HTML/JS in reason field.
        Consumers must escape before rendering.
        """
        mock_dt.utcnow.return_value = FROZEN_NOW
        xss_payload = '<script>alert("XSS")</script>'
        session = SampleSession(id="1", name="s1")
        session.soft_delete(reason=xss_payload)
        # Stored verbatim: no sanitization
        assert session._deletion_metadata.reason == xss_payload
        assert "<script>" in session._deletion_metadata.reason

    @patch("backend.app.utils.soft_delete.datetime")
    def test_xss_in_deleted_by(self, mock_dt):
        """XSS in deleted_by is also stored verbatim."""
        mock_dt.utcnow.return_value = FROZEN_NOW
        xss = '<img onerror="alert(1)" src=x>'
        session = SampleSession(id="1", name="s1")
        session.soft_delete(deleted_by=xss)
        assert session._deletion_metadata.deleted_by == xss

    @patch("backend.app.utils.soft_delete.datetime")
    def test_negative_retention_days(self, mock_dt):
        """
        Negative retention_days: since the condition is `retention_days > 0`,
        negative values result in no expires_at (same as 0).
        """
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.soft_delete(retention_days=-5)
        assert session._deletion_metadata.expires_at is None

    @patch("backend.app.utils.soft_delete.datetime")
    def test_null_bytes_in_strings(self, mock_dt):
        """Null bytes in strings are stored."""
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.soft_delete(
            deleted_by="user\x00injected",
            reason="reason\x00with\x00nulls",
        )
        assert "\x00" in session._deletion_metadata.deleted_by
        assert "\x00" in session._deletion_metadata.reason

    @patch("backend.app.utils.soft_delete.datetime")
    def test_sql_injection_in_reason(self, mock_dt):
        """SQL injection payload stored verbatim (document as finding)."""
        mock_dt.utcnow.return_value = FROZEN_NOW
        sqli = "'; DROP TABLE sessions; --"
        session = SampleSession(id="1", name="s1")
        session.soft_delete(reason=sqli)
        assert session._deletion_metadata.reason == sqli

    @patch("backend.app.utils.soft_delete.datetime")
    def test_empty_string_deleted_by_and_reason(self, mock_dt):
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="1", name="s1")
        session.soft_delete(deleted_by="", reason="")
        assert session._deletion_metadata.deleted_by == ""
        assert session._deletion_metadata.reason == ""


# ==========================================================================
# 7. USABILITY — Realistic scenarios
# ==========================================================================


class TestUsabilityRealisticScenarios:

    @patch("backend.app.utils.soft_delete.datetime")
    def test_session_soft_delete_and_recovery(self, mock_dt):
        """Realistic: user accidentally deletes a session, admin recovers it."""
        mock_dt.utcnow.return_value = FROZEN_NOW

        # User creates a session
        session = SampleSession(id="session-001", name="Q4 Report Analysis")
        assert session.is_active

        # User accidentally deletes
        session.soft_delete(
            deleted_by="user@company.com",
            reason="Accidental deletion",
            retention_days=30,
        )
        assert session.is_deleted

        # Admin checks recovery info
        manager = SoftDeleteManager(retention_days=30)
        info = manager.get_recovery_info(session)
        assert info["deleted_by"] == "user@company.com"
        assert info["reason"] == "Accidental deletion"
        assert info["can_restore"] is True
        assert info["has_preserved_data"] is True

        # Admin restores
        session.restore()
        assert session.is_active
        assert session.id == "session-001"
        assert session.name == "Q4 Report Analysis"

    @patch("backend.app.utils.soft_delete.datetime")
    def test_batch_operations_workflow(self, mock_dt):
        """Realistic: batch delete, partial restore, cleanup."""
        mock_dt.utcnow.return_value = FROZEN_NOW
        manager = SoftDeleteManager(retention_days=30)

        sessions = [
            SampleSession(id=f"s-{i}", name=f"Session {i}")
            for i in range(10)
        ]

        # Delete sessions 0-4
        for s in sessions[:5]:
            s.soft_delete(
                deleted_by="system",
                reason="Bulk cleanup",
                retention_days=7,
            )

        assert len(manager.filter_active(sessions)) == 5
        assert len(manager.filter_deleted(sessions)) == 5

        # Restore sessions 0-1
        sessions[0].restore()
        sessions[1].restore()
        assert len(manager.filter_active(sessions)) == 7
        assert len(manager.filter_deleted(sessions)) == 3

        # Advance past expiry of remaining deleted (7 days retention)
        mock_dt.utcnow.return_value = FROZEN_NOW + timedelta(days=8)

        expired = manager.filter_expired(sessions)
        assert len(expired) == 3

        count, remaining = manager.cleanup_expired(sessions)
        assert count == 3
        assert len(remaining) == 7
        for r in remaining:
            assert r.is_active

    @patch("backend.app.utils.soft_delete.datetime")
    def test_soft_deletable_dict_in_api_response(self, mock_dt):
        """Realistic: converting items to API response format."""
        mock_dt.utcnow.return_value = FROZEN_NOW

        active_session = SampleSession(id="active-1", name="Current Work")
        deleted_session = SampleSession(id="del-1", name="Old Work")
        deleted_session.soft_delete(deleted_by="admin", reason="archiving")

        active_dict = soft_deletable_dict(active_session)
        assert active_dict["id"] == "active-1"
        assert active_dict["_is_deleted"] is False
        assert "_deletion_info" not in active_dict

        deleted_dict = soft_deletable_dict(deleted_session)
        assert deleted_dict["id"] == "del-1"
        assert deleted_dict["_is_deleted"] is True
        assert deleted_dict["_deletion_info"]["deleted_by"] == "admin"
        assert deleted_dict["_deletion_info"]["reason"] == "archiving"

    @patch("backend.app.utils.soft_delete.datetime")
    def test_manager_retention_days_attribute(self, mock_dt):
        """Manager stores its own retention_days configuration."""
        mock_dt.utcnow.return_value = FROZEN_NOW
        manager = SoftDeleteManager(retention_days=90)
        assert manager.retention_days == 90

    def test_default_retention_days_constant(self):
        assert DEFAULT_RETENTION_DAYS == 30

    @patch("backend.app.utils.soft_delete.datetime")
    def test_multiple_delete_restore_cycles(self, mock_dt):
        """An item can be soft-deleted and restored multiple times."""
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="cycle", name="cycled")

        for i in range(5):
            assert session.soft_delete(reason=f"delete #{i+1}") is True
            assert session.is_deleted
            assert session.deletion_metadata.reason == f"delete #{i+1}"
            assert session.restore() is True
            assert session.is_active
            assert session.deletion_metadata is None

    @patch("backend.app.utils.soft_delete.datetime")
    def test_preserved_data_snapshot_at_delete_time(self, mock_dt):
        """
        Preserved data is a snapshot taken at the time of deletion.
        Mutating the object after deletion should not affect the snapshot.
        """
        mock_dt.utcnow.return_value = FROZEN_NOW
        session = SampleSession(id="snap", name="original_name")
        session.soft_delete()

        # Mutate the live object
        session.name = "changed_name"

        # Snapshot still has the original value
        assert session._deletion_metadata.original_data["name"] == "original_name"
        assert session.name == "changed_name"
