"""
AI Agents API Integration Tests
Tests for agent API endpoints and request/response handling.
"""
import json
import pytest
from unittest.mock import Mock, patch

import os

from backend.app.services.agents.service import (
    AgentService,
    AgentType,
    AgentStatus,
    ResearchReport,
    DataAnalysisResult,
    EmailDraft,
    RepurposedContent,
    ProofreadingResult,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def service():
    """Get agent service instance."""
    return AgentService()


# =============================================================================
# RESEARCH AGENT API TESTS
# =============================================================================


class TestResearchAgentAPI:
    """Tests for research agent API integration."""

    @pytest.mark.asyncio
    async def test_research_api_full_request(self, service):
        """Full research request with all parameters."""
        with patch.object(service._agents[AgentType.RESEARCH], '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "summary": "Comprehensive research on AI",
                "sections": [
                    {"title": "Overview", "content": "AI is transforming industries..."},
                    {"title": "Applications", "content": "Healthcare, finance, etc..."},
                ],
                "key_findings": ["AI adoption is growing", "Healthcare leads adoption"],
                "recommendations": ["Invest in AI training", "Start with pilot projects"],
                "sources": [
                    {"title": "AI Report 2026", "url": "https://example.com/report"},
                ],
            })

            task = await service.run_agent(
                agent_type=AgentType.RESEARCH,
                topic="AI in Enterprise",
                depth="comprehensive",
                focus_areas=["Healthcare", "Finance"],
                max_sections=5,
            )

            assert task.status == AgentStatus.COMPLETED
            result = task.result
            assert "AI" in result["summary"]
            assert len(result["sections"]) == 2
            assert len(result["key_findings"]) == 2

    @pytest.mark.asyncio
    async def test_research_api_minimal_request(self, service):
        """Minimal research request with only topic."""
        with patch.object(service._agents[AgentType.RESEARCH], '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "summary": "Brief research",
                "sections": [],
                "key_findings": [],
                "recommendations": [],
                "sources": [],
            })

            task = await service.run_agent(
                agent_type=AgentType.RESEARCH,
                topic="Test Topic",
            )

            assert task.status == AgentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_research_api_depth_levels(self, service):
        """Research with different depth levels."""
        depths = ["quick", "moderate", "comprehensive"]

        for depth in depths:
            with patch.object(service._agents[AgentType.RESEARCH], '_call_llm') as mock_call:
                mock_call.return_value = json.dumps({
                    "summary": f"Research at {depth} depth",
                    "sections": [],
                    "key_findings": [],
                    "recommendations": [],
                    "sources": [],
                })

                task = await service.run_agent(
                    agent_type=AgentType.RESEARCH,
                    topic="Test",
                    depth=depth,
                )

                assert task.status == AgentStatus.COMPLETED
                # Verify depth was passed to prompt - service uses kwargs
                system_prompt = mock_call.call_args.kwargs.get("system_prompt", "")
                assert depth in system_prompt.lower() or "comprehensive" in system_prompt.lower()


# =============================================================================
# DATA ANALYST AGENT API TESTS
# =============================================================================


