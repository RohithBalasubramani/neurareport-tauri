# mypy: ignore-errors
"""
Enhanced Analysis Schemas - Comprehensive data models for AI-powered document analysis.

Covers:
- Intelligent Data Extraction (entities, metrics, forms, invoices)
- Analysis Engines (summaries, sentiment, comparisons)
- Visualization specifications
- Export configurations
- Integration settings
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


# =============================================================================
# ENUMS
# =============================================================================

class DocumentType(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    IMAGE = "image"
    WORD = "word"
    TEXT = "text"
    UNKNOWN = "unknown"


class EntityType(str, Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    MONEY = "money"
    PERCENTAGE = "percentage"
    PRODUCT = "product"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    CUSTOM = "custom"


class MetricType(str, Enum):
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    COUNT = "count"
    RATIO = "ratio"
    DURATION = "duration"
    QUANTITY = "quantity"
    SCORE = "score"
    RATE = "rate"


class SummaryMode(str, Enum):
    EXECUTIVE = "executive"
    DATA = "data"
    QUICK = "quick"
    COMPREHENSIVE = "comprehensive"
    ACTION_ITEMS = "action_items"
    RISKS = "risks"
    OPPORTUNITIES = "opportunities"


class SentimentLevel(str, Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    HISTOGRAM = "histogram"
    BOX = "box"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    SANKEY = "sankey"
    FUNNEL = "funnel"
    RADAR = "radar"
    CANDLESTICK = "candlestick"
    BUBBLE = "bubble"
    SUNBURST = "sunburst"
    WATERFALL = "waterfall"
    GAUGE = "gauge"


class ExportFormat(str, Enum):
    EXCEL = "excel"
    PDF = "pdf"
    CSV = "csv"
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"
    POWERPOINT = "powerpoint"
    WORD = "word"


class AnalysisDepth(str, Enum):
    QUICK = "quick"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    DEEP = "deep"


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# =============================================================================
# EXTRACTION MODELS
# =============================================================================

class ExtractedEntity(BaseModel):
    """An extracted named entity from the document."""
    id: str
    type: EntityType
    value: str
    normalized_value: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    context: Optional[str] = None
    page: Optional[int] = None
    position: Optional[Dict[str, int]] = None  # {"start": 0, "end": 10}
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExtractedMetric(BaseModel):
    """A key metric or KPI extracted from the document."""
    id: str
    name: str
    value: Union[float, int, str, None] = None
    raw_value: str
    metric_type: MetricType
    unit: Optional[str] = None
    currency: Optional[str] = None
    period: Optional[str] = None  # "Q3 2025", "FY2024", etc.
    normalized_period: Optional[str] = None  # ISO date range
    change: Optional[float] = None  # % change if mentioned
    change_direction: Optional[str] = None  # "increase", "decrease"
    comparison_base: Optional[str] = None  # "vs last year"
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    context: Optional[str] = None
    page: Optional[int] = None
    importance_score: float = Field(ge=0.0, le=1.0, default=0.5)


class FormField(BaseModel):
    """An extracted form field."""
    id: str
    label: str
    value: Optional[str] = None
    field_type: str = "text"  # text, checkbox, radio, date, signature, dropdown
    required: bool = False
    section: Optional[str] = None
    validation_pattern: Optional[str] = None
    options: Optional[List[str]] = None  # For dropdown/radio
    is_filled: bool = False
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class ExtractedForm(BaseModel):
    """Structured form data."""
    id: str
    title: Optional[str] = None
    form_type: Optional[str] = None
    fields: List[FormField] = Field(default_factory=list)
    sections: List[Dict[str, Any]] = Field(default_factory=list)
    submission_status: str = "incomplete"
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class InvoiceLineItem(BaseModel):
    """A line item from an invoice."""
    id: str
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None
    tax: Optional[float] = None
    discount: Optional[float] = None
    sku: Optional[str] = None
    category: Optional[str] = None


class ExtractedInvoice(BaseModel):
    """Structured invoice data."""
    id: str
    vendor_name: Optional[str] = None
    vendor_address: Optional[str] = None
    vendor_tax_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    purchase_order: Optional[str] = None
    line_items: List[InvoiceLineItem] = Field(default_factory=list)
    subtotal: Optional[float] = None
    tax_total: Optional[float] = None
    discount_total: Optional[float] = None
    grand_total: Optional[float] = None
    currency: str = "USD"
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class ContractClause(BaseModel):
    """A clause from a contract."""
    id: str
    clause_type: str  # "term", "obligation", "termination", "confidentiality", "liability", etc.
    title: Optional[str] = None
    content: str
    section: Optional[str] = None
    page: Optional[int] = None
    obligations: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    importance: str = "medium"  # low, medium, high, critical
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class ExtractedContract(BaseModel):
    """Structured contract data."""
    id: str
    contract_type: Optional[str] = None
    parties: List[Dict[str, str]] = Field(default_factory=list)
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None
    auto_renewal: bool = False
    renewal_terms: Optional[str] = None
    key_terms: List[str] = Field(default_factory=list)
    clauses: List[ContractClause] = Field(default_factory=list)
    obligations: List[Dict[str, Any]] = Field(default_factory=list)
    termination_clauses: List[str] = Field(default_factory=list)
    governing_law: Optional[str] = None
    signatures: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class TableRelationship(BaseModel):
    """Relationship between tables (for cross-page stitching)."""
    table1_id: str
    table2_id: str
    relationship_type: str  # "continuation", "related", "parent_child"
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class EnhancedExtractedTable(BaseModel):
    """Enhanced table with additional metadata."""
    id: str
    title: Optional[str] = None
    headers: List[str] = Field(default_factory=list)
    rows: List[List[Any]] = Field(default_factory=list)
    data_types: List[str] = Field(default_factory=list)
    column_descriptions: List[str] = Field(default_factory=list)
    source_page: Optional[int] = None
    source_sheet: Optional[str] = None
    is_nested: bool = False
    parent_table_id: Optional[str] = None
    related_tables: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.9)
    row_count: int = 0
    column_count: int = 0
    has_totals_row: bool = False
    has_header_row: bool = True
    statistics: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# ANALYSIS ENGINE MODELS
# =============================================================================

class DocumentSummary(BaseModel):
    """Multi-mode document summary."""
    mode: SummaryMode
    title: str
    content: str
    bullet_points: List[str] = Field(default_factory=list)
    key_figures: List[Dict[str, Any]] = Field(default_factory=list)
    word_count: int = 0
    reading_time_minutes: float = 0
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SentimentAnalysis(BaseModel):
    """Document sentiment analysis results."""
    overall_sentiment: SentimentLevel
    overall_score: float = Field(ge=-1.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    section_sentiments: List[Dict[str, Any]] = Field(default_factory=list)
    emotional_tone: str = "neutral"  # formal, casual, urgent, optimistic, etc.
    urgency_level: str = "normal"  # low, normal, high, critical
    bias_indicators: List[str] = Field(default_factory=list)
    key_phrases: Dict[str, List[str]] = Field(default_factory=dict)  # positive/negative phrases


class TextAnalytics(BaseModel):
    """Text analytics results."""
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    avg_sentence_length: float = 0
    readability_score: float = 0  # Flesch-Kincaid
    readability_grade: str = ""  # Grade level
    keywords: List[Dict[str, Any]] = Field(default_factory=list)  # [{word, frequency, importance}]
    topics: List[Dict[str, Any]] = Field(default_factory=list)  # Topic modeling results
    named_entities_summary: Dict[str, int] = Field(default_factory=dict)  # Entity type counts
    language: str = "en"
    language_confidence: float = 0.95


class FinancialAnalysis(BaseModel):
    """Financial analysis results."""
    metrics_found: int = 0
    currency: str = "USD"

    # Profitability ratios
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    roe: Optional[float] = None  # Return on Equity
    roa: Optional[float] = None  # Return on Assets

    # Liquidity ratios
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    cash_ratio: Optional[float] = None

    # Efficiency ratios
    inventory_turnover: Optional[float] = None
    receivables_turnover: Optional[float] = None
    asset_turnover: Optional[float] = None

    # Growth metrics
    revenue_growth: Optional[float] = None
    profit_growth: Optional[float] = None
    yoy_comparison: Dict[str, Any] = Field(default_factory=dict)

    # Variance analysis
    variance_analysis: List[Dict[str, Any]] = Field(default_factory=list)

    # Insights
    insights: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class StatisticalAnalysis(BaseModel):
    """Statistical analysis of numeric data."""
    column_stats: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    # Per column: mean, median, std, min, max, percentiles, skewness, kurtosis

    correlations: List[Dict[str, Any]] = Field(default_factory=list)
    # [{col1, col2, correlation, p_value}]

    outliers: List[Dict[str, Any]] = Field(default_factory=list)
    # [{column, value, row_index, zscore}]

    distributions: Dict[str, str] = Field(default_factory=dict)
    # {column: "normal", "uniform", "exponential", etc.}

    trends: List[Dict[str, Any]] = Field(default_factory=list)
    # [{column, trend_direction, slope, r_squared}]


class ComparativeAnalysis(BaseModel):
    """Comparison between documents or versions."""
    comparison_type: str  # "version_diff", "multi_doc", "benchmark"
    documents_compared: List[str] = Field(default_factory=list)

    # Differences found
    additions: List[Dict[str, Any]] = Field(default_factory=list)
    deletions: List[Dict[str, Any]] = Field(default_factory=list)
    modifications: List[Dict[str, Any]] = Field(default_factory=list)

    # Metric comparisons
    metric_changes: List[Dict[str, Any]] = Field(default_factory=list)

    # Summary
    similarity_score: float = Field(ge=0.0, le=1.0, default=0.0)
    change_summary: str = ""
    significant_changes: List[str] = Field(default_factory=list)


# =============================================================================
# VISUALIZATION MODELS
# =============================================================================

class ChartDataSeries(BaseModel):
    """A data series for charting."""
    name: str
    data: List[Any] = Field(default_factory=list)
    color: Optional[str] = None
    type: Optional[str] = None  # For mixed charts
    y_axis: Optional[int] = None  # For dual-axis charts


class ChartAnnotation(BaseModel):
    """Annotation on a chart."""
    type: str  # "point", "line", "region", "text"
    label: str
    value: Optional[Any] = None
    position: Optional[Dict[str, Any]] = None
    style: Dict[str, Any] = Field(default_factory=dict)


class EnhancedChartSpec(BaseModel):
    """Enhanced chart specification with AI insights."""
    id: str
    type: ChartType
    title: str
    description: Optional[str] = None

    # Data configuration
    x_field: str
    y_fields: List[str] = Field(default_factory=list)
    group_field: Optional[str] = None
    size_field: Optional[str] = None  # For bubble charts
    color_field: Optional[str] = None

    # Data
    data: List[Dict[str, Any]] = Field(default_factory=list)
    series: List[ChartDataSeries] = Field(default_factory=list)

    # Axes
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    x_axis_type: str = "category"  # category, time, linear, log
    y_axis_type: str = "linear"

    # Styling
    colors: List[str] = Field(default_factory=list)
    show_legend: bool = True
    show_grid: bool = True
    show_labels: bool = False

    # AI-powered features
    trend_line: Optional[Dict[str, Any]] = None
    forecast: Optional[Dict[str, Any]] = None
    anomalies: List[Dict[str, Any]] = Field(default_factory=list)
    annotations: List[ChartAnnotation] = Field(default_factory=list)
    ai_insights: List[str] = Field(default_factory=list)

    # Interactivity
    is_interactive: bool = True
    drill_down_enabled: bool = False

    # Metadata
    source_table_id: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    suggested_by_ai: bool = True


class VisualizationSuggestion(BaseModel):
    """AI suggestion for a visualization."""
    chart_spec: EnhancedChartSpec
    rationale: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    complexity: str = "simple"  # simple, moderate, complex
    insights_potential: List[str] = Field(default_factory=list)


# =============================================================================
# INSIGHTS & RECOMMENDATIONS
# =============================================================================

class Insight(BaseModel):
    """An AI-generated insight."""
    id: str
    type: str  # "finding", "trend", "anomaly", "recommendation", "warning"
    title: str
    description: str
    priority: Priority
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_data: List[Dict[str, Any]] = Field(default_factory=list)
    source_references: List[str] = Field(default_factory=list)  # Page/table references
    actionable: bool = False
    suggested_actions: List[str] = Field(default_factory=list)


class RiskItem(BaseModel):
    """An identified risk."""
    id: str
    title: str
    description: str
    risk_level: RiskLevel
    category: str  # financial, operational, compliance, market, etc.
    probability: float = Field(ge=0.0, le=1.0, default=0.5)
    impact: float = Field(ge=0.0, le=1.0, default=0.5)
    risk_score: float = Field(ge=0.0, le=1.0, default=0.0)
    mitigation_suggestions: List[str] = Field(default_factory=list)
    source_references: List[str] = Field(default_factory=list)


class OpportunityItem(BaseModel):
    """An identified opportunity."""
    id: str
    title: str
    description: str
    opportunity_type: str  # growth, efficiency, cost_saving, innovation
    potential_value: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    requirements: List[str] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)
    source_references: List[str] = Field(default_factory=list)


class ActionItem(BaseModel):
    """A recommended action."""
    id: str
    title: str
    description: str
    priority: Priority
    category: str
    assignee_suggestion: Optional[str] = None
    due_date_suggestion: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    expected_outcome: Optional[str] = None
    effort_estimate: Optional[str] = None  # "low", "medium", "high"


# =============================================================================
# EXPORT & TRANSFORMATION
# =============================================================================

class DataTransformation(BaseModel):
    """Data transformation operation."""
    operation: str  # "clean", "normalize", "merge", "split", "aggregate", "pivot"
    source_columns: List[str] = Field(default_factory=list)
    target_column: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    description: str = ""


class DataQualityIssue(BaseModel):
    """A specific data quality issue."""
    id: str
    issue_type: str  # "missing", "duplicate", "invalid", "outlier", "inconsistent"
    severity: str = "medium"  # low, medium, high, critical
    column: Optional[str] = None
    row_indices: List[int] = Field(default_factory=list)
    description: str
    suggested_fix: Optional[str] = None
    affected_count: int = 0


class DataQualityReport(BaseModel):
    """Data quality assessment."""
    total_rows: int = 0
    total_columns: int = 0

    # Issues list
    issues: List[DataQualityIssue] = Field(default_factory=list)

    # Completeness
    missing_values: Dict[str, int] = Field(default_factory=dict)
    missing_percentage: Dict[str, float] = Field(default_factory=dict)

    # Uniqueness
    duplicate_rows: int = 0
    unique_values_per_column: Dict[str, int] = Field(default_factory=dict)

    # Validity
    invalid_values: Dict[str, List[Any]] = Field(default_factory=dict)
    type_mismatches: Dict[str, List[int]] = Field(default_factory=dict)

    # Consistency
    format_inconsistencies: Dict[str, List[str]] = Field(default_factory=dict)

    # Outliers
    outliers_detected: Dict[str, List[int]] = Field(default_factory=dict)

    # Overall score
    quality_score: float = Field(ge=0.0, le=1.0, default=0.0)
    recommendations: List[str] = Field(default_factory=list)


class ExportConfiguration(BaseModel):
    """Export configuration."""
    format: ExportFormat
    include_raw_data: bool = True
    include_charts: bool = True
    include_analysis: bool = True
    include_insights: bool = True
    sections: List[str] = Field(default_factory=list)  # Empty = all
    styling: Dict[str, Any] = Field(default_factory=dict)
    filename: Optional[str] = None


# =============================================================================
# USER PREFERENCES & SETTINGS
# =============================================================================

class AnalysisPreferences(BaseModel):
    """User preferences for analysis."""
    analysis_depth: AnalysisDepth = AnalysisDepth.STANDARD
    focus_areas: List[str] = Field(default_factory=list)  # financial, operational, etc.
    output_format: str = "executive"  # executive, technical, visual
    language: str = "en"
    industry: Optional[str] = None
    company_size: Optional[str] = None
    currency_preference: str = "USD"
    date_format: str = "YYYY-MM-DD"
    number_format: str = "1,234.56"
    timezone: str = "UTC"
    enable_predictions: bool = True
    enable_recommendations: bool = True
    auto_chart_generation: bool = True
    max_charts: int = 10
    summary_mode: SummaryMode = SummaryMode.EXECUTIVE


# =============================================================================
# INTEGRATION MODELS
# =============================================================================

class WebhookConfig(BaseModel):
    """Webhook configuration for notifications."""
    url: str
    events: List[str] = Field(default_factory=list)  # analysis_complete, risk_detected, etc.
    secret: Optional[str] = None
    enabled: bool = True


class IntegrationConfig(BaseModel):
    """External integration configuration."""
    type: str  # slack, teams, email, jira, salesforce, etc.
    enabled: bool = True
    credentials: Dict[str, str] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)


class ScheduledAnalysis(BaseModel):
    """Scheduled analysis configuration."""
    id: str
    name: str
    source_type: str  # upload, url, database, api
    source_config: Dict[str, Any] = Field(default_factory=dict)
    schedule: str  # Cron expression
    analysis_config: AnalysisPreferences = Field(default_factory=AnalysisPreferences)
    notifications: List[str] = Field(default_factory=list)  # Email addresses
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    enabled: bool = True


# =============================================================================
# MAIN ANALYSIS RESULT
# =============================================================================

class EnhancedAnalysisResult(BaseModel):
    """Complete enhanced analysis result."""
    # Identifiers
    analysis_id: str
    document_name: str
    document_type: DocumentType
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: int = 0

    # Extraction results
    tables: List[EnhancedExtractedTable] = Field(default_factory=list)
    entities: List[ExtractedEntity] = Field(default_factory=list)
    metrics: List[ExtractedMetric] = Field(default_factory=list)
    forms: List[FormField] = Field(default_factory=list)
    invoices: List[ExtractedInvoice] = Field(default_factory=list)
    contracts: List[ExtractedContract] = Field(default_factory=list)
    table_relationships: List[TableRelationship] = Field(default_factory=list)

    # Analysis results
    summaries: Dict[str, DocumentSummary] = Field(default_factory=dict)
    sentiment: Optional[SentimentAnalysis] = None
    text_analytics: Optional[TextAnalytics] = None
    financial_analysis: Optional[FinancialAnalysis] = None
    statistical_analysis: Optional[StatisticalAnalysis] = None
    comparative_analysis: Optional[ComparativeAnalysis] = None

    # Visualizations
    chart_suggestions: List[EnhancedChartSpec] = Field(default_factory=list)
    visualization_suggestions: List[VisualizationSuggestion] = Field(default_factory=list)

    # Insights & recommendations
    insights: List[Insight] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    opportunities: List[OpportunityItem] = Field(default_factory=list)
    action_items: List[ActionItem] = Field(default_factory=list)

    # Data quality
    data_quality: Optional[DataQualityReport] = None

    # Metadata
    page_count: int = 0
    total_tables: int = 0
    total_entities: int = 0
    total_metrics: int = 0
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.8)

    # Settings used
    preferences: Optional[AnalysisPreferences] = None

    # Warnings and errors
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


# =============================================================================
# API REQUEST/RESPONSE MODELS
# =============================================================================

class AnalyzeRequest(BaseModel):
    """Request to analyze a document."""
    preferences: Optional[AnalysisPreferences] = None
    focus_areas: List[str] = Field(default_factory=list)
    comparison_document_ids: List[str] = Field(default_factory=list)
    custom_prompts: Dict[str, str] = Field(default_factory=dict)


class ChartGenerationRequest(BaseModel):
    """Request to generate charts."""
    analysis_id: str
    natural_language_query: Optional[str] = None
    chart_type: Optional[ChartType] = None
    data_columns: List[str] = Field(default_factory=list)
    include_trends: bool = True
    include_forecasts: bool = False


class ExportRequest(BaseModel):
    """Request to export analysis."""
    analysis_id: str
    config: ExportConfiguration


class QuestionRequest(BaseModel):
    """Request to ask a question about the document."""
    analysis_id: str
    question: str
    include_sources: bool = True
    max_context_chunks: int = 5


class QuestionResponse(BaseModel):
    """Response to a document question."""
    answer: str
    confidence: float
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    suggested_followups: List[str] = Field(default_factory=list)


class QAResponse(BaseModel):
    """Enhanced Q&A response with detailed source information."""
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    context_used: List[str] = Field(default_factory=list)
    suggested_followups: List[str] = Field(default_factory=list)
    reasoning: Optional[str] = None
    citations: List[Dict[str, Any]] = Field(default_factory=list)


class TransformRequest(BaseModel):
    """Request to transform data."""
    analysis_id: str
    transformations: List[DataTransformation]
    output_format: str = "json"
