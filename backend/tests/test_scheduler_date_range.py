"""Tests for Scheduler date range enforcement."""
import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch, AsyncMock

from backend.app.services.jobs.report_scheduler import (
    ReportScheduler,
    _parse_iso,
    _now_utc,
)


class TestSchedulerDateRangeEnforcement:
    """Test scheduler date range enforcement functionality."""

    @pytest.fixture
    def mock_runner(self):
        """Create a mock runner function."""
        async def runner(payload, kind, job_tracker=None):
            return {"html_url": "test.html", "pdf_url": "test.pdf"}
        return runner

    @pytest.fixture
    def mock_state_store(self):
        """Create a mock state store."""
        mock = MagicMock()
        mock.create_job = MagicMock(return_value={"id": "job-123"})
        mock.record_schedule_run = MagicMock()
        return mock

    def test_parse_iso_with_timezone(self):
        """Test parsing ISO timestamp with timezone."""
        result = _parse_iso("2024-01-15T10:00:00+00:00")
        assert result is not None
        assert result.tzinfo is not None

    def test_parse_iso_without_timezone(self):
        """Test parsing ISO timestamp without timezone assumes UTC."""
        result = _parse_iso("2024-01-15T10:00:00")
        assert result is not None
        assert result.tzinfo == timezone.utc

    def test_parse_iso_invalid(self):
        """Test parsing invalid ISO timestamp returns None."""
        assert _parse_iso(None) is None
        assert _parse_iso("") is None
        assert _parse_iso("not-a-date") is None

    @pytest.mark.asyncio
    async def test_scheduler_skips_past_end_date(self, mock_runner):
        """Test that scheduler skips schedules past their end_date."""
        past_end = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        past_start = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

        schedules = [
            {
                "id": "schedule-past",
                "active": True,
                "start_date": past_start,
                "end_date": past_end,  # End date is in the past
                "next_run_at": None,
                "interval_minutes": 1440,
                "template_id": "template-1",
                "connection_id": "conn-1",
            }
        ]

        with patch("backend.app.services.jobs.report_scheduler.state_store") as mock_store:
            mock_store.list_schedules.return_value = schedules

            scheduler = ReportScheduler(mock_runner, poll_seconds=5)

            # Dispatch should not create any tasks because schedule is past end_date
            await scheduler._dispatch_due_jobs()

            # No schedules should be in-flight
            assert len(scheduler._inflight) == 0

    @pytest.mark.asyncio
    async def test_scheduler_skips_future_start_date(self, mock_runner):
        """Test that scheduler skips schedules before their start_date."""
        future_start = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        future_end = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

        schedules = [
            {
                "id": "schedule-future",
                "active": True,
                "start_date": future_start,  # Start date is in the future
                "end_date": future_end,
                "next_run_at": None,
                "interval_minutes": 1440,
                "template_id": "template-1",
                "connection_id": "conn-1",
            }
        ]

        with patch("backend.app.services.jobs.report_scheduler.state_store") as mock_store:
            mock_store.list_schedules.return_value = schedules

            scheduler = ReportScheduler(mock_runner, poll_seconds=5)

            # Dispatch should not create any tasks because schedule hasn't started
            await scheduler._dispatch_due_jobs()

            # No schedules should be in-flight
            assert len(scheduler._inflight) == 0

    @pytest.mark.asyncio
    async def test_scheduler_runs_within_date_range(self, mock_runner):
        """Test that scheduler runs schedules within their date range."""
        past_start = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        future_end = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        past_next_run = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

        schedules = [
            {
                "id": "schedule-active",
                "active": True,
                "start_date": past_start,  # Started in the past
                "end_date": future_end,  # Ends in the future
                "next_run_at": past_next_run,  # Due to run
                "interval_minutes": 1440,
                "template_id": "template-1",
                "connection_id": "conn-1",
                "template_kind": "pdf",
            }
        ]

        with patch("backend.app.services.jobs.report_scheduler.state_store") as mock_store:
            mock_store.list_schedules.return_value = schedules
            mock_store.create_job.return_value = {"id": "job-123"}

            scheduler = ReportScheduler(mock_runner, poll_seconds=5)

            # Dispatch should create a task because schedule is within range
            await scheduler._dispatch_due_jobs()

            # Schedule should be in-flight
            assert "schedule-active" in scheduler._inflight

    @pytest.mark.asyncio
    async def test_scheduler_handles_null_dates(self, mock_runner):
        """Test that scheduler handles null start/end dates gracefully."""
        past_next_run = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

        schedules = [
            {
                "id": "schedule-no-dates",
                "active": True,
                "start_date": None,  # No start date
                "end_date": None,  # No end date
                "next_run_at": past_next_run,  # Due to run
                "interval_minutes": 1440,
                "template_id": "template-1",
                "connection_id": "conn-1",
                "template_kind": "pdf",
            }
        ]

        with patch("backend.app.services.jobs.report_scheduler.state_store") as mock_store:
            mock_store.list_schedules.return_value = schedules
            mock_store.create_job.return_value = {"id": "job-123"}

            scheduler = ReportScheduler(mock_runner, poll_seconds=5)

            # Dispatch should create a task because no date restrictions
            await scheduler._dispatch_due_jobs()

            # Schedule should be in-flight
            assert "schedule-no-dates" in scheduler._inflight

    @pytest.mark.asyncio
    async def test_scheduler_skips_inactive_schedules(self, mock_runner):
        """Test that scheduler skips inactive schedules."""
        schedules = [
            {
                "id": "schedule-inactive",
                "active": False,  # Inactive
                "start_date": None,
                "end_date": None,
                "next_run_at": None,
                "interval_minutes": 1440,
                "template_id": "template-1",
                "connection_id": "conn-1",
            }
        ]

        with patch("backend.app.services.jobs.report_scheduler.state_store") as mock_store:
            mock_store.list_schedules.return_value = schedules

            scheduler = ReportScheduler(mock_runner, poll_seconds=5)

            await scheduler._dispatch_due_jobs()

            # No schedules should be in-flight
            assert len(scheduler._inflight) == 0


class TestSchedulerStartStop:
    """Test scheduler start/stop functionality."""

    @pytest.fixture
    def mock_runner(self):
        """Create a mock runner function."""
        async def runner(payload, kind, job_tracker=None):
            return {}
        return runner

    @pytest.mark.asyncio
    async def test_scheduler_start_creates_task(self, mock_runner):
        """Test that starting scheduler creates a task."""
        scheduler = ReportScheduler(mock_runner, poll_seconds=1)

        with patch("backend.app.services.jobs.report_scheduler.state_store") as mock_store:
            mock_store.list_schedules.return_value = []

            await scheduler.start()

            assert scheduler._task is not None
            assert not scheduler._task.done()

            await scheduler.stop()

    @pytest.mark.asyncio
    async def test_scheduler_stop_cancels_task(self, mock_runner):
        """Test that stopping scheduler cancels the task."""
        scheduler = ReportScheduler(mock_runner, poll_seconds=1)

        with patch("backend.app.services.jobs.report_scheduler.state_store") as mock_store:
            mock_store.list_schedules.return_value = []

            await scheduler.start()
            await scheduler.stop()

            assert scheduler._task is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