class TestDataAnalystAgentAPI:
    """Tests for data analyst agent API integration."""

    @pytest.mark.asyncio
    async def test_data_analyst_full_request(self, service):
        """Full data analysis request."""
        with patch.object(service._agents[AgentType.DATA_ANALYST], '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "answer": "The total revenue is $1,000,000",
                "data_summary": {"total_revenue": 1000000, "avg_order": 500},
                "insights": ["Revenue growing 20% YoY", "Q4 is strongest quarter"],
                "charts": [
                    {"type": "line", "title": "Revenue Trend", "x_column": "month", "y_columns": ["revenue"]},
                    {"type": "bar", "title": "Revenue by Quarter", "x_column": "quarter", "y_columns": ["revenue"]},
                ],
                "sql_queries": ["SELECT SUM(revenue) FROM orders"],
                "confidence": 0.92,
            })

            task = await service.run_agent(
                agent_type=AgentType.DATA_ANALYST,
                question="What is the total revenue?",
                data=[
                    {"month": "Jan", "revenue": 100000},
                    {"month": "Feb", "revenue": 120000},
                    {"month": "Mar", "revenue": 150000},
                ],
                data_description="Monthly revenue data",
                generate_charts=True,
            )

            assert task.status == AgentStatus.COMPLETED
            result = task.result
            assert "1,000,000" in result["answer"]
            assert len(result["charts"]) == 2
            assert result["confidence"] > 0.9

    @pytest.mark.asyncio
    async def test_data_analyst_large_dataset(self, service):
        """Data analysis with large dataset (tests sampling)."""
        with patch.object(service._agents[AgentType.DATA_ANALYST], '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "answer": "Analysis complete",
                "data_summary": {},
                "insights": [],
                "charts": [],
                "sql_queries": [],
                "confidence": 0.8,
            })

            # Generate large dataset
            large_data = [{"id": i, "value": i * 10} for i in range(1000)]

            task = await service.run_agent(
                agent_type=AgentType.DATA_ANALYST,
                question="What patterns exist?",
                data=large_data,
            )

            assert task.status == AgentStatus.COMPLETED
            # Verify that data size info was sent - service uses kwargs
            user_prompt = mock_call.call_args.kwargs.get("user_prompt", "")
            system_prompt = mock_call.call_args.kwargs.get("system_prompt", "")
            # Check that row count info is present in either prompt
            combined = system_prompt + user_prompt
            assert "1000" in combined or "Total" in combined or "rows" in combined.lower()

    @pytest.mark.asyncio
    async def test_data_analyst_empty_data(self, service):
        """Data analysis with empty data."""
        with patch.object(service._agents[AgentType.DATA_ANALYST], '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "answer": "No data provided for analysis",
                "data_summary": {},
                "insights": [],
                "charts": [],
                "sql_queries": [],
                "confidence": 0.0,
            })

            task = await service.run_agent(
                agent_type=AgentType.DATA_ANALYST,
                question="What is the average?",
                data=[],
            )

            assert task.status == AgentStatus.COMPLETED


# =============================================================================
# EMAIL DRAFT AGENT API TESTS
# =============================================================================


class TestEmailDraftAgentAPI:
    """Tests for email draft agent API integration."""

    @pytest.mark.asyncio
    async def test_email_draft_full_request(self, service):
        """Full email draft request."""
        with patch.object(service._agents[AgentType.EMAIL_DRAFT], '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "subject": "Follow-up: Quarterly Review Meeting",
                "body": "Dear Team,\n\nThank you for attending the quarterly review...",
                "tone": "professional",
                "suggested_recipients": ["team@company.com"],
                "attachments_suggested": ["Q4_Report.pdf", "Action_Items.xlsx"],
                "follow_up_actions": ["Schedule next review", "Send updated forecasts"],
            })

            task = await service.run_agent(
                agent_type=AgentType.EMAIL_DRAFT,
                context="Just finished Q4 review meeting, need to send summary",
                purpose="Send meeting follow-up with action items",
                tone="professional",
                recipient_info="Entire project team, 10 people",
                previous_emails=["Previous email about meeting schedule"],
            )

            assert task.status == AgentStatus.COMPLETED
            result = task.result
            assert "Follow-up" in result["subject"]
            assert len(result["attachments_suggested"]) == 2

    @pytest.mark.asyncio
    @pytest.mark.parametrize("tone", ["professional", "friendly", "formal", "casual"])
    async def test_email_draft_tone_variations(self, service, tone):
        """Email draft with different tones."""
        with patch.object(service._agents[AgentType.EMAIL_DRAFT], '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "subject": "Test",
                "body": f"Email body with {tone} tone",
                "tone": tone,
                "suggested_recipients": [],
                "attachments_suggested": [],
                "follow_up_actions": [],
            })

            task = await service.run_agent(
                agent_type=AgentType.EMAIL_DRAFT,
                context="Test context",
                purpose="Test purpose",
                tone=tone,
            )

            assert task.status == AgentStatus.COMPLETED
            assert task.result["tone"] == tone


# =============================================================================
# CONTENT REPURPOSING AGENT API TESTS
# =============================================================================


