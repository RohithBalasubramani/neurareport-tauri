"""
Spreadsheet AI Service Error Injection Tests
Tests for error handling, edge cases, and failure scenarios.
Updated for unified LLMClient architecture.
"""
import json
import pytest
from unittest.mock import Mock, patch

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
    InputValidationError,
    LLMResponseError,
    LLMUnavailableError,
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
# CLIENT INITIALIZATION ERRORS
# =============================================================================


class TestClientInitializationErrors:
    """Tests for LLM client initialization failures."""

    def test_client_creation_success(self, service):
        """Client creates successfully when LLM module is available."""
        fresh_service = SpreadsheetAIService()
        fresh_service._llm_client = None

        with patch('backend.app.services.llm.client.get_llm_client') as mock_get:
            mock_get.return_value = Mock()
            client = fresh_service._get_llm_client()
            assert client is not None

    def test_invalid_api_key(self, service):
        """Handle invalid API key error."""
        service._llm_client = None

        with patch('backend.app.services.llm.client.get_llm_client') as mock_get:
            mock_get.side_effect = Exception("Invalid API key")

            with pytest.raises(Exception, match="Invalid API key"):
                service._get_llm_client()

    def test_network_error_on_init(self, service):
        """Handle network error during initialization."""
        service._llm_client = None

        with patch('backend.app.services.llm.client.get_llm_client') as mock_get:
            mock_get.side_effect = ConnectionError("Network unreachable")

            with pytest.raises(ConnectionError):
                service._get_llm_client()


# =============================================================================
# API CALL ERRORS
# =============================================================================


class TestAPICallErrors:
    """Tests for LLM call failures."""

    @pytest.mark.asyncio
    async def test_api_rate_limit_error(self, service):
        """Handle rate limit error through LLM client."""
        mock_client = Mock()
        mock_client.complete.side_effect = RuntimeError("Rate limit exceeded")
        service._llm_client = mock_client

        with pytest.raises(LLMResponseError):
            await service.natural_language_to_formula("Sum column A")

    @pytest.mark.asyncio
    async def test_api_timeout_error(self, service):
        """Handle timeout error."""
        mock_client = Mock()
        mock_client.complete.side_effect = TimeoutError("Request timed out")
        service._llm_client = mock_client

        with pytest.raises(LLMResponseError, match="LLM call failed"):
            await service.natural_language_to_formula("Sum column A")

    @pytest.mark.asyncio
    async def test_api_server_error(self, service):
        """Handle server error (500)."""
        mock_client = Mock()
        mock_client.complete.side_effect = RuntimeError("Internal server error")
        service._llm_client = mock_client

        with pytest.raises(LLMResponseError):
            await service.natural_language_to_formula("Sum column A")


# =============================================================================
# JSON PARSING ERRORS
# =============================================================================


class TestJSONParsingErrors:
    """Tests for JSON parsing failures.

    In the new architecture, invalid JSON raises LLMResponseError
    instead of silently falling back to defaults.
    """

    @pytest.mark.asyncio
    async def test_formula_invalid_json(self, service):
        """Formula conversion raises LLMResponseError on invalid JSON."""
        async def mock_call(*args, **kwargs):
            return "This is not JSON {invalid"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError, match="invalid JSON"):
                await service.natural_language_to_formula("Sum column A")

    @pytest.mark.asyncio
    async def test_data_quality_invalid_json(self, service):
        """Data quality analysis raises LLMResponseError on invalid JSON."""
        async def mock_call(*args, **kwargs):
            return "Invalid JSON"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError, match="invalid JSON"):
                await service.analyze_data_quality([{"a": 1}])

    @pytest.mark.asyncio
    async def test_anomaly_invalid_json(self, service):
        """Anomaly detection raises LLMResponseError on invalid JSON."""
        async def mock_call(*args, **kwargs):
            return "Not valid JSON"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError, match="invalid JSON"):
                await service.detect_anomalies([{"value": 100}])

    @pytest.mark.asyncio
    async def test_prediction_invalid_json(self, service):
        """Prediction raises LLMResponseError on invalid JSON."""
        async def mock_call(*args, **kwargs):
            return "Invalid"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError, match="invalid JSON"):
                await service.generate_predictive_column(
                    [{"x": 1}], "Predict", ["x"]
                )

    @pytest.mark.asyncio
    async def test_explanation_invalid_json(self, service):
        """Formula explanation raises LLMResponseError on invalid JSON."""
        async def mock_call(*args, **kwargs):
            return "Bad JSON"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError, match="invalid JSON"):
                await service.explain_formula("=SUM(A:A)")

    @pytest.mark.asyncio
    async def test_suggestions_invalid_json(self, service):
        """Formula suggestions raises LLMResponseError on invalid JSON."""
        async def mock_call(*args, **kwargs):
            return "Not JSON"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError, match="invalid JSON"):
                await service.suggest_formulas([{"a": 1}])


# =============================================================================
# MALFORMED RESPONSE TESTS
# =============================================================================


