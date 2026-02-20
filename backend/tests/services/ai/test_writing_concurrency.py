"""
Writing Service Concurrency Tests
Tests for concurrent request handling and thread safety.
Updated for unified LLMClient architecture.
"""
import json
import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from concurrent.futures import ThreadPoolExecutor

import os

from backend.app.services.ai.writing_service import (
    WritingService,
    WritingTone,
    GrammarCheckResult,
    SummarizeResult,
    RewriteResult,
    ExpandResult,
    TranslateResult,
    LLMResponseError,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def service():
    """Create WritingService instance."""
    return WritingService()


def _make_llm_response(content: str) -> dict:
    """Create an OpenAI-compatible response dict."""
    return {
        "choices": [{"message": {"content": content}}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 50},
    }


# =============================================================================
# CONCURRENT ASYNC TESTS
# =============================================================================


class TestConcurrentAsyncOperations:
    """Tests for concurrent async operations."""

    @pytest.mark.asyncio
    async def test_multiple_grammar_checks(self, service):
        """Multiple concurrent grammar checks."""
        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return json.dumps({
                "issues": [],
                "corrected_text": f"text {call_count}",
                "score": 100.0,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.check_grammar(f"text {i}")
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert all(isinstance(r, GrammarCheckResult) for r in results)
            assert call_count == 5

    @pytest.mark.asyncio
    async def test_multiple_summarizations(self, service):
        """Multiple concurrent summarizations."""
        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return json.dumps({
                "summary": f"Summary {call_count}",
                "key_points": [f"Point {call_count}"],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.summarize(f"long text " * 50)
                for _ in range(5)
            ]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert all(isinstance(r, SummarizeResult) for r in results)

    @pytest.mark.asyncio
    async def test_multiple_rewrites(self, service):
        """Multiple concurrent rewrites."""
        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return json.dumps({
                "rewritten_text": f"Rewritten {call_count}",
                "changes_made": ["Change"],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.rewrite(f"text {i}", tone=WritingTone.PROFESSIONAL)
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert all(isinstance(r, RewriteResult) for r in results)

    @pytest.mark.asyncio
    async def test_multiple_expansions(self, service):
        """Multiple concurrent expansions."""
        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return json.dumps({
                "expanded_text": f"Expanded text {call_count} " * 10,
                "sections_added": ["Section"],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.expand(f"short {i}")
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert all(isinstance(r, ExpandResult) for r in results)

    @pytest.mark.asyncio
    async def test_multiple_translations(self, service):
        """Multiple concurrent translations."""
        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return json.dumps({
                "translated_text": f"Traducido {call_count}",
                "source_language": "English",
                "confidence": 0.95,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.translate(f"text {i}", "Spanish")
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert all(isinstance(r, TranslateResult) for r in results)


# =============================================================================
# MIXED OPERATION TESTS
# =============================================================================


class TestMixedConcurrentOperations:
    """Tests for mixed concurrent operations."""

    @pytest.mark.asyncio
    async def test_mixed_operations_concurrent(self, service):
        """Different operations run concurrently."""
        call_count = 0

        async def mock_call(system_prompt, user_prompt, **kwargs):
            nonlocal call_count
            call_count += 1

            if "grammar" in system_prompt.lower():
                return json.dumps({
                    "issues": [], "corrected_text": "text", "score": 100.0,
                })
            elif "summar" in system_prompt.lower():
                return json.dumps({
                    "summary": "Summary", "key_points": [],
                })
            elif "rewrite" in system_prompt.lower():
                return json.dumps({
                    "rewritten_text": "Rewritten", "changes_made": [],
                })
            elif "expand" in system_prompt.lower():
                return json.dumps({
                    "expanded_text": "Expanded", "sections_added": [],
                })
            elif "translat" in system_prompt.lower():
                return json.dumps({
                    "translated_text": "Traducido",
                    "source_language": "English",
                    "confidence": 0.9,
                })
            else:
                return "Generated content"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.check_grammar("text"),
                service.summarize("long text " * 50),
                service.rewrite("text"),
                service.expand("short"),
                service.translate("hello", "Spanish"),
            ]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert isinstance(results[0], GrammarCheckResult)
            assert isinstance(results[1], SummarizeResult)
            assert isinstance(results[2], RewriteResult)
            assert isinstance(results[3], ExpandResult)
            assert isinstance(results[4], TranslateResult)

    @pytest.mark.asyncio
    async def test_high_concurrency(self, service):
        """High number of concurrent operations."""
        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return json.dumps({
                "issues": [], "corrected_text": "text", "score": 100.0,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.check_grammar(f"text {i}")
                for i in range(50)
            ]
            results = await asyncio.gather(*tasks)

            assert len(results) == 50
            assert call_count == 50


# =============================================================================
# CLIENT SHARING TESTS
# =============================================================================


class TestClientSharing:
    """Tests for LLM client sharing across operations."""

    @pytest.mark.asyncio
    async def test_client_reused_across_operations(self, service):
        """Same LLM client reused for all operations."""
        mock_client = Mock()
        mock_client.complete.return_value = _make_llm_response(
            json.dumps({"issues": [], "corrected_text": "text", "score": 100.0})
        )
        service._llm_client = mock_client

        await service.check_grammar("text1")
        await service.check_grammar("text2")
        await service.check_grammar("text3")

        assert mock_client.complete.call_count == 3

    @pytest.mark.asyncio
    async def test_client_reused_across_concurrent_operations(self, service):
        """Same LLM client reused for concurrent operations."""
        mock_client = Mock()
        mock_client.complete.return_value = _make_llm_response(
            json.dumps({"issues": [], "corrected_text": "text", "score": 100.0})
        )
        service._llm_client = mock_client

        tasks = [
            service.check_grammar(f"text {i}")
            for i in range(10)
        ]
        await asyncio.gather(*tasks)

        assert mock_client.complete.call_count == 10


# =============================================================================
# ERROR HANDLING IN CONCURRENT OPERATIONS
# =============================================================================


class TestConcurrentErrorHandling:
    """Tests for error handling in concurrent operations."""

    @pytest.mark.asyncio
    async def test_partial_failure_in_concurrent(self, service):
        """Some operations fail while others succeed."""
        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 3:
                raise LLMResponseError("Simulated failure")
            return json.dumps({
                "issues": [], "corrected_text": "text", "score": 100.0,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.check_grammar(f"text {i}")
                for i in range(5)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            successes = [r for r in results if isinstance(r, GrammarCheckResult)]
            failures = [r for r in results if isinstance(r, Exception)]

            assert len(successes) == 4
            assert len(failures) == 1

    @pytest.mark.asyncio
    async def test_json_errors_dont_affect_others(self, service):
        """JSON parse errors don't affect other operations."""
        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                return "Invalid JSON {"
            return json.dumps({
                "issues": [], "corrected_text": "text", "score": 100.0,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.check_grammar(f"text {i}")
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            successes = [r for r in results if isinstance(r, GrammarCheckResult)]
            failures = [r for r in results if isinstance(r, LLMResponseError)]

            assert len(successes) == 4
            assert len(failures) == 1


# =============================================================================
# RATE LIMITING SIMULATION
# =============================================================================


class TestRateLimitingSimulation:
    """Tests simulating rate limiting scenarios."""

    @pytest.mark.asyncio
    async def test_delayed_responses(self, service):
        """Handle delayed responses gracefully."""
        async def mock_call(*args, **kwargs):
            await asyncio.sleep(0.01)  # Small delay
            return json.dumps({
                "issues": [], "corrected_text": "text", "score": 100.0,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.check_grammar(f"text {i}")
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5


# =============================================================================
# THREAD POOL TESTS
# =============================================================================


class TestThreadPoolExecution:
    """Tests for thread pool execution."""

    def test_multiple_services_in_threads(self):
        """Multiple service instances in thread pool."""
        def run_grammar_check(text: str):
            service = WritingService()

            async def mock_call(*args, **kwargs):
                return json.dumps({
                    "issues": [], "corrected_text": text, "score": 100.0,
                })

            with patch.object(service, '_call_llm', side_effect=mock_call):
                async def run():
                    return await service.check_grammar(text)
                return asyncio.run(run())

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(run_grammar_check, f"text {i}")
                for i in range(5)
            ]
            results = [f.result() for f in futures]

        assert len(results) == 5
        assert all(isinstance(r, GrammarCheckResult) for r in results)

    def test_shared_service_in_threads(self):
        """Shared service instance across threads."""
        service = WritingService()

        # Assign mock directly to avoid patch.object thread-safety issues
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "issues": [], "corrected_text": "text", "score": 100.0,
            })

        service._call_llm = mock_call

        def run_grammar_check(text: str):
            async def run():
                return await service.check_grammar(text)
            return asyncio.run(run())

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(run_grammar_check, f"text {i}")
                for i in range(3)
            ]
            results = [f.result() for f in futures]

        assert len(results) == 3


# =============================================================================
# STRESS TESTS
# =============================================================================


class TestStressScenarios:
    """Stress tests for edge cases."""

    @pytest.mark.asyncio
    async def test_many_small_requests(self, service):
        """Many small requests in parallel."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "issues": [], "corrected_text": "x", "score": 100.0,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [service.check_grammar("x") for _ in range(100)]
            results = await asyncio.gather(*tasks)

            assert len(results) == 100

    @pytest.mark.asyncio
    async def test_few_large_requests(self, service):
        """Few large requests in parallel."""
        large_text = "word " * 10000

        async def mock_call(*args, **kwargs):
            return json.dumps({
                "summary": "Summary of large text",
                "key_points": ["Point 1", "Point 2"],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [service.summarize(large_text) for _ in range(5)]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert all(r.word_count_original == 10000 for r in results)

    @pytest.mark.asyncio
    async def test_mixed_size_requests(self, service):
        """Mixed size requests in parallel."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "issues": [], "corrected_text": "text", "score": 100.0,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            texts = [
                "x",                    # Tiny
                "word " * 10,           # Small
                "word " * 100,          # Medium
                "word " * 1000,         # Large
                "word " * 10000,        # Very large
            ]

            tasks = [service.check_grammar(t) for t in texts]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5


# =============================================================================
# SINGLETON BEHAVIOR TESTS
# =============================================================================


class TestSingletonBehavior:
    """Tests for module-level singleton behavior."""

    def test_singleton_instance_exists(self):
        """Module-level singleton instance exists."""
        from backend.app.services.ai.writing_service import writing_service

        assert writing_service is not None
        assert isinstance(writing_service, WritingService)

    def test_singleton_reuses_client(self):
        """Singleton reuses client across imports."""
        from backend.app.services.ai.writing_service import writing_service
        from backend.app.services.ai import writing_service as ws2

        assert writing_service is ws2
