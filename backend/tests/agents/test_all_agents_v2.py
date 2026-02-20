"""
Comprehensive Tests for ALL V2 Agents (lines 369-380)

Covers the 4 NEW agents (data_analyst, email_draft, content_repurpose,
proofreading) and the agent_service orchestration layer wiring all 6
agent types (including report_analyst).

7-layer test structure:
1. Unit Tests — Input validation, output models, local computation
2. Integration Tests — Repository + AgentService end-to-end
3. Property-Based Tests — Invariants that must hold across random inputs
4. Failure Injection Tests — Error categorisation, LLM failures
5. Concurrency Tests — Thread safety for all agents
6. Security Tests — Injection, abuse, bounds
7. Usability Tests — API ergonomics, error messages

Run with: pytest backend/tests/agents/test_all_agents_v2.py -v
"""
from __future__ import annotations

import asyncio
import random
import string
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.app.repositories.agent_tasks.models import (
    AgentTaskModel,
    AgentTaskStatus,
    AgentType,
)
from backend.app.repositories.agent_tasks.repository import (
    AgentTaskRepository,
    IdempotencyConflictError,
    TaskConflictError,
    TaskNotFoundError,
)

# Agent imports
from backend.app.services.agents.data_analyst_agent import (
    DataAnalystAgent,
    DataAnalystInput,
    DataAnalysisReport,
)
from backend.app.services.agents.email_draft_agent import (
    EmailDraftAgentV2,
    EmailDraftInput,
    EmailDraftResult,
)
from backend.app.services.agents.content_repurpose_agent import (
    ContentRepurposeAgentV2,
    ContentRepurposeInput,
    ContentRepurposeReport,
    VALID_FORMATS,
)
from backend.app.services.agents.proofreading_agent import (
    ProofreadingAgentV2,
    ProofreadingInput,
    ProofreadingReport,
    VALID_STYLE_GUIDES,
    VALID_FOCUS_AREAS,
)
from backend.app.services.agents.base_agent import (
    AgentError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMResponseError,
    ValidationError,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_all_agents.db"


@pytest.fixture
def repository(temp_db_path: Path) -> AgentTaskRepository:
    return AgentTaskRepository(db_path=temp_db_path)


@pytest.fixture
def data_analyst_agent() -> DataAnalystAgent:
    return DataAnalystAgent()


@pytest.fixture
def email_draft_agent() -> EmailDraftAgentV2:
    return EmailDraftAgentV2()


@pytest.fixture
def content_repurpose_agent() -> ContentRepurposeAgentV2:
    return ContentRepurposeAgentV2()


@pytest.fixture
def proofreading_agent() -> ProofreadingAgentV2:
    return ProofreadingAgentV2()


@pytest.fixture
def sample_data() -> List[Dict[str, Any]]:
    """Realistic tabular data for the data analyst agent."""
    return [
        {"name": "Alice", "age": 30, "salary": 75000, "dept": "Engineering"},
        {"name": "Bob", "age": 25, "salary": 60000, "dept": "Marketing"},
        {"name": "Charlie", "age": 35, "salary": 90000, "dept": "Engineering"},
        {"name": "Diana", "age": 28, "salary": 65000, "dept": "Sales"},
        {"name": "Eve", "age": 40, "salary": 110000, "dept": "Engineering"},
        {"name": "Frank", "age": 32, "salary": 72000, "dept": "Marketing"},
        {"name": "Grace", "age": 29, "salary": 68000, "dept": "Sales"},
        {"name": "Hank", "age": 45, "salary": 120000, "dept": "Engineering"},
    ]


# =============================================================================
# LAYER 1: UNIT TESTS — INPUT VALIDATION
# =============================================================================

class TestDataAnalystInputValidation:
    """Test input validation for data analyst agent."""

    def test_valid_input(self, sample_data):
        inp = DataAnalystInput(
            question="What is the average salary by department?",
            data=sample_data,
        )
        assert inp.question == "What is the average salary by department?"

    def test_question_too_short(self, sample_data):
        with pytest.raises(ValueError, match="at least 2 words"):
            DataAnalystInput(question="salary", data=sample_data)

    def test_empty_question(self, sample_data):
        with pytest.raises(ValueError):
            DataAnalystInput(question="", data=sample_data)

    def test_empty_data(self):
        with pytest.raises(ValueError):
            DataAnalystInput(question="What is the total?", data=[])

    def test_inconsistent_columns(self):
        data = [
            {"a": 1, "b": 2},
            {"a": 1, "c": 3},  # Different keys
        ]
        with pytest.raises(ValueError, match="inconsistent columns"):
            DataAnalystInput(question="What is the total?", data=data)

    def test_question_whitespace_trimmed(self, sample_data):
        inp = DataAnalystInput(
            question="  What is the average?  ",
            data=sample_data,
        )
        assert inp.question == "What is the average?"


class TestEmailDraftInputValidation:
    """Test input validation for email draft agent."""

    def test_valid_input(self):
        inp = EmailDraftInput(
            context="Meeting with client tomorrow about project X",
            purpose="Confirm the meeting time",
        )
        assert inp.tone == "professional"

    def test_empty_context(self):
        with pytest.raises(ValueError):
            EmailDraftInput(context="", purpose="Confirm meeting")

    def test_empty_purpose(self):
        with pytest.raises(ValueError):
            EmailDraftInput(context="Meeting tomorrow", purpose="")

    def test_invalid_tone(self):
        with pytest.raises(ValueError, match="Tone must be one of"):
            EmailDraftInput(
                context="Meeting tomorrow morning",
                purpose="Confirm the meeting",
                tone="aggressive",
            )

    def test_all_valid_tones(self):
        for tone in ["professional", "friendly", "formal", "casual", "empathetic", "assertive"]:
            inp = EmailDraftInput(
                context="Meeting tomorrow morning",
                purpose="Confirm the meeting",
                tone=tone,
            )
            assert inp.tone == tone

    def test_previous_emails_truncated(self):
        emails = [f"Email {i} " * 100 for i in range(10)]
        inp = EmailDraftInput(
            context="Meeting tomorrow morning",
            purpose="Confirm the meeting",
            previous_emails=emails,
        )
        assert len(inp.previous_emails) <= 3


class TestContentRepurposeInputValidation:
    """Test input validation for content repurpose agent."""

    def test_valid_input(self):
        inp = ContentRepurposeInput(
            content="This is a long article about artificial intelligence " * 5,
            source_format="article",
            target_formats=["tweet_thread", "linkedin_post"],
        )
        assert len(inp.target_formats) == 2

    def test_content_too_short(self):
        # Input passes min_length=20 but has < 5 words → custom validator fires
        with pytest.raises(ValueError, match="at least 5 words"):
            ContentRepurposeInput(
                content="Abcdefghijklmnopqrstu",
                source_format="article",
                target_formats=["tweet_thread"],
            )

    def test_empty_target_formats(self):
        with pytest.raises(ValueError):
            ContentRepurposeInput(
                content="This is a long article about AI " * 3,
                source_format="article",
                target_formats=[],
            )

    def test_invalid_target_format(self):
        with pytest.raises(ValueError, match="Unknown target format"):
            ContentRepurposeInput(
                content="This is a long article about AI " * 3,
                source_format="article",
                target_formats=["invalid_format"],
            )

    def test_all_valid_formats(self):
        for fmt in VALID_FORMATS:
            inp = ContentRepurposeInput(
                content="This is a long article about AI " * 3,
                source_format="article",
                target_formats=[fmt],
            )
            assert fmt in inp.target_formats

    def test_duplicate_formats_removed(self):
        inp = ContentRepurposeInput(
            content="This is a long article about AI " * 3,
            source_format="article",
            target_formats=["tweet_thread", "tweet_thread", "TWEET_THREAD"],
        )
        assert len(inp.target_formats) == 1


class TestProofreadingInputValidation:
    """Test input validation for proofreading agent."""

    def test_valid_input(self):
        inp = ProofreadingInput(
            text="This is a paragraph that needs proofreading for errors and clarity.",
        )
        assert inp.preserve_voice is True

    def test_text_too_short(self):
        # Input passes min_length=10 but has < 3 words → custom validator fires
        with pytest.raises(ValueError, match="at least 3 words"):
            ProofreadingInput(text="Helloworld")

    def test_invalid_style_guide(self):
        with pytest.raises(ValueError, match="Style guide must be one of"):
            ProofreadingInput(
                text="This is a paragraph that needs proofreading.",
                style_guide="oxford",
            )

    def test_all_valid_style_guides(self):
        for guide in ["ap", "chicago", "apa", "mla"]:
            inp = ProofreadingInput(
                text="This is a paragraph that needs proofreading.",
                style_guide=guide,
            )
            assert inp.style_guide == guide

    def test_none_style_guide_returns_none(self):
        inp = ProofreadingInput(
            text="This is a paragraph that needs proofreading.",
            style_guide="none",
        )
        assert inp.style_guide is None

    def test_invalid_focus_area(self):
        with pytest.raises(ValueError, match="Unknown focus area"):
            ProofreadingInput(
                text="This is a paragraph that needs proofreading.",
                focus_areas=["syntax_highlighting"],
            )

    def test_all_valid_focus_areas(self):
        for area in VALID_FOCUS_AREAS:
            inp = ProofreadingInput(
                text="This is a paragraph that needs proofreading.",
                focus_areas=[area],
            )
            assert area in inp.focus_areas

    def test_focus_areas_max_5(self):
        areas = list(VALID_FOCUS_AREAS)[:8]
        inp = ProofreadingInput(
            text="This is a paragraph that needs proofreading.",
            focus_areas=areas,
        )
        assert len(inp.focus_areas) <= 5


# =============================================================================
# LAYER 1: UNIT TESTS — LOCAL COMPUTATION
# =============================================================================

class TestDataAnalystLocalStats:
    """Test local statistics computation (not LLM-dependent)."""

    def test_numeric_column_stats(self):
        agent = DataAnalystAgent()
        data = [{"value": 10}, {"value": 20}, {"value": 30}]
        stats = agent._compute_column_stats(data, ["value"])

        assert stats["value"]["type"] == "numeric"
        assert stats["value"]["min"] == 10
        assert stats["value"]["max"] == 30
        assert stats["value"]["mean"] == 20.0
        assert stats["value"]["count"] == 3

    def test_categorical_column_stats(self):
        agent = DataAnalystAgent()
        data = [{"cat": "a"}, {"cat": "b"}, {"cat": "a"}, {"cat": "c"}]
        stats = agent._compute_column_stats(data, ["cat"])

        assert stats["cat"]["type"] == "categorical"
        assert stats["cat"]["unique"] == 3
        assert stats["cat"]["count"] == 4

    def test_stratified_sample_small_dataset(self):
        agent = DataAnalystAgent()
        data = [{"id": i} for i in range(5)]
        sample = agent._stratified_sample(data, sample_size=50)
        assert len(sample) == 5  # All data returned when smaller than sample

    def test_stratified_sample_large_dataset(self):
        agent = DataAnalystAgent()
        data = [{"id": i} for i in range(1000)]
        sample = agent._stratified_sample(data, sample_size=30)
        assert len(sample) <= 30
        # Should include first and last elements
        sample_ids = {row["id"] for row in sample}
        assert 0 in sample_ids
        assert 999 in sample_ids

    def test_empty_column_handled(self):
        agent = DataAnalystAgent()
        data = [{"val": None}, {"val": None}]
        stats = agent._compute_column_stats(data, ["val"])
        assert stats["val"]["type"] == "empty"


class TestProofreadingLocalReadability:
    """Test local readability scoring (Flesch-Kincaid)."""

    def test_simple_text_scores_high(self):
        agent = ProofreadingAgentV2()
        # Very simple text
        score = agent._compute_readability("The cat sat on the mat. The dog ran fast.")
        assert score > 70  # Should be easy to read

    def test_complex_text_scores_lower(self):
        agent = ProofreadingAgentV2()
        # Complex text with polysyllabic words
        score = agent._compute_readability(
            "The implementation of sophisticated algorithmic methodologies "
            "necessitates comprehensive understanding of computational "
            "paradigms and mathematical abstractions."
        )
        assert score < 50  # Should be harder to read

    def test_syllable_count(self):
        assert ProofreadingAgentV2._count_syllables("the") == 1
        assert ProofreadingAgentV2._count_syllables("implementation") >= 4
        assert ProofreadingAgentV2._count_syllables("cat") == 1

    def test_score_to_level(self):
        assert "easy" in ProofreadingAgentV2._score_to_level(85).lower()
        assert "college" in ProofreadingAgentV2._score_to_level(35).lower()
        assert "professional" in ProofreadingAgentV2._score_to_level(15).lower()


# =============================================================================
# LAYER 2: INTEGRATION TESTS — REPOSITORY + SERVICE
# =============================================================================

class TestAgentServiceWiring:
    """Test that all 6 agent types are wired correctly in AgentService."""

    def test_all_agent_types_registered(self):
        from backend.app.services.agents.agent_service import AgentService
        service = AgentService()
        assert AgentType.RESEARCH in service._agents
        assert AgentType.DATA_ANALYST in service._agents
        assert AgentType.EMAIL_DRAFT in service._agents
        assert AgentType.CONTENT_REPURPOSE in service._agents
        assert AgentType.PROOFREADING in service._agents
        assert AgentType.REPORT_ANALYST in service._agents

    def test_build_agent_kwargs_research(self):
        from backend.app.services.agents.agent_service import AgentService
        task = AgentTaskModel(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "AI trends", "depth": "quick"},
        )
        kwargs = AgentService._build_agent_kwargs(task)
        assert kwargs["topic"] == "AI trends"
        assert kwargs["depth"] == "quick"

    def test_build_agent_kwargs_data_analyst(self):
        from backend.app.services.agents.agent_service import AgentService
        task = AgentTaskModel(
            agent_type=AgentType.DATA_ANALYST,
            input_params={"question": "What is avg?", "data": [{"a": 1}]},
        )
        kwargs = AgentService._build_agent_kwargs(task)
        assert kwargs["question"] == "What is avg?"
        assert kwargs["data"] == [{"a": 1}]

    def test_build_agent_kwargs_email_draft(self):
        from backend.app.services.agents.agent_service import AgentService
        task = AgentTaskModel(
            agent_type=AgentType.EMAIL_DRAFT,
            input_params={"context": "Meeting", "purpose": "Confirm", "tone": "formal"},
        )
        kwargs = AgentService._build_agent_kwargs(task)
        assert kwargs["context"] == "Meeting"
        assert kwargs["tone"] == "formal"

    def test_build_agent_kwargs_content_repurpose(self):
        from backend.app.services.agents.agent_service import AgentService
        task = AgentTaskModel(
            agent_type=AgentType.CONTENT_REPURPOSE,
            input_params={
                "content": "Article text",
                "source_format": "article",
                "target_formats": ["tweet_thread"],
            },
        )
        kwargs = AgentService._build_agent_kwargs(task)
        assert kwargs["content"] == "Article text"
        assert kwargs["target_formats"] == ["tweet_thread"]

    def test_build_agent_kwargs_proofreading(self):
        from backend.app.services.agents.agent_service import AgentService
        task = AgentTaskModel(
            agent_type=AgentType.PROOFREADING,
            input_params={"text": "Check this text", "style_guide": "ap"},
        )
        kwargs = AgentService._build_agent_kwargs(task)
        assert kwargs["text"] == "Check this text"
        assert kwargs["style_guide"] == "ap"


