"""
AI Agents Service Tests
Comprehensive tests for all 5 specialized AI agents.
"""
import json
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

import os

from backend.app.services.agents.service import (
    AgentService,
    AgentType,
    AgentStatus,
    AgentTask,
    ResearchAgent,
    DataAnalystAgent,
    EmailDraftAgent,
    ContentRepurposingAgent,
    ProofreadingAgent,
    ResearchReport,
    DataAnalysisResult,
    EmailDraft,
    RepurposedContent,
    ProofreadingResult,
    BaseAgent,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def agent_service():
    """Create fresh AgentService instance."""
    return AgentService()


@pytest.fixture
def research_agent():
    """Create ResearchAgent instance."""
    return ResearchAgent()


@pytest.fixture
def data_analyst_agent():
    """Create DataAnalystAgent instance."""
    return DataAnalystAgent()


@pytest.fixture
def email_draft_agent():
    """Create EmailDraftAgent instance."""
    return EmailDraftAgent()


@pytest.fixture
def content_repurpose_agent():
    """Create ContentRepurposingAgent instance."""
    return ContentRepurposingAgent()


@pytest.fixture
def proofreading_agent():
    """Create ProofreadingAgent instance."""
    return ProofreadingAgent()


# =============================================================================
# AGENT TYPE AND STATUS ENUM TESTS
# =============================================================================


class TestAgentEnums:
    """Tests for agent-related enums."""

    def test_agent_types_exist(self):
        """All expected agent types are defined."""
        expected = ["research", "data_analyst", "email_draft", "content_repurpose", "proofreading"]
        actual = [t.value for t in AgentType]
        assert sorted(actual) == sorted(expected)

    def test_agent_status_values(self):
        """All status values are defined."""
        expected = ["idle", "running", "completed", "failed"]
        actual = [s.value for s in AgentStatus]
        assert sorted(actual) == sorted(expected)

    def test_agent_type_is_string_enum(self):
        """AgentType is a string enum."""
        assert AgentType.RESEARCH == "research"
        assert isinstance(AgentType.RESEARCH, str)


# =============================================================================
# BASE AGENT TESTS
# =============================================================================


class TestBaseAgent:
    """Tests for BaseAgent functionality."""

    def test_client_lazy_loaded(self, research_agent):
        """Client is not initialized immediately."""
        assert research_agent._client is None

    def test_get_client_creates_client(self, research_agent):
        """_get_client creates LLM client."""
        with patch('backend.app.services.llm.client.get_llm_client') as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            client = research_agent._get_client()
            assert client is not None
            mock_get_client.assert_called_once()

    def test_get_client_reuses_client(self, research_agent):
        """_get_client reuses existing client."""
        mock_client = Mock()
        research_agent._client = mock_client
        client = research_agent._get_client()
        assert client is mock_client

    def test_safe_parse_json_valid_json(self, research_agent):
        """_safe_parse_json handles valid JSON."""
        result = research_agent._safe_parse_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_safe_parse_json_markdown_block(self, research_agent):
        """_safe_parse_json handles markdown code blocks."""
        content = '```json\n{"key": "value"}\n```'
        result = research_agent._safe_parse_json(content)
        assert result == {"key": "value"}

    def test_safe_parse_json_invalid_returns_default(self, research_agent):
        """_safe_parse_json returns default on invalid JSON."""
        result = research_agent._safe_parse_json("not json", default={"error": True})
        assert result == {"error": True}

    def test_safe_parse_json_empty_returns_default(self, research_agent):
        """_safe_parse_json returns default on empty input."""
        result = research_agent._safe_parse_json("", default={"empty": True})
        assert result == {"empty": True}

    def test_safe_parse_json_extracts_from_text(self, research_agent):
        """_safe_parse_json extracts JSON from surrounding text."""
        content = 'Here is the result: {"key": "value"} and more text.'
        result = research_agent._safe_parse_json(content)
        assert result == {"key": "value"}


# =============================================================================
# RESEARCH AGENT TESTS
# =============================================================================


class TestResearchAgent:
    """Tests for ResearchAgent."""

    @pytest.mark.asyncio
    async def test_research_success(self, research_agent):
        """Successful research execution."""
        with patch.object(research_agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "summary": "Executive summary of the research",
                "sections": [
                    {"title": "Introduction", "content": "Overview of the topic"},
                    {"title": "Analysis", "content": "Detailed analysis"},
                ],
                "key_findings": ["Finding 1", "Finding 2"],
                "recommendations": ["Recommendation 1"],
                "sources": [{"title": "Source 1", "url": "https://example.com"}],
            })

            result = await research_agent.execute(
                topic="AI in Healthcare",
                depth="comprehensive",
                focus_areas=["Diagnostics", "Treatment"],
                max_sections=5,
            )

            assert isinstance(result, ResearchReport)
            assert result.topic == "AI in Healthcare"
            assert len(result.sections) == 2
            assert len(result.key_findings) == 2

    @pytest.mark.asyncio
    async def test_research_with_different_depths(self, research_agent):
        """Research with different depth levels."""
        # Map depth levels to expected prompt text
        depth_text_map = {
            "quick": "brief overview",
            "moderate": "balanced report",
            "comprehensive": "in-depth analysis",
        }

        for depth, expected_text in depth_text_map.items():
            with patch.object(research_agent, '_call_llm') as mock_call:
                mock_call.return_value = json.dumps({
                    "summary": f"Summary for {depth} research",
                    "sections": [],
                    "key_findings": [],
                    "recommendations": [],
                    "sources": [],
                })

                result = await research_agent.execute(topic="Test", depth=depth)
                # Service uses kwargs, not positional args
                system_prompt = mock_call.call_args.kwargs.get("system_prompt", "")
                assert expected_text in system_prompt.lower()

    @pytest.mark.asyncio
    async def test_research_json_error_fallback(self, research_agent):
        """Research handles JSON parse error."""
        with patch.object(research_agent, '_call_llm') as mock_call:
            mock_call.return_value = "Invalid JSON response"

            result = await research_agent.execute(topic="Test Topic")

            assert result.topic == "Test Topic"
            assert "Unable to parse" in result.summary

    @pytest.mark.asyncio
    async def test_research_api_error(self, research_agent):
        """Research handles API error gracefully."""
        with patch.object(research_agent, '_call_llm') as mock_call:
            mock_call.side_effect = Exception("API Error")

            result = await research_agent.execute(topic="Test")

            assert "Research failed" in result.summary


