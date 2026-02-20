"""
Spreadsheet AI API Tests
Tests for spreadsheet AI API endpoints focusing on service integration.
Updated for unified LLMClient architecture.
"""
import json
import pytest
from unittest.mock import Mock, patch, AsyncMock

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
    LLMResponseError,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def service():
    """Create SpreadsheetAIService instance."""
    return SpreadsheetAIService()


@pytest.fixture
def sample_data():
    """Sample spreadsheet data for testing."""
    return [
        {"Name": "Alice", "Age": 30, "Salary": 50000, "Department": "Engineering"},
        {"Name": "Bob", "Age": 25, "Salary": 45000, "Department": "Marketing"},
        {"Name": "Carol", "Age": 35, "Salary": 60000, "Department": "Engineering"},
        {"Name": "David", "Age": 28, "Salary": 48000, "Department": "Sales"},
        {"Name": "Eve", "Age": 32, "Salary": 55000, "Department": "Marketing"},
    ]


# =============================================================================
# FORMULA GENERATION INTEGRATION TESTS
# =============================================================================


class TestFormulaGenerationIntegration:
    """Integration tests for formula generation service."""

    @pytest.mark.asyncio
    async def test_formula_generation_with_context(self, service):
        """Formula generation includes context in prompt."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "formula": "=SUM(C:C)",
                "explanation": "Sums all salaries",
                "examples": [],
                "alternative_formulas": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call) as mock_llm:
            result = await service.natural_language_to_formula(
                "Sum all salaries",
                context="Columns: Name, Age, Salary, Department"
            )

            assert result.formula == "=SUM(C:C)"
            # Verify context was passed to the prompt
            call_args = mock_llm.call_args[0]
            assert "Salary" in call_args[1] or "salaries" in call_args[1].lower()

    @pytest.mark.asyncio
    async def test_formula_generation_excel_type(self, service):
        """Formula generation uses Excel syntax by default."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "formula": "=VLOOKUP(A1,B:C,2,FALSE)",
                "explanation": "Lookup formula",
                "examples": [],
                "alternative_formulas": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call) as mock_llm:
            result = await service.natural_language_to_formula(
                "Lookup value from column B",
                spreadsheet_type="excel"
            )

            # Verify Excel is mentioned in prompt
            call_args = mock_llm.call_args[0]
            assert "excel" in call_args[0].lower()

    @pytest.mark.asyncio
    async def test_formula_generation_google_sheets(self, service):
        """Formula generation uses Google Sheets syntax."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "formula": "=ARRAYFORMULA(A:A*B:B)",
                "explanation": "Array formula",
                "examples": [],
                "alternative_formulas": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call) as mock_llm:
            result = await service.natural_language_to_formula(
                "Multiply columns",
                spreadsheet_type="google_sheets"
            )

            # Verify Google Sheets is mentioned
            call_args = mock_llm.call_args[0]
            assert "google_sheets" in call_args[0].lower()


# =============================================================================
# DATA QUALITY ANALYSIS INTEGRATION TESTS
# =============================================================================


class TestDataQualityIntegration:
    """Integration tests for data quality analysis."""

    @pytest.mark.asyncio
    async def test_data_quality_with_issues(self, service, sample_data):
        """Data quality analysis detects issues."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "suggestions": [
                    {
                        "column": "Salary",
                        "issue": "Potential outliers detected",
                        "suggestion": "Review salary values above 55000",
                        "severity": "medium",
                        "affected_rows": 1,
                        "auto_fixable": False,
                    }
                ],
                "quality_score": 85.0,
                "summary": "Found 1 potential data quality issue",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.analyze_data_quality(sample_data)

            assert len(result.suggestions) == 1
            assert result.quality_score == 85.0
            assert result.suggestions[0].column == "Salary"

    @pytest.mark.asyncio
    async def test_data_quality_with_column_info(self, service, sample_data):
        """Data quality uses column type info."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "suggestions": [],
                "quality_score": 100.0,
                "summary": "No issues",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call) as mock_llm:
            await service.analyze_data_quality(
                sample_data,
                column_info={"Age": "integer", "Salary": "currency"}
            )

            # Verify column info was included
            call_args = mock_llm.call_args[0]
            assert "integer" in call_args[1]
            assert "currency" in call_args[1]

    @pytest.mark.asyncio
    async def test_data_quality_perfect_data(self, service, sample_data):
        """Data quality returns 100 for perfect data."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "suggestions": [],
                "quality_score": 100.0,
                "summary": "Data quality is excellent",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.analyze_data_quality(sample_data)

            assert result.quality_score == 100.0
            assert len(result.suggestions) == 0