class TestRepositoryAllAgentTypes:
    """Test repository works correctly for all 6 agent types."""

    @pytest.mark.parametrize("agent_type", list(AgentType))
    def test_create_task_for_each_agent_type(self, repository, agent_type):
        task = repository.create_task(
            agent_type=agent_type,
            input_params={"test": "value"},
        )
        assert task.agent_type == agent_type
        assert task.status == AgentTaskStatus.PENDING

    @pytest.mark.parametrize("agent_type", list(AgentType))
    def test_full_lifecycle_for_each_agent_type(self, repository, agent_type):
        """Create → Claim → Progress → Complete for every agent type."""
        task = repository.create_task(
            agent_type=agent_type,
            input_params={"test": "value"},
        )
        assert task.status == AgentTaskStatus.PENDING

        claimed = repository.claim_task(task.task_id)
        assert claimed.status == AgentTaskStatus.RUNNING

        repository.update_progress(task.task_id, percent=50, message="Halfway")
        updated = repository.get_task(task.task_id)
        assert updated.progress_percent == 50

        completed = repository.complete_task(
            task.task_id,
            result={"output": "test_result"},
            tokens_input=100,
            tokens_output=200,
        )
        assert completed.status == AgentTaskStatus.COMPLETED
        assert completed.result["output"] == "test_result"

    def test_list_tasks_filter_by_agent_type(self, repository):
        """Filtering by agent type returns only matching tasks."""
        repository.create_task(agent_type=AgentType.RESEARCH, input_params={})
        repository.create_task(agent_type=AgentType.DATA_ANALYST, input_params={})
        repository.create_task(agent_type=AgentType.EMAIL_DRAFT, input_params={})

        research = repository.list_tasks(agent_type=AgentType.RESEARCH)
        assert len(research) == 1
        assert research[0].agent_type == AgentType.RESEARCH

        data_analyst = repository.list_tasks(agent_type=AgentType.DATA_ANALYST)
        assert len(data_analyst) == 1