# =============================================================================
# DATA ANALYST AGENT TESTS
# =============================================================================


class TestDataAnalystAgent:
    """Tests for DataAnalystAgent."""

    @pytest.mark.asyncio
    async def test_analysis_success(self, data_analyst_agent):
        """Successful data analysis execution."""
        with patch.object(data_analyst_agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "answer": "The average sales is $5000",
                "data_summary": {"total_rows": 100, "avg_sales": 5000},
                "insights": ["Sales trending upward", "Q4 is strongest"],
                "charts": [{"type": "bar", "title": "Sales by Quarter", "x_column": "quarter", "y_columns": ["sales"]}],
                "sql_queries": ["SELECT AVG(sales) FROM data"],
                "confidence": 0.85,
            })

            result = await data_analyst_agent.execute(
                question="What is the average sales?",
                data=[{"quarter": "Q1", "sales": 4000}, {"quarter": "Q2", "sales": 6000}],
                data_description="Quarterly sales data",
                generate_charts=True,
            )

            assert isinstance(result, DataAnalysisResult)
            assert "5000" in result.answer
            assert len(result.insights) == 2
            assert len(result.charts) == 1

    @pytest.mark.asyncio
    async def test_analysis_without_charts(self, data_analyst_agent):
        """Analysis without chart generation."""
        with patch.object(data_analyst_agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "answer": "The total is 100",
                "data_summary": {},
                "insights": [],
                "charts": [{"type": "line"}],  # Should be filtered out
                "sql_queries": [],
                "confidence": 0.9,
            })

            result = await data_analyst_agent.execute(
                question="What is total?",
                data=[{"value": 100}],
                generate_charts=False,
            )

            assert result.charts == []  # Charts filtered

    @pytest.mark.asyncio
    async def test_analysis_empty_data(self, data_analyst_agent):
        """Analysis with empty data."""
        with patch.object(data_analyst_agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "answer": "No data provided",
                "data_summary": {},
                "insights": [],
                "charts": [],
                "sql_queries": [],
                "confidence": 0.1,
            })

            result = await data_analyst_agent.execute(
                question="What is the total?",
                data=[],
            )

            assert isinstance(result, DataAnalysisResult)

    def test_compute_column_stats_numeric(self, data_analyst_agent):
        """Column stats computation for numeric data."""
        data = [
            {"value": 10},
            {"value": 20},
            {"value": 30},
        ]
        stats = data_analyst_agent._compute_column_stats(data, ["value"])

        assert stats["value"]["type"] == "numeric"
        assert stats["value"]["min"] == 10
        assert stats["value"]["max"] == 30
        assert stats["value"]["mean"] == 20

    def test_compute_column_stats_categorical(self, data_analyst_agent):
        """Column stats computation for categorical data."""
        data = [
            {"category": "A"},
            {"category": "B"},
            {"category": "A"},
        ]
        stats = data_analyst_agent._compute_column_stats(data, ["category"])

        assert stats["category"]["type"] == "categorical"
        assert stats["category"]["unique"] == 2

    def test_stratified_sample_small_data(self, data_analyst_agent):
        """Stratified sample returns all data for small datasets."""
        data = [{"id": i} for i in range(10)]
        sample = data_analyst_agent._stratified_sample(data, sample_size=50)
        assert len(sample) == 10

    def test_stratified_sample_large_data(self, data_analyst_agent):
        """Stratified sample limits data for large datasets."""
        data = [{"id": i} for i in range(200)]
        sample = data_analyst_agent._stratified_sample(data, sample_size=50)
        assert len(sample) <= 50


