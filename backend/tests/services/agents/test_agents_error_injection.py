"""
AI Agents Error Injection Tests
Destructive simulation and edge case testing for all agents.
"""
import json
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone, timedelta

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


# =============================================================================
# CLIENT INITIALIZATION ERRORS
# =============================================================================


class TestClientInitializationErrors:
    """Tests for OpenAI client initialization failures."""

    def test_invalid_api_key(self, research_agent):
        """Handle invalid API key."""
        with patch('openai.OpenAI') as mock_class:
            mock_class.side_effect = Exception("Invalid API key")

            with pytest.raises(Exception, match="Invalid API key"):
                research_agent._get_client()

    def test_network_error_on_init(self, research_agent):
        """Handle network error during initialization."""
        with patch('openai.OpenAI') as mock_class:
            mock_class.side_effect = ConnectionError("Network unreachable")

            with pytest.raises(ConnectionError):
                research_agent._get_client()

    def test_import_error(self, research_agent):
        """Handle OpenAI import error."""
        research_agent._client = None

        with patch.dict('sys.modules', {'openai': None}):
            with patch('builtins.__import__', side_effect=ImportError("No module named openai")):
                # The agent should handle this gracefully or raise
                pass  # Can't easily test import in isolated way


# =============================================================================
# API CALL ERRORS
# =============================================================================


class TestAPICallErrors:
    """Tests for API call failures."""

    def test_rate_limit_error(self, research_agent):
        """Handle rate limit error."""
        with patch('openai.OpenAI') as mock_class:
            mock_client = Mock()
            mock_class.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")

            with pytest.raises(Exception, match="Rate limit"):
                research_agent._call_llm("system", "user")

    def test_timeout_error(self, research_agent):
        """Handle timeout error."""
        with patch('openai.OpenAI') as mock_class:
            mock_client = Mock()
            mock_class.return_value = mock_client
            mock_client.chat.completions.create.side_effect = TimeoutError("Request timed out")

            with pytest.raises(TimeoutError):
                research_agent._call_llm("system", "user")

    def test_server_error(self, research_agent):
        """Handle server error (500)."""
        with patch('openai.OpenAI') as mock_class:
            mock_client = Mock()
            mock_class.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("Internal server error")

            with pytest.raises(Exception, match="server error"):
                research_agent._call_llm("system", "user")

    def test_connection_reset(self, research_agent):
        """Handle connection reset."""
        with patch('openai.OpenAI') as mock_class:
            mock_client = Mock()
            mock_class.return_value = mock_client
            mock_client.chat.completions.create.side_effect = ConnectionResetError()

            with pytest.raises(ConnectionResetError):
                research_agent._call_llm("system", "user")


# =============================================================================
# JSON PARSING ERRORS
# =============================================================================


class TestJSONParsingErrors:
    """Tests for JSON parsing edge cases."""

    @pytest.mark.asyncio
    async def test_research_invalid_json(self, research_agent):
        """Research handles invalid JSON."""
        with patch.object(research_agent, '_call_llm') as mock_call:
            mock_call.return_value = "This is not JSON {invalid"

            result = await research_agent.execute(topic="Test")

            assert "Unable to parse" in result.summary

    @pytest.mark.asyncio
    async def test_research_null_json(self, research_agent):
        """Research handles null JSON."""
        with patch.object(research_agent, '_call_llm') as mock_call:
            mock_call.return_value = "null"

            result = await research_agent.execute(topic="Test")

            # Should use defaults since null parses to None
            assert result.topic == "Test"

    @pytest.mark.asyncio
    async def test_research_empty_json(self, research_agent):
        """Research handles empty JSON object."""
        with patch.object(research_agent, '_call_llm') as mock_call:
            mock_call.return_value = "{}"

            result = await research_agent.execute(topic="Test")

            assert result.summary == ""
            assert result.sections == []

    @pytest.mark.asyncio
    async def test_data_analyst_malformed_response(self, data_analyst_agent):
        """Data analyst handles malformed response."""
        with patch.object(data_analyst_agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "answer": "The answer",
                # Missing other expected fields
            })

            result = await data_analyst_agent.execute(
                question="Test?",
                data=[{"a": 1}],
            )

            assert result.answer == "The answer"
            assert result.insights == []
            assert result.charts == []


# =============================================================================
# INPUT EDGE CASES
# =============================================================================