class TestContentRepurposingAgentAPI:
    """Tests for content repurposing agent API integration."""

    @pytest.mark.asyncio
    async def test_content_repurpose_single_format(self, service):
        """Repurpose to single format."""
        with patch.object(service._agents[AgentType.CONTENT_REPURPOSE], '_call_llm') as mock_call:
            mock_call.return_value = "Tweet 1/5: AI is transforming...\n\nTweet 2/5: Key benefits include..."

            task = await service.run_agent(
                agent_type=AgentType.CONTENT_REPURPOSE,
                content="Long article about AI transformation in business...",
                source_format="article",
                target_formats=["tweet_thread"],
            )

            assert task.status == AgentStatus.COMPLETED
            result = task.result
            assert len(result["outputs"]) == 1
            assert result["outputs"][0]["format"] == "tweet_thread"

    @pytest.mark.asyncio
    async def test_content_repurpose_multiple_formats(self, service):
        """Repurpose to multiple formats."""
        with patch.object(service._agents[AgentType.CONTENT_REPURPOSE], '_call_llm') as mock_call:
            mock_call.return_value = "Repurposed content for this format"

            task = await service.run_agent(
                agent_type=AgentType.CONTENT_REPURPOSE,
                content="Original article content...",
                source_format="blog_post",
                target_formats=["tweet_thread", "linkedin_post", "executive_summary"],
            )

            assert task.status == AgentStatus.COMPLETED
            result = task.result
            assert len(result["outputs"]) == 3

    @pytest.mark.asyncio
    async def test_content_repurpose_all_formats(self, service):
        """Repurpose to all supported formats."""
        all_formats = [
            "tweet_thread", "linkedin_post", "blog_summary", "slides",
            "email_newsletter", "video_script", "infographic",
            "podcast_notes", "press_release", "executive_summary",
        ]

        with patch.object(service._agents[AgentType.CONTENT_REPURPOSE], '_call_llm') as mock_call:
            mock_call.return_value = "Repurposed content"

            task = await service.run_agent(
                agent_type=AgentType.CONTENT_REPURPOSE,
                content="Comprehensive original content...",
                source_format="whitepaper",
                target_formats=all_formats,
            )

            assert task.status == AgentStatus.COMPLETED
            assert len(task.result["outputs"]) == 10

    @pytest.mark.asyncio
    async def test_content_repurpose_with_options(self, service):
        """Repurpose with preserve_key_points and adapt_length options."""
        with patch.object(service._agents[AgentType.CONTENT_REPURPOSE], '_call_llm') as mock_call:
            mock_call.return_value = "Repurposed content"

            task = await service.run_agent(
                agent_type=AgentType.CONTENT_REPURPOSE,
                content="Original content",
                source_format="report",
                target_formats=["slides"],
                preserve_key_points=True,
                adapt_length=True,
            )

            assert task.status == AgentStatus.COMPLETED
            # Verify options were passed to prompt - service uses kwargs
            system_prompt = mock_call.call_args.kwargs.get("system_prompt", "")
            assert "Preserve" in system_prompt or "preserve" in system_prompt.lower()
            assert "Adapt" in system_prompt or "adapt" in system_prompt.lower()


# =============================================================================
# PROOFREADING AGENT API TESTS
# =============================================================================


class TestProofreadingAgentAPI:
    """Tests for proofreading agent API integration."""

    @pytest.mark.asyncio
    async def test_proofread_full_request(self, service):
        """Full proofreading request."""
        with patch.object(service._agents[AgentType.PROOFREADING], '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "corrected_text": "This is the corrected and improved text.",
                "issues_found": [
                    {"type": "grammar", "original": "teh", "correction": "the", "explanation": "Misspelling"},
                    {"type": "punctuation", "original": "However", "correction": "However,", "explanation": "Missing comma"},
                ],
                "style_suggestions": ["Consider using more active voice", "Vary sentence length"],
                "readability_score": 78,
                "reading_level": "10th grade",
            })

            task = await service.run_agent(
                agent_type=AgentType.PROOFREADING,
                text="This is teh original text However it has some issues.",
                style_guide="AP",
                focus_areas=["grammar", "punctuation"],
                preserve_voice=True,
            )

            assert task.status == AgentStatus.COMPLETED
            result = task.result
            assert len(result["issues_found"]) == 2
            assert result["readability_score"] == 78

    @pytest.mark.asyncio
    async def test_proofread_style_guides(self, service):
        """Proofreading with different style guides."""
        style_guides = ["AP", "Chicago", "APA", "MLA"]

        for guide in style_guides:
            with patch.object(service._agents[AgentType.PROOFREADING], '_call_llm') as mock_call:
                mock_call.return_value = json.dumps({
                    "corrected_text": "Corrected text",
                    "issues_found": [],
                    "style_suggestions": [],
                    "readability_score": 85,
                    "reading_level": "College",
                })

                task = await service.run_agent(
                    agent_type=AgentType.PROOFREADING,
                    text="Test text",
                    style_guide=guide,
                )

                assert task.status == AgentStatus.COMPLETED
                # Verify style guide was passed - service uses kwargs
                system_prompt = mock_call.call_args.kwargs.get("system_prompt", "")
                assert guide in system_prompt

    @pytest.mark.asyncio
    async def test_proofread_long_text(self, service):
        """Proofreading long text."""
        with patch.object(service._agents[AgentType.PROOFREADING], '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "corrected_text": "Long corrected text...",
                "issues_found": [{"type": "style", "original": "", "correction": "", "explanation": ""}],
                "style_suggestions": [],
                "readability_score": 70,
                "reading_level": "Professional",
            })

            long_text = "This is a sentence. " * 500

            task = await service.run_agent(
                agent_type=AgentType.PROOFREADING,
                text=long_text,
            )

            assert task.status == AgentStatus.COMPLETED
            assert task.result["word_count"] == len(long_text.split())


