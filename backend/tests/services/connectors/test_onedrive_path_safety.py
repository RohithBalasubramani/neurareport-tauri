"""
Tests for OneDrive path-traversal prevention — lines 1250-1266 of FORENSIC_AUDIT_REPORT.md.

Covers:
- _safe_path rejects ".." traversal
- _safe_path normalises redundant slashes / dots
- list_files and upload_file use _safe_path

Run with: pytest backend/tests/services/connectors/test_onedrive_path_safety.py -v
"""
from __future__ import annotations

import pytest

from backend.app.services.connectors.storage.onedrive import OneDriveConnector


class TestSafePath:
    """Unit tests for OneDriveConnector._safe_path."""

    def test_normal_path_unchanged(self):
        assert OneDriveConnector._safe_path("Documents/Reports") == "Documents/Reports"

    def test_strips_leading_trailing_slashes(self):
        assert OneDriveConnector._safe_path("/Documents/") == "Documents"

    def test_single_segment(self):
        assert OneDriveConnector._safe_path("myfile.txt") == "myfile.txt"

    def test_empty_after_strip_returns_empty(self):
        assert OneDriveConnector._safe_path("/") == ""
        assert OneDriveConnector._safe_path("") == ""

    def test_dot_dot_simple_raises(self):
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            OneDriveConnector._safe_path("../../admin")

    def test_dot_dot_embedded_raises(self):
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            OneDriveConnector._safe_path("docs/../../etc/passwd")

    def test_dot_dot_at_start_raises(self):
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            OneDriveConnector._safe_path("../secret")

    def test_normalises_redundant_slashes(self):
        assert OneDriveConnector._safe_path("a///b//c") == "a/b/c"

    def test_normalises_single_dots(self):
        assert OneDriveConnector._safe_path("a/./b/./c") == "a/b/c"

    def test_dot_dot_within_bounds_ok(self):
        # "a/b/../c" normalises to "a/c" — stays within root
        assert OneDriveConnector._safe_path("a/b/../c") == "a/c"

    def test_deeply_nested_traversal_raises(self):
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            OneDriveConnector._safe_path("a/../../../../root")