# =============================================================================
# EMAIL DRAFT AGENT TESTS
# =============================================================================


class TestEmailDraftAgent:
    """Tests for EmailDraftAgent."""

    @pytest.mark.asyncio
    async def test_email_draft_success(self, email_draft_agent):
        """Successful email draft execution."""
        with patch.object(email_draft_agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "subject": "Follow-up on our meeting",
                "body": "Dear John,\n\nThank you for meeting with me...",
                "tone": "professional",
                "suggested_recipients": ["john@example.com"],
                "attachments_suggested": ["meeting_notes.pdf"],
                "follow_up_actions": ["Schedule next meeting"],
            })

            result = await email_draft_agent.execute(
                context="Had a meeting with John about the project",
                purpose="Follow up on action items",
                tone="professional",
                recipient_info="John Smith, Project Manager",
            )

            assert isinstance(result, EmailDraft)
            assert "Follow-up" in result.subject
            assert result.tone == "professional"

    @pytest.mark.asyncio
    async def test_email_draft_with_previous_emails(self, email_draft_agent):
        """Email draft with previous email context."""
        with patch.object(email_draft_agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "subject": "Re: Project Update",
                "body": "Thanks for the update...",
                "tone": "friendly",
                "suggested_recipients": [],
                "attachments_suggested": [],
                "follow_up_actions": [],
            })

            previous_emails = [
                "From: John\nSubject: Project Update\nThe project is on track...",
                "From: Me\nSubject: Re: Project Update\nThanks for letting me know...",
            ]

            result = await email_draft_agent.execute(
                context="Project discussion",
                purpose="Reply to update",
                tone="friendly",
                previous_emails=previous_emails,
            )

            # Service uses kwargs, not positional args
            system_prompt = mock_call.call_args.kwargs.get("system_prompt", "")
            user_prompt = mock_call.call_args.kwargs.get("user_prompt", "")
            # Previous emails context may be in either prompt
            assert "Previous emails" in system_prompt or "previous" in (system_prompt + user_prompt).lower()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tone", ["professional", "friendly", "formal", "casual"])
    async def test_email_draft_different_tones(self, email_draft_agent, tone):
        """Email draft with different tones."""
        with patch.object(email_draft_agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "subject": "Test",
                "body": "Test body",
                "tone": tone,
                "suggested_recipients": [],
                "attachments_suggested": [],
                "follow_up_actions": [],
            })

            result = await email_draft_agent.execute(
                context="Test",
                purpose="Test",
                tone=tone,
            )

            assert result.tone == tone


# =============================================================================
# CONTENT REPURPOSING AGENT TESTS
# =============================================================================


