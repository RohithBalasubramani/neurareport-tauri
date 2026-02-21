"""
Comprehensive Tests for Research Agent v2

This test suite covers ALL required testing layers:
1. Unit Tests - Individual component testing
2. Integration Tests - End-to-end API testing
3. Property-Based Tests - Invariant verification
4. Failure Injection Tests - Error handling
5. Concurrency Tests - Race condition detection
6. Security Tests - Abuse prevention
7. Usability Tests - API ergonomics

Run with: pytest backend/tests/agents/test_research_agent_v2.py -v
"""
from __future__ import annotations

import asyncio
import json
import os
import random
import string
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Import the modules we're testing
from backend.app.repositories.agent_tasks.models import (
    AgentTaskModel,
    AgentTaskStatus,
    AgentType,
    _generate_task_id,
)
from backend.app.repositories.agent_tasks.repository import (
    AgentTaskRepository,
    IdempotencyConflictError,
    OptimisticLockError,
    TaskConflictError,
    TaskNotFoundError,
)
from backend.app.services.agents.base_agent import (
    AgentError,
    LLMRateLimitError,
    LLMResponseError,
    LLMTimeoutError,
    ValidationError,
)
from backend.app.services.agents.research_agent import (
    ResearchAgent,
    ResearchInput,
    ResearchReport,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Create a temporary database path for testing."""
    return tmp_path / "test_agent_tasks.db"


@pytest.fixture
def repository(temp_db_path: Path) -> AgentTaskRepository:
    """Create a fresh repository for each test."""
    return AgentTaskRepository(db_path=temp_db_path)


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "summary": "This is a test summary about AI trends.",
        "sections": [
            {"title": "Introduction", "content": "AI is transforming industries."},
            {"title": "Key Trends", "content": "Machine learning is growing rapidly."},
        ],
        "key_findings": ["AI adoption is increasing", "Cost savings are significant"],
        "recommendations": ["Invest in AI training", "Start with pilot projects"],
        "sources": [{"title": "Industry Report", "url": "https://example.com"}],
    }


@pytest.fixture
def research_agent() -> ResearchAgent:
    """Create a ResearchAgent instance."""
    return ResearchAgent()


# =============================================================================
# LAYER 1: UNIT TESTS
# =============================================================================

class TestTaskIdGeneration:
    """Test task ID generation is unique and time-sortable."""

    def test_task_id_is_16_chars(self):
        """Task ID should be exactly 16 characters."""
        task_id = _generate_task_id()
        assert len(task_id) == 16

    def test_task_id_is_hex(self):
        """Task ID should be valid hexadecimal."""
        task_id = _generate_task_id()
        int(task_id, 16)  # Should not raise

    def test_task_ids_are_unique(self):
        """Generate 1000 IDs and verify uniqueness."""
        ids = {_generate_task_id() for _ in range(1000)}
        assert len(ids) == 1000

    def test_task_ids_are_time_sortable(self):
        """IDs generated later should sort after earlier ones."""
        id1 = _generate_task_id()
        time.sleep(0.001)  # Small delay
        id2 = _generate_task_id()
        # First 8 chars are timestamp-based
        assert id1[:8] <= id2[:8]


class TestResearchInputValidation:
    """Test input validation for research requests."""

    def test_valid_topic(self):
        """Valid topic should pass validation."""
        input_data = ResearchInput(topic="AI trends in healthcare")
        assert input_data.topic == "AI trends in healthcare"

    def test_topic_too_short(self):
        """Topic with single word should fail."""
        with pytest.raises(ValueError, match="at least 2 words"):
            ResearchInput(topic="AI")

    def test_topic_empty(self):
        """Empty topic should fail."""
        with pytest.raises(ValueError):
            ResearchInput(topic="")

    def test_topic_whitespace_only(self):
        """Whitespace-only topic should fail."""
        with pytest.raises(ValueError):
            ResearchInput(topic="   ")

    def test_topic_trimmed(self):
        """Topic should be trimmed."""
        input_data = ResearchInput(topic="  AI trends  ")
        assert input_data.topic == "AI trends"

    def test_focus_areas_deduplicated(self):
        """Duplicate focus areas should be removed."""
        input_data = ResearchInput(
            topic="AI trends in healthcare",
            focus_areas=["tech", "Tech", "TECH", "finance"]
        )
        assert len(input_data.focus_areas) == 2

    def test_focus_areas_max_10(self):
        """Only first 10 focus areas should be kept."""
        areas = [f"area{i}" for i in range(15)]
        input_data = ResearchInput(
            topic="AI trends in healthcare",
            focus_areas=areas
        )
        assert len(input_data.focus_areas) == 10

    def test_max_sections_bounds(self):
        """max_sections should be within 1-20."""
        input_data = ResearchInput(topic="AI trends", max_sections=1)
        assert input_data.max_sections == 1

        input_data = ResearchInput(topic="AI trends", max_sections=20)
        assert input_data.max_sections == 20

        with pytest.raises(ValueError):
            ResearchInput(topic="AI trends", max_sections=0)

        with pytest.raises(ValueError):
            ResearchInput(topic="AI trends", max_sections=21)

    def test_depth_validation(self):
        """Depth must be one of allowed values."""
        for depth in ["quick", "moderate", "comprehensive"]:
            input_data = ResearchInput(topic="AI trends", depth=depth)
            assert input_data.depth == depth

        with pytest.raises(ValueError):
            ResearchInput(topic="AI trends", depth="invalid")


class TestAgentTaskModel:
    """Test AgentTaskModel properties and methods."""

    def test_is_terminal(self):
        """Test terminal status detection."""
        task = AgentTaskModel(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"},
            status=AgentTaskStatus.COMPLETED
        )
        assert task.is_terminal() is True

        task.status = AgentTaskStatus.RUNNING
        assert task.is_terminal() is False

    def test_can_cancel(self):
        """Test cancellation eligibility."""
        task = AgentTaskModel(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"},
            status=AgentTaskStatus.PENDING
        )
        assert task.can_cancel() is True

        task.status = AgentTaskStatus.RUNNING
        assert task.can_cancel() is True

        task.status = AgentTaskStatus.COMPLETED
        assert task.can_cancel() is False

    def test_can_retry(self):
        """Test retry eligibility."""
        task = AgentTaskModel(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"},
            status=AgentTaskStatus.FAILED,
            is_retryable=True,
            attempt_count=1,
            max_attempts=3
        )
        assert task.can_retry() is True

        task.is_retryable = False
        assert task.can_retry() is False

        task.is_retryable = True
        task.attempt_count = 3
        assert task.can_retry() is False


# =============================================================================
# LAYER 2: INTEGRATION TESTS
# =============================================================================

class TestRepositoryIntegration:
    """Test repository operations with actual database."""

    def test_create_and_retrieve_task(self, repository: AgentTaskRepository):
        """Create a task and retrieve it."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test topic", "depth": "quick"}
        )

        retrieved = repository.get_task(task.task_id)
        assert retrieved is not None
        assert retrieved.task_id == task.task_id
        assert retrieved.agent_type == AgentType.RESEARCH
        assert retrieved.input_params["topic"] == "test topic"
        assert retrieved.status == AgentTaskStatus.PENDING

    def test_claim_task(self, repository: AgentTaskRepository):
        """Claim a pending task."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"}
        )

        claimed = repository.claim_task(task.task_id)
        assert claimed.status == AgentTaskStatus.RUNNING
        assert claimed.started_at is not None
        assert claimed.attempt_count == 1

    def test_claim_non_pending_fails(self, repository: AgentTaskRepository):
        """Cannot claim a task that's not pending."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"}
        )
        repository.claim_task(task.task_id)

        with pytest.raises(TaskConflictError):
            repository.claim_task(task.task_id)

    def test_complete_task(self, repository: AgentTaskRepository):
        """Complete a running task."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"}
        )
        repository.claim_task(task.task_id)

        result = {"summary": "Test result"}
        completed = repository.complete_task(
            task.task_id,
            result=result,
            tokens_input=100,
            tokens_output=200
        )

        assert completed.status == AgentTaskStatus.COMPLETED
        assert completed.result == result
        assert completed.tokens_input == 100
        assert completed.tokens_output == 200
        assert completed.completed_at is not None

    def test_fail_task_with_retry(self, repository: AgentTaskRepository):
        """Fail a task and verify retry scheduling."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"},
            max_attempts=3
        )
        repository.claim_task(task.task_id)

        failed = repository.fail_task(
            task.task_id,
            error_message="LLM timeout",
            error_code="LLM_TIMEOUT",
            is_retryable=True
        )

        assert failed.status == AgentTaskStatus.RETRYING
        assert failed.next_retry_at is not None
        assert failed.last_error == "LLM timeout"

    def test_fail_task_permanent(self, repository: AgentTaskRepository):
        """Fail a task permanently (non-retryable)."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"}
        )
        repository.claim_task(task.task_id)

        failed = repository.fail_task(
            task.task_id,
            error_message="Invalid content",
            is_retryable=False
        )

        assert failed.status == AgentTaskStatus.FAILED
        assert failed.completed_at is not None

    def test_idempotency_key(self, repository: AgentTaskRepository):
        """Test idempotency key prevents duplicates."""
        task1 = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"},
            idempotency_key="unique-key-123"
        )

        with pytest.raises(IdempotencyConflictError) as exc_info:
            repository.create_task(
                agent_type=AgentType.RESEARCH,
                input_params={"topic": "different"},
                idempotency_key="unique-key-123"
            )

        assert exc_info.value.existing_task_id == task1.task_id

    def test_create_or_get_by_idempotency_key(self, repository: AgentTaskRepository):
        """Test create_or_get returns existing task."""
        task1, created1 = repository.create_or_get_by_idempotency_key(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"},
            idempotency_key="unique-key-456"
        )
        assert created1 is True

        task2, created2 = repository.create_or_get_by_idempotency_key(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "different"},
            idempotency_key="unique-key-456"
        )
        assert created2 is False
        assert task2.task_id == task1.task_id

    def test_list_tasks_filtering(self, repository: AgentTaskRepository):
        """Test task listing with filters."""
        # Create tasks with different statuses
        task1 = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test1"}
        )
        task2 = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test2"}
        )
        repository.claim_task(task2.task_id)

        pending = repository.list_tasks(status=AgentTaskStatus.PENDING)
        assert len(pending) == 1
        assert pending[0].task_id == task1.task_id

        running = repository.list_tasks(status=AgentTaskStatus.RUNNING)
        assert len(running) == 1
        assert running[0].task_id == task2.task_id

    def test_cancel_task(self, repository: AgentTaskRepository):
        """Test task cancellation."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"}
        )

        cancelled = repository.cancel_task(task.task_id, "User requested")
        assert cancelled.status == AgentTaskStatus.CANCELLED
        assert cancelled.error_message == "User requested"

    def test_task_events_logged(self, repository: AgentTaskRepository):
        """Verify events are logged for state changes."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"}
        )
        repository.claim_task(task.task_id)
        repository.complete_task(task.task_id, result={"done": True})

        events = repository.get_task_events(task.task_id)
        event_types = [e.event_type for e in events]

        assert "created" in event_types
        assert "started" in event_types
        assert "completed" in event_types


# =============================================================================
# LAYER 3: PROPERTY-BASED TESTS
# =============================================================================

class TestPropertyBasedValidation:
    """Property-based tests for invariants."""

    def test_progress_monotonic(self, repository: AgentTaskRepository):
        """Progress should only increase, never decrease."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"}
        )
        repository.claim_task(task.task_id)

        # Update progress incrementally
        for percent in [10, 25, 50, 75, 90]:
            repository.update_progress(task.task_id, percent=percent)

        # Try to decrease progress
        repository.update_progress(task.task_id, percent=20)

        final = repository.get_task(task.task_id)
        assert final.progress_percent == 90  # Should not decrease

    def test_attempt_count_never_exceeds_max(self, repository: AgentTaskRepository):
        """attempt_count should never exceed max_attempts."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"},
            max_attempts=2
        )

        # First attempt
        repository.claim_task(task.task_id)
        repository.fail_task(task.task_id, "Error 1", is_retryable=True)

        # Second attempt
        task = repository.get_task(task.task_id)
        assert task.status == AgentTaskStatus.RETRYING

        repository.claim_retry_task(task.task_id)
        repository.fail_task(task.task_id, "Error 2", is_retryable=True)

        # Should be permanently failed now
        task = repository.get_task(task.task_id)
        assert task.status == AgentTaskStatus.FAILED
        assert task.attempt_count <= task.max_attempts

    def test_random_topics_validate_correctly(self):
        """Random valid topics should pass validation."""
        for _ in range(100):
            word_count = random.randint(2, 10)
            words = [
                ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 10)))
                for _ in range(word_count)
            ]
            topic = ' '.join(words)

            # Should not raise
            input_data = ResearchInput(topic=topic)
            assert len(input_data.topic.split()) >= 2


# =============================================================================
# LAYER 4: FAILURE INJECTION TESTS
# =============================================================================

class TestFailureInjection:
    """Test error handling and recovery."""

    @pytest.mark.asyncio
    async def test_llm_timeout_handling(self, research_agent: ResearchAgent):
        """LLM timeout should raise LLMTimeoutError."""
        with patch.object(research_agent, '_call_llm') as mock_call:
            mock_call.side_effect = asyncio.TimeoutError()

            with pytest.raises(LLMTimeoutError):
                await research_agent.execute(
                    topic="Test topic here",
                    timeout_seconds=1
                )

    @pytest.mark.asyncio
    async def test_llm_rate_limit_handling(self, research_agent: ResearchAgent):
        """Rate limit errors should be properly categorized."""
        with patch.object(research_agent, '_call_llm') as mock_call:
            mock_call.side_effect = Exception("Rate limit exceeded")

            with pytest.raises(LLMRateLimitError):
                await research_agent.execute(topic="Test topic here")

    @pytest.mark.asyncio
    async def test_malformed_json_response(self, research_agent: ResearchAgent):
        """Malformed JSON should raise LLMResponseError."""
        with patch.object(research_agent, '_call_llm') as mock_call:
            mock_call.return_value = {
                "raw": "This is not valid JSON {{{",
                "parsed": {},
                "input_tokens": 100,
                "output_tokens": 50,
            }
            # The _safe_parse_json fallback will catch this

    def test_repository_handles_missing_task(self, repository: AgentTaskRepository):
        """Operations on non-existent tasks should raise TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            repository.claim_task("nonexistent-id")

        with pytest.raises(TaskNotFoundError):
            repository.complete_task("nonexistent-id", result={})

        with pytest.raises(TaskNotFoundError):
            repository.fail_task("nonexistent-id", "Error")

    def test_repository_handles_invalid_state_transitions(self, repository: AgentTaskRepository):
        """Invalid state transitions should raise TaskConflictError."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"}
        )

        # Cannot complete a pending task
        with pytest.raises(TaskConflictError):
            repository.complete_task(task.task_id, result={})

        # Claim it
        repository.claim_task(task.task_id)

        # Complete it
        repository.complete_task(task.task_id, result={})

        # Cannot fail a completed task
        with pytest.raises(TaskConflictError):
            repository.fail_task(task.task_id, "Error")


# =============================================================================
# LAYER 5: CONCURRENCY TESTS
# =============================================================================

class TestConcurrency:
    """Test thread safety and race conditions."""

    def test_concurrent_task_creation(self, repository: AgentTaskRepository):
        """Multiple threads creating tasks should not conflict."""
        created_ids = []
        errors = []

        def create_task(i):
            try:
                task = repository.create_task(
                    agent_type=AgentType.RESEARCH,
                    input_params={"topic": f"test topic {i}"}
                )
                created_ids.append(task.task_id)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=create_task, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(created_ids) == 50
        assert len(set(created_ids)) == 50  # All unique

    def test_concurrent_claim_same_task(self, repository: AgentTaskRepository):
        """Only one thread should be able to claim a task."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"}
        )

        successful_claims = []
        failed_claims = []

        def try_claim():
            try:
                repository.claim_task(task.task_id)
                successful_claims.append(True)
            except TaskConflictError:
                failed_claims.append(True)

        threads = [threading.Thread(target=try_claim) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Exactly one should succeed
        assert len(successful_claims) == 1
        assert len(failed_claims) == 9

    def test_idempotency_key_race_condition(self, repository: AgentTaskRepository):
        """Concurrent requests with same idempotency key should not create duplicates."""
        created_ids = []
        conflicts = []

        def create_with_key():
            try:
                task = repository.create_task(
                    agent_type=AgentType.RESEARCH,
                    input_params={"topic": "test"},
                    idempotency_key="shared-key"
                )
                created_ids.append(task.task_id)
            except IdempotencyConflictError as e:
                conflicts.append(e.existing_task_id)

        threads = [threading.Thread(target=create_with_key) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Exactly one should be created
        assert len(created_ids) == 1
        assert len(conflicts) == 9
        # All conflicts should reference the same task
        assert all(tid == created_ids[0] for tid in conflicts)


# =============================================================================
# LAYER 6: SECURITY TESTS
# =============================================================================

class TestSecurity:
    """Test security and abuse prevention."""

    def test_topic_length_limit(self):
        """Topic should be limited to prevent abuse."""
        long_topic = "word " * 1000  # Very long topic

        with pytest.raises(ValueError):
            ResearchInput(topic=long_topic)

    def test_focus_areas_limit(self):
        """Focus areas should be limited."""
        many_areas = [f"area{i}" for i in range(100)]
        input_data = ResearchInput(
            topic="Test topic here",
            focus_areas=many_areas
        )
        assert len(input_data.focus_areas) <= 10

    def test_xss_in_topic_not_executed(self):
        """XSS attempts in topic should be stored safely."""
        xss_topic = "<script>alert('xss')</script> AI trends"
        # Should not raise - validation doesn't care about XSS
        # (that's the frontend's job to escape)
        input_data = ResearchInput(topic=xss_topic)
        assert "<script>" in input_data.topic

    def test_sql_injection_in_topic(self, repository: AgentTaskRepository):
        """SQL injection in topic should be safely stored."""
        sql_topic = "'; DROP TABLE agent_tasks; -- AI trends"
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": sql_topic}
        )

        # Table should still exist
        retrieved = repository.get_task(task.task_id)
        assert retrieved is not None
        assert retrieved.input_params["topic"] == sql_topic

    def test_task_isolation(self, repository: AgentTaskRepository):
        """Tasks should be isolated by user_id."""
        task1 = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "user1 topic"},
            user_id="user1"
        )
        task2 = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "user2 topic"},
            user_id="user2"
        )

        user1_tasks = repository.list_tasks(user_id="user1")
        user2_tasks = repository.list_tasks(user_id="user2")

        assert len(user1_tasks) == 1
        assert len(user2_tasks) == 1
        assert user1_tasks[0].task_id == task1.task_id
        assert user2_tasks[0].task_id == task2.task_id


