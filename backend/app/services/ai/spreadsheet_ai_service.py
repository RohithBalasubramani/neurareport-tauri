"""
AI Spreadsheet Service
Provides AI-powered spreadsheet features using the unified LLM client for
natural language to formula conversion, data cleaning, anomaly detection,
and predictions.

Uses the unified LLMClient which provides:
- Circuit breaker for fault tolerance
- Response caching (memory + disk)
- Token usage tracking
- Multi-provider support (OpenAI, Claude, Gemini, DeepSeek, Ollama, Azure)
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.app.services.ai.writing_service import (
    _extract_json,
    InputValidationError,
    LLMResponseError,
    LLMUnavailableError,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Limits
# ---------------------------------------------------------------------------
MAX_DATA_ROWS = 5_000
MAX_FORMULA_LENGTH = 5_000


class FormulaResult(BaseModel):
    """Result of natural language to formula conversion."""
    formula: str = Field(..., description="Excel/spreadsheet formula")
    explanation: str = Field(..., description="Explanation of what the formula does")
    examples: List[str] = Field(default_factory=list, description="Example inputs/outputs")
    alternative_formulas: List[str] = Field(default_factory=list, description="Alternative approaches")


class DataCleaningSuggestion(BaseModel):
    """A single data cleaning suggestion."""
    column: str = Field(..., description="Column name or reference")
    issue: str = Field(..., description="Description of the data quality issue")
    suggestion: str = Field(..., description="Suggested fix")
    severity: str = Field(default="medium", description="Severity: high, medium, low")
    affected_rows: int = Field(default=0, description="Number of affected rows")
    auto_fixable: bool = Field(default=False, description="Can be auto-fixed")


class DataCleaningResult(BaseModel):
    """Result of data cleaning analysis."""
    suggestions: List[DataCleaningSuggestion] = Field(default_factory=list)
    quality_score: float = Field(..., description="Overall data quality score 0-100", ge=0, le=100)
    summary: str = Field(..., description="Summary of data quality issues")


class Anomaly(BaseModel):
    """Detected data anomaly."""
    location: str = Field(..., description="Cell reference or row number")
    value: Any = Field(..., description="The anomalous value")
    expected_range: str = Field(..., description="Expected value range")
    confidence: float = Field(..., description="Confidence that this is an anomaly 0-1", ge=0, le=1)
    explanation: str = Field(..., description="Why this is considered anomalous")
    anomaly_type: str = Field(..., description="Type: outlier, missing, inconsistent, etc.")


class AnomalyDetectionResult(BaseModel):
    """Result of anomaly detection."""
    anomalies: List[Anomaly] = Field(default_factory=list)
    total_rows_analyzed: int = Field(..., description="Number of rows analyzed")
    anomaly_count: int = Field(..., description="Number of anomalies found")
    summary: str = Field(..., description="Summary of findings")


class PredictionColumn(BaseModel):
    """Result of predictive column generation."""
    column_name: str = Field(..., description="Name for the new column")
    predictions: List[Any] = Field(default_factory=list, description="Predicted values")
    confidence_scores: List[float] = Field(default_factory=list, description="Confidence for each prediction")
    methodology: str = Field(..., description="Prediction methodology used")
    accuracy_estimate: float = Field(..., description="Estimated accuracy 0-1", ge=0, le=1)


class FormulaExplanation(BaseModel):
    """Explanation of a formula."""
    formula: str = Field(..., description="The formula being explained")
    summary: str = Field(..., description="Brief summary of what it does")
    step_by_step: List[str] = Field(default_factory=list, description="Step-by-step breakdown")
    components: Dict[str, str] = Field(default_factory=dict, description="Explanation of each component")
    potential_issues: List[str] = Field(default_factory=list, description="Potential issues or edge cases")


class SpreadsheetAIService:
    """
    AI-powered spreadsheet assistance service.
    Uses the unified LLMClient for all LLM interactions.
    """

    def __init__(self):
        self._llm_client = None

    def _get_llm_client(self):
        """Get the unified LLM client (lazy-loaded, singleton)."""
        if self._llm_client is None:
            from backend.app.services.llm.client import get_llm_client
            self._llm_client = get_llm_client()
        return self._llm_client

    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2000,
        description: str = "spreadsheet_ai",
    ) -> str:
        """
        Make an LLM call through the unified client.

        Runs synchronous LLMClient.complete() in a thread pool
        to avoid blocking the async event loop.
        """
        client = self._get_llm_client()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = await asyncio.to_thread(
                client.complete,
                messages=messages,
                description=description,
                max_tokens=max_tokens,
            )
        except RuntimeError as exc:
            if "temporarily unavailable" in str(exc).lower():
                raise LLMUnavailableError(str(exc)) from exc
            raise LLMResponseError(str(exc)) from exc
        except Exception as exc:
            raise LLMResponseError(f"LLM call failed: {exc}") from exc

        content = (
            response.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        if not content:
            raise LLMResponseError("LLM returned empty response")

        return content

    async def natural_language_to_formula(
        self,
        description: str,
        context: Optional[str] = None,
        spreadsheet_type: str = "excel",
    ) -> FormulaResult:
        """
        Convert natural language description to spreadsheet formula.

        Args:
            description: Natural language description of desired calculation
            context: Additional context (column names, data types, etc.)
            spreadsheet_type: Type of spreadsheet (excel, google_sheets, libreoffice)

        Returns:
            FormulaResult with formula and explanation
        """
        if not description.strip():
            raise InputValidationError("Description cannot be empty.")

        context_info = f"\n\nContext about the data:\n{context}" if context else ""

        system_prompt = f"""You are an expert {spreadsheet_type} formula writer.