class TestInputEdgeCases:
    """Tests for edge case inputs."""

    @pytest.mark.asyncio
    async def test_very_long_topic(self, research_agent):
        """Handle very long topic string."""
        with patch.object(research_agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "summary": "Summary",
                "sections": [],
                "key_findings": [],
                "recommendations": [],
                "sources": [],
            })

            long_topic = "A" * 10000

            result = await research_agent.execute(topic=long_topic)

            assert result.topic == long_topic

    @pytest.mark.asyncio
    async def test_special_characters_in_input(self, research_agent):
        """Handle special characters in input."""
        with patch.object(research_agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "summary": "Summary",
                "sections": [],
                "key_findings": [],
                "recommendations": [],
                "sources": [],
            })

            special_topic = "Test <script>alert('xss')</script> & \"quotes\" 'apostrophes'"

            result = await research_agent.execute(topic=special_topic)

            assert result.topic == special_topic

    @pytest.mark.asyncio
    async def test_unicode_in_input(self, research_agent):
        """Handle unicode in input."""
        with patch.object(research_agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "summary": "研究摘要",
                "sections": [],
                "key_findings": [],
                "recommendations": [],
                "sources": [],
            })

            unicode_topic = "研究テーマ: 人工知能 🤖"

            result = await research_agent.execute(topic=unicode_topic)

            assert result.topic == unicode_topic

    @pytest.mark.asyncio
    async def test_empty_data_list(self, data_analyst_agent):
        """Handle empty data list."""
        with patch.object(data_analyst_agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "answer": "No data",
                "data_summary": {},
                "insights": [],
                "charts": [],
                "sql_queries": [],
                "confidence": 0,
            })

            result = await data_analyst_agent.execute(
                question="What is the average?",
                data=[],
            )

            assert result.query == "What is the average?"

    @pytest.mark.asyncio
    async def test_data_with_null_values(self, data_analyst_agent):
        """Handle data with null/None values."""
        with patch.object(data_analyst_agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "answer": "Handled nulls",
                "data_summary": {},
                "insights": [],
                "charts": [],
                "sql_queries": [],
                "confidence": 0.5,
            })

            data_with_nulls = [
                {"a": 1, "b": None},
                {"a": None, "b": 2},
                {"a": None, "b": None},
            ]

            result = await data_analyst_agent.execute(
                question="Test?",
                data=data_with_nulls,
            )

            assert result is not None


# =============================================================================
# CONCURRENT EXECUTION TESTS
# =============================================================================


