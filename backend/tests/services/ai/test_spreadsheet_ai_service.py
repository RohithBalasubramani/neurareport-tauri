"""
Spreadsheet AI Service Tests
Comprehensive tests for SpreadsheetAIService with unified LLMClient.
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
    DataCleaningSuggestion,
    AnomalyDetectionResult,
    Anomaly,
    PredictionColumn,
    FormulaExplanation,
)
from backend.app.services.ai.writing_service import (
    InputValidationError,
    LLMResponseError,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def service():
    """Create SpreadsheetAIService instance."""
    return SpreadsheetAIService()


# =============================================================================
# INITIALIZATION TESTS
# =============================================================================


class TestSpreadsheetAIServiceInit:
    """Tests for SpreadsheetAIService initialization."""

    def test_service_creates_successfully(self):
        """Service instantiates without error."""
        service = SpreadsheetAIService()
        assert service is not None

    def test_client_not_initialized_immediately(self, service):
        """Client is lazy-loaded."""
        assert service._llm_client is None


# =============================================================================
# FORMULA CONVERSION TESTS
# =============================================================================


class TestNaturalLanguageToFormula:
    """Tests for natural_language_to_formula method."""

    @pytest.mark.asyncio
    async def test_formula_conversion_success(self, service):
        """Successful formula conversion."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "formula": "=SUM(A1:A10)",
                "explanation": "Sums values in cells A1 through A10",
                "examples": ["Input: 1,2,3 -> Output: 6"],
                "alternative_formulas": ["=A1+A2+A3+..."],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.natural_language_to_formula(
                "Sum all values in column A"
            )

            assert isinstance(result, FormulaResult)
            assert result.formula == "=SUM(A1:A10)"

    @pytest.mark.asyncio
    async def test_formula_with_context(self, service):
        """Formula conversion with data context."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "formula": "=AVERAGE(B:B)",
                "explanation": "Calculates average",
                "examples": [],
                "alternative_formulas": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call) as mock_llm:
            await service.natural_language_to_formula(
                "Calculate the average",
                context="Column B contains prices"
            )

            call_args = mock_llm.call_args[0]
            assert "prices" in call_args[1].lower()

    @pytest.mark.asyncio
    async def test_formula_google_sheets_type(self, service):
        """Formula for Google Sheets."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "formula": "=ARRAYFORMULA(A:A*B:B)",
                "explanation": "Array formula for Google Sheets",
                "examples": [],
                "alternative_formulas": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call) as mock_llm:
            await service.natural_language_to_formula(
                "Multiply columns",
                spreadsheet_type="google_sheets"
            )

            call_args = mock_llm.call_args[0]
            assert "google_sheets" in call_args[0].lower()

    @pytest.mark.asyncio
    async def test_formula_json_error_raises(self, service):
        """Formula raises LLMResponseError on invalid JSON."""
        async def mock_call(*args, **kwargs):
            return "=SUM(A:A)"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError, match="invalid JSON"):
                await service.natural_language_to_formula("Sum column A")


# =============================================================================
# DATA QUALITY TESTS
# =============================================================================


class TestAnalyzeDataQuality:
    """Tests for analyze_data_quality method."""

    @pytest.mark.asyncio
    async def test_data_quality_success(self, service):
        """Successful data quality analysis."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "suggestions": [
                    {
                        "column": "email",
                        "issue": "Invalid email format",
                        "suggestion": "Fix email addresses",
                        "severity": "high",
                        "affected_rows": 5,
                        "auto_fixable": False,
                    }
                ],
                "quality_score": 75.0,
                "summary": "Found 1 data quality issue",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.analyze_data_quality([
                {"email": "invalid"},
                {"email": "test@example.com"},
            ])

            assert isinstance(result, DataCleaningResult)
            assert len(result.suggestions) == 1
            assert result.quality_score == 75.0

    @pytest.mark.asyncio
    async def test_data_quality_empty_data(self, service):
        """Data quality with empty data."""
        result = await service.analyze_data_quality([])

        assert result.quality_score == 100.0
        assert "no data" in result.summary.lower()

    @pytest.mark.asyncio
    async def test_data_quality_with_column_info(self, service):
        """Data quality with column type info."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "suggestions": [],
                "quality_score": 100.0,
                "summary": "No issues found",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call) as mock_llm:
            await service.analyze_data_quality(
                [{"age": 25}],
                column_info={"age": "integer"}
            )

            call_args = mock_llm.call_args[0]
            assert "integer" in call_args[1]

    @pytest.mark.asyncio
    async def test_data_quality_json_error(self, service):
        """Data quality raises LLMResponseError on invalid JSON."""
        async def mock_call(*args, **kwargs):
            return "Invalid JSON"

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError, match="invalid JSON"):
                await service.analyze_data_quality([{"a": 1}])