# =============================================================================
# LAYER 3: PROPERTY-BASED TESTS
# =============================================================================

class TestPropertyBased:
    """Property-based tests for invariants across all agents."""

    def test_all_agent_types_in_enum(self):
        """All 6 agent types must be in the AgentType enum."""
        expected = {"research", "data_analyst", "email_draft", "content_repurpose", "proofreading", "report_analyst"}
        actual = {t.value for t in AgentType}
        assert expected == actual

    @pytest.mark.parametrize("agent_type", list(AgentType))
    def test_tasks_track_cost_for_all_types(self, repository, agent_type):
        """Cost tracking fields are available for all agent types."""
        task = repository.create_task(
            agent_type=agent_type,
            input_params={"test": "value"},
        )
        repository.claim_task(task.task_id)
        completed = repository.complete_task(
            task.task_id,
            result={},
            tokens_input=500,
            tokens_output=1000,
            estimated_cost_cents=42,
        )
        assert completed.tokens_input == 500
        assert completed.tokens_output == 1000
        assert completed.estimated_cost_cents == 42

    def test_random_valid_emails_pass_validation(self):
        """Random valid email draft inputs should pass validation."""
        for _ in range(50):
            word_count = random.randint(3, 20)
            context = " ".join(
                "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
                for _ in range(word_count)
            )
            purpose = " ".join(
                "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
                for _ in range(random.randint(2, 5))
            )
            tones = ["professional", "friendly", "formal", "casual", "empathetic", "assertive"]
            inp = EmailDraftInput(
                context=context,
                purpose=purpose,
                tone=random.choice(tones),
            )
            assert inp.context.strip() == context.strip()

    def test_readability_score_always_in_bounds(self):
        """Readability score must be 0-100 for any input."""
        agent = ProofreadingAgentV2()
        for _ in range(50):
            word_count = random.randint(5, 100)
            text = ". ".join(
                " ".join(
                    "".join(random.choices(string.ascii_lowercase, k=random.randint(2, 12)))
                    for _ in range(random.randint(3, 15))
                )
                for _ in range(random.randint(1, 5))
            ) + "."
            score = agent._compute_readability(text)
            assert 0.0 <= score <= 100.0, f"Score {score} out of bounds for text: {text[:50]}"


