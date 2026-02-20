"""
Spreadsheet AI Service Concurrency Tests
Tests for concurrent request handling and thread safety.
Updated for unified LLMClient architecture.
"""
import json
import asyncio
import pytest
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor

import os

from backend.app.services.ai.spreadsheet_ai_service import (
    SpreadsheetAIService,
    FormulaResult,
    DataCleaningResult,
    AnomalyDetectionResult,
    PredictionColumn,
    FormulaExplanation,
)
from backend.app.services.ai.writing_service import (
    LLMResponseError,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def service():
    """Create SpreadsheetAIService instance."""
    return SpreadsheetAIService()


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
    async def test_multiple_formula_conversions(self, service):
        """Multiple concurrent formula conversions."""
        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return json.dumps({
                "formula": f"=SUM(A{call_count}:A10)",
                "explanation": f"Formula {call_count}",
                "examples": [],
                "alternative_formulas": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.natural_language_to_formula(f"Sum column {i}")
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert all(isinstance(r, FormulaResult) for r in results)
            assert call_count == 5

    @pytest.mark.asyncio
    async def test_multiple_data_quality_analyses(self, service):
        """Multiple concurrent data quality analyses."""
        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return json.dumps({
                "suggestions": [],
                "quality_score": 90.0 + call_count,
                "summary": f"Analysis {call_count}",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.analyze_data_quality([{"col": i}])
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert all(isinstance(r, DataCleaningResult) for r in results)

    @pytest.mark.asyncio
    async def test_multiple_anomaly_detections(self, service):
        """Multiple concurrent anomaly detections."""
        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return json.dumps({
                "anomalies": [],
                "total_rows_analyzed": call_count * 10,
                "summary": f"Analysis {call_count}",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.detect_anomalies([{"value": i}])
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert all(isinstance(r, AnomalyDetectionResult) for r in results)

    @pytest.mark.asyncio
    async def test_multiple_predictions(self, service):
        """Multiple concurrent prediction generations."""
        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return json.dumps({
                "column_name": f"Predicted_{call_count}",
                "predictions": [1, 2, 3],
                "confidence_scores": [0.9, 0.85, 0.8],
                "methodology": f"Method {call_count}",
                "accuracy_estimate": 0.85,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.generate_predictive_column(
                    [{"x": i}],
                    f"Predict {i}",
                    ["x"]
                )
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert all(isinstance(r, PredictionColumn) for r in results)

    @pytest.mark.asyncio
    async def test_multiple_formula_explanations(self, service):
        """Multiple concurrent formula explanations."""
        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return json.dumps({
                "formula": f"=SUM(A{call_count}:A10)",
                "summary": f"Explanation {call_count}",
                "step_by_step": [],
                "components": {},
                "potential_issues": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.explain_formula(f"=SUM(A{i}:A10)")
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert all(isinstance(r, FormulaExplanation) for r in results)


# =============================================================================
# MIXED OPERATION TESTS
# =============================================================================


class TestMixedConcurrentOperations:
    """Tests for mixed concurrent operations."""

    @pytest.mark.asyncio
    async def test_mixed_operations_concurrent(self, service):
        """Different operations run concurrently."""
        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            system_prompt = args[0] if args else ""
            if "formula writer" in system_prompt.lower():
                return json.dumps({
                    "formula": "=SUM(A:A)",
                    "explanation": "Sum",
                    "examples": [],
                    "alternative_formulas": [],
                })
            elif "data quality" in system_prompt.lower():
                return json.dumps({
                    "suggestions": [],
                    "quality_score": 100.0,
                    "summary": "No issues",
                })
            elif "anomaly" in system_prompt.lower():
                return json.dumps({
                    "anomalies": [],
                    "total_rows_analyzed": 10,
                    "summary": "No anomalies",
                })
            elif "predictive" in system_prompt.lower():
                return json.dumps({
                    "column_name": "Predicted",
                    "predictions": [1, 2, 3],
                    "confidence_scores": [0.9],
                    "methodology": "ML",
                    "accuracy_estimate": 0.8,
                })
            elif "explain" in system_prompt.lower():
                return json.dumps({
                    "formula": "=SUM(A:A)",
                    "summary": "Sums values",
                    "step_by_step": [],
                    "components": {},
                    "potential_issues": [],
                })
            else:
                return "{}"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.natural_language_to_formula("Sum column A"),
                service.analyze_data_quality([{"a": 1}]),
                service.detect_anomalies([{"value": 100}]),
                service.generate_predictive_column([{"x": 1}], "Predict", ["x"]),
                service.explain_formula("=SUM(A:A)"),
            ]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert isinstance(results[0], FormulaResult)
            assert isinstance(results[1], DataCleaningResult)
            assert isinstance(results[2], AnomalyDetectionResult)
            assert isinstance(results[3], PredictionColumn)
            assert isinstance(results[4], FormulaExplanation)

    @pytest.mark.asyncio
    async def test_high_concurrency(self, service):
        """High number of concurrent operations."""
        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return json.dumps({
                "formula": f"=SUM(A{call_count}:A10)",
                "explanation": "Sum",
                "examples": [],
                "alternative_formulas": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.natural_language_to_formula(f"Sum {i}")
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
            json.dumps({
                "formula": "=SUM(A:A)",
                "explanation": "Sum",
                "examples": [],
                "alternative_formulas": [],
            })
        )
        service._llm_client = mock_client

        await service.natural_language_to_formula("Sum 1")
        await service.natural_language_to_formula("Sum 2")
        await service.natural_language_to_formula("Sum 3")

        assert mock_client.complete.call_count == 3

    @pytest.mark.asyncio
    async def test_client_reused_across_concurrent_operations(self, service):
        """Same LLM client reused for concurrent operations."""
        mock_client = Mock()
        mock_client.complete.return_value = _make_llm_response(
            json.dumps({
                "formula": "=SUM(A:A)",
                "explanation": "Sum",
                "examples": [],
                "alternative_formulas": [],
            })
        )
        service._llm_client = mock_client

        tasks = [
            service.natural_language_to_formula(f"Sum {i}")
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
                "formula": "=SUM(A:A)",
                "explanation": "Sum",
                "examples": [],
                "alternative_formulas": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.natural_language_to_formula(f"Sum {i}")
                for i in range(5)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 4 successes, 1 failure
            successes = [r for r in results if isinstance(r, FormulaResult)]
            failures = [r for r in results if isinstance(r, Exception)]

            assert len(successes) == 4
            assert len(failures) == 1

    @pytest.mark.asyncio
    async def test_all_operations_fail(self, service):
        """All concurrent operations fail."""
        async def mock_call(*args, **kwargs):
            raise LLMResponseError("Service unavailable")

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.natural_language_to_formula(f"Sum {i}")
                for i in range(5)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            assert all(isinstance(r, Exception) for r in results)


# =============================================================================
# THREAD POOL TESTS
# =============================================================================


class TestThreadPoolExecution:
    """Tests for thread pool execution."""

    def test_multiple_services_in_threads(self):
        """Multiple service instances in thread pool."""
        def run_formula_conversion(description: str):
            service = SpreadsheetAIService()

            async def mock_call(*args, **kwargs):
                return json.dumps({
                    "formula": f"=SUM({description})",
                    "explanation": description,
                    "examples": [],
                    "alternative_formulas": [],
                })

            with patch.object(service, '_call_llm', side_effect=mock_call):
                async def run():
                    return await service.natural_language_to_formula(description)

                return asyncio.run(run())

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(run_formula_conversion, f"column{i}")
                for i in range(5)
            ]
            results = [f.result() for f in futures]

        assert len(results) == 5
        assert all(isinstance(r, FormulaResult) for r in results)


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
                "formula": "=1",
                "explanation": "One",
                "examples": [],
                "alternative_formulas": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.natural_language_to_formula("x")
                for _ in range(100)
            ]
            results = await asyncio.gather(*tasks)

            assert len(results) == 100

    @pytest.mark.asyncio
    async def test_large_data_requests(self, service):
        """Large data in concurrent requests."""
        large_data = [{"col" + str(i): j for i in range(50)} for j in range(100)]

        async def mock_call(*args, **kwargs):
            return json.dumps({
                "suggestions": [],
                "quality_score": 100.0,
                "summary": "Analysis complete",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            tasks = [
                service.analyze_data_quality(large_data)
                for _ in range(5)
            ]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert all(r.quality_score == 100.0 for r in results)


# =============================================================================
# SINGLETON BEHAVIOR TESTS
# =============================================================================


class TestSingletonBehavior:
    """Tests for module-level singleton behavior."""

    def test_singleton_instance_exists(self):
        """Module-level singleton instance exists."""
        from backend.app.services.ai.spreadsheet_ai_service import spreadsheet_ai_service

        assert spreadsheet_ai_service is not None
        assert isinstance(spreadsheet_ai_service, SpreadsheetAIService)

    def test_singleton_reuses_client(self):
        """Singleton reuses client across imports."""
        from backend.app.services.ai.spreadsheet_ai_service import spreadsheet_ai_service

        # Both should be same instance
        from backend.app.services.ai import spreadsheet_ai_service as svc2

        assert spreadsheet_ai_service is svc2