# =============================================================================
# ANOMALY DETECTION TESTS
# =============================================================================


class TestDetectAnomalies:
    """Tests for detect_anomalies method."""

    @pytest.mark.asyncio
    async def test_anomaly_detection_success(self, service):
        """Successful anomaly detection."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "anomalies": [
                    {
                        "location": "Row 5",
                        "value": 99999,
                        "expected_range": "0-100",
                        "confidence": 0.95,
                        "explanation": "Value far exceeds normal range",
                        "anomaly_type": "outlier",
                    }
                ],
                "total_rows_analyzed": 10,
                "summary": "Found 1 anomaly",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.detect_anomalies([
                {"value": 50},
                {"value": 99999},
            ])

            assert isinstance(result, AnomalyDetectionResult)
            assert result.anomaly_count == 1

    @pytest.mark.asyncio
    async def test_anomaly_detection_empty_data(self, service):
        """Anomaly detection with empty data."""
        result = await service.detect_anomalies([])

        assert result.total_rows_analyzed == 0
        assert result.anomaly_count == 0

    @pytest.mark.asyncio
    async def test_anomaly_detection_specific_columns(self, service):
        """Anomaly detection on specific columns."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "anomalies": [],
                "total_rows_analyzed": 5,
                "summary": "No anomalies",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call) as mock_llm:
            await service.detect_anomalies(
                [{"a": 1, "b": 2}],
                columns_to_analyze=["a"]
            )

            call_args = mock_llm.call_args[0]
            assert "a" in call_args[1]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("sensitivity", ["low", "medium", "high"])
    async def test_anomaly_detection_sensitivity_levels(self, service, sensitivity):
        """Anomaly detection with different sensitivity levels."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "anomalies": [],
                "total_rows_analyzed": 5,
                "summary": f"Analysis with {sensitivity} sensitivity",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call) as mock_llm:
            await service.detect_anomalies([{"x": 1}], sensitivity=sensitivity)

            call_args = mock_llm.call_args[0]
            assert sensitivity in call_args[0].lower()


# =============================================================================
# PREDICTION TESTS
# =============================================================================


class TestGeneratePredictiveColumn:
    """Tests for generate_predictive_column method."""

    @pytest.mark.asyncio
    async def test_prediction_success(self, service):
        """Successful prediction generation."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "column_name": "Predicted_Sales",
                "predictions": [100, 120, 140],
                "confidence_scores": [0.9, 0.85, 0.8],
                "methodology": "Linear regression",
                "accuracy_estimate": 0.85,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.generate_predictive_column(
                [{"month": 1}, {"month": 2}, {"month": 3}],
                "Predict sales",
                ["month"]
            )

            assert isinstance(result, PredictionColumn)
            assert len(result.predictions) == 3

    @pytest.mark.asyncio
    async def test_prediction_empty_data(self, service):
        """Prediction with empty data raises InputValidationError."""
        with pytest.raises(InputValidationError, match="cannot be empty"):
            await service.generate_predictive_column(
                [],
                "Predict",
                ["col"]
            )


# =============================================================================
# FORMULA EXPLANATION TESTS
# =============================================================================


class TestExplainFormula:
    """Tests for explain_formula method."""

    @pytest.mark.asyncio
    async def test_explain_formula_success(self, service):
        """Successful formula explanation."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "formula": "=VLOOKUP(A1,B:C,2,FALSE)",
                "summary": "Looks up a value in first column and returns corresponding value",
                "step_by_step": [
                    "1. Find A1 in column B",
                    "2. Return value from column C",
                ],
                "components": {
                    "A1": "Lookup value",
                    "B:C": "Table range",
                },
                "potential_issues": ["Exact match required"],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.explain_formula("=VLOOKUP(A1,B:C,2,FALSE)")

            assert isinstance(result, FormulaExplanation)
            assert len(result.step_by_step) > 0

    @pytest.mark.asyncio
    async def test_explain_formula_with_context(self, service):
        """Formula explanation with context."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "formula": "=SUM(A:A)",
                "summary": "Sums sales values",
                "step_by_step": [],
                "components": {},
                "potential_issues": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call) as mock_llm:
            await service.explain_formula(
                "=SUM(A:A)",
                context="Column A contains sales"
            )

            call_args = mock_llm.call_args[0]
            assert "sales" in call_args[1].lower()


# =============================================================================
# FORMULA SUGGESTION TESTS
# =============================================================================