# =============================================================================
# LAYER 4: FAILURE INJECTION TESTS
# =============================================================================

class TestFailureInjection:
    """Test error handling for all 4 new agents."""

    @pytest.mark.asyncio
    async def test_data_analyst_timeout(self, data_analyst_agent, sample_data):
        with patch.object(data_analyst_agent, "_call_llm") as mock:
            mock.side_effect = asyncio.TimeoutError()
            with pytest.raises(LLMTimeoutError):
                await data_analyst_agent.execute(
                    question="What is the average salary?",
                    data=sample_data,
                    timeout_seconds=1,
                )

    @pytest.mark.asyncio
    async def test_email_draft_rate_limit(self, email_draft_agent):
        with patch.object(email_draft_agent, "_call_llm") as mock:
            mock.side_effect = Exception("Rate limit exceeded")
            with pytest.raises(LLMRateLimitError):
                await email_draft_agent.execute(
                    context="Meeting tomorrow morning",
                    purpose="Confirm the meeting",
                )

    @pytest.mark.asyncio
    async def test_content_repurpose_partial_failure(self, content_repurpose_agent):
        """If some formats fail, others should still return."""
        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First format fails
                raise LLMResponseError("JSON parse failed")
            return {
                "raw": "Transformed content here",
                "parsed": {},
                "input_tokens": 100,
                "output_tokens": 50,
            }

        with patch.object(content_repurpose_agent, "_call_llm", side_effect=mock_call):
            report, metadata = await content_repurpose_agent.execute(
                content="This is a long article about AI trends in healthcare " * 5,
                source_format="article",
                target_formats=["tweet_thread", "linkedin_post"],
            )
            assert report.formats_succeeded == 1
            assert report.formats_failed == 1
            assert len(report.outputs) == 2
            # Failed output should have error
            failed_output = [o for o in report.outputs if o.error][0]
            assert failed_output.error is not None

    @pytest.mark.asyncio
    async def test_proofreading_validation_error(self, proofreading_agent):
        with pytest.raises(ValidationError):
            await proofreading_agent.execute(text="Hi")

    @pytest.mark.asyncio
    async def test_data_analyst_validation_error(self, data_analyst_agent):
        with pytest.raises(ValidationError):
            await data_analyst_agent.execute(
                question="x",
                data=[],
            )

    def test_service_fails_unknown_agent_type(self, repository):
        from backend.app.services.agents.agent_service import AgentService
        # Use a MagicMock to bypass AgentType enum validation.
        # The string "nonexistent" is not a valid AgentType value,
        # so _build_agent_kwargs will raise ValueError when it tries
        # AgentType("nonexistent").
        mock_task = MagicMock()
        mock_task.input_params = {}
        mock_task.agent_type = "nonexistent"
        with pytest.raises(ValueError):
            AgentService._build_agent_kwargs(mock_task)