class TestConcurrentExecution:
    """Tests for concurrent agent execution."""

    @pytest.mark.asyncio
    async def test_multiple_agents_concurrent(self, agent_service):
        """Multiple agents can run concurrently."""
        import asyncio

        with patch.object(agent_service._agents[AgentType.RESEARCH], '_call_llm') as mock_research:
            mock_research.return_value = json.dumps({
                "summary": "Research result",
                "sections": [],
                "key_findings": [],
                "recommendations": [],
                "sources": [],
            })

            with patch.object(agent_service._agents[AgentType.PROOFREADING], '_call_llm') as mock_proofread:
                mock_proofread.return_value = json.dumps({
                    "corrected_text": "Corrected",
                    "issues_found": [],
                    "style_suggestions": [],
                    "readability_score": 80,
                    "reading_level": "10th grade",
                })

                # Run two agents concurrently
                tasks = await asyncio.gather(
                    agent_service.run_agent(AgentType.RESEARCH, topic="Topic 1"),
                    agent_service.run_agent(AgentType.PROOFREADING, text="Text to check"),
                )

                assert len(tasks) == 2
                assert all(t.status == AgentStatus.COMPLETED for t in tasks)

    @pytest.mark.asyncio
    async def test_same_agent_concurrent(self, agent_service):
        """Same agent type can handle concurrent requests."""
        import asyncio

        with patch.object(agent_service._agents[AgentType.RESEARCH], '_call_llm') as mock_call:
            call_count = 0

            async def delayed_response(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                await asyncio.sleep(0.01)  # Small delay
                return json.dumps({
                    "summary": f"Result {call_count}",
                    "sections": [],
                    "key_findings": [],
                    "recommendations": [],
                    "sources": [],
                })

            mock_call.side_effect = lambda *a, **k: json.dumps({
                "summary": "Result",
                "sections": [],
                "key_findings": [],
                "recommendations": [],
                "sources": [],
            })

            tasks = await asyncio.gather(
                agent_service.run_agent(AgentType.RESEARCH, topic="Topic 1"),
                agent_service.run_agent(AgentType.RESEARCH, topic="Topic 2"),
                agent_service.run_agent(AgentType.RESEARCH, topic="Topic 3"),
            )

            assert len(tasks) == 3
            assert len(set(t.task_id for t in tasks)) == 3  # All unique IDs


# =============================================================================
# TASK MANAGEMENT EDGE CASES
# =============================================================================


class TestTaskManagementEdgeCases:
    """Tests for task management edge cases."""

    def test_max_task_limit_enforcement(self, agent_service):
        """Task cleanup enforces maximum limit."""
        # Add more than MAX_COMPLETED_TASKS
        for i in range(agent_service.MAX_COMPLETED_TASKS + 50):
            agent_service._tasks[f"task_{i}"] = AgentTask(
                task_id=f"task_{i}",
                agent_type=AgentType.RESEARCH,
                input={},
                status=AgentStatus.COMPLETED,
                completed_at=datetime.now(timezone.utc) - timedelta(minutes=i),
            )

        agent_service._cleanup_old_tasks()

        # Should be at or under limit
        completed_count = sum(
            1 for t in agent_service._tasks.values()
            if t.status == AgentStatus.COMPLETED
        )
        assert completed_count <= agent_service.MAX_COMPLETED_TASKS

    def test_old_tasks_cleaned_up(self, agent_service):
        """Old completed tasks are removed."""
        old_time = datetime.now(timezone.utc) - timedelta(seconds=agent_service.MAX_TASK_AGE_SECONDS + 100)

        agent_service._tasks["old_task"] = AgentTask(
            task_id="old_task",
            agent_type=AgentType.RESEARCH,
            input={},
            status=AgentStatus.COMPLETED,
            completed_at=old_time,
        )

        agent_service._cleanup_old_tasks()

        assert "old_task" not in agent_service._tasks

    def test_running_tasks_not_cleaned(self, agent_service):
        """Running tasks are not cleaned up."""
        agent_service._tasks["running_task"] = AgentTask(
            task_id="running_task",
            agent_type=AgentType.RESEARCH,
            input={},
            status=AgentStatus.RUNNING,
        )

        agent_service._cleanup_old_tasks()

        assert "running_task" in agent_service._tasks


# =============================================================================
# REPURPOSING AGENT EDGE CASES
# =============================================================================


class TestRepurposingEdgeCases:
    """Tests for content repurposing edge cases."""

    @pytest.mark.asyncio
    async def test_repurpose_empty_content(self):
        """Handle empty content."""
        agent = ContentRepurposingAgent()

        with patch.object(agent, '_call_llm') as mock_call:
            mock_call.return_value = "Repurposed empty content"

            result = await agent.execute(
                content="",
                source_format="article",
                target_formats=["tweet_thread"],
            )

            assert len(result.outputs) == 1

    @pytest.mark.asyncio
    async def test_repurpose_unknown_format(self):
        """Handle unknown target format."""
        agent = ContentRepurposingAgent()

        with patch.object(agent, '_call_llm') as mock_call:
            mock_call.return_value = "Repurposed to custom format"

            result = await agent.execute(
                content="Test content",
                source_format="article",
                target_formats=["unknown_format"],
            )

            # Should still process with generic guidelines
            assert len(result.outputs) == 1
            assert result.outputs[0]["format"] == "unknown_format"

    @pytest.mark.asyncio
    async def test_repurpose_all_formats_fail(self):
        """Handle all format conversions failing."""
        agent = ContentRepurposingAgent()

        with patch.object(agent, '_call_llm') as mock_call:
            mock_call.side_effect = Exception("All conversions failed")

            result = await agent.execute(
                content="Test content",
                source_format="article",
                target_formats=["tweet_thread", "linkedin_post"],
            )

            # All outputs should have errors
            assert len(result.outputs) == 2
            assert all("error" in o.get("metadata", {}) or "failed" in o["content"].lower() for o in result.outputs)


# =============================================================================
# EMAIL DRAFT EDGE CASES
# =============================================================================


class TestEmailDraftEdgeCases:
    """Tests for email draft edge cases."""

    @pytest.mark.asyncio
    async def test_email_with_many_previous_emails(self):
        """Handle many previous emails (should limit)."""
        agent = EmailDraftAgent()

        with patch.object(agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "subject": "Re: Thread",
                "body": "Response",
                "tone": "professional",
                "suggested_recipients": [],
                "attachments_suggested": [],
                "follow_up_actions": [],
            })

            # 10 previous emails
            previous_emails = [f"Email {i}: Content..." for i in range(10)]

            result = await agent.execute(
                context="Reply to thread",
                purpose="Respond",
                previous_emails=previous_emails,
            )

            # Check that previous emails were included - service uses kwargs
            system_prompt = mock_call.call_args.kwargs.get("system_prompt", "")
            user_prompt = mock_call.call_args.kwargs.get("user_prompt", "")
            combined = system_prompt + user_prompt
            # At least some of the recent emails should be in the prompt
            assert "Email" in combined or "previous" in combined.lower()


