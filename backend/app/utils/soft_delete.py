"""
Soft Delete Support for Data Recovery.

UX Laws Addressed:
- Make every action reversible where possible
- Prevent errors before handling them
- User mistakes are expected, system mistakes are unacceptable

This module provides:
- Soft delete patterns (mark as deleted instead of hard delete)
- Recovery/restore functionality
- Automatic cleanup of old soft-deleted items
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, TypeVar, Generic, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

# Default retention period for soft-deleted items
DEFAULT_RETENTION_DAYS = 30


class DeletionStatus(str, Enum):
    """Status of a deletable item."""
    ACTIVE = "active"
    SOFT_DELETED = "soft_deleted"
    PERMANENTLY_DELETED = "permanently_deleted"


@dataclass
class SoftDeleteMetadata:
    """Metadata for soft-deleted items."""
    deleted_at: datetime
    deleted_by: Optional[str] = None
    reason: Optional[str] = None
    expires_at: Optional[datetime] = None
    original_data: Optional[Dict[str, Any]] = None

    def is_expired(self) -> bool:
        """Check if the soft-deleted item has expired (should be permanently deleted)."""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def days_until_expiry(self) -> Optional[int]:
        """Get days until permanent deletion."""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.now(timezone.utc)
        return max(0, delta.days)


@dataclass
class SoftDeletable:
    """
    Mixin class for items that support soft deletion.

    Usage:
        @dataclass
        class Session(SoftDeletable):
            id: str
            name: str
            # ... other fields

        session = Session(id="123", name="Test")
        session.soft_delete(deleted_by="user@example.com", reason="User requested deletion")
        session.is_deleted  # True
        session.restore()
        session.is_deleted  # False
    """
    _deletion_status: DeletionStatus = field(default=DeletionStatus.ACTIVE, repr=False)
    _deletion_metadata: Optional[SoftDeleteMetadata] = field(default=None, repr=False)

    @property
    def is_deleted(self) -> bool:
        """Check if item is soft-deleted."""
        return self._deletion_status == DeletionStatus.SOFT_DELETED

    @property
    def is_active(self) -> bool:
        """Check if item is active (not deleted)."""
        return self._deletion_status == DeletionStatus.ACTIVE

    @property
    def deletion_metadata(self) -> Optional[SoftDeleteMetadata]:
        """Get deletion metadata if soft-deleted."""
        return self._deletion_metadata if self.is_deleted else None

    def soft_delete(
        self,
        deleted_by: Optional[str] = None,
        reason: Optional[str] = None,
        retention_days: int = DEFAULT_RETENTION_DAYS,
        preserve_data: bool = True,
    ) -> bool:
        """
        Mark item as soft-deleted.

        Args:
            deleted_by: User or system that initiated deletion
            reason: Optional reason for deletion
            retention_days: Days to retain before permanent deletion
            preserve_data: Whether to snapshot original data for recovery

        Returns:
            True if successfully soft-deleted, False if already deleted
        """
        if self._deletion_status != DeletionStatus.ACTIVE:
            return False

        now = datetime.now(timezone.utc)
        self._deletion_status = DeletionStatus.SOFT_DELETED
        self._deletion_metadata = SoftDeleteMetadata(
            deleted_at=now,
            deleted_by=deleted_by,
            reason=reason,
            expires_at=now + timedelta(days=retention_days) if retention_days > 0 else None,
            original_data=self._get_preservable_data() if preserve_data else None,
        )
        return True

    def restore(self) -> bool:
        """
        Restore a soft-deleted item.

        Returns:
            True if successfully restored, False if not soft-deleted
        """
        if self._deletion_status != DeletionStatus.SOFT_DELETED:
            return False

        self._deletion_status = DeletionStatus.ACTIVE
        self._deletion_metadata = None
        return True

    def permanently_delete(self) -> bool:
        """
        Mark item for permanent deletion.

        Returns:
            True if successfully marked for permanent deletion
        """
        self._deletion_status = DeletionStatus.PERMANENTLY_DELETED
        return True

    def _get_preservable_data(self) -> Dict[str, Any]:
        """
        Get data to preserve for potential recovery.
        Override in subclass to customize.
        """
        # By default, preserve all public attributes
        return {
            k: v for k, v in vars(self).items()
            if not k.startswith('_')
        }


class SoftDeleteManager:
    """
    Manager for handling soft-deleted items in a collection.

    Provides:
    - Filtering active vs deleted items
    - Batch restore/permanent delete
    - Automatic cleanup of expired items
    """

    def __init__(self, retention_days: int = DEFAULT_RETENTION_DAYS):
        self.retention_days = retention_days

    def filter_active(self, items: List[SoftDeletable]) -> List[SoftDeletable]:
        """Get only active (non-deleted) items."""
        return [item for item in items if item.is_active]

    def filter_deleted(self, items: List[SoftDeletable]) -> List[SoftDeletable]:
        """Get only soft-deleted items."""
        return [item for item in items if item.is_deleted]

    def filter_expired(self, items: List[SoftDeletable]) -> List[SoftDeletable]:
        """Get soft-deleted items that have expired and can be permanently deleted."""
        return [
            item for item in items
            if item.is_deleted and item._deletion_metadata and item._deletion_metadata.is_expired()
        ]

    def cleanup_expired(self, items: List[SoftDeletable]) -> tuple[int, List[SoftDeletable]]:
        """
        Mark expired soft-deleted items for permanent deletion.

        Returns:
            Tuple of (count of items marked, list of remaining items)
        """
        expired = self.filter_expired(items)
        for item in expired:
            item.permanently_delete()

        remaining = [item for item in items if item._deletion_status != DeletionStatus.PERMANENTLY_DELETED]
        return len(expired), remaining

    def restore_all(self, items: List[SoftDeletable]) -> int:
        """
        Restore all soft-deleted items.

        Returns:
            Count of items restored
        """
        count = 0
        for item in items:
            if item.restore():
                count += 1
        return count

    def get_recovery_info(self, item: SoftDeletable) -> Optional[Dict[str, Any]]:
        """
        Get information about recovering a soft-deleted item.

        Returns:
            Recovery info dict or None if not recoverable
        """
        if not item.is_deleted or not item._deletion_metadata:
            return None

        return {
            "deleted_at": item._deletion_metadata.deleted_at.isoformat(),
            "deleted_by": item._deletion_metadata.deleted_by,
            "reason": item._deletion_metadata.reason,
            "days_until_permanent_deletion": item._deletion_metadata.days_until_expiry(),
            "can_restore": not item._deletion_metadata.is_expired(),
            "has_preserved_data": item._deletion_metadata.original_data is not None,
        }


def soft_deletable_dict(item: SoftDeletable) -> Dict[str, Any]:
    """
    Convert a soft-deletable item to dict including deletion metadata.

    Useful for API responses.
    """
    result = {
        k: v for k, v in vars(item).items()
        if not k.startswith('_')
    }

    result['_is_deleted'] = item.is_deleted

    if item.is_deleted and item._deletion_metadata:
        result['_deletion_info'] = {
            "deleted_at": item._deletion_metadata.deleted_at.isoformat(),
            "deleted_by": item._deletion_metadata.deleted_by,
            "reason": item._deletion_metadata.reason,
            "days_until_permanent_deletion": item._deletion_metadata.days_until_expiry(),
        }

    return result