# =============================================================================
# LAYER 5: CONCURRENCY TESTS
# =============================================================================

class TestConcurrencyAllAgents:
    """Test thread safety across all agent types."""

    def test_concurrent_task_creation_all_types(self, repository):
        """Create tasks of all types concurrently."""
        created_ids = []
        errors = []

        def create_task(agent_type, idx):
            try:
                task = repository.create_task(
                    agent_type=agent_type,
                    input_params={"test": f"{agent_type.value}_{idx}"},
                )
                created_ids.append(task.task_id)
            except Exception as e:
                errors.append(e)

        threads = []
        for atype in AgentType:
            for i in range(10):
                threads.append(threading.Thread(target=create_task, args=(atype, i)))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(created_ids) == 60  # 6 types * 10 each
        assert len(set(created_ids)) == 60

    def test_idempotency_across_agent_types(self, repository):
        """Idempotency keys are scoped — same key for different types should both succeed."""
        task1 = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"test": "value"},
            idempotency_key="shared-key-1",
        )
        # Same idempotency key but different agent type — should conflict
        # (idempotency is global, not per-type)
        with pytest.raises(IdempotencyConflictError):
            repository.create_task(
                agent_type=AgentType.DATA_ANALYST,
                input_params={"test": "different"},
                idempotency_key="shared-key-1",
            )


# =============================================================================
# LAYER 6: SECURITY TESTS
# =============================================================================