# =============================================================================
# PROOFREADING EDGE CASES
# =============================================================================


class TestProofreadingEdgeCases:
    """Tests for proofreading edge cases."""

    @pytest.mark.asyncio
    async def test_proofread_very_long_text(self):
        """Handle very long text."""
        agent = ProofreadingAgent()

        with patch.object(agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "corrected_text": "Long corrected text...",
                "issues_found": [],
                "style_suggestions": [],
                "readability_score": 75,
                "reading_level": "College",
            })

            long_text = "This is a sentence. " * 1000

            result = await agent.execute(text=long_text)

            assert result.word_count == len(long_text.split())

    @pytest.mark.asyncio
    async def test_proofread_only_whitespace(self):
        """Handle whitespace-only text."""
        agent = ProofreadingAgent()

        with patch.object(agent, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                "corrected_text": "",
                "issues_found": [],
                "style_suggestions": [],
                "readability_score": 100,
                "reading_level": "N/A",
            })

            result = await agent.execute(text="   \n\t   ")

            assert result.original_text == "   \n\t   "


# =============================================================================
# MODEL PARAMETER TESTS
# =============================================================================


class TestModelParameters:
    """Tests for model-specific parameter handling."""

    def test_gpt5_model_uses_new_params(self, research_agent):
        """GPT-5 model uses max_completion_tokens."""
        with patch('openai.OpenAI') as mock_class:
            mock_client = Mock()
            mock_class.return_value = mock_client
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "response"
            mock_client.chat.completions.create.return_value = mock_response

            with patch.object(research_agent, '_get_model', return_value='gpt-5'):
                research_agent._client = None
                research_agent._call_llm("system", "user")

            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert "max_completion_tokens" in call_kwargs

    def test_gpt4_model_uses_legacy_params(self, research_agent):
        """GPT-4 model uses legacy max_tokens."""
        with patch('openai.OpenAI') as mock_class:
            mock_client = Mock()
            mock_class.return_value = mock_client
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "response"
            mock_client.chat.completions.create.return_value = mock_response

            with patch.object(research_agent, '_get_model', return_value='gpt-4'):
                research_agent._client = None
                research_agent._call_llm("system", "user")

            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert "max_tokens" in call_kwargs
            assert "temperature" in call_kwargs


# =============================================================================
# RECOVERY TESTS
# =============================================================================


class TestRecoveryScenarios:
    """Tests for error recovery scenarios."""

    @pytest.mark.asyncio
    async def test_service_recovers_after_error(self, agent_service):
        """Service continues working after an error."""
        call_count = 0

        def mock_response(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Temporary error")
            return json.dumps({
                "summary": "Success",
                "sections": [],
                "key_findings": [],
                "recommendations": [],
                "sources": [],
            })

        with patch.object(agent_service._agents[AgentType.RESEARCH], '_call_llm', side_effect=mock_response):
            # First call fails - but agent catches it gracefully
            task1 = await agent_service.run_agent(AgentType.RESEARCH, topic="Topic 1")
            # Agent catches internal errors and returns COMPLETED with error info
            assert task1.status == AgentStatus.COMPLETED
            assert "failed" in task1.result.get("summary", "").lower() or "unable" in task1.result.get("summary", "").lower()

            # Second call succeeds
            task2 = await agent_service.run_agent(AgentType.RESEARCH, topic="Topic 2")
            assert task2.status == AgentStatus.COMPLETED
            # Second result should have actual content, not error
            assert "Success" in task2.result.get("summary", "")

    @pytest.mark.asyncio
    async def test_partial_success_in_repurposing(self):
        """Repurposing continues even if some formats fail."""
        agent = ContentRepurposingAgent()
        call_count = 0

        def mock_response(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise Exception("This format failed")
            return "Successful conversion"

        with patch.object(agent, '_call_llm', side_effect=mock_response):
            result = await agent.execute(
                content="Test",
                source_format="article",
                target_formats=["format1", "format2", "format3"],
            )

            # Should have 3 outputs, one with error
            assert len(result.outputs) == 3
            successful = [o for o in result.outputs if "error" not in o.get("metadata", {})]
            assert len(successful) >= 2