# =============================================================================
# TASK MANAGEMENT API TESTS
# =============================================================================


class TestTaskManagementAPI:
    """Tests for task management API functionality."""

    @pytest.mark.asyncio
    async def test_get_task_by_id(self, service):
        """Get task by ID."""
        with patch.object(service._agents[AgentType.RESEARCH], '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "summary": "Test",
                "sections": [],
                "key_findings": [],
                "recommendations": [],
                "sources": [],
            })

            task = await service.run_agent(
                agent_type=AgentType.RESEARCH,
                topic="Test",
            )

            retrieved = service.get_task(task.task_id)
            assert retrieved is not None
            assert retrieved.task_id == task.task_id

    def test_get_nonexistent_task(self, service):
        """Get nonexistent task returns None."""
        result = service.get_task("nonexistent_id")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_tasks_ordering(self, service):
        """Tasks are listed in reverse chronological order."""
        with patch.object(service._agents[AgentType.RESEARCH], '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "summary": "Test",
                "sections": [],
                "key_findings": [],
                "recommendations": [],
                "sources": [],
            })

            # Create multiple tasks
            task1 = await service.run_agent(AgentType.RESEARCH, topic="First")
            task2 = await service.run_agent(AgentType.RESEARCH, topic="Second")
            task3 = await service.run_agent(AgentType.RESEARCH, topic="Third")

            tasks = service.list_tasks()

            # Most recent first
            assert tasks[0].task_id == task3.task_id
            assert tasks[1].task_id == task2.task_id
            assert tasks[2].task_id == task1.task_id

    @pytest.mark.asyncio
    async def test_list_tasks_limit(self, service):
        """Tasks list respects limit."""
        with patch.object(service._agents[AgentType.RESEARCH], '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "summary": "Test",
                "sections": [],
                "key_findings": [],
                "recommendations": [],
                "sources": [],
            })

            # Create 5 tasks
            for i in range(5):
                await service.run_agent(AgentType.RESEARCH, topic=f"Topic {i}")

            limited_tasks = service.list_tasks(limit=3)
            assert len(limited_tasks) == 3


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


class TestAgentAPIErrorHandling:
    """Tests for API error handling."""

    @pytest.mark.asyncio
    async def test_api_error_handled_gracefully(self, service):
        """API error is handled gracefully - agent returns completed with error info."""
        with patch.object(service._agents[AgentType.RESEARCH], '_call_llm') as mock_call:
            mock_call.side_effect = Exception("API rate limit exceeded")

            task = await service.run_agent(
                agent_type=AgentType.RESEARCH,
                topic="Test",
            )

            # Agent catches internal errors and returns COMPLETED with error info in result
            assert task.status == AgentStatus.COMPLETED
            # Error info should be in the result summary
            assert "failed" in task.result.get("summary", "").lower() or "unable" in task.result.get("summary", "").lower()

    @pytest.mark.asyncio
    async def test_json_parse_error_handled(self, service):
        """JSON parse error is handled gracefully."""
        with patch.object(service._agents[AgentType.RESEARCH], '_call_llm') as mock_call:
            mock_call.return_value = "This is not valid JSON at all"

            task = await service.run_agent(
                agent_type=AgentType.RESEARCH,
                topic="Test",
            )

            # Should complete but with fallback values
            assert task.status == AgentStatus.COMPLETED
            assert "Unable to parse" in task.result["summary"]

    @pytest.mark.asyncio
    async def test_timeout_error_handled(self, service):
        """Timeout error is handled gracefully."""
        with patch.object(service._agents[AgentType.RESEARCH], '_call_llm') as mock_call:
            mock_call.side_effect = TimeoutError("Request timed out")

            task = await service.run_agent(
                agent_type=AgentType.RESEARCH,
                topic="Test",
            )

            # Agent catches internal errors and returns COMPLETED with error info
            assert task.status == AgentStatus.COMPLETED
            # Error info should be in the result summary
            assert "failed" in task.result.get("summary", "").lower() or "unable" in task.result.get("summary", "").lower()