# =============================================================================
# ANOMALY DETECTION INTEGRATION TESTS
# =============================================================================


class TestAnomalyDetectionIntegration:
    """Integration tests for anomaly detection."""

    @pytest.mark.asyncio
    async def test_anomaly_detection_finds_outliers(self, service, sample_data):
        """Anomaly detection identifies outliers."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "anomalies": [
                    {
                        "location": "Row 3",
                        "value": 60000,
                        "expected_range": "45000-55000",
                        "confidence": 0.8,
                        "explanation": "Salary significantly above mean",
                        "anomaly_type": "outlier",
                    }
                ],
                "total_rows_analyzed": 5,
                "summary": "Found 1 potential outlier",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.detect_anomalies(sample_data)

            assert result.anomaly_count == 1
            assert result.total_rows_analyzed == 5
            assert result.anomalies[0].anomaly_type == "outlier"

    @pytest.mark.asyncio
    async def test_anomaly_detection_column_filter(self, service, sample_data):
        """Anomaly detection focuses on specified columns."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "anomalies": [],
                "total_rows_analyzed": 5,
                "summary": "No anomalies in Age column",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call) as mock_llm:
            await service.detect_anomalies(
                sample_data,
                columns_to_analyze=["Age"]
            )

            # Verify column filter was included
            call_args = mock_llm.call_args[0]
            assert "Age" in call_args[1]

    @pytest.mark.asyncio
    async def test_anomaly_detection_high_sensitivity(self, service, sample_data):
        """High sensitivity detects more anomalies."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "anomalies": [
                    {
                        "location": "Row 2",
                        "value": 25,
                        "expected_range": "28-35",
                        "confidence": 0.6,
                        "explanation": "Age slightly below average",
                        "anomaly_type": "outlier",
                    },
                    {
                        "location": "Row 3",
                        "value": 35,
                        "expected_range": "25-32",
                        "confidence": 0.55,
                        "explanation": "Age slightly above average",
                        "anomaly_type": "outlier",
                    },
                ],
                "total_rows_analyzed": 5,
                "summary": "High sensitivity detected 2 potential anomalies",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call) as mock_llm:
            result = await service.detect_anomalies(
                sample_data,
                sensitivity="high"
            )

            assert result.anomaly_count == 2
            # Verify sensitivity was included
            call_args = mock_llm.call_args[0]
            assert "high" in call_args[0].lower()


# =============================================================================
# PREDICTION GENERATION INTEGRATION TESTS
# =============================================================================


class TestPredictionGenerationIntegration:
    """Integration tests for predictive column generation."""

    @pytest.mark.asyncio
    async def test_prediction_generation(self, service, sample_data):
        """Prediction generation creates valid predictions."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "column_name": "Predicted_Bonus",
                "predictions": [5000, 4500, 6000, 4800, 5500],
                "confidence_scores": [0.9, 0.88, 0.92, 0.87, 0.89],
                "methodology": "Linear regression based on Salary and Age",
                "accuracy_estimate": 0.85,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.generate_predictive_column(
                sample_data,
                "Predict annual bonus",
                ["Salary", "Age"]
            )

            assert result.column_name == "Predicted_Bonus"
            assert len(result.predictions) == 5
            assert result.accuracy_estimate == 0.85

    @pytest.mark.asyncio
    async def test_prediction_with_multiple_columns(self, service, sample_data):
        """Prediction uses multiple source columns."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "column_name": "Performance_Score",
                "predictions": [85, 78, 92, 80, 88],
                "confidence_scores": [0.85, 0.82, 0.9, 0.83, 0.87],
                "methodology": "Multi-variate analysis",
                "accuracy_estimate": 0.8,
            })

        with patch.object(service, '_call_llm', side_effect=mock_call) as mock_llm:
            await service.generate_predictive_column(
                sample_data,
                "Predict performance score",
                ["Salary", "Age", "Department"]
            )

            # Verify all columns were included
            call_args = mock_llm.call_args[0]
            assert "Salary" in call_args[1]
            assert "Age" in call_args[1]


# =============================================================================
# FORMULA EXPLANATION INTEGRATION TESTS
# =============================================================================


class TestFormulaExplanationIntegration:
    """Integration tests for formula explanation."""

    @pytest.mark.asyncio
    async def test_explain_complex_formula(self, service):
        """Explain a complex nested formula."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "formula": "=IF(VLOOKUP(A1,B:C,2,FALSE)>100,\"High\",\"Low\")",
                "summary": "Looks up a value and returns High if over 100, else Low",
                "step_by_step": [
                    "1. VLOOKUP finds A1 in column B",
                    "2. Returns the value from column C",
                    "3. IF checks if that value is greater than 100",
                    "4. Returns 'High' if true, 'Low' if false",
                ],
                "components": {
                    "VLOOKUP": "Searches for A1 in range B:C",
                    "IF": "Conditional check against 100",
                },
                "potential_issues": [
                    "Will return #N/A if A1 not found in column B",
                    "Requires exact match (FALSE parameter)",
                ],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.explain_formula(
                "=IF(VLOOKUP(A1,B:C,2,FALSE)>100,\"High\",\"Low\")"
            )

            assert len(result.step_by_step) == 4
            assert len(result.potential_issues) == 2
            assert "VLOOKUP" in result.components

    @pytest.mark.asyncio
    async def test_explain_with_context(self, service):
        """Formula explanation includes context."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "formula": "=SUM(C:C)",
                "summary": "Sums all values in the Salary column",
                "step_by_step": ["Adds up all salary values"],
                "components": {"C:C": "Salary column"},
                "potential_issues": [],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call) as mock_llm:
            await service.explain_formula(
                "=SUM(C:C)",
                context="Column C contains salaries"
            )

            # Verify context was included
            call_args = mock_llm.call_args[0]
            assert "salaries" in call_args[1].lower()


# =============================================================================
# FORMULA SUGGESTION INTEGRATION TESTS
# =============================================================================


class TestFormulaSuggestionIntegration:
    """Integration tests for formula suggestions."""

    @pytest.mark.asyncio
    async def test_suggest_formulas_for_data(self, service, sample_data):
        """Suggest relevant formulas for data structure."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "suggestions": [
                    {
                        "formula": "=SUM(Salary)",
                        "explanation": "Calculate total salary expenditure",
                        "examples": ["Total: 258000"],
                        "alternative_formulas": ["=SUMPRODUCT(Salary)"],
                    },
                    {
                        "formula": "=AVERAGE(Age)",
                        "explanation": "Calculate average employee age",
                        "examples": ["Average: 30"],
                        "alternative_formulas": [],
                    },
                    {
                        "formula": "=COUNTIF(Department,\"Engineering\")",
                        "explanation": "Count engineers",
                        "examples": ["Count: 2"],
                        "alternative_formulas": [],
                    },
                ]
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.suggest_formulas(sample_data)

            assert len(result) == 3
            assert any("SUM" in r.formula for r in result)
            assert any("AVERAGE" in r.formula for r in result)

    @pytest.mark.asyncio
    async def test_suggest_formulas_with_goals(self, service, sample_data):
        """Suggest formulas aligned with analysis goals."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "suggestions": [
                    {
                        "formula": "=CORREL(Age,Salary)",
                        "explanation": "Calculate correlation between age and salary",
                        "examples": ["Correlation: 0.85"],
                        "alternative_formulas": [],
                    },
                ]
            })

        with patch.object(service, '_call_llm', side_effect=mock_call) as mock_llm:
            await service.suggest_formulas(
                sample_data,
                analysis_goals="Find relationships between variables"
            )

            # Verify goals were included
            call_args = mock_llm.call_args[0]
            assert "relationships" in call_args[1].lower()


# =============================================================================
# ERROR SCENARIO TESTS
# =============================================================================


class TestErrorScenarios:
    """Tests for error handling scenarios."""

    @pytest.mark.asyncio
    async def test_api_error_propagates(self, service):
        """API errors propagate as LLMResponseError."""
        async def mock_call(*args, **kwargs):
            raise LLMResponseError("LLM API Error")

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError, match="LLM"):
                await service.natural_language_to_formula("Sum column A")

    @pytest.mark.asyncio
    async def test_graceful_json_fallback(self, service):
        """Invalid JSON responses raise LLMResponseError."""
        async def mock_call(*args, **kwargs):
            return "=SUM(A:A)"  # Plain text, not JSON

        with patch.object(service, '_call_llm', side_effect=mock_call):
            with pytest.raises(LLMResponseError, match="invalid JSON"):
                await service.natural_language_to_formula("Sum column A")

    @pytest.mark.asyncio
    async def test_empty_data_handled(self, service):
        """Empty data input handled correctly."""
        result = await service.analyze_data_quality([])

        assert result.quality_score == 100.0
        assert "no data" in result.summary.lower()

    @pytest.mark.asyncio
    async def test_missing_fields_handled(self, service):
        """Missing response fields handled with defaults."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "formula": "=SUM(A:A)",
                # Missing other fields
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.natural_language_to_formula("Sum")

            assert result.formula == "=SUM(A:A)"
            assert result.examples == []
            assert result.alternative_formulas == []