Convert natural language descriptions into {spreadsheet_type} formulas.
Always provide working, accurate formulas.

Respond ONLY with valid JSON (no markdown fences):
{{
    "formula": "<the formula>",
    "explanation": "<clear explanation of what it does>",
    "examples": ["<example input/output 1>", "<example input/output 2>"],
    "alternative_formulas": ["<alternative approach 1>"]
}}"""

        user_prompt = f"Create a formula for: {description}{context_info}"

        raw = await self._call_llm(
            system_prompt,
            user_prompt,
            description="nl_to_formula",
        )

        try:
            result = _extract_json(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            raise LLMResponseError(f"Formula generation returned invalid JSON: {exc}") from exc

        return FormulaResult(
            formula=result.get("formula", ""),
            explanation=result.get("explanation", ""),
            examples=result.get("examples", []),
            alternative_formulas=result.get("alternative_formulas", []),
        )

    async def analyze_data_quality(
        self,
        data_sample: List[Dict[str, Any]],
        column_info: Optional[Dict[str, str]] = None,
    ) -> DataCleaningResult:
        """
        Analyze data for quality issues and provide cleaning suggestions.
        """
        if not data_sample:
            return DataCleaningResult(
                suggestions=[],
                quality_score=100.0,
                summary="No data provided for analysis",
            )

        if len(data_sample) > MAX_DATA_ROWS:
            raise InputValidationError(
                f"Data sample exceeds maximum of {MAX_DATA_ROWS:,} rows."
            )

        data_preview = json.dumps(data_sample[:20], indent=2, default=str)
        column_context = ""
        if column_info:
            column_context = f"\n\nExpected column types:\n{json.dumps(column_info, indent=2)}"

        system_prompt = """You are a data quality expert. Analyze the data for issues like:
1. Missing values
2. Inconsistent formatting
3. Invalid data types
4. Duplicates
5. Outliers
6. Inconsistent naming/spelling