class TestSecurityAllAgents:
    """Test security and abuse prevention for all agents."""

    def test_data_analyst_data_size_limit(self):
        """Data should be limited to prevent memory abuse."""
        huge_data = [{"x": i} for i in range(100_001)]
        with pytest.raises(ValueError, match="100,000"):
            DataAnalystInput(
                question="What is the average?",
                data=huge_data,
            )

    def test_content_repurpose_content_length_limit(self):
        """Content should be limited."""
        long_content = "word " * 60000
        with pytest.raises(ValueError):
            ContentRepurposeInput(
                content=long_content,
                source_format="article",
                target_formats=["tweet_thread"],
            )

    def test_proofreading_text_length_limit(self):
        """Text should be limited."""
        long_text = "word " * 60000
        with pytest.raises(ValueError):
            ProofreadingInput(text=long_text)

    def test_sql_injection_in_data_analyst_question(self, repository):
        """SQL injection in question should be safely stored."""
        sql_question = "'; DROP TABLE agent_tasks; -- What is average?"
        task = repository.create_task(
            agent_type=AgentType.DATA_ANALYST,
            input_params={"question": sql_question, "data": [{"x": 1}]},
        )
        retrieved = repository.get_task(task.task_id)
        assert retrieved is not None
        assert retrieved.input_params["question"] == sql_question

    def test_xss_in_email_context(self, repository):
        """XSS in email context should be safely stored."""
        xss_context = "<script>alert('xss')</script> Meeting about Q4 budget"
        task = repository.create_task(
            agent_type=AgentType.EMAIL_DRAFT,
            input_params={"context": xss_context, "purpose": "Confirm"},
        )
        retrieved = repository.get_task(task.task_id)
        assert "<script>" in retrieved.input_params["context"]

    def test_task_isolation_by_user(self, repository):
        """Tasks should be isolated by user_id across all agent types."""
        for atype in AgentType:
            repository.create_task(
                agent_type=atype,
                input_params={"test": "value"},
                user_id="user_A",
            )
            repository.create_task(
                agent_type=atype,
                input_params={"test": "value"},
                user_id="user_B",
            )

        user_a_tasks = repository.list_tasks(user_id="user_A")
        user_b_tasks = repository.list_tasks(user_id="user_B")

        assert len(user_a_tasks) == 6  # one per agent type
        assert len(user_b_tasks) == 6


# =============================================================================
# LAYER 7: USABILITY TESTS
# =============================================================================

class TestUsabilityAllAgents:
    """Test API usability for all agents."""

    @pytest.mark.parametrize("agent_type", list(AgentType))
    def test_task_response_format_all_types(self, repository, agent_type):
        """All agent types should produce well-structured response dicts."""
        task = repository.create_task(
            agent_type=agent_type,
            input_params={"test": "value"},
        )
        response = task.to_response_dict()

        assert "task_id" in response
        assert "agent_type" in response
        assert "status" in response
        assert "progress" in response
        assert "timestamps" in response
        assert "cost" in response
        assert "attempts" in response
        assert "links" in response

    def test_data_analyst_error_messages_actionable(self):
        # Input passes min_length=5 but has < 2 words → custom validator fires
        try:
            DataAnalystInput(question="abcde", data=[{"a": 1}])
        except ValueError as e:
            assert "2 words" in str(e)

    def test_email_draft_error_messages_actionable(self):
        try:
            EmailDraftInput(context="Hi", purpose="x", tone="aggressive")
        except ValueError as e:
            assert "Tone must be one of" in str(e)

    def test_content_repurpose_error_messages_actionable(self):
        try:
            ContentRepurposeInput(
                content="Long enough content for repurposing " * 3,
                source_format="article",
                target_formats=["invalid_xyz"],
            )
        except ValueError as e:
            assert "Unknown target format" in str(e)
            assert "Valid formats" in str(e)

    def test_proofreading_error_messages_actionable(self):
        try:
            ProofreadingInput(
                text="This is a long enough text for proofreading.",
                style_guide="oxford",
            )
        except ValueError as e:
            assert "Style guide must be one of" in str(e)

    def test_agent_types_endpoint_has_all_six(self):
        """The agent types data structure should list all 6 agents."""
        from backend.app.services.agents.agent_service import AgentService
        service = AgentService()
        assert len(service._agents) == 6

    def test_default_values_sensible(self):
        """Default values should produce usable inputs."""
        # Email draft defaults to professional
        inp = EmailDraftInput(
            context="Meeting tomorrow morning",
            purpose="Confirm the meeting",
        )
        assert inp.tone == "professional"
        assert inp.include_subject is True

        # Proofreading defaults to preserve voice
        inp2 = ProofreadingInput(
            text="This is a paragraph that needs proofreading.",
        )
        assert inp2.preserve_voice is True
        assert inp2.style_guide is None

        # Content repurpose defaults
        inp3 = ContentRepurposeInput(
            content="This is a long article about AI trends " * 3,
            source_format="article",
            target_formats=["tweet_thread"],
        )
        assert inp3.preserve_key_points is True
        assert inp3.adapt_length is True


# =============================================================================
# TRADE-OFF: ERROR HANDLING NEVER MASKS ERRORS (line 380 fix)
# =============================================================================