# =============================================================================
# VALIDATION TESTS
# =============================================================================


class TestValidation:
    """Tests for input/output validation."""

    @pytest.mark.asyncio
    async def test_formula_result_structure(self, service):
        """FormulaResult has correct structure."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "formula": "=SUM(A:A)",
                "explanation": "Sums column A",
                "examples": ["1+2=3"],
                "alternative_formulas": ["=A1+A2+A3"],
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.natural_language_to_formula("Sum")

            assert isinstance(result, FormulaResult)
            assert isinstance(result.formula, str)
            assert isinstance(result.examples, list)
            assert isinstance(result.alternative_formulas, list)

    @pytest.mark.asyncio
    async def test_data_cleaning_result_structure(self, service, sample_data):
        """DataCleaningResult has correct structure."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "suggestions": [
                    {
                        "column": "A",
                        "issue": "Test",
                        "suggestion": "Fix",
                        "severity": "high",
                        "affected_rows": 1,
                        "auto_fixable": True,
                    }
                ],
                "quality_score": 90.0,
                "summary": "Found issue",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.analyze_data_quality(sample_data)

            assert isinstance(result, DataCleaningResult)
            assert isinstance(result.suggestions, list)
            assert all(isinstance(s, DataCleaningSuggestion) for s in result.suggestions)
            assert isinstance(result.quality_score, float)

    @pytest.mark.asyncio
    async def test_anomaly_result_structure(self, service, sample_data):
        """AnomalyDetectionResult has correct structure."""
        async def mock_call(*args, **kwargs):
            return json.dumps({
                "anomalies": [
                    {
                        "location": "A1",
                        "value": 999,
                        "expected_range": "0-100",
                        "confidence": 0.95,
                        "explanation": "Outlier",
                        "anomaly_type": "outlier",
                    }
                ],
                "total_rows_analyzed": 5,
                "summary": "Found anomaly",
            })

        with patch.object(service, '_call_llm', side_effect=mock_call):
            result = await service.detect_anomalies(sample_data)

            assert isinstance(result, AnomalyDetectionResult)
            assert isinstance(result.anomalies, list)
            assert all(isinstance(a, Anomaly) for a in result.anomalies)
            assert isinstance(result.anomaly_count, int)