class TestContentRepurposingAgent:
    """Tests for ContentRepurposingAgent."""

    @pytest.mark.asyncio
    async def test_repurpose_single_format(self, content_repurpose_agent):
        """Repurpose content to single format."""
        with patch.object(content_repurpose_agent, '_call_llm') as mock_call:
            mock_call.return_value = "Tweet 1/5: Key point about the article...\n\nTweet 2/5: ..."

            result = await content_repurpose_agent.execute(
                content="This is a long article about technology...",
                source_format="article",
                target_formats=["tweet_thread"],
            )

            assert isinstance(result, RepurposedContent)
            assert len(result.outputs) == 1
            assert result.outputs[0]["format"] == "tweet_thread"

    @pytest.mark.asyncio
    async def test_repurpose_multiple_formats(self, content_repurpose_agent):
        """Repurpose content to multiple formats."""
        with patch.object(content_repurpose_agent, '_call_llm') as mock_call:
            mock_call.return_value = "Transformed content"

            result = await content_repurpose_agent.execute(
                content="Original content",
                source_format="report",
                target_formats=["tweet_thread", "linkedin_post", "blog_summary"],
            )

            assert len(result.outputs) == 3
            formats = [o["format"] for o in result.outputs]
            assert "tweet_thread" in formats
            assert "linkedin_post" in formats
            assert "blog_summary" in formats

    @pytest.mark.asyncio
    async def test_repurpose_all_formats(self, content_repurpose_agent):
        """Repurpose content to all supported formats."""
        all_formats = [
            "tweet_thread", "linkedin_post", "blog_summary", "slides",
            "email_newsletter", "video_script", "infographic",
            "podcast_notes", "press_release", "executive_summary",
        ]

        with patch.object(content_repurpose_agent, '_call_llm') as mock_call:
            mock_call.return_value = "Transformed content"

            result = await content_repurpose_agent.execute(
                content="Test content",
                source_format="article",
                target_formats=all_formats,
            )

            assert len(result.outputs) == len(all_formats)

    @pytest.mark.asyncio
    async def test_repurpose_partial_failure(self, content_repurpose_agent):
        """Repurpose handles partial failures."""
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise Exception("API Error")
            return "Transformed content"

        with patch.object(content_repurpose_agent, '_call_llm', side_effect=side_effect):
            result = await content_repurpose_agent.execute(
                content="Test",
                source_format="article",
                target_formats=["tweet_thread", "linkedin_post", "blog_summary"],
            )

            # Should have 3 outputs, one with error
            assert len(result.outputs) == 3
            error_outputs = [o for o in result.outputs if o.get("metadata", {}).get("error")]
            assert len(error_outputs) == 1


# =============================================================================
# PROOFREADING AGENT TESTS
# =============================================================================


class TestProofreadingAgent:
    """Tests for ProofreadingAgent."""

    @pytest.mark.asyncio
    async def test_proofread_success(self, proofreading_agent):
        """Successful proofreading execution."""
        with patch.object(proofreading_agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "corrected_text": "This is the corrected text.",
                "issues_found": [
                    {"type": "spelling", "original": "teh", "correction": "the", "explanation": "Typo"},
                ],
                "style_suggestions": ["Consider using active voice"],
                "readability_score": 85,
                "reading_level": "8th grade",
            })

            result = await proofreading_agent.execute(
                text="This is teh original text.",
                style_guide="AP",
                preserve_voice=True,
            )

            assert isinstance(result, ProofreadingResult)
            assert "corrected" in result.corrected_text
            assert len(result.issues_found) == 1
            assert result.readability_score == 85

    @pytest.mark.asyncio
    async def test_proofread_with_style_guide(self, proofreading_agent):
        """Proofreading with style guide."""
        with patch.object(proofreading_agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "corrected_text": "Corrected text",
                "issues_found": [],
                "style_suggestions": [],
                "readability_score": 90,
                "reading_level": "College",
            })

            await proofreading_agent.execute(
                text="Test text",
                style_guide="Chicago",
            )

            # Service uses kwargs, not positional args
            system_prompt = mock_call.call_args.kwargs.get("system_prompt", "")
            assert "Chicago" in system_prompt

    @pytest.mark.asyncio
    async def test_proofread_with_focus_areas(self, proofreading_agent):
        """Proofreading with specific focus areas."""
        with patch.object(proofreading_agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "corrected_text": "Corrected text",
                "issues_found": [],
                "style_suggestions": [],
                "readability_score": 80,
                "reading_level": "High school",
            })

            await proofreading_agent.execute(
                text="Test text",
                focus_areas=["grammar", "punctuation"],
            )

            # Service uses kwargs, not positional args
            system_prompt = mock_call.call_args.kwargs.get("system_prompt", "")
            assert "grammar" in system_prompt.lower()
            assert "punctuation" in system_prompt.lower()

    @pytest.mark.asyncio
    async def test_proofread_preserves_original_on_error(self, proofreading_agent):
        """Proofreading returns original text on error."""
        with patch.object(proofreading_agent, '_call_llm') as mock_call:
            mock_call.side_effect = Exception("API Error")

            result = await proofreading_agent.execute(text="Original text")

            assert result.original_text == "Original text"
            assert result.corrected_text == "Original text"