class TestMalformedResponses:
    """Tests for malformed API responses."""

    @pytest.mark.asyncio
    async def test_formula_null_response(self, service):
        """Formula raises LLMResponseError on JSON null response."""
        async def mock_call(*args, **kwargs):
            return "null"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            # "null" parses to None → _extract_json raises ValueError (not a dict)
            with pytest.raises(LLMResponseError, match="invalid JSON"):
                await service.natural_language_to_formula("Sum")

    @pytest.mark.asyncio
    async def test_formula_empty_object(self, service):
        """Formula handles empty object response."""
        async def mock_call(*args, **kwargs):
            return "{}"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.natural_language_to_formula("Sum")

            assert result.formula == ""
            assert result.examples == []

    @pytest.mark.asyncio
    async def test_data_quality_missing_fields(self, service):
        """Data quality handles response with missing fields."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "quality_score": 75.0,
                # Missing suggestions and summary
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.analyze_data_quality([{"a": 1}])

            assert result.quality_score == 75.0
            assert result.suggestions == []

    @pytest.mark.asyncio
    async def test_anomaly_wrong_types(self, service):
        """Anomaly detection handles wrong types in response."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "anomalies": "not an array",  # Should be array
                "total_rows_analyzed": "five",  # Should be int
                "summary": 123,  # Should be string
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            # String "not an array" is iterable — each char fails Anomaly(**char)
            # and is skipped, but total_rows_analyzed="five" causes ValidationError
            with pytest.raises(Exception):
                await service.detect_anomalies([{"value": 100}])


# =============================================================================
# EMPTY DATA TESTS
# =============================================================================


class TestEmptyDataHandling:
    """Tests for handling empty data."""

    @pytest.mark.asyncio
    async def test_data_quality_empty_list(self, service):
        """Data quality handles empty data list."""
        result = await service.analyze_data_quality([])

        assert result.quality_score == 100.0
        assert "no data" in result.summary.lower()

    @pytest.mark.asyncio
    async def test_anomaly_empty_list(self, service):
        """Anomaly detection handles empty data list."""
        result = await service.detect_anomalies([])

        assert result.total_rows_analyzed == 0
        assert result.anomaly_count == 0

    @pytest.mark.asyncio
    async def test_prediction_empty_list(self, service):
        """Prediction with empty data raises InputValidationError."""
        with pytest.raises(InputValidationError, match="cannot be empty"):
            await service.generate_predictive_column([], "Predict", ["x"])

    @pytest.mark.asyncio
    async def test_suggestions_empty_list(self, service):
        """Formula suggestions handles empty data list."""
        result = await service.suggest_formulas([])

        assert result == []


# =============================================================================
# CONTENT EDGE CASES
# =============================================================================