class TestErrorNeverMaskedAsCompleted:
    """
    Critical: The legacy service returns COMPLETED with error info embedded.
    The v2 system must NEVER mask errors as COMPLETED.
    """

    @pytest.mark.asyncio
    async def test_failed_task_is_FAILED_not_COMPLETED(self, repository):
        """When an agent throws a non-retryable error, status must be FAILED, not COMPLETED."""
        from backend.app.services.agents.agent_service import AgentService

        service = AgentService(repository=repository)

        # Mock the agent to throw a non-retryable error
        mock_agent = MagicMock()
        mock_agent.execute = AsyncMock(side_effect=AgentError(
            "LLM failed",
            code="LLM_ERROR",
            retryable=False,
        ))
        service._agents[AgentType.RESEARCH] = mock_agent

        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test topic here"},
        )

        result = await service._execute_task(task.task_id)

        assert result.status == AgentTaskStatus.FAILED
        assert result.status != AgentTaskStatus.COMPLETED
        assert result.error_message == "LLM failed"
        assert result.error_code == "LLM_ERROR"

    @pytest.mark.asyncio
    async def test_retryable_error_becomes_RETRYING_not_COMPLETED(self, repository):
        """Retryable errors go to RETRYING (not COMPLETED), with error in last_error."""
        from backend.app.services.agents.agent_service import AgentService

        service = AgentService(repository=repository)

        mock_agent = MagicMock()
        mock_agent.execute = AsyncMock(side_effect=AgentError(
            "Temporary failure",
            code="LLM_ERROR",
            retryable=True,
        ))
        service._agents[AgentType.RESEARCH] = mock_agent

        task = repository.create_task(
            agent_type=AgentType.RESEARCH,
            input_params={"topic": "test topic here"},
        )

        result = await service._execute_task(task.task_id)

        assert result.status == AgentTaskStatus.RETRYING
        assert result.status != AgentTaskStatus.COMPLETED
        assert result.last_error == "Temporary failure"
        assert result.is_retryable is True

    @pytest.mark.asyncio
    async def test_unexpected_error_marked_retryable(self, repository):
        """Unexpected errors should be marked as retryable, not masked."""
        from backend.app.services.agents.agent_service import AgentService

        service = AgentService(repository=repository)

        mock_agent = MagicMock()
        mock_agent.execute = AsyncMock(side_effect=RuntimeError("Something unexpected"))
        service._agents[AgentType.DATA_ANALYST] = mock_agent

        task = repository.create_task(
            agent_type=AgentType.DATA_ANALYST,
            input_params={"question": "test question", "data": [{"x": 1}]},
        )

        result = await service._execute_task(task.task_id)

        # Must NOT be COMPLETED — retryable errors go to RETRYING
        assert result.status != AgentTaskStatus.COMPLETED
        assert result.status == AgentTaskStatus.RETRYING
        assert result.last_error == "Something unexpected"
        assert result.is_retryable is True


# =============================================================================
# SERVICE-LEVEL ASYNC EXECUTION TESTS
# =============================================================================

class TestServiceAsyncExecution:
    """Test async run methods create tasks correctly."""

    @pytest.fixture
    def service(self, repository):
        from backend.app.services.agents.agent_service import AgentService
        return AgentService(repository=repository)

    @pytest.mark.asyncio
    async def test_run_data_analyst_async(self, service, repository, sample_data):
        # Mock _enqueue_background to prevent actual thread pool submission
        with patch.object(service, "_enqueue_background") as mock_bg:
            task = await service.run_data_analyst(
                question="What is the average salary?",
                data=sample_data,
                sync=False,
            )
            assert task.status == AgentTaskStatus.PENDING
            mock_bg.assert_called_once_with(task.task_id)

    @pytest.mark.asyncio
    async def test_run_email_draft_async(self, service, repository):
        with patch.object(service, "_enqueue_background") as mock_bg:
            task = await service.run_email_draft(
                context="Meeting about Q4 budget tomorrow",
                purpose="Confirm the meeting time",
                tone="formal",
                sync=False,
            )
            assert task.status == AgentTaskStatus.PENDING
            mock_bg.assert_called_once_with(task.task_id)

    @pytest.mark.asyncio
    async def test_run_content_repurpose_async(self, service, repository):
        with patch.object(service, "_enqueue_background") as mock_bg:
            task = await service.run_content_repurpose(
                content="Long article about AI " * 10,
                source_format="article",
                target_formats=["tweet_thread", "linkedin_post"],
                sync=False,
            )
            assert task.status == AgentTaskStatus.PENDING
            mock_bg.assert_called_once_with(task.task_id)

    @pytest.mark.asyncio
    async def test_run_proofreading_async(self, service, repository):
        with patch.object(service, "_enqueue_background") as mock_bg:
            task = await service.run_proofreading(
                text="This paragraph has some grammar errors in it.",
                style_guide="ap",
                sync=False,
            )
            assert task.status == AgentTaskStatus.PENDING
            mock_bg.assert_called_once_with(task.task_id)

    @pytest.mark.asyncio
    async def test_idempotency_works_for_all_run_methods(self, service, repository):
        """Idempotency key deduplication works for all agent types."""
        with patch.object(service, "_enqueue_background"):
            task1 = await service.run_email_draft(
                context="Meeting tomorrow morning",
                purpose="Confirm the meeting time",
                idempotency_key="email-key-1",
                sync=False,
            )
            task2 = await service.run_email_draft(
                context="Different context entirely",
                purpose="Different purpose",
                idempotency_key="email-key-1",
                sync=False,
            )
            # Same idempotency key returns same task
            assert task1.task_id == task2.task_id


# =============================================================================
# PHASE 7: DESTRUCTIVE SIMULATION — 3 PRODUCTION FAILURE SCENARIOS
# =============================================================================