# =============================================================================
# AGENT SERVICE TESTS
# =============================================================================


class TestAgentService:
    """Tests for AgentService."""

    def test_service_has_all_agents(self, agent_service):
        """Service has all agent types registered."""
        assert AgentType.RESEARCH in agent_service._agents
        assert AgentType.DATA_ANALYST in agent_service._agents
        assert AgentType.EMAIL_DRAFT in agent_service._agents
        assert AgentType.CONTENT_REPURPOSE in agent_service._agents
        assert AgentType.PROOFREADING in agent_service._agents

    @pytest.mark.asyncio
    async def test_run_research_agent(self, agent_service):
        """Run research agent through service."""
        with patch.object(agent_service._agents[AgentType.RESEARCH], '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "summary": "Test summary",
                "sections": [],
                "key_findings": [],
                "recommendations": [],
                "sources": [],
            })

            task = await agent_service.run_agent(
                agent_type=AgentType.RESEARCH,
                topic="Test Topic",
            )

            assert task.status == AgentStatus.COMPLETED
            assert task.result is not None
            assert task.error is None

    @pytest.mark.asyncio
    async def test_run_agent_creates_task(self, agent_service):
        """Running agent creates and stores task."""
        with patch.object(agent_service._agents[AgentType.RESEARCH], '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "summary": "Test",
                "sections": [],
                "key_findings": [],
                "recommendations": [],
                "sources": [],
            })

            task = await agent_service.run_agent(
                agent_type=AgentType.RESEARCH,
                topic="Test",
            )

            stored_task = agent_service.get_task(task.task_id)
            assert stored_task is not None
            assert stored_task.task_id == task.task_id

    @pytest.mark.asyncio
    async def test_run_agent_failure_handling(self, agent_service):
        """Run agent handles failures properly - agent catches internal errors gracefully."""
        with patch.object(agent_service._agents[AgentType.RESEARCH], '_call_llm') as mock_call:
            mock_call.side_effect = Exception("Test error")

            task = await agent_service.run_agent(
                agent_type=AgentType.RESEARCH,
                topic="Test",
            )

            # Agent catches _call_openai errors internally and returns COMPLETED with error info
            # The agent's execute() method has try/except that returns fallback result
            assert task.status == AgentStatus.COMPLETED
            # Error info should be in the result summary
            assert "failed" in task.result.get("summary", "").lower() or "unable" in task.result.get("summary", "").lower()

    @pytest.mark.asyncio
    async def test_run_unknown_agent_type(self, agent_service):
        """Running unknown agent type fails."""
        # Remove an agent to simulate unknown type
        del agent_service._agents[AgentType.RESEARCH]

        task = await agent_service.run_agent(
            agent_type=AgentType.RESEARCH,
            topic="Test",
        )

        assert task.status == AgentStatus.FAILED
        assert task.error is not None  # Error should be set

    @pytest.mark.asyncio
    async def test_list_tasks_empty(self, agent_service):
        """List tasks returns empty for fresh service."""
        tasks = await agent_service.list_tasks()
        assert tasks == []

    @pytest.mark.asyncio
    async def test_list_tasks_with_filter(self, agent_service):
        """List tasks can be filtered by agent type."""
        with patch.object(agent_service._agents[AgentType.RESEARCH], '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "summary": "Test",
                "sections": [],
                "key_findings": [],
                "recommendations": [],
                "sources": [],
            })

            await agent_service.run_agent(AgentType.RESEARCH, topic="Test")

        with patch.object(agent_service._agents[AgentType.EMAIL_DRAFT], '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "subject": "Test",
                "body": "Test",
                "tone": "professional",
                "suggested_recipients": [],
                "attachments_suggested": [],
                "follow_up_actions": [],
            })

            await agent_service.run_agent(
                AgentType.EMAIL_DRAFT,
                context="Test",
                purpose="Test",
            )

        all_tasks = await agent_service.list_tasks()
        research_tasks = await agent_service.list_tasks(agent_type=AgentType.RESEARCH)

        assert len(all_tasks) == 2
        assert len(research_tasks) == 1

    @pytest.mark.asyncio
    async def test_clear_completed_tasks(self, agent_service):
        """Clear completed tasks removes them."""
        # Add some fake completed tasks
        from datetime import datetime, timezone
        agent_service._tasks["task1"] = AgentTask(
            task_id="task1",
            agent_type=AgentType.RESEARCH,
            input={},
            status=AgentStatus.COMPLETED,
        )
        agent_service._tasks["task2"] = AgentTask(
            task_id="task2",
            agent_type=AgentType.RESEARCH,
            input={},
            status=AgentStatus.RUNNING,
        )

        cleared = await agent_service.clear_completed_tasks()

        assert cleared == 1
        assert "task1" not in agent_service._tasks
        assert "task2" in agent_service._tasks

    def test_cleanup_old_tasks(self, agent_service):
        """Old completed tasks are cleaned up."""
        from datetime import timedelta

        # Add an old completed task
        old_time = datetime.now(timezone.utc) - timedelta(hours=2)
        agent_service._tasks["old_task"] = AgentTask(
            task_id="old_task",
            agent_type=AgentType.RESEARCH,
            input={},
            status=AgentStatus.COMPLETED,
            completed_at=old_time,
        )

        # Add a recent completed task
        agent_service._tasks["new_task"] = AgentTask(
            task_id="new_task",
            agent_type=AgentType.RESEARCH,
            input={},
            status=AgentStatus.COMPLETED,
            completed_at=datetime.now(timezone.utc),
        )

        agent_service._cleanup_old_tasks()

        assert "old_task" not in agent_service._tasks
        assert "new_task" in agent_service._tasks


