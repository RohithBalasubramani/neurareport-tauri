"""Comprehensive tests for backend.app.utils.job_status."""
from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from backend.app.utils.job_status import (
    ACTIVE_STATUSES,
    STATUS_CANCELLED,
    STATUS_CANCELLING,
    STATUS_FAILED,
    STATUS_PENDING_RETRY,
    STATUS_QUEUED,
    STATUS_RUNNING,
    STATUS_SUCCEEDED,
    TERMINAL_STATUSES,
    can_retry,
    is_active_status,
    is_pending_retry,
    is_terminal_status,
    normalize_job,
    normalize_job_status,
)


# ==========================================================================
# 1. UNIT TESTS — normalize_job_status
# ==========================================================================

class TestNormalizeJobStatus:
    """Every documented alias maps to the correct canonical status."""

    @pytest.mark.parametrize("raw,expected", [
        ("succeeded", STATUS_SUCCEEDED),
        ("success", STATUS_SUCCEEDED),
        ("done", STATUS_SUCCEEDED),
        ("completed", STATUS_SUCCEEDED),
        ("SUCCEEDED", STATUS_SUCCEEDED),
        ("  Completed  ", STATUS_SUCCEEDED),
    ])
    def test_succeeded_aliases(self, raw, expected):
        assert normalize_job_status(raw) == expected

    @pytest.mark.parametrize("raw,expected", [
        ("queued", STATUS_QUEUED),
        ("pending", STATUS_QUEUED),
        ("waiting", STATUS_QUEUED),
        ("QUEUED", STATUS_QUEUED),
    ])
    def test_queued_aliases(self, raw, expected):
        assert normalize_job_status(raw) == expected

    @pytest.mark.parametrize("raw,expected", [
        ("running", STATUS_RUNNING),
        ("in_progress", STATUS_RUNNING),
        ("started", STATUS_RUNNING),
        ("processing", STATUS_RUNNING),
    ])
    def test_running_aliases(self, raw, expected):
        assert normalize_job_status(raw) == expected

    @pytest.mark.parametrize("raw,expected", [
        ("failed", STATUS_FAILED),
        ("error", STATUS_FAILED),
        ("errored", STATUS_FAILED),
    ])
    def test_failed_aliases(self, raw, expected):
        assert normalize_job_status(raw) == expected

    @pytest.mark.parametrize("raw,expected", [
        ("cancelled", STATUS_CANCELLED),
        ("canceled", STATUS_CANCELLED),
    ])
    def test_cancelled_aliases(self, raw, expected):
        assert normalize_job_status(raw) == expected

    def test_cancelling(self):
        assert normalize_job_status("cancelling") == STATUS_CANCELLING

    @pytest.mark.parametrize("raw", [
        "pending_retry", "retry_pending", "retry_scheduled", "awaiting_retry",
    ])
    def test_pending_retry_aliases(self, raw):
        assert normalize_job_status(raw) == STATUS_PENDING_RETRY

    def test_none_defaults_to_queued(self):
        assert normalize_job_status(None) == STATUS_QUEUED

    def test_empty_string_defaults_to_queued(self):
        assert normalize_job_status("") == STATUS_QUEUED

    def test_unknown_defaults_to_queued(self):
        assert normalize_job_status("foobar") == STATUS_QUEUED


# ==========================================================================
# 2. UNIT TESTS — normalize_job
# ==========================================================================

class TestNormalizeJob:
    def test_normalizes_status_field(self):
        job = {"id": "j1", "status": "completed"}
        result = normalize_job(job)
        assert result["status"] == STATUS_SUCCEEDED

    def test_normalizes_state_field(self):
        job = {"id": "j2", "state": "in_progress"}
        result = normalize_job(job)
        assert result["status"] == STATUS_RUNNING

    def test_none_returns_none(self):
        assert normalize_job(None) is None

    def test_empty_dict_returns_empty(self):
        result = normalize_job({})
        assert result == {}

    def test_preserves_other_fields(self):
        job = {"id": "j3", "status": "done", "result": {"path": "/out.pdf"}}
        result = normalize_job(job)
        assert result["result"]["path"] == "/out.pdf"
        assert result["id"] == "j3"

    def test_does_not_mutate_original(self):
        job = {"status": "completed"}
        normalize_job(job)
        assert job["status"] == "completed"