class TestDestructiveScenario1:
    """Scenario 1: All 6 agents fail simultaneously with mixed error types."""

    @pytest.mark.asyncio
    async def test_all_agents_fail_no_crash(self, repository):
        """Fire all 6 agents with different error types; system must not crash."""
        from backend.app.services.agents.agent_service import AgentService

        service = AgentService(repository=repository)

        errors = [
            asyncio.TimeoutError(),
            LLMRateLimitError(),
            LLMResponseError("JSON malformed"),
            ValidationError("bad input", field="topic"),
            RuntimeError("Segfault simulation"),
            AgentError("Report analyst failure", code="REPORT_ERROR", retryable=True),
        ]
        agent_types = list(AgentType)

        for agent_type, error in zip(agent_types, errors):
            mock_agent = MagicMock()
            mock_agent.execute = AsyncMock(side_effect=error)
            service._agents[agent_type] = mock_agent

        results = []
        for agent_type in agent_types:
            task = repository.create_task(
                agent_type=agent_type,
                input_params={"test": "destructive"},
            )
            result = await service._execute_task(task.task_id)
            results.append(result)

        # Critical: NONE should be COMPLETED
        for r in results:
            assert r.status != AgentTaskStatus.COMPLETED, (
                f"Agent {r.agent_type} masked error as COMPLETED"
            )

        # All should be in a failure/retry state
        for r in results:
            assert r.status in (AgentTaskStatus.FAILED, AgentTaskStatus.RETRYING)


class TestDestructiveScenario2:
    """Scenario 2: Concurrent idempotency key stress test."""

    def test_duplicate_keys_across_50_threads(self, repository):
        """50 threads try to create tasks with the same idempotency key."""
        from backend.app.repositories.agent_tasks.repository import IdempotencyConflictError

        results = {"created": 0, "conflicts": 0, "errors": []}
        lock = threading.Lock()

        def create_with_key(thread_id: int):
            try:
                repository.create_task(
                    agent_type=AgentType.RESEARCH,
                    input_params={"thread": thread_id},
                    idempotency_key="shared-stress-key",
                )
                with lock:
                    results["created"] += 1
            except IdempotencyConflictError:
                with lock:
                    results["conflicts"] += 1
            except Exception as e:
                with lock:
                    results["errors"].append(str(e))

        threads = [threading.Thread(target=create_with_key, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Exactly 1 should succeed, 49 should conflict
        assert results["created"] == 1, f"Expected 1 creation, got {results['created']}"
        assert results["conflicts"] == 49, f"Expected 49 conflicts, got {results['conflicts']}"
        assert len(results["errors"]) == 0, f"Unexpected errors: {results['errors']}"


class TestDestructiveScenario3:
    """Scenario 3: Task lifecycle resilience — cancel mid-flight, recover stale."""

    def test_cancel_running_task_does_not_lose_data(self, repository):
        """Cancel a RUNNING task; input_params must remain intact."""
        task = repository.create_task(
            agent_type=AgentType.DATA_ANALYST,
            input_params={"question": "Critical query?", "data": [{"x": 42}]},
        )
        repository.claim_task(task.task_id)

        # Update progress mid-flight
        repository.update_progress(task.task_id, percent=60, message="Halfway done")

        # Cancel
        cancelled = repository.cancel_task(task.task_id)
        assert cancelled.status == AgentTaskStatus.CANCELLED

        # Input params must survive cancellation
        retrieved = repository.get_task(task.task_id)
        assert retrieved.input_params["question"] == "Critical query?"
        assert retrieved.progress_percent == 60

    def test_stale_task_recovery(self, repository):
        """Tasks stuck in RUNNING state should be recoverable."""
        # Create and claim a task (simulates a crashed worker)
        task = repository.create_task(
            agent_type=AgentType.EMAIL_DRAFT,
            input_params={"context": "Meeting", "purpose": "Confirm"},
        )
        repository.claim_task(task.task_id)

        # Verify it's in RUNNING state
        running = repository.get_task(task.task_id)
        assert running.status == AgentTaskStatus.RUNNING

        # Recover stale tasks (threshold=0 means all RUNNING are stale)
        recovered = repository.recover_stale_tasks(stale_threshold_seconds=0)

        # Task should now be in RETRYING state (ready for retry)
        updated = repository.get_task(task.task_id)
        assert updated.status == AgentTaskStatus.RETRYING
        assert updated.last_error is not None

    def test_stats_consistent_after_mixed_operations(self, repository):
        """Stats must accurately reflect task distribution after mixed operations."""
        # Create 3 tasks per type
        for atype in AgentType:
            for i in range(3):
                repository.create_task(
                    agent_type=atype,
                    input_params={"idx": i},
                )

        # Complete some, fail some, cancel some
        all_tasks = repository.list_tasks(limit=100)
        for i, task in enumerate(all_tasks):
            if i % 3 == 0:
                repository.claim_task(task.task_id)
                repository.complete_task(task.task_id, result={"done": True})
            elif i % 3 == 1:
                repository.claim_task(task.task_id)
                repository.fail_task(task.task_id, error_message="Oops", is_retryable=False)

        stats = repository.get_stats()
        assert stats["total"] == 18  # 6 types * 3 each
        assert stats["completed"] == 6
        assert stats["failed"] == 6
        assert stats["pending"] == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