# =============================================================================
# MODEL TESTS
# =============================================================================


class TestAgentModels:
    """Tests for agent data models."""

    def test_research_report_model(self):
        """ResearchReport model validation."""
        report = ResearchReport(
            topic="AI",
            summary="Summary",
            sections=[{"title": "Intro", "content": "Content"}],
            sources=[{"title": "Source", "url": "https://example.com"}],
            key_findings=["Finding 1"],
            recommendations=["Recommendation 1"],
            word_count=100,
        )
        assert report.topic == "AI"
        assert len(report.sections) == 1

    def test_data_analysis_result_model(self):
        """DataAnalysisResult model validation."""
        result = DataAnalysisResult(
            query="What is the average?",
            answer="The average is 50",
            data_summary={"avg": 50},
            insights=["Insight 1"],
            charts=[{"type": "bar"}],
            sql_queries=["SELECT AVG(value) FROM data"],
            confidence=0.9,
        )
        assert result.confidence == 0.9

    def test_email_draft_model(self):
        """EmailDraft model validation."""
        draft = EmailDraft(
            subject="Test Subject",
            body="Test body",
            tone="professional",
            suggested_recipients=["test@example.com"],
            attachments_suggested=["file.pdf"],
            follow_up_actions=["Review document"],
        )
        assert draft.tone == "professional"

    def test_repurposed_content_model(self):
        """RepurposedContent model validation."""
        content = RepurposedContent(
            original_format="article",
            outputs=[{"format": "tweet_thread", "content": "Tweet 1...", "metadata": {}}],
            adaptations_made=["Converted to tweet_thread"],
        )
        assert content.original_format == "article"

    def test_proofreading_result_model(self):
        """ProofreadingResult model validation."""
        result = ProofreadingResult(
            original_text="Original",
            corrected_text="Corrected",
            issues_found=[{"type": "spelling", "original": "teh", "correction": "the", "explanation": "Typo"}],
            style_suggestions=["Use active voice"],
            readability_score=85,
            word_count=10,
            reading_level="8th grade",
        )
        assert result.readability_score == 85

    def test_agent_task_model(self):
        """AgentTask model validation."""
        task = AgentTask(
            task_id="test123",
            agent_type=AgentType.RESEARCH,
            input={"topic": "AI"},
            status=AgentStatus.RUNNING,
            progress=0.5,
        )
        assert task.status == AgentStatus.RUNNING
        assert task.progress == 0.5