Respond ONLY with valid JSON (no markdown fences):
{
    "suggestions": [
        {
            "column": "<column name>",
            "issue": "<description of issue>",
            "suggestion": "<how to fix>",
            "severity": "<high|medium|low>",
            "affected_rows": <estimated count>,
            "auto_fixable": <true|false>
        }
    ],
    "quality_score": <0-100>,
    "summary": "<overall summary>"
}"""

        user_prompt = f"Analyze this data for quality issues:\n\n{data_preview}{column_context}"

        raw = await self._call_llm(
            system_prompt,
            user_prompt,
            description="data_quality",
        )

        try:
            result = _extract_json(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            raise LLMResponseError(f"Data quality analysis returned invalid JSON: {exc}") from exc

        suggestions = []
        for s in result.get("suggestions", []):
            try:
                suggestions.append(DataCleaningSuggestion(**s))
            except Exception:
                logger.warning("Skipping malformed data cleaning suggestion: %s", s)

        score = result.get("quality_score", 0)
        score = max(0.0, min(100.0, float(score)))

        return DataCleaningResult(
            suggestions=suggestions,
            quality_score=score,
            summary=result.get("summary", ""),
        )

    async def detect_anomalies(
        self,
        data: List[Dict[str, Any]],
        columns_to_analyze: Optional[List[str]] = None,
        sensitivity: str = "medium",
    ) -> AnomalyDetectionResult:
        """
        Detect anomalies in data.
        """
        if not data:
            return AnomalyDetectionResult(
                anomalies=[],
                total_rows_analyzed=0,
                anomaly_count=0,
                summary="No data provided",
            )

        if len(data) > MAX_DATA_ROWS:
            raise InputValidationError(
                f"Data exceeds maximum of {MAX_DATA_ROWS:,} rows."
            )

        data_preview = json.dumps(data[:50], indent=2, default=str)
        columns_context = ""
        if columns_to_analyze:
            columns_context = f"\n\nFocus on these columns: {', '.join(columns_to_analyze)}"

        sensitivity_desc = {
            "low": "Only flag clear, obvious anomalies",
            "medium": "Flag moderately suspicious values",
            "high": "Flag any potentially unusual values",
        }

        system_prompt = f"""You are a data anomaly detection expert.
Sensitivity level: {sensitivity} - {sensitivity_desc.get(sensitivity, sensitivity_desc['medium'])}

Look for:
1. Statistical outliers
2. Missing or null values in unexpected places
3. Inconsistent patterns
4. Data entry errors
5. Values outside expected ranges

Respond ONLY with valid JSON (no markdown fences):
{{
    "anomalies": [
        {{
            "location": "<cell reference or row number>",
            "value": "<the anomalous value>",
            "expected_range": "<what was expected>",
            "confidence": <0.0-1.0>,
            "explanation": "<why it's anomalous>",
            "anomaly_type": "<outlier|missing|inconsistent|error>"
        }}
    ],
    "total_rows_analyzed": <number>,
    "summary": "<summary of findings>"
}}"""

        user_prompt = f"Detect anomalies in this data:\n\n{data_preview}{columns_context}"

        raw = await self._call_llm(
            system_prompt,
            user_prompt,
            description="anomaly_detection",
        )

        try:
            result = _extract_json(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            raise LLMResponseError(f"Anomaly detection returned invalid JSON: {exc}") from exc

        anomalies = []
        for a in result.get("anomalies", []):
            try:
                anomalies.append(Anomaly(**a))
            except Exception:
                logger.warning("Skipping malformed anomaly: %s", a)

        return AnomalyDetectionResult(
            anomalies=anomalies,
            total_rows_analyzed=result.get("total_rows_analyzed", len(data)),
            anomaly_count=len(anomalies),
            summary=result.get("summary", ""),
        )

    async def generate_predictive_column(
        self,
        data: List[Dict[str, Any]],
        target_description: str,
        based_on_columns: List[str],
    ) -> PredictionColumn:
        """
        Generate predictions for a new column based on existing data.
        """
        if not data:
            raise InputValidationError("Data cannot be empty for predictions.")

        if len(data) > MAX_DATA_ROWS:
            raise InputValidationError(
                f"Data exceeds maximum of {MAX_DATA_ROWS:,} rows."
            )

        if not based_on_columns:
            raise InputValidationError("At least one input column is required.")

        data_preview = json.dumps(data[:30], indent=2, default=str)

        system_prompt = """You are a predictive analytics expert.
Generate predictions based on patterns in the provided data.