# ==========================================================================
# 3. UNIT TESTS — status predicates
# ==========================================================================

class TestStatusPredicates:
    @pytest.mark.parametrize("status,expected", [
        ("succeeded", True), ("failed", True), ("cancelled", True),
        ("running", False), ("queued", False), ("cancelling", False),
    ])
    def test_is_terminal(self, status, expected):
        assert is_terminal_status(status) == expected

    @pytest.mark.parametrize("status,expected", [
        ("queued", True), ("running", True), ("cancelling", True),
        ("pending_retry", True),
        ("succeeded", False), ("failed", False),
    ])
    def test_is_active(self, status, expected):
        assert is_active_status(status) == expected

    def test_is_pending_retry(self):
        assert is_pending_retry("pending_retry") is True
        assert is_pending_retry("running") is False

    def test_terminal_and_active_no_overlap(self):
        assert TERMINAL_STATUSES & ACTIVE_STATUSES == frozenset()


class TestCanRetry:
    def test_failed_job_can_retry(self):
        assert can_retry({"status": "failed", "retryCount": 0}) is True

    def test_succeeded_job_cannot_retry(self):
        assert can_retry({"status": "succeeded"}) is False

    def test_running_job_cannot_retry(self):
        assert can_retry({"status": "running"}) is False

    def test_none_job_cannot_retry(self):
        assert can_retry(None) is False

    def test_exceeded_max_retries(self):
        assert can_retry({"status": "failed", "retryCount": 3, "maxRetries": 3}) is False

    def test_below_max_retries(self):
        assert can_retry({"status": "failed", "retryCount": 2, "maxRetries": 3}) is True

    def test_snake_case_retry_fields(self):
        assert can_retry({"status": "failed", "retry_count": 1, "max_retries": 3}) is True

    def test_default_max_retries_is_3(self):
        assert can_retry({"status": "failed", "retryCount": 2}) is True
        assert can_retry({"status": "failed", "retryCount": 3}) is False


# ==========================================================================
# 4. PROPERTY-BASED
# ==========================================================================

class TestPropertyBased:
    @given(st.text(max_size=100))
    @settings(max_examples=200)
    def test_normalize_always_returns_known_status(self, raw):
        result = normalize_job_status(raw)
        all_statuses = {STATUS_QUEUED, STATUS_RUNNING, STATUS_SUCCEEDED,
                        STATUS_FAILED, STATUS_CANCELLED, STATUS_CANCELLING,
                        STATUS_PENDING_RETRY}
        assert result in all_statuses

    @given(st.text(max_size=100))
    @settings(max_examples=100)
    def test_idempotent(self, raw):
        once = normalize_job_status(raw)
        twice = normalize_job_status(once)
        assert once == twice

    @given(st.text(max_size=100))
    @settings(max_examples=100)
    def test_terminal_xor_active_or_neither(self, raw):
        """A status is either terminal, active, or unknown (but never both)."""
        status = normalize_job_status(raw)
        terminal = status in TERMINAL_STATUSES
        active = status in ACTIVE_STATUSES
        # Can't be both terminal and active
        assert not (terminal and active)


# ==========================================================================
# 5. USABILITY
# ==========================================================================

class TestUsability:
    def test_realistic_job_lifecycle(self):
        job = {"id": "j1", "status": "pending"}
        assert normalize_job(job)["status"] == STATUS_QUEUED
        assert is_active_status(job["status"])

        job["status"] = "in_progress"
        assert normalize_job(job)["status"] == STATUS_RUNNING
        assert is_active_status(job["status"])

        job["status"] = "completed"
        assert normalize_job(job)["status"] == STATUS_SUCCEEDED
        assert is_terminal_status(job["status"])