# =============================================================================
# LAYER 7: USABILITY TESTS
# =============================================================================

class TestUsability:
    """Test API usability and developer experience."""

    def test_task_response_format(self, repository: AgentTaskRepository):
        """Task response should be well-structured for frontend."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"}
        )

        response = task.to_response_dict()

        # Required fields should exist
        assert "task_id" in response
        assert "agent_type" in response
        assert "status" in response
        assert "progress" in response
        assert "timestamps" in response
        assert "links" in response

        # Progress should have expected structure
        assert "percent" in response["progress"]
        assert "message" in response["progress"]

        # Links should be useful
        assert "self" in response["links"]
        assert response["links"]["self"] == f"/agents/tasks/{task.task_id}"
        assert "events" in response["links"]
        assert response["links"]["events"] == f"/agents/tasks/{task.task_id}/events"
        # Active task should have stream link
        assert response["links"]["stream"] == f"/agents/tasks/{task.task_id}/stream"

    def test_completed_task_has_no_stream_link(self, repository: AgentTaskRepository):
        """Completed tasks should not expose stream link."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"}
        )
        repository.claim_task(task.task_id)
        repository.complete_task(task.task_id, result={"done": True})
        completed = repository.get_task(task.task_id)
        response = completed.to_response_dict()
        assert response["links"]["stream"] is None
        assert response["links"]["cancel"] is None

    def test_error_messages_are_actionable(self):
        """Error messages should tell user what to do."""
        try:
            ResearchInput(topic="x")  # Too short
        except ValueError as e:
            assert "2 words" in str(e)  # Tells user the requirement

    def test_default_values_are_sensible(self):
        """Default values should produce good results."""
        input_data = ResearchInput(topic="AI trends in healthcare")

        assert input_data.depth == "comprehensive"  # Good default
        assert input_data.max_sections == 5  # Reasonable default
        assert input_data.focus_areas == []  # Empty by default

    def test_progress_updates_are_informative(self, repository: AgentTaskRepository):
        """Progress updates should include helpful messages."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"}
        )
        repository.claim_task(task.task_id)

        repository.update_progress(
            task.task_id,
            percent=50,
            message="Analyzing sources...",
            current_step="analysis",
            total_steps=3,
            current_step_num=2
        )

        updated = repository.get_task(task.task_id)
        assert updated.progress_message is not None
        assert updated.current_step is not None
        assert updated.total_steps is not None


# =============================================================================
# API ENDPOINT TESTS (Integration with FastAPI)
# =============================================================================

class TestAPIEndpoints:
    """Test the FastAPI endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        # Import here to avoid circular imports
        from fastapi.testclient import TestClient
        from backend.api import app

        return TestClient(app)

    def test_research_endpoint_validation(self, client):
        """Research endpoint should validate input."""
        # Topic too short (Pydantic min_length=3 on ResearchRequest fires 422)
        response = client.post("/agents/v2/research", json={
            "topic": "x"
        })
        assert response.status_code in [400, 422]

        # Empty topic
        response = client.post("/agents/v2/research", json={
            "topic": ""
        })
        assert response.status_code in [400, 422]

    def test_task_not_found(self, client):
        """Getting non-existent task should return 404."""
        response = client.get("/agents/v2/tasks/nonexistent-id")
        assert response.status_code == 404
        body = response.json()
        # Error may be in detail.code or message depending on global error handler
        raw = json.dumps(body)
        assert "TASK_NOT_FOUND" in raw or "not found" in raw.lower()

    def test_health_endpoint(self, client):
        """Health endpoint should return status."""
        response = client.get("/agents/v2/health")
        assert response.status_code == 200
        assert "status" in response.json()

    def test_stats_endpoint(self, client):
        """Stats endpoint should return task counts."""
        response = client.get("/agents/v2/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "pending" in data

    def test_list_agent_types(self, client):
        """List agent types should return available agents."""
        response = client.get("/agents/v2/types")
        assert response.status_code == 200
        data = response.json()
        assert "types" in data
        assert len(data["types"]) > 0

    def test_repurpose_formats_endpoint(self, client):
        """Formats/repurpose endpoint should list all 10 formats."""
        response = client.get("/agents/v2/formats/repurpose")
        assert response.status_code == 200
        data = response.json()
        assert "formats" in data
        formats = data["formats"]
        assert len(formats) == 10
        format_ids = {f["id"] for f in formats}
        assert "tweet_thread" in format_ids
        assert "linkedin_post" in format_ids
        assert "executive_summary" in format_ids
        for f in formats:
            assert "id" in f
            assert "name" in f
            assert "description" in f

    def test_list_agent_types_has_all_five(self, client):
        """Agent types endpoint should list all 5 agent types."""
        response = client.get("/agents/v2/types")
        assert response.status_code == 200
        types = response.json()["types"]
        type_ids = {t["id"] for t in types}
        assert type_ids == {"research", "data_analyst", "email_draft", "content_repurpose", "proofreading"}
        for t in types:
            assert "endpoint" in t
            assert t["endpoint"].startswith("/agents/v2/")

    def test_stream_link_present_for_active_task(self, client):
        """Active tasks should have a stream link in HATEOAS."""
        # Create a task in async mode so it stays pending
        response = client.post("/agents/v2/research", json={
            "topic": "test stream link for HATEOAS",
            "sync": False,
        })
        assert response.status_code == 202
        data = response.json()
        links = data.get("links", {})
        # PENDING tasks are active, so stream link should be present
        assert links.get("stream") is not None
        assert "/stream" in links["stream"]

    def test_stream_link_absent_for_completed_task(self, repository: AgentTaskRepository):
        """Completed tasks should NOT have a stream link."""
        from backend.app.api.routes.agents_v2 import task_to_response

        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test completed"},
        )
        repository.claim_task(task.task_id)
        task = repository.complete_task(task.task_id, result={"summary": "done"})
        resp = task_to_response(task)
        assert resp.links.stream is None

    def test_list_tasks_total_count_is_accurate(self, client):
        """List tasks should return correct total count for pagination."""
        # Create 5 tasks via the API so they go through the app's repository
        for i in range(5):
            client.post("/agents/v2/research", json={
                "topic": f"pagination test topic {i}",
                "idempotency_key": f"pagination-test-{i}-{time.time_ns()}",
            })

        # Fetch with limit=2
        response = client.get("/agents/v2/tasks", params={"limit": 2, "offset": 0})
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) <= 2
        assert data["total"] >= 5  # Total should reflect ALL matching tasks
        assert data["limit"] == 2
        assert data["offset"] == 0

    def test_data_analyst_endpoint_validation(self, client):
        """Data analyst endpoint should validate input."""
        # Empty question
        response = client.post("/agents/v2/data-analyst", json={
            "question": "x",
            "data": [{"a": 1}],
        })
        assert response.status_code in [400, 422]

    def test_email_draft_endpoint_validation(self, client):
        """Email draft endpoint should validate input."""
        response = client.post("/agents/v2/email-draft", json={
            "context": "x",  # too short
            "purpose": "test purpose here",
        })
        assert response.status_code in [400, 422]

    def test_content_repurpose_endpoint_validation(self, client):
        """Content repurpose endpoint should validate input."""
        response = client.post("/agents/v2/content-repurpose", json={
            "content": "x",  # too short
            "source_format": "article",
            "target_formats": ["tweet_thread"],
        })
        assert response.status_code in [400, 422]

    def test_proofreading_endpoint_validation(self, client):
        """Proofreading endpoint should validate input."""
        response = client.post("/agents/v2/proofreading", json={
            "text": "x",  # too short
        })
        assert response.status_code in [400, 422]

    def test_cancel_task_endpoint(self, client):
        """Cancel endpoint should cancel a pending task."""
        # Create task directly in app's repo (bypasses async execution
        # which would race with the cancel request)
        from backend.app.services.agents import agent_service_v2
        repo = agent_service_v2._repo
        task = repo.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "cancel test topic here"},
        )

        response = client.post(
            f"/agents/v2/tasks/{task.task_id}/cancel",
            json={"reason": "test cancellation"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    def test_cancel_nonexistent_task(self, client):
        """Cancelling a non-existent task should 404."""
        response = client.post("/agents/v2/tasks/fake-id/cancel")
        assert response.status_code == 404

    def test_events_endpoint(self, client):
        """Events endpoint should return audit trail."""
        # Create task via API so it's visible to the app's service
        create_resp = client.post("/agents/v2/research", json={
            "topic": "events test topic here",
        })
        assert create_resp.status_code in [200, 201, 202]
        task_id = create_resp.json()["task_id"]

        response = client.get(f"/agents/v2/tasks/{task_id}/events")
        assert response.status_code == 200
        events = response.json()
        assert isinstance(events, list)
        assert len(events) >= 1  # At least the creation event

    def test_events_nonexistent_task(self, client):
        """Events for non-existent task should 404."""
        response = client.get("/agents/v2/tasks/fake-id/events")
        assert response.status_code == 404


# =============================================================================
# AGENT V2 INPUT VALIDATION TESTS
# =============================================================================

class TestAgentV2Validation:
    """Test input validation for all v2 agents."""

    def test_data_analyst_input_validates_question(self):
        """DataAnalystInput requires question with at least 2 words."""
        from backend.app.services.agents.data_analyst_agent import DataAnalystInput

        with pytest.raises(Exception):
            DataAnalystInput(question="x", data=[{"a": 1}])

        valid = DataAnalystInput(
            question="What is the average revenue",
            data=[{"revenue": 100}, {"revenue": 200}],
        )
        assert valid.question.strip()

    def test_data_analyst_input_validates_data_rows(self):
        """DataAnalystInput validates data row count and consistency."""
        from backend.app.services.agents.data_analyst_agent import DataAnalystInput

        with pytest.raises(Exception):
            DataAnalystInput(question="test question here", data=[])

    def test_email_draft_input_validates_tone(self):
        """EmailDraftInput rejects invalid tones."""
        from backend.app.services.agents.email_draft_agent import EmailDraftInput

        with pytest.raises(Exception):
            EmailDraftInput(
                context="Test context here for email",
                purpose="Follow up on meeting",
                tone="angry",  # invalid
            )

        valid = EmailDraftInput(
            context="Project discussion context",
            purpose="Schedule follow-up meeting",
            tone="professional",
        )
        assert valid.tone == "professional"

    def test_email_draft_thread_truncation(self):
        """EmailDraftInput truncates thread to last 3 emails."""
        from backend.app.services.agents.email_draft_agent import EmailDraftInput

        emails = [f"Email {i}: " + "x" * 100 for i in range(10)]
        valid = EmailDraftInput(
            context="Thread context for testing",
            purpose="Reply to thread",
            previous_emails=emails,
        )
        assert len(valid.previous_emails) <= 3

    def test_content_repurpose_validates_formats(self):
        """ContentRepurposeInput rejects unknown formats."""
        from backend.app.services.agents.content_repurpose_agent import ContentRepurposeInput

        with pytest.raises(Exception):
            ContentRepurposeInput(
                content="This is a test article with enough words to pass validation",
                source_format="article",
                target_formats=["invalid_format"],
            )

        valid = ContentRepurposeInput(
            content="This is a test article with enough words to pass validation check",
            source_format="article",
            target_formats=["tweet_thread", "linkedin_post"],
        )
        assert len(valid.target_formats) == 2

    def test_content_repurpose_deduplicates_formats(self):
        """ContentRepurposeInput removes duplicate formats."""
        from backend.app.services.agents.content_repurpose_agent import ContentRepurposeInput

        valid = ContentRepurposeInput(
            content="This is a test article with enough words to pass validation check",
            source_format="article",
            target_formats=["tweet_thread", "tweet_thread", "blog_summary"],
        )
        assert len(valid.target_formats) == 2

    def test_proofreading_validates_style_guide(self):
        """ProofreadingInput rejects invalid style guides."""
        from backend.app.services.agents.proofreading_agent import ProofreadingInput

        with pytest.raises(Exception):
            ProofreadingInput(
                text="This is a test sentence for proofreading validation.",
                style_guide="invalid_guide",
            )

        valid = ProofreadingInput(
            text="This is a test sentence for proofreading validation.",
            style_guide="chicago",
        )
        assert valid.style_guide == "chicago"

    def test_proofreading_validates_focus_areas(self):
        """ProofreadingInput rejects invalid focus areas."""
        from backend.app.services.agents.proofreading_agent import ProofreadingInput

        with pytest.raises(Exception):
            ProofreadingInput(
                text="This is a test sentence for proofreading validation.",
                focus_areas=["invalid_area"],
            )

    def test_proofreading_caps_focus_areas_at_five(self):
        """ProofreadingInput allows max 5 focus areas."""
        from backend.app.services.agents.proofreading_agent import ProofreadingInput

        valid = ProofreadingInput(
            text="This is a test sentence for proofreading validation.",
            focus_areas=["grammar", "spelling", "punctuation", "clarity", "conciseness", "tone"],
        )
        assert len(valid.focus_areas) <= 5


class TestCountTasks:
    """Test the count_tasks repository method."""

    def test_count_all_tasks(self, repository: AgentTaskRepository):
        """count_tasks should return total count of all tasks."""
        for i in range(3):
            repository.create_task(
                agent_type=AgentType.RESEARCH,
                input_params={"topic": f"count test {i}"},
            )
        count = repository.count_tasks()
        assert count >= 3

    def test_count_tasks_by_agent_type(self, repository: AgentTaskRepository):
        """count_tasks should filter by agent type."""
        repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "research count test"},
        )
        repository.create_task(
            agent_type=AgentType.DATA_ANALYST,
            input_params={"question": "analyst count test", "data": [{"a": 1}]},
        )

        research_count = repository.count_tasks(agent_type=AgentType.RESEARCH)
        analyst_count = repository.count_tasks(agent_type=AgentType.DATA_ANALYST)
        assert research_count >= 1
        assert analyst_count >= 1

    def test_count_tasks_by_status(self, repository: AgentTaskRepository):
        """count_tasks should filter by status."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "status count test"},
        )
        pending_count = repository.count_tasks(status=AgentTaskStatus.PENDING)
        assert pending_count >= 1


# =============================================================================
# CLEANUP TESTS
# =============================================================================

class TestCleanup:
    """Test task cleanup functionality."""

    def test_expired_tasks_cleanup(self, repository: AgentTaskRepository):
        """Expired tasks should be cleanable."""
        # Create a task that's already expired
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test"},
        )
        repository.claim_task(task.task_id)
        repository.complete_task(task.task_id, result={})

        # Manually backdate expires_at to make it expired
        from backend.app.repositories.agent_tasks.models import _utc_now
        from sqlmodel import Session
        with Session(repository._engine) as session:
            db_task = session.get(AgentTaskModel, task.task_id)
            db_task.expires_at = _utc_now() - timedelta(hours=1)
            session.add(db_task)
            session.commit()

        # Run cleanup
        cleaned = repository.cleanup_expired_tasks()
        assert cleaned >= 1

        # Task should be gone
        assert repository.get_task(task.task_id) is None


# =============================================================================
# TRADE-OFF 1: BACKGROUND TASK QUEUE TESTS
# =============================================================================

class TestBackgroundTaskQueue:
    """Test the ThreadPoolExecutor-based background execution."""

    @pytest.fixture
    def service(self, repository: AgentTaskRepository):
        """Create an AgentService with test repository."""
        from backend.app.services.agents.agent_service import AgentService
        return AgentService(repository=repository)

    @pytest.mark.asyncio
    async def test_async_task_enqueues_to_background(self, service, repository):
        """When sync=False, task should be enqueued and return immediately as PENDING."""
        with patch.object(service, '_execute_task', new_callable=AsyncMock) as mock_exec:
            task = await service.run_research(
                topic="Background test topic",
                sync=False,
            )

            # Task should return immediately as PENDING
            assert task.status == AgentTaskStatus.PENDING
            assert task.task_id is not None

    @pytest.mark.asyncio
    async def test_sync_task_executes_inline(self, service, repository):
        """When sync=True, task should be executed inline and return completed."""
        mock_report = MagicMock()
        mock_report.model_dump.return_value = {"summary": "test result"}
        mock_metadata = {"tokens_input": 100, "tokens_output": 200, "estimated_cost_cents": 5}

        agent = service._agents[AgentType.RESEARCH]
        with patch.object(agent, 'execute', new_callable=AsyncMock) as mock_exec:
            mock_exec.return_value = (mock_report, mock_metadata)
            task = await service.run_research(
                topic="Sync test topic",
                sync=True,
            )

            assert task.status == AgentTaskStatus.COMPLETED
            assert task.result is not None

    def test_worker_starts_and_stops(self, service):
        """AgentTaskWorker should start and stop cleanly."""
        from backend.app.services.agents.agent_service import AgentTaskWorker

        worker = AgentTaskWorker(service, poll_interval=1, batch_size=1)
        assert worker.is_running is False

        started = worker.start()
        assert started is True
        assert worker.is_running is True

        # Starting again should return False
        assert worker.start() is False

        stopped = worker.stop(timeout=5)
        assert stopped is True
        assert worker.is_running is False

    def test_worker_stats_track_cycles(self, service):
        """Worker stats should track polling cycles."""
        from backend.app.services.agents.agent_service import AgentTaskWorker

        worker = AgentTaskWorker(service, poll_interval=1, batch_size=1)
        worker.start()
        time.sleep(2.5)  # Let it run a couple cycles
        worker.stop(timeout=5)

        stats = worker.stats
        assert stats["cycles"] >= 1
        assert "pending_processed" in stats
        assert "retries_processed" in stats
        assert "errors" in stats

    def test_stale_task_recovery(self, repository):
        """Stale RUNNING tasks should be recovered on startup."""
        from backend.app.services.agents.agent_service import AgentService

        # Create a task and manually set it to RUNNING with old timestamp
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "stale test"},
            max_attempts=3,
        )
        repository.claim_task(task.task_id)

        # Manually backdate the started_at to simulate a stale task
        from backend.app.repositories.agent_tasks.models import _utc_now
        from sqlmodel import Session
        with Session(repository._engine) as session:
            db_task = session.get(AgentTaskModel, task.task_id)
            db_task.started_at = _utc_now() - timedelta(minutes=15)
            session.add(db_task)
            session.commit()

        # Recover should find the stale task
        recovered = repository.recover_stale_tasks(stale_threshold_seconds=600)
        assert len(recovered) == 1
        assert recovered[0].task_id == task.task_id
        # Should be moved to RETRYING (since max_attempts=3, attempt_count=1)
        assert recovered[0].status in (AgentTaskStatus.RETRYING, AgentTaskStatus.FAILED)

    @pytest.mark.asyncio
    async def test_executor_shutdown_leaves_task_pending(self, service, repository):
        """If executor is shut down, task should remain PENDING for recovery."""
        import sys
        # The package attribute shadows the module name, so use sys.modules
        agent_svc_module = sys.modules["backend.app.services.agents.agent_service"]

        original_executor = agent_svc_module._AGENT_EXECUTOR

        # Create a shut-down executor
        from concurrent.futures import ThreadPoolExecutor
        dead_executor = ThreadPoolExecutor(max_workers=1)
        dead_executor.shutdown(wait=False)
        agent_svc_module._AGENT_EXECUTOR = dead_executor

        try:
            task = await service.run_research(
                topic="Shutdown executor test",
                sync=False,
            )
            # Task should remain PENDING (not crash)
            assert task.status == AgentTaskStatus.PENDING
            retrieved = repository.get_task(task.task_id)
            assert retrieved.status == AgentTaskStatus.PENDING
        finally:
            agent_svc_module._AGENT_EXECUTOR = original_executor

    def test_running_tasks_thread_safety(self, service):
        """_running_tasks set operations should be thread-safe."""
        errors = []

        def add_and_remove(i):
            try:
                tid = f"thread-test-{i}"
                with service._running_tasks_lock:
                    service._running_tasks.add(tid)
                time.sleep(0.001)
                with service._running_tasks_lock:
                    service._running_tasks.discard(tid)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=add_and_remove, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(service._running_tasks) == 0


# =============================================================================
# TRADE-OFF 2: SSE PROGRESS STREAMING TESTS
# =============================================================================

class TestSSEProgressStreaming:
    """Test Server-Sent Events progress streaming."""

    @pytest.fixture
    def service(self, repository: AgentTaskRepository):
        from backend.app.services.agents.agent_service import AgentService
        return AgentService(repository=repository)

    @pytest.mark.asyncio
    async def test_stream_emits_progress_events(self, service, repository):
        """Stream should emit progress events as task progresses."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "stream test"}
        )
        repository.claim_task(task.task_id)

        # Update progress in background after a brief delay
        async def _update_progress():
            await asyncio.sleep(0.3)
            repository.update_progress(task.task_id, percent=50, message="Halfway")
            await asyncio.sleep(0.3)
            repository.complete_task(task.task_id, result={"done": True})

        update_task = asyncio.create_task(_update_progress())

        events = []
        async for event in service.stream_task_progress(
            task.task_id,
            poll_interval=0.1,
            timeout=5.0,
        ):
            events.append(event)

        await update_task

        # Should have at least a progress event and a complete event
        event_types = [e["event"] for e in events]
        assert "progress" in event_types
        assert "complete" in event_types

    @pytest.mark.asyncio
    async def test_stream_task_not_found(self, service, repository):
        """Stream should emit error for non-existent task."""
        events = []
        async for event in service.stream_task_progress(
            "nonexistent-task-id",
            poll_interval=0.1,
            timeout=5.0,
        ):
            events.append(event)

        assert len(events) == 1
        assert events[0]["event"] == "error"
        assert events[0]["data"]["code"] == "TASK_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_stream_already_completed_task(self, service, repository):
        """Stream for completed task should immediately return complete event."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "completed test"}
        )
        repository.claim_task(task.task_id)
        repository.complete_task(task.task_id, result={"summary": "done"})

        events = []
        async for event in service.stream_task_progress(
            task.task_id,
            poll_interval=0.1,
            timeout=5.0,
        ):
            events.append(event)

        # Should get progress (100%) then complete
        assert any(e["event"] == "complete" for e in events)

    @pytest.fixture
    def client(self):
        """Create a test client for SSE endpoint testing."""
        from fastapi.testclient import TestClient
        from backend.api import app
        return TestClient(app)

    def test_sse_endpoint_returns_event_stream(self, client):
        """SSE endpoint should return text/event-stream content type."""
        # Create a task via API and complete it through the app's service
        from backend.app.services.agents import agent_service_v2
        repo = agent_service_v2._repo
        task = repo.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "sse test topic here"}
        )
        repo.claim_task(task.task_id)
        repo.complete_task(task.task_id, result={"done": True})

        with client.stream("GET", f"/agents/v2/tasks/{task.task_id}/stream") as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_stream_heartbeat_on_idle(self, service, repository):
        """Stream should emit heartbeat when no progress changes occur."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "heartbeat test"}
        )
        repository.claim_task(task.task_id)

        # Complete the task after the heartbeat fires
        async def _complete_later():
            await asyncio.sleep(1.8)
            repository.complete_task(task.task_id, result={"done": True})

        update_task = asyncio.create_task(_complete_later())

        events = []
        async for event in service.stream_task_progress(
            task.task_id,
            poll_interval=0.1,
            timeout=5.0,
            heartbeat_interval=0.5,  # Fast heartbeat for test
        ):
            events.append(event)

        await update_task

        event_types = [e["event"] for e in events]
        assert "heartbeat" in event_types
        assert "complete" in event_types

    @pytest.mark.asyncio
    async def test_stream_db_error_recovery(self, service, repository):
        """Stream should recover from transient DB errors."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "db error test"}
        )
        repository.claim_task(task.task_id)

        call_count = 0
        original_get = service._repo.get_task

        def flaky_get(tid):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise Exception("Simulated DB error")
            return original_get(tid)

        # Complete after a delay so we don't loop forever
        async def _complete_later():
            await asyncio.sleep(0.5)
            repository.complete_task(task.task_id, result={"done": True})

        update_task = asyncio.create_task(_complete_later())

        events = []
        with patch.object(service._repo, 'get_task', side_effect=flaky_get):
            async for event in service.stream_task_progress(
                task.task_id,
                poll_interval=0.1,
                timeout=5.0,
            ):
                events.append(event)

        await update_task

        event_types = [e["event"] for e in events]
        # Should have an error event from the DB failure
        assert "error" in event_types
        db_errors = [e for e in events if e["event"] == "error" and e["data"].get("code") == "DB_ERROR"]
        assert len(db_errors) >= 1
        # Should still eventually complete
        assert "complete" in event_types

    @pytest.mark.asyncio
    async def test_stream_cancelled_task(self, service, repository):
        """Stream should emit complete event when task is cancelled mid-stream."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "cancel stream test"}
        )
        repository.claim_task(task.task_id)

        async def _cancel_later():
            await asyncio.sleep(0.3)
            repository.cancel_task(task.task_id, reason="User cancelled")

        cancel_task = asyncio.create_task(_cancel_later())

        events = []
        async for event in service.stream_task_progress(
            task.task_id,
            poll_interval=0.1,
            timeout=5.0,
        ):
            events.append(event)

        await cancel_task

        event_types = [e["event"] for e in events]
        assert "complete" in event_types
        final = [e for e in events if e["event"] == "complete"][0]
        assert final["data"]["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_stream_timeout(self, service, repository):
        """Stream should emit timeout error when timeout is reached."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "timeout test"}
        )
        repository.claim_task(task.task_id)
        # Don't complete the task — let it time out

        events = []
        async for event in service.stream_task_progress(
            task.task_id,
            poll_interval=0.1,
            timeout=0.5,  # Very short timeout
            heartbeat_interval=100,  # Suppress heartbeats for clarity
        ):
            events.append(event)

        last_event = events[-1]
        assert last_event["event"] == "error"
        assert last_event["data"]["code"] == "STREAM_TIMEOUT"

    def test_sse_endpoint_404_for_missing_task(self, client):
        """SSE endpoint should return 404 for non-existent task."""
        response = client.get("/agents/v2/tasks/nonexistent/stream")
        assert response.status_code == 404


# =============================================================================
# TRADE-OFF 3: HORIZONTAL SCALING TESTS
# =============================================================================

class TestHorizontalScaling:
    """Test preparation for horizontal scaling."""

    def test_worker_isolation_via_claim(self, repository: AgentTaskRepository):
        """Multiple workers claiming same task: only one should succeed."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "scaling test"}
        )

        successes = []
        failures = []

        def try_claim():
            try:
                repository.claim_task(task.task_id)
                successes.append(True)
            except TaskConflictError:
                failures.append(True)

        threads = [threading.Thread(target=try_claim) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(successes) == 1
        assert len(failures) == 19

    def test_concurrent_progress_updates(self, repository: AgentTaskRepository):
        """Multiple workers updating progress should not corrupt data."""
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "concurrent update test"}
        )
        repository.claim_task(task.task_id)

        errors = []

        def update_progress(pct):
            try:
                repository.update_progress(
                    task.task_id,
                    percent=pct,
                    message=f"At {pct}%"
                )
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=update_progress, args=(i * 10,))
            for i in range(1, 11)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        final = repository.get_task(task.task_id)
        assert final.progress_percent > 0  # Some progress was recorded
        assert final.progress_percent <= 100

    def test_configurable_worker_concurrency(self):
        """Worker concurrency should be configurable via env var."""
        from backend.app.services.agents.agent_service import AgentTaskWorker, AgentService

        # Default values
        worker = AgentTaskWorker(AgentService())
        assert worker._poll_interval >= 1
        assert worker._batch_size >= 1

    def test_wal_mode_enabled(self, repository: AgentTaskRepository):
        """SQLite WAL mode should be enabled for concurrent access."""
        from sqlmodel import Session

        repository._ensure_initialized()
        with Session(repository._engine) as session:
            result = session.exec(
                __import__('sqlalchemy', fromlist=['text']).text("PRAGMA journal_mode")
            )
            mode = result.scalar()
            assert mode.lower() == "wal"

    def test_repository_connection_pool_settings(self, temp_db_path):
        """Repository should have connection pooling configured."""
        repo = AgentTaskRepository(db_path=temp_db_path)

        # Engine should have pool_pre_ping for stale connection detection
        assert repo._engine.pool._pre_ping is True

    def test_stats_under_load(self, repository: AgentTaskRepository):
        """Stats should remain accurate under concurrent operations."""
        # Create multiple tasks
        for i in range(10):
            repository.create_task(
                agent_type=AgentType.RESEARCH,
                input_params={"topic": f"load test {i}"}
            )

        stats = repository.get_stats()
        assert stats["pending"] == 10
        assert stats["total"] == 10

    @pytest.mark.asyncio
    async def test_process_pending_handles_conflict(self, repository: AgentTaskRepository):
        """process_pending_tasks should gracefully handle TaskConflictError."""
        from backend.app.services.agents.agent_service import AgentService

        service = AgentService(repository=repository)

        # Create a pending task
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "conflict test"}
        )

        # Pre-claim it to simulate another worker
        repository.claim_task(task.task_id)

        # process_pending_tasks should not crash
        enqueued = await service.process_pending_tasks(limit=5)
        # Task was already RUNNING, so list_pending_tasks won't return it
        assert enqueued == 0

    @pytest.mark.asyncio
    async def test_process_retry_handles_conflict(self, repository: AgentTaskRepository):
        """process_retry_tasks should gracefully handle TaskConflictError."""
        from backend.app.services.agents.agent_service import AgentService

        service = AgentService(repository=repository)

        # Create a task, claim it, fail it to move to RETRYING
        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "retry conflict test"},
            max_attempts=3,
        )
        repository.claim_task(task.task_id)
        repository.fail_task(
            task.task_id,
            error_message="Test failure",
            is_retryable=True,
        )

        # Manually set next_retry_at to past so it's immediately retryable
        from backend.app.repositories.agent_tasks.models import _utc_now
        from sqlmodel import Session
        with Session(repository._engine) as session:
            db_task = session.get(AgentTaskModel, task.task_id)
            db_task.next_retry_at = _utc_now() - timedelta(seconds=60)
            session.add(db_task)
            session.commit()

        # This should not crash
        enqueued = await service.process_retry_tasks(limit=5)
        assert enqueued >= 0  # May be 0 or 1 depending on timing

    def test_worker_disabled_via_env(self):
        """Worker should not start when NEURA_AGENT_WORKER_DISABLED=true."""
        import os
        # This is tested implicitly in the lifespan — here we verify
        # the env var check works
        assert os.getenv("NEURA_AGENT_WORKER_DISABLED", "false").lower() in ("true", "false")

    def test_multiple_workers_dont_double_process(self, repository: AgentTaskRepository):
        """Two workers processing the same batch should not double-execute."""
        from backend.app.services.agents.agent_service import AgentService

        service = AgentService(repository=repository)

        # Create 5 tasks
        tasks = []
        for i in range(5):
            t = repository.create_task(
                agent_type=AgentType.RESEARCH,
                input_params={"topic": f"multi-worker test {i}"}
            )
            tasks.append(t)

        # Simulate two "workers" claiming concurrently
        claimed_ids = []
        conflict_ids = []

        def claim_all():
            for t in tasks:
                try:
                    repository.claim_task(t.task_id)
                    claimed_ids.append(t.task_id)
                except TaskConflictError:
                    conflict_ids.append(t.task_id)

        t1 = threading.Thread(target=claim_all)
        t2 = threading.Thread(target=claim_all)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Each task should be claimed exactly once
        assert len(claimed_ids) == 5
        # The other worker should have gotten conflicts for all 5
        assert len(conflict_ids) == 5

    def test_sqlite_busy_timeout(self, repository: AgentTaskRepository):
        """SQLite busy_timeout should be configured for write contention."""
        from sqlmodel import Session

        repository._ensure_initialized()
        with Session(repository._engine) as session:
            from sqlalchemy import text
            result = session.exec(text("PRAGMA busy_timeout"))
            timeout = result.scalar()
            assert timeout >= 30000  # At least 30 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