class TestContentEdgeCases:
    """Tests for content edge cases."""

    @pytest.mark.asyncio
    async def test_very_long_description(self, service):
        """Handle very long description input."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "formula": "=SUM(A:A)",
                "explanation": "Sum",
                "examples": [],
                "alternative_formulas": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            long_description = "Sum all values " * 1000
            result = await service.natural_language_to_formula(long_description)

            assert isinstance(result, FormulaResult)

    @pytest.mark.asyncio
    async def test_special_characters_in_formula(self, service):
        """Handle special characters in formula."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "formula": '=IF(A1="test",B1,C1)',
                "summary": "Conditional",
                "step_by_step": [],
                "components": {},
                "potential_issues": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.explain_formula('=IF(A1="special<>chars",B1,C1)')

            assert isinstance(result, FormulaExplanation)

    @pytest.mark.asyncio
    async def test_unicode_in_data(self, service):
        """Handle unicode characters in data."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "suggestions": [],
                "quality_score": 100.0,
                "summary": "No issues",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            unicode_data = [
                {"名前": "田中太郎", "年齢": 30},
                {"名前": "鈴木花子", "年齢": 25},
            ]
            result = await service.analyze_data_quality(unicode_data)

            assert isinstance(result, DataCleaningResult)

    @pytest.mark.asyncio
    async def test_null_values_in_data(self, service):
        """Handle null values in data."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "anomalies": [],
                "total_rows_analyzed": 3,
                "summary": "No anomalies",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            data_with_nulls = [
                {"a": None, "b": 1},
                {"a": 2, "b": None},
                {"a": None, "b": None},
            ]
            result = await service.detect_anomalies(data_with_nulls)

            assert isinstance(result, AnomalyDetectionResult)

    @pytest.mark.asyncio
    async def test_mixed_types_in_data(self, service):
        """Handle mixed types in data."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "suggestions": [],
                "quality_score": 80.0,
                "summary": "Mixed types detected",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            mixed_data = [
                {"value": 100},
                {"value": "hundred"},
                {"value": 100.5},
                {"value": True},
            ]
            result = await service.analyze_data_quality(mixed_data)

            assert isinstance(result, DataCleaningResult)


# =============================================================================
# CONCURRENT ERROR SCENARIOS
# =============================================================================


class TestConcurrentErrors:
    """Tests for concurrent operation error handling."""

    @pytest.mark.asyncio
    async def test_client_error_during_call(self, service):
        """Handle client error during API call."""
        call_count = 0

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise LLMResponseError("Client error")
            return json.dumps({
                "formula": "=SUM(A:A)",
                "explanation": "Sum",
                "examples": [],
                "alternative_formulas": [],
            })

        with patch.object(service, '_call_llm', side_effect=side_effect):
            result1 = await service.natural_language_to_formula("Sum 1")
            assert isinstance(result1, FormulaResult)

            with pytest.raises(LLMResponseError):
                await service.natural_language_to_formula("Sum 2")

    @pytest.mark.asyncio
    async def test_recovery_after_error(self, service):
        """Service recovers after error."""
        call_count = 0

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise LLMResponseError("Temporary error")
            return json.dumps({
                "formula": "=SUM(A:A)",
                "explanation": "Sum",
                "examples": [],
                "alternative_formulas": [],
            })

        with patch.object(service, '_call_llm', side_effect=side_effect):
            # First call fails
            with pytest.raises(LLMResponseError):
                await service.natural_language_to_formula("Sum")

            # Second call succeeds
            result = await service.natural_language_to_formula("Sum")
            assert isinstance(result, FormulaResult)


# =============================================================================
# MODEL-SPECIFIC BEHAVIOR
# =============================================================================


class TestModelSpecificErrors:
    """Tests for model-specific behavior via LLM client.

    Model parameter selection is handled by the unified LLMClient internally.
    We test that the service passes parameters correctly to the client.
    """

    @pytest.mark.asyncio
    async def test_service_passes_max_tokens(self, service):
        """Service passes max_tokens to LLM client."""
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

        await service.natural_language_to_formula("Sum column A")
        call_kwargs = mock_client.complete.call_args[1]
        assert "max_tokens" in call_kwargs

    @pytest.mark.asyncio
    async def test_service_passes_description(self, service):
        """Service passes description to LLM client for tracking."""
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

        await service.natural_language_to_formula("Sum column A")
        call_kwargs = mock_client.complete.call_args[1]
        assert "description" in call_kwargs
        assert call_kwargs["description"] == "nl_to_formula"

    @pytest.mark.asyncio
    async def test_service_passes_messages_format(self, service):
        """Service passes messages in correct format."""
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

        await service.natural_language_to_formula("Sum column A")
        call_kwargs = mock_client.complete.call_args[1]
        messages = call_kwargs["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"


# =============================================================================
# NETWORK EDGE CASES
# =============================================================================


class TestNetworkEdgeCases:
    """Tests for network-related edge cases via LLM client."""

    @pytest.mark.asyncio
    async def test_connection_reset(self, service):
        """Handle connection reset via LLM client."""
        mock_client = Mock()
        mock_client.complete.side_effect = ConnectionResetError()
        service._llm_client = mock_client

        with pytest.raises(LLMResponseError, match="LLM call failed"):
            await service.natural_language_to_formula("Sum column A")

    @pytest.mark.asyncio
    async def test_broken_pipe(self, service):
        """Handle broken pipe error via LLM client."""
        mock_client = Mock()
        mock_client.complete.side_effect = BrokenPipeError()
        service._llm_client = mock_client

        with pytest.raises(LLMResponseError, match="LLM call failed"):
            await service.natural_language_to_formula("Sum column A")

    def test_dns_resolution_failure(self, service):
        """Handle DNS resolution failure."""
        service._llm_client = None

        with patch('backend.app.services.llm.client.get_llm_client') as mock_get:
            mock_get.side_effect = Exception("getaddrinfo failed")

            with pytest.raises(Exception, match="getaddrinfo"):
                service._get_llm_client()


# =============================================================================
# RESPONSE VALIDATION TESTS
# =============================================================================


class TestResponseValidation:
    """Tests for response structure validation."""

    @pytest.mark.asyncio
    async def test_formula_missing_required_field(self, service):
        """Formula handles missing required 'formula' field."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "explanation": "Missing formula field",
                "examples": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.natural_language_to_formula("Sum")

            # Should use default empty string
            assert result.formula == ""

    @pytest.mark.asyncio
    async def test_data_cleaning_suggestion_validation(self, service):
        """Data cleaning validates suggestion structure."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "suggestions": [
                    {
                        "column": "A",
                        "issue": "Test",
                        "suggestion": "Fix",
                        # Missing optional fields
                    }
                ],
                "quality_score": 90.0,
                "summary": "Found issue",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.analyze_data_quality([{"a": 1}])

            assert len(result.suggestions) == 1
            # Default values should be applied
            assert result.suggestions[0].severity == "medium"

    @pytest.mark.asyncio
    async def test_anomaly_validation(self, service):
        """Anomaly detection validates anomaly structure."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "anomalies": [
                    {
                        "location": "Row 1",
                        "value": 999,
                        "expected_range": "0-100",
                        "confidence": 0.95,
                        "explanation": "Outlier",
                        "anomaly_type": "outlier",
                    }
                ],
                "total_rows_analyzed": 10,
                "summary": "Found anomaly",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.detect_anomalies([{"value": 999}])

            assert result.anomaly_count == 1
            assert result.anomalies[0].confidence == 0.95
