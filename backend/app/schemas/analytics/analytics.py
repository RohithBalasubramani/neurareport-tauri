"""Analytics Schemas.

Pydantic models for analytics services - insights, trends, anomalies, and correlations.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class DataPoint(BaseModel):
    """A single data point with timestamp and value."""
    timestamp: Optional[datetime] = None
    index: Optional[int] = None
    value: float
    label: Optional[str] = None


class DataSeries(BaseModel):
    """A time series or data series."""
    name: str
    values: List[float]
    timestamps: Optional[List[datetime]] = None
    labels: Optional[List[str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Insights


class InsightType(str, Enum):
    """Types of insights that can be generated."""
    SUMMARY = "summary"
    TREND = "trend"
    ANOMALY = "anomaly"
    CORRELATION = "correlation"
    COMPARISON = "comparison"
    DISTRIBUTION = "distribution"
    RANKING = "ranking"
    MILESTONE = "milestone"


class InsightSeverity(str, Enum):
    """Severity/importance of an insight."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Insight(BaseModel):
    """A generated insight."""
    id: str
    type: InsightType
    title: str
    description: str
    severity: InsightSeverity = InsightSeverity.MEDIUM
    confidence: float = Field(ge=0.0, le=1.0)
    related_columns: List[str] = Field(default_factory=list)
    data: Optional[Dict[str, Any]] = None
    visualization_hint: Optional[str] = None  # e.g., "line_chart", "bar_chart"


class InsightsRequest(BaseModel):
    """Request for generating insights."""
    data: List[DataSeries]
    columns: Optional[List[str]] = None
    max_insights: int = Field(default=10, ge=1, le=50)
    insight_types: Optional[List[InsightType]] = None
    time_column: Optional[str] = None
    context: Optional[str] = None  # Business context for better insights


class InsightsResponse(BaseModel):
    """Response containing generated insights."""
    insights: List[Insight]
    summary: str
    data_quality_score: float = Field(ge=0.0, le=1.0)
    processing_time_ms: int


# Trends


class TrendDirection(str, Enum):
    """Direction of a trend."""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"
    VOLATILE = "volatile"


class ForecastMethod(str, Enum):
    """Methods for forecasting."""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    ARIMA = "arima"
    PROPHET = "prophet"
    HOLT_WINTERS = "holt_winters"
    AUTO = "auto"


class TrendResult(BaseModel):
    """Result of trend analysis."""
    direction: TrendDirection
    slope: float
    strength: float = Field(ge=0.0, le=1.0)
    seasonality: Optional[str] = None  # e.g., "daily", "weekly", "monthly"
    change_points: List[int] = Field(default_factory=list)
    description: str


class ForecastPoint(BaseModel):
    """A forecasted point with confidence interval."""
    timestamp: Optional[datetime] = None
    index: int
    predicted: float
    lower_bound: float
    upper_bound: float


class TrendRequest(BaseModel):
    """Request for trend analysis and forecasting."""
    data: DataSeries
    forecast_periods: int = Field(default=10, ge=1, le=365)
    method: ForecastMethod = ForecastMethod.AUTO
    confidence_level: float = Field(default=0.95, ge=0.5, le=0.99)
    detect_seasonality: bool = True
    detect_change_points: bool = True


class TrendResponse(BaseModel):
    """Response containing trend analysis and forecast."""
    trend: TrendResult
    forecast: List[ForecastPoint]
    model_accuracy: float = Field(ge=0.0, le=1.0)
    method_used: ForecastMethod
    processing_time_ms: int


# Anomalies


class AnomalyType(str, Enum):
    """Types of anomalies."""
    POINT = "point"  # Single point anomaly
    CONTEXTUAL = "contextual"  # Anomaly given context
    COLLECTIVE = "collective"  # Pattern anomaly
    TREND = "trend"  # Sudden trend change


class AnomalySeverity(str, Enum):
    """Severity of anomaly."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Anomaly(BaseModel):
    """A detected anomaly."""
    id: str
    type: AnomalyType
    severity: AnomalySeverity
    index: int
    timestamp: Optional[datetime] = None
    value: float
    expected_value: float
    deviation: float  # Standard deviations from expected
    description: str
    possible_causes: List[str] = Field(default_factory=list)


class AnomaliesRequest(BaseModel):
    """Request for anomaly detection."""
    data: DataSeries
    sensitivity: float = Field(default=0.95, ge=0.5, le=0.999)
    min_severity: AnomalySeverity = AnomalySeverity.LOW
    context_window: int = Field(default=10, ge=3, le=100)
    detect_collective: bool = True


class AnomaliesResponse(BaseModel):
    """Response containing detected anomalies."""
    anomalies: List[Anomaly]
    anomaly_rate: float  # Percentage of data points that are anomalies
    baseline_stats: Dict[str, float]  # mean, std, etc.
    processing_time_ms: int


# Correlations


class CorrelationType(str, Enum):
    """Types of correlation."""
    PEARSON = "pearson"
    SPEARMAN = "spearman"
    KENDALL = "kendall"


class CorrelationStrength(str, Enum):
    """Strength of correlation."""
    STRONG_POSITIVE = "strong_positive"
    MODERATE_POSITIVE = "moderate_positive"
    WEAK_POSITIVE = "weak_positive"
    NONE = "none"
    WEAK_NEGATIVE = "weak_negative"
    MODERATE_NEGATIVE = "moderate_negative"
    STRONG_NEGATIVE = "strong_negative"


class CorrelationPair(BaseModel):
    """Correlation between two variables."""
    variable_a: str
    variable_b: str
    correlation: float = Field(ge=-1.0, le=1.0)
    p_value: float
    strength: CorrelationStrength
    significant: bool
    description: str


class CorrelationsRequest(BaseModel):
    """Request for correlation analysis."""
    data: List[DataSeries]
    method: CorrelationType = CorrelationType.PEARSON
    min_correlation: float = Field(default=0.3, ge=0.0, le=1.0)
    significance_level: float = Field(default=0.05, ge=0.01, le=0.1)


class CorrelationsResponse(BaseModel):
    """Response containing correlation analysis."""
    correlations: List[CorrelationPair]
    correlation_matrix: Dict[str, Dict[str, float]]
    strongest_positive: Optional[CorrelationPair] = None
    strongest_negative: Optional[CorrelationPair] = None
    processing_time_ms: int


# What-If Analysis


class WhatIfScenario(BaseModel):
    """A what-if scenario definition."""
    name: str
    variable: str
    change_type: str  # "absolute", "percentage", "value"
    change_value: float


class WhatIfResult(BaseModel):
    """Result of a what-if scenario."""
    scenario_name: str
    original_value: float
    projected_value: float
    change: float
    change_percentage: float
    confidence: float = Field(ge=0.0, le=1.0)
    affected_metrics: Dict[str, float] = Field(default_factory=dict)


class WhatIfRequest(BaseModel):
    """Request for what-if analysis."""
    data: List[DataSeries]
    target_variable: str
    scenarios: List[WhatIfScenario]
    model_type: str = "linear"  # linear, polynomial, neural


class WhatIfResponse(BaseModel):
    """Response containing what-if analysis results."""
    results: List[WhatIfResult]
    baseline: float
    model_r_squared: float
    processing_time_ms: int