Respond ONLY with valid JSON (no markdown fences):
{
    "column_name": "<suggested name for predicted column>",
    "predictions": [<predicted value for each row>],
    "confidence_scores": [<0.0-1.0 confidence for each prediction>],
    "methodology": "<explain the prediction methodology>",
    "accuracy_estimate": <0.0-1.0 estimated accuracy>
}"""

        user_prompt = f"""Generate predictions for: {target_description}
Based on columns: {', '.join(based_on_columns)}

Data sample:
{data_preview}"""

        raw = await self._call_llm(
            system_prompt,
            user_prompt,
            max_tokens=4000,
            description="predictive_column",
        )

        try:
            result = _extract_json(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            raise LLMResponseError(f"Prediction generation returned invalid JSON: {exc}") from exc

        accuracy = result.get("accuracy_estimate", 0)
        accuracy = max(0.0, min(1.0, float(accuracy)))

        return PredictionColumn(
            column_name=result.get("column_name", "Predicted"),
            predictions=result.get("predictions", []),
            confidence_scores=result.get("confidence_scores", []),
            methodology=result.get("methodology", ""),
            accuracy_estimate=accuracy,
        )

    async def explain_formula(
        self,
        formula: str,
        context: Optional[str] = None,
    ) -> FormulaExplanation:
        """
        Explain what a formula does in plain language.
        """
        if not formula.strip():
            raise InputValidationError("Formula cannot be empty.")

        if len(formula) > MAX_FORMULA_LENGTH:
            raise InputValidationError(
                f"Formula exceeds maximum length of {MAX_FORMULA_LENGTH:,} characters."
            )

        context_info = f"\n\nContext: {context}" if context else ""

        system_prompt = """You are a spreadsheet formula expert.
Explain formulas in clear, understandable terms.

Respond ONLY with valid JSON (no markdown fences):
{
    "formula": "<the formula>",
    "summary": "<one-sentence summary>",
    "step_by_step": ["<step 1>", "<step 2>", ...],
    "components": {
        "<component>": "<what it does>"
    },
    "potential_issues": ["<potential issue or edge case 1>", ...]
}"""

        user_prompt = f"Explain this formula: {formula}{context_info}"

        raw = await self._call_llm(
            system_prompt,
            user_prompt,
            description="explain_formula",
        )

        try:
            result = _extract_json(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            raise LLMResponseError(f"Formula explanation returned invalid JSON: {exc}") from exc

        return FormulaExplanation(
            formula=formula,
            summary=result.get("summary", ""),
            step_by_step=result.get("step_by_step", []),
            components=result.get("components", {}),
            potential_issues=result.get("potential_issues", []),
        )

    async def suggest_formulas(
        self,
        data_sample: List[Dict[str, Any]],
        analysis_goals: Optional[str] = None,
    ) -> List[FormulaResult]:
        """
        Suggest useful formulas based on data structure.
        """
        if not data_sample:
            return []

        if len(data_sample) > MAX_DATA_ROWS:
            raise InputValidationError(
                f"Data sample exceeds maximum of {MAX_DATA_ROWS:,} rows."
            )

        data_preview = json.dumps(data_sample[:10], indent=2, default=str)
        goals_context = f"\n\nAnalysis goals: {analysis_goals}" if analysis_goals else ""

        system_prompt = """You are a spreadsheet analytics expert.
Suggest useful formulas based on the data structure.

Respond ONLY with valid JSON (no markdown fences):
{
    "suggestions": [
        {
            "formula": "<formula>",
            "explanation": "<what it calculates>",
            "examples": ["<example>"],
            "alternative_formulas": []
        }
    ]
}"""

        user_prompt = f"Suggest useful formulas for this data:\n\n{data_preview}{goals_context}"

        raw = await self._call_llm(
            system_prompt,
            user_prompt,
            description="suggest_formulas",
        )

        try:
            result = _extract_json(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            raise LLMResponseError(f"Formula suggestion returned invalid JSON: {exc}") from exc

        suggestions = []
        for s in result.get("suggestions", []):
            try:
                suggestions.append(FormulaResult(**s))
            except Exception:
                logger.warning("Skipping malformed formula suggestion: %s", s)

        return suggestions


# Singleton instance
spreadsheet_ai_service = SpreadsheetAIService()