class TestSuggestFormulas:
    """Tests for suggest_formulas method."""

    @pytest.mark.asyncio
    async def test_suggest_formulas_success(self, service):
        """Successful formula suggestions."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "suggestions": [
                    {
                        "formula": "=SUM(B:B)",
                        "explanation": "Calculate total",
                        "examples": [],
                        "alternative_formulas": [],
                    },
                    {
                        "formula": "=AVERAGE(B:B)",
                        "explanation": "Calculate average",
                        "examples": [],
                        "alternative_formulas": [],
                    },
                ]
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.suggest_formulas([
                {"name": "A", "amount": 100},
                {"name": "B", "amount": 200},
            ])

            assert len(result) == 2
            assert all(isinstance(r, FormulaResult) for r in result)

    @pytest.mark.asyncio
    async def test_suggest_formulas_empty_data(self, service):
        """Suggest formulas with empty data."""
        result = await service.suggest_formulas([])

        assert result == []

    @pytest.mark.asyncio
    async def test_suggest_formulas_with_goals(self, service):
        """Suggest formulas with analysis goals."""
        async def mock_call(*args, **kwargs):
            return json.dumps({"suggestions": []})

        with patch.object(service, '_call_llm', side_effect=mock_call) as mock_llm:
            await service.suggest_formulas(
                [{"x": 1}],
                analysis_goals="Find trends"
            )

            call_args = mock_llm.call_args[0]
            assert "trends" in call_args[1].lower()


# =============================================================================
# MODEL TESTS
# =============================================================================


class TestSpreadsheetModels:
    """Tests for spreadsheet AI data models."""

    def test_formula_result_model(self):
        """FormulaResult model validation."""
        result = FormulaResult(
            formula="=SUM(A:A)",
            explanation="Sums column A",
            examples=["1+2=3"],
            alternative_formulas=["=A1+A2+A3"],
        )
        assert result.formula == "=SUM(A:A)"

    def test_data_cleaning_suggestion_model(self):
        """DataCleaningSuggestion model validation."""
        suggestion = DataCleaningSuggestion(
            column="email",
            issue="Invalid format",
            suggestion="Fix emails",
            severity="high",
            affected_rows=10,
            auto_fixable=True,
        )
        assert suggestion.severity == "high"

    def test_anomaly_model(self):
        """Anomaly model validation."""
        anomaly = Anomaly(
            location="A5",
            value=9999,
            expected_range="0-100",
            confidence=0.95,
            explanation="Outlier",
            anomaly_type="outlier",
        )
        assert anomaly.confidence == 0.95

    def test_prediction_column_model(self):
        """PredictionColumn model validation."""
        prediction = PredictionColumn(
            column_name="Predicted",
            predictions=[1, 2, 3],
            confidence_scores=[0.9, 0.85, 0.8],
            methodology="ML",
            accuracy_estimate=0.85,
        )
        assert len(prediction.predictions) == 3

    def test_formula_explanation_model(self):
        """FormulaExplanation model validation."""
        explanation = FormulaExplanation(
            formula="=SUM(A:A)",
            summary="Sums values",
            step_by_step=["Step 1", "Step 2"],
            components={"A:A": "Range"},
            potential_issues=["Issue 1"],
        )
        assert len(explanation.step_by_step) == 2


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


class TestSpreadsheetErrorHandling:
    """Error handling tests for SpreadsheetAIService."""

    @pytest.mark.asyncio
    async def test_formula_api_error(self, service):
        """Formula raises LLMResponseError on API error."""
        async def mock_call(*args, **kwargs):
            raise LLMResponseError("API Error")

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError):
                await service.natural_language_to_formula("Sum")

    @pytest.mark.asyncio
    async def test_data_quality_api_error(self, service):
        """Data quality raises LLMResponseError on API error."""
        async def mock_call(*args, **kwargs):
            raise LLMResponseError("API Error")

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError):
                await service.analyze_data_quality([{"a": 1}])

    def test_llm_client_initialization(self, service):
        """Verify LLM client is obtained through get_llm_client."""
        fresh_service = SpreadsheetAIService()
        fresh_service._llm_client = None

        with patch('backend.app.services.llm.client.get_llm_client') as mock_get:
            mock_get.return_value = Mock()
            client = fresh_service._get_llm_client()
            assert client is not None
            mock_get.assert_called_once()


# =============================================================================
# SINGLETON TESTS
# =============================================================================


class TestSpreadsheetSingleton:
    """Tests for module-level singleton."""

    def test_singleton_exists(self):
        """Singleton instance exists."""
        from backend.app.services.ai.spreadsheet_ai_service import spreadsheet_ai_service

        assert spreadsheet_ai_service is not None
        assert isinstance(spreadsheet_ai_service, SpreadsheetAIService)
