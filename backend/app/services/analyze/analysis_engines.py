# mypy: ignore-errors
"""
AI-Powered Analysis Engines - Document summarization, sentiment, and statistical analysis.

Features:
2.1 Document Summarization Suite
2.2 Sentiment & Tone Analysis
2.3 Comparative Analysis
"""
from __future__ import annotations

import json
import logging
import math
import re
import uuid
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from backend.app.schemas.analyze.enhanced_analysis import (
    ActionItem,
    ComparativeAnalysis,
    DocumentSummary,
    EnhancedExtractedTable,
    ExtractedMetric,
    FinancialAnalysis,
    Insight,
    OpportunityItem,
    Priority,
    RiskItem,
    RiskLevel,
    SentimentAnalysis,
    SentimentLevel,
    StatisticalAnalysis,
    SummaryMode,
    TextAnalytics,
)
from backend.app.services.utils.llm import call_chat_completion, extract_json_from_llm_response
from backend.app.services.llm.client import get_llm_client

logger = logging.getLogger("neura.analyze.engines")


# =============================================================================
# DOCUMENT SUMMARIZATION
# =============================================================================

SUMMARY_PROMPTS = {
    SummaryMode.EXECUTIVE: """Create a C-suite executive summary of this document.
- Maximum 3 bullet points
- Focus on key business decisions and bottom-line impact
- Use clear, decisive language
- Highlight the most critical number or outcome

Format:
Title: [Brief title]
Bullets:
- [Key point 1]
- [Key point 2]
- [Key point 3]
Key Figure: [The single most important number/metric]""",

    SummaryMode.DATA: """Create a data-focused summary of this document.
- List all key figures, metrics, and KPIs found
- Include trends and comparisons
- Note data quality or completeness issues

Format:
Title: Data Summary
Key Metrics:
- [Metric 1]: [Value] ([context])
- [Metric 2]: [Value] ([context])
Trends: [Notable trends]
Data Quality: [Any issues noted]""",

    SummaryMode.QUICK: """Provide a one-sentence summary capturing the essence of this document.
Keep it under 30 words. Focus on the main purpose and key outcome.""",

    SummaryMode.COMPREHENSIVE: """Create a comprehensive structured summary of this document.

Format:
Title: [Document title]
Overview: [2-3 sentence overview]
Key Sections:
1. [Section 1 name]: [Summary]
2. [Section 2 name]: [Summary]
Key Findings:
- [Finding 1]
- [Finding 2]
- [Finding 3]
Data Highlights:
- [Key metric/number 1]
- [Key metric/number 2]
Conclusions: [Main conclusions]
Limitations: [Any caveats or limitations noted]""",

    SummaryMode.ACTION_ITEMS: """Extract all action items, to-dos, and next steps from this document.

Format:
Title: Action Items Summary
Immediate Actions:
- [Action 1] (Priority: High/Medium/Low)
- [Action 2] (Priority: High/Medium/Low)
Follow-up Required:
- [Follow-up 1]
Deadlines Mentioned:
- [Deadline 1]: [Date]
Responsibilities:
- [Person/Team]: [Their action items]""",

    SummaryMode.RISKS: """Identify and summarize all risks, concerns, and potential issues mentioned in this document.

Format:
Title: Risk Summary
Critical Risks:
- [Risk 1]: [Description] - Impact: [High/Medium/Low]
Warnings/Concerns:
- [Concern 1]
Compliance Issues:
- [Any compliance or regulatory concerns]
Mitigation Mentioned:
- [Any risk mitigation strategies noted]
Overall Risk Level: [Low/Medium/High/Critical]""",

    SummaryMode.OPPORTUNITIES: """Identify opportunities, growth areas, and positive developments in this document.

Format:
Title: Opportunities Summary
Growth Opportunities:
- [Opportunity 1]: [Description] - Potential: [High/Medium/Low]
Positive Trends:
- [Trend 1]
Recommendations for Action:
- [Recommendation 1]
Quick Wins:
- [Any easily achievable improvements noted]""",
}


def generate_summary(
    text: str,
    mode: SummaryMode,
    tables: List[EnhancedExtractedTable] = None,
    metrics: List[ExtractedMetric] = None,
) -> DocumentSummary:
    """Generate a document summary in the specified mode."""
    # Build context
    context_parts = [f"Document text:\n{text[:8000]}"]

    if tables:
        table_info = "\n\nTables found:\n"
        for t in tables[:5]:
            table_info += f"- {t.title or t.id}: {t.row_count} rows, columns: {', '.join(t.headers[:5])}\n"
        context_parts.append(table_info)

    if metrics:
        metrics_info = "\n\nKey metrics extracted:\n"
        for m in metrics[:10]:
            metrics_info += f"- {m.name}: {m.raw_value}\n"
        context_parts.append(metrics_info)

    context = "\n".join(context_parts)
    prompt = f"{SUMMARY_PROMPTS[mode]}\n\nDocument:\n{context}"

    try:
        client = get_llm_client()
        response = call_chat_completion(
            client,
            model=None,
            messages=[{"role": "user", "content": prompt}],
            description=f"summary_{mode.value}",
            temperature=0.3,
        )

        content = response.choices[0].message.content or ""

        # Parse the response
        title = ""
        bullet_points = []
        key_figures = []

        # Extract title
        title_match = re.search(r'Title:\s*(.+?)(?:\n|$)', content)
        if title_match:
            title = title_match.group(1).strip()

        # Extract bullet points
        bullet_matches = re.findall(r'^[\s]*[-•*]\s*(.+?)$', content, re.MULTILINE)
        bullet_points = [b.strip() for b in bullet_matches if b.strip()]

        # Extract key figures
        figure_matches = re.findall(r'[\$€£¥]?\d[\d,]*(?:\.\d+)?[%]?', content)
        key_figures = [{"value": f, "context": ""} for f in figure_matches[:5]]

        # Word count
        words = len(content.split())
        reading_time = max(1, words / 200)  # 200 words per minute

        return DocumentSummary(
            mode=mode,
            title=title or f"{mode.value.title()} Summary",
            content=content,
            bullet_points=bullet_points[:10],
            key_figures=key_figures,
            word_count=words,
            reading_time_minutes=reading_time,
        )
    except Exception as e:
        logger.error("Summary generation failed: %s", e, exc_info=True)
        return DocumentSummary(
            mode=mode,
            title="Summary Generation Failed",
            content="Could not generate summary due to an internal error.",
        )


def generate_all_summaries(
    text: str,
    tables: List[EnhancedExtractedTable] = None,
    metrics: List[ExtractedMetric] = None,
) -> Dict[str, DocumentSummary]:
    """Generate all summary types."""
    summaries = {}
    for mode in SummaryMode:
        summaries[mode.value] = generate_summary(text, mode, tables, metrics)
    return summaries


# =============================================================================
# SENTIMENT ANALYSIS
# =============================================================================

def analyze_sentiment(text: str) -> SentimentAnalysis:
    """Analyze document sentiment and tone."""
    prompt = f"""Analyze the sentiment and tone of this document.

Document:
{text[:8000]}

Provide analysis in JSON format:
```json
{{
  "overall_sentiment": "positive|negative|neutral|very_positive|very_negative",
  "overall_score": 0.5,  // -1.0 (very negative) to 1.0 (very positive)
  "confidence": 0.85,
  "emotional_tone": "formal|casual|urgent|optimistic|pessimistic|neutral|analytical|persuasive",
  "urgency_level": "low|normal|high|critical",
  "section_sentiments": [
    {{"section": "Introduction", "sentiment": "positive", "score": 0.6}},
    {{"section": "Financial Results", "sentiment": "negative", "score": -0.3}}
  ],
  "positive_phrases": ["exceeded expectations", "strong growth"],
  "negative_phrases": ["challenges ahead", "declining margins"],
  "bias_indicators": ["overly optimistic language", "missing context for claims"]
}}
```

Be objective and thorough in your analysis."""

    try:
        client = get_llm_client()
        response = call_chat_completion(
            client,
            model=None,
            messages=[{"role": "user", "content": prompt}],
            description="sentiment_analysis",
            temperature=0.2,
        )

        raw_text = response.choices[0].message.content or ""
        data = extract_json_from_llm_response(raw_text, default=None)

        if data:
            sentiment_map = {
                "very_positive": SentimentLevel.VERY_POSITIVE,
                "positive": SentimentLevel.POSITIVE,
                "neutral": SentimentLevel.NEUTRAL,
                "negative": SentimentLevel.NEGATIVE,
                "very_negative": SentimentLevel.VERY_NEGATIVE,
            }

            return SentimentAnalysis(
                overall_sentiment=sentiment_map.get(
                    data.get("overall_sentiment", "neutral").lower(),
                    SentimentLevel.NEUTRAL
                ),
                overall_score=float(data.get("overall_score", 0)),
                confidence=float(data.get("confidence", 0.8)),
                section_sentiments=data.get("section_sentiments", []),
                emotional_tone=data.get("emotional_tone", "neutral"),
                urgency_level=data.get("urgency_level", "normal"),
                bias_indicators=data.get("bias_indicators", []),
                key_phrases={
                    "positive": data.get("positive_phrases", []),
                    "negative": data.get("negative_phrases", []),
                },
            )
    except Exception as e:
        logger.warning(f"Sentiment analysis failed: {e}")

    return SentimentAnalysis(
        overall_sentiment=SentimentLevel.NEUTRAL,
        overall_score=0.0,
        confidence=0.5,
    )


# =============================================================================
# TEXT ANALYTICS
# =============================================================================

def analyze_text(text: str) -> TextAnalytics:
    """Perform text analytics including readability and keyword extraction."""
    # Basic counts
    words = text.split()
    word_count = len(words)
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    paragraphs = text.split('\n\n')
    paragraph_count = len([p for p in paragraphs if p.strip()])

    avg_sentence_length = word_count / max(sentence_count, 1)

    # Flesch-Kincaid readability
    syllables = sum(_count_syllables(word) for word in words)
    if word_count > 0 and sentence_count > 0:
        flesch_score = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllables / word_count)
        flesch_score = max(0, min(100, flesch_score))
    else:
        flesch_score = 50

    # Grade level
    if flesch_score >= 90:
        grade = "5th grade"
    elif flesch_score >= 80:
        grade = "6th grade"
    elif flesch_score >= 70:
        grade = "7th grade"
    elif flesch_score >= 60:
        grade = "8th-9th grade"
    elif flesch_score >= 50:
        grade = "10th-12th grade"
    elif flesch_score >= 30:
        grade = "College"
    else:
        grade = "College graduate"

    # Keyword extraction
    stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
                 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'and', 'or',
                 'but', 'if', 'because', 'as', 'of', 'at', 'by', 'for', 'with',
                 'to', 'from', 'in', 'on', 'not', 'no', 'so', 'than', 'too', 'very'}

    word_freq = Counter(w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', text)
                        if w.lower() not in stopwords)
    keywords = [
        {"word": word, "frequency": count, "importance": min(1.0, count / 50)}
        for word, count in word_freq.most_common(20)
    ]

    # Detect language (simple heuristic)
    language = "en"  # Default to English

    return TextAnalytics(
        word_count=word_count,
        sentence_count=sentence_count,
        paragraph_count=paragraph_count,
        avg_sentence_length=round(avg_sentence_length, 1),
        readability_score=round(flesch_score, 1),
        readability_grade=grade,
        keywords=keywords,
        language=language,
        language_confidence=0.95,
    )


def _count_syllables(word: str) -> int:
    """Count syllables in a word."""
    word = word.lower()
    vowels = "aeiouy"
    count = 0
    prev_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel

    # Adjust for silent e
    if word.endswith('e'):
        count -= 1

    return max(1, count)


# =============================================================================
# STATISTICAL ANALYSIS
# =============================================================================

def analyze_statistics(tables: List[EnhancedExtractedTable]) -> StatisticalAnalysis:
    """Perform statistical analysis on numeric data in tables."""
    column_stats = {}
    correlations = []
    outliers = []
    distributions = {}
    trends = []

    for table in tables:
        numeric_columns = {}

        # Extract numeric columns
        for col_idx, (header, dtype) in enumerate(zip(table.headers, table.data_types)):
            if dtype == "numeric":
                values = []
                for row_idx, row in enumerate(table.rows):
                    if col_idx < len(row):
                        try:
                            val = float(str(row[col_idx]).replace(",", "").replace("$", "").replace("%", ""))
                            values.append((row_idx, val))
                        except (ValueError, TypeError):
                            pass

                if len(values) >= 3:
                    numeric_columns[header] = values

        # Calculate statistics for each column
        for header, indexed_values in numeric_columns.items():
            values = [v for _, v in indexed_values]
            n = len(values)

            mean = sum(values) / n
            sorted_vals = sorted(values)
            median = sorted_vals[n // 2] if n % 2 == 1 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2

            variance = sum((x - mean) ** 2 for x in values) / n
            std = math.sqrt(variance)

            # Percentiles
            p25 = sorted_vals[int(n * 0.25)]
            p75 = sorted_vals[int(n * 0.75)]

            column_stats[f"{table.id}.{header}"] = {
                "count": n,
                "mean": round(mean, 4),
                "median": round(median, 4),
                "std": round(std, 4),
                "min": min(values),
                "max": max(values),
                "p25": p25,
                "p75": p75,
            }

            # Detect outliers (values beyond 2 standard deviations)
            if std > 0:
                for row_idx, val in indexed_values:
                    zscore = abs((val - mean) / std)
                    if zscore > 2:
                        outliers.append({
                            "table": table.id,
                            "column": header,
                            "row_index": row_idx,
                            "value": val,
                            "zscore": round(zscore, 2),
                        })

            # Simple trend detection (for sequential data)
            if n >= 5:
                first_half = sum(values[:n // 2]) / (n // 2)
                second_half = sum(values[n // 2:]) / (n - n // 2)

                if second_half > first_half * 1.1:
                    trend_dir = "increasing"
                elif second_half < first_half * 0.9:
                    trend_dir = "decreasing"
                else:
                    trend_dir = "stable"

                trends.append({
                    "table": table.id,
                    "column": header,
                    "trend_direction": trend_dir,
                    "change_ratio": round(second_half / first_half, 4) if first_half != 0 else 0,
                })

        # Calculate correlations between numeric columns
        col_names = list(numeric_columns.keys())
        for i in range(len(col_names)):
            for j in range(i + 1, len(col_names)):
                col1, col2 = col_names[i], col_names[j]
                vals1 = [v for _, v in numeric_columns[col1]]
                vals2 = [v for _, v in numeric_columns[col2]]

                # Align by index
                min_len = min(len(vals1), len(vals2))
                if min_len >= 5:
                    corr = _pearson_correlation(vals1[:min_len], vals2[:min_len])
                    if abs(corr) > 0.3:  # Only report meaningful correlations
                        correlations.append({
                            "table": table.id,
                            "column1": col1,
                            "column2": col2,
                            "correlation": round(corr, 4),
                        })

    return StatisticalAnalysis(
        column_stats=column_stats,
        correlations=correlations,
        outliers=outliers[:20],  # Limit to top 20
        distributions=distributions,
        trends=trends,
    )


def _pearson_correlation(x: List[float], y: List[float]) -> float:
    """Calculate Pearson correlation coefficient."""
    n = len(x)
    if n < 2:
        return 0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    denom_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
    denom_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))

    if denom_x == 0 or denom_y == 0:
        return 0

    return numerator / (denom_x * denom_y)


# =============================================================================
# FINANCIAL ANALYSIS
# =============================================================================

def analyze_financials(
    text: str,
    metrics: List[ExtractedMetric],
    tables: List[EnhancedExtractedTable],
) -> FinancialAnalysis:
    """Perform financial analysis using LLM."""
    # Build context
    metrics_context = "\n".join([
        f"- {m.name}: {m.raw_value}" + (f" ({m.change}% {m.change_direction})" if m.change else "")
        for m in metrics[:20]
    ])

    prompt = f"""Analyze this document for financial insights. Calculate ratios where data is available.

Metrics found:
{metrics_context}

Document excerpt:
{text[:5000]}

Return JSON:
```json
{{
  "currency": "USD",
  "gross_margin": 0.35,
  "operating_margin": 0.20,
  "net_margin": 0.15,
  "revenue_growth": 0.12,
  "profit_growth": 0.08,
  "yoy_comparison": {{"revenue": {{"current": 1000000, "previous": 900000, "change": 0.11}}}},
  "variance_analysis": [
    {{"metric": "Revenue", "actual": 1000000, "budget": 950000, "variance": 50000, "variance_pct": 5.26}}
  ],
  "insights": [
    "Revenue grew 11% year-over-year, exceeding industry average of 8%",
    "Operating margin improved despite increased costs"
  ],
  "warnings": [
    "Debt-to-equity ratio increased significantly",
    "Cash reserves declining quarter-over-quarter"
  ]
}}
```

Only include metrics you can calculate or find. Use null for unavailable data."""

    try:
        client = get_llm_client()
        response = call_chat_completion(
            client,
            model=None,
            messages=[{"role": "user", "content": prompt}],
            description="financial_analysis",
            temperature=0.2,
        )

        raw_text = response.choices[0].message.content or ""
        data = extract_json_from_llm_response(raw_text, default=None)

        if data:
            return FinancialAnalysis(
                metrics_found=len(metrics),
                currency=data.get("currency", "USD"),
                gross_margin=data.get("gross_margin"),
                operating_margin=data.get("operating_margin"),
                net_margin=data.get("net_margin"),
                revenue_growth=data.get("revenue_growth"),
                profit_growth=data.get("profit_growth"),
                yoy_comparison=data.get("yoy_comparison", {}),
                variance_analysis=data.get("variance_analysis", []),
                insights=data.get("insights", []),
                warnings=data.get("warnings", []),
            )
    except Exception as e:
        logger.warning(f"Financial analysis failed: {e}")

    return FinancialAnalysis(metrics_found=len(metrics))


# =============================================================================
# INSIGHTS, RISKS & OPPORTUNITIES
# =============================================================================

def generate_insights(
    text: str,
    metrics: List[ExtractedMetric],
    tables: List[EnhancedExtractedTable],
    sentiment: SentimentAnalysis,
    stats: StatisticalAnalysis,
) -> Tuple[List[Insight], List[RiskItem], List[OpportunityItem], List[ActionItem]]:
    """Generate insights, risks, opportunities, and action items."""
    context = f"""Document analysis context:
- Sentiment: {sentiment.overall_sentiment.value} (score: {sentiment.overall_score})
- Urgency: {sentiment.urgency_level}
- Key metrics: {len(metrics)}
- Tables: {len(tables)}
- Outliers detected: {len(stats.outliers)}
- Trends: {[t['trend_direction'] for t in stats.trends]}

Metrics:
{chr(10).join([f"- {m.name}: {m.raw_value}" for m in metrics[:15]])}

Document excerpt:
{text[:4000]}"""

    prompt = f"""{context}

Analyze this document and generate:
1. Key insights (findings, trends, anomalies)
2. Risks and concerns
3. Opportunities
4. Recommended action items

Return JSON:
```json
{{
  "insights": [
    {{
      "type": "finding|trend|anomaly|recommendation|warning",
      "title": "Short title",
      "description": "Detailed description",
      "priority": "critical|high|medium|low",
      "confidence": 0.85,
      "supporting_data": ["Revenue: $1.5M", "Growth: 15%"],
      "actionable": true,
      "suggested_actions": ["Review pricing strategy"]
    }}
  ],
  "risks": [
    {{
      "title": "Declining Cash Reserves",
      "description": "Cash reserves have decreased 20% this quarter",
      "risk_level": "high",
      "category": "financial",
      "probability": 0.7,
      "impact": 0.8,
      "mitigation_suggestions": ["Reduce non-essential spending"]
    }}
  ],
  "opportunities": [
    {{
      "title": "Market Expansion",
      "description": "Emerging market shows 30% growth potential",
      "opportunity_type": "growth",
      "potential_value": "$500K annual revenue",
      "confidence": 0.75,
      "requirements": ["Localization", "Partner network"],
      "suggested_actions": ["Conduct market research"]
    }}
  ],
  "action_items": [
    {{
      "title": "Review Q3 budget",
      "description": "Budget variance exceeds 10% threshold",
      "priority": "high",
      "category": "financial",
      "expected_outcome": "Realigned budget for Q4"
    }}
  ]
}}
```

Be specific and actionable. Base insights on actual data found."""

    insights = []
    risks = []
    opportunities = []
    action_items = []

    try:
        client = get_llm_client()
        response = call_chat_completion(
            client,
            model=None,
            messages=[{"role": "user", "content": prompt}],
            description="insights_generation",
            temperature=0.3,
        )

        raw_text = response.choices[0].message.content or ""
        data = extract_json_from_llm_response(raw_text, default=None)

        if data:
            # Parse insights
            for item in data.get("insights", []):
                priority_map = {"critical": Priority.CRITICAL, "high": Priority.HIGH,
                               "medium": Priority.MEDIUM, "low": Priority.LOW}
                insights.append(Insight(
                    id=f"ins_{uuid.uuid4().hex[:8]}",
                    type=item.get("type", "finding"),
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    priority=priority_map.get(item.get("priority", "medium"), Priority.MEDIUM),
                    confidence=item.get("confidence", 0.8),
                    supporting_data=item.get("supporting_data", []),
                    actionable=item.get("actionable", False),
                    suggested_actions=item.get("suggested_actions", []),
                ))

            # Parse risks
            for item in data.get("risks", []):
                risk_map = {"critical": RiskLevel.CRITICAL, "high": RiskLevel.HIGH,
                           "medium": RiskLevel.MEDIUM, "low": RiskLevel.LOW, "minimal": RiskLevel.MINIMAL}
                risk_level = risk_map.get(item.get("risk_level", "medium"), RiskLevel.MEDIUM)
                prob = item.get("probability", 0.5)
                impact = item.get("impact", 0.5)

                risks.append(RiskItem(
                    id=f"risk_{uuid.uuid4().hex[:8]}",
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    risk_level=risk_level,
                    category=item.get("category", "general"),
                    probability=prob,
                    impact=impact,
                    risk_score=prob * impact,
                    mitigation_suggestions=item.get("mitigation_suggestions", []),
                ))

            # Parse opportunities
            for item in data.get("opportunities", []):
                opportunities.append(OpportunityItem(
                    id=f"opp_{uuid.uuid4().hex[:8]}",
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    opportunity_type=item.get("opportunity_type", "growth"),
                    potential_value=item.get("potential_value"),
                    confidence=item.get("confidence", 0.7),
                    requirements=item.get("requirements", []),
                    suggested_actions=item.get("suggested_actions", []),
                ))

            # Parse action items
            for item in data.get("action_items", []):
                priority_map = {"critical": Priority.CRITICAL, "high": Priority.HIGH,
                               "medium": Priority.MEDIUM, "low": Priority.LOW}
                action_items.append(ActionItem(
                    id=f"act_{uuid.uuid4().hex[:8]}",
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    priority=priority_map.get(item.get("priority", "medium"), Priority.MEDIUM),
                    category=item.get("category", "general"),
                    expected_outcome=item.get("expected_outcome"),
                ))

    except Exception as e:
        logger.warning(f"Insights generation failed: {e}")

    return insights, risks, opportunities, action_items


# =============================================================================
# COMPARATIVE ANALYSIS
# =============================================================================

def compare_documents(
    text1: str,
    text2: str,
    metrics1: List[ExtractedMetric] = None,
    metrics2: List[ExtractedMetric] = None,
) -> ComparativeAnalysis:
    """Compare two documents and identify differences."""
    metrics1 = metrics1 or []
    metrics2 = metrics2 or []

    # Build metrics comparison
    metrics1_dict = {m.name: m for m in metrics1}
    metrics2_dict = {m.name: m for m in metrics2}

    metric_changes = []
    all_metric_names = set(metrics1_dict.keys()) | set(metrics2_dict.keys())

    for name in all_metric_names:
        m1 = metrics1_dict.get(name)
        m2 = metrics2_dict.get(name)

        if m1 and m2:
            try:
                v1 = float(m1.value) if isinstance(m1.value, (int, float)) else 0
                v2 = float(m2.value) if isinstance(m2.value, (int, float)) else 0
                change = ((v2 - v1) / v1 * 100) if v1 != 0 else 0
                metric_changes.append({
                    "metric": name,
                    "value_doc1": m1.raw_value,
                    "value_doc2": m2.raw_value,
                    "change_pct": round(change, 2),
                })
            except (ValueError, TypeError):
                pass
        elif m1:
            metric_changes.append({
                "metric": name,
                "value_doc1": m1.raw_value,
                "value_doc2": None,
                "status": "removed",
            })
        elif m2:
            metric_changes.append({
                "metric": name,
                "value_doc1": None,
                "value_doc2": m2.raw_value,
                "status": "added",
            })

    prompt = f"""Compare these two document excerpts and identify key differences.

Document 1:
{text1[:3000]}

Document 2:
{text2[:3000]}

Return JSON:
```json
{{
  "similarity_score": 0.75,
  "additions": [
    {{"location": "Section 3", "content": "New paragraph about...", "significance": "high"}}
  ],
  "deletions": [
    {{"location": "Section 2", "content": "Removed reference to...", "significance": "medium"}}
  ],
  "modifications": [
    {{"location": "Section 1", "original": "Revenue was $1M", "modified": "Revenue was $1.2M", "significance": "high"}}
  ],
  "change_summary": "Brief summary of overall changes",
  "significant_changes": ["Key change 1", "Key change 2"]
}}
```"""

    try:
        client = get_llm_client()
        response = call_chat_completion(
            client,
            model=None,
            messages=[{"role": "user", "content": prompt}],
            description="document_comparison",
            temperature=0.2,
        )

        raw_text = response.choices[0].message.content or ""
        data = extract_json_from_llm_response(raw_text, default=None)

        if data:
            return ComparativeAnalysis(
                comparison_type="version_diff",
                documents_compared=["document_1", "document_2"],
                additions=data.get("additions", []),
                deletions=data.get("deletions", []),
                modifications=data.get("modifications", []),
                metric_changes=metric_changes,
                similarity_score=data.get("similarity_score", 0.5),
                change_summary=data.get("change_summary", ""),
                significant_changes=data.get("significant_changes", []),
            )
    except Exception as e:
        logger.warning(f"Document comparison failed: {e}")

    return ComparativeAnalysis(
        comparison_type="version_diff",
        documents_compared=["document_1", "document_2"],
        metric_changes=metric_changes,
    )


# =============================================================================
# ANALYSIS ENGINE ORCHESTRATOR
# =============================================================================

class AnalysisEngineService:
    """Orchestrates all analysis engines."""

    def run_all_analyses(
        self,
        text: str,
        tables: List[EnhancedExtractedTable],
        metrics: List[ExtractedMetric],
    ) -> Dict[str, Any]:
        """
        Run all analysis engines.

        Uses a single consolidated LLM call for summary + sentiment +
        financial + insights instead of 10+ separate calls.
        """
        # ---- Pure-Python analyses (no LLM) ----
        text_analytics = analyze_text(text)
        statistical = analyze_statistics(tables)

        # ---- Single consolidated LLM call ----
        llm_results = self._run_consolidated_analysis(text, tables, metrics)

        return {
            "summaries": llm_results.get("summaries", {}),
            "sentiment": llm_results.get("sentiment", SentimentAnalysis(
                overall_sentiment=SentimentLevel.NEUTRAL,
                overall_score=0.0, confidence=0.5,
            )),
            "text_analytics": text_analytics,
            "statistical_analysis": statistical,
            "financial_analysis": llm_results.get("financial_analysis", FinancialAnalysis(
                metrics_found=len(metrics),
            )),
            "insights": llm_results.get("insights", []),
            "risks": llm_results.get("risks", []),
            "opportunities": llm_results.get("opportunities", []),
            "action_items": llm_results.get("action_items", []),
        }

    def _run_consolidated_analysis(
        self,
        text: str,
        tables: List[EnhancedExtractedTable],
        metrics: List[ExtractedMetric],
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis in ONE LLM call.

        Combines: executive summary, comprehensive summary, sentiment,
        financial analysis, insights, risks, opportunities, and action items.
        """
        # Build context
        metrics_context = "\n".join([
            f"- {m.name}: {m.raw_value}" + (f" ({m.change}% {m.change_direction})" if m.change else "")
            for m in metrics[:20]
        ]) or "(no metrics extracted)"

        table_info = ""
        for t in tables[:5]:
            table_info += f"- {t.title or t.id}: {t.row_count} rows, columns: {', '.join(t.headers[:8])}\n"
        table_info = table_info or "(no tables found)"

        prompt = f"""Analyze this document comprehensively. Return a SINGLE JSON object with all analyses.

DOCUMENT TEXT:
{text[:10000]}

TABLES FOUND:
{table_info}

METRICS EXTRACTED:
{metrics_context}

Return a JSON object with these keys:

{{
  "executive_summary": {{
    "title": "Brief title",
    "content": "2-3 paragraph executive summary for C-suite",
    "bullet_points": ["Key point 1", "Key point 2", "Key point 3"]
  }},
  "comprehensive_summary": {{
    "title": "Document title",
    "content": "Detailed structured summary covering all major sections",
    "bullet_points": ["Finding 1", "Finding 2", "Finding 3", "Finding 4", "Finding 5"]
  }},
  "sentiment": {{
    "overall_sentiment": "positive|negative|neutral|very_positive|very_negative",
    "overall_score": 0.5,
    "confidence": 0.85,
    "emotional_tone": "formal|casual|urgent|optimistic|pessimistic|neutral|analytical",
    "urgency_level": "low|normal|high|critical"
  }},
  "financial": {{
    "currency": "USD",
    "revenue_growth": null,
    "profit_growth": null,
    "insights": ["Financial insight 1"],
    "warnings": ["Financial warning 1"]
  }},
  "insights": [
    {{
      "type": "finding|trend|anomaly|recommendation|warning",
      "title": "Short title",
      "description": "Detailed description",
      "priority": "critical|high|medium|low",
      "confidence": 0.85,
      "actionable": true,
      "suggested_actions": ["Action 1"]
    }}
  ],
  "risks": [
    {{
      "title": "Risk title",
      "description": "Risk description",
      "risk_level": "critical|high|medium|low|minimal",
      "category": "financial|operational|compliance|market",
      "probability": 0.7,
      "impact": 0.8,
      "mitigation_suggestions": ["Suggestion 1"]
    }}
  ],
  "opportunities": [
    {{
      "title": "Opportunity title",
      "description": "Description",
      "opportunity_type": "growth|efficiency|cost_saving|innovation",
      "potential_value": "$500K",
      "confidence": 0.75,
      "suggested_actions": ["Action 1"]
    }}
  ],
  "action_items": [
    {{
      "title": "Action title",
      "description": "Description",
      "priority": "critical|high|medium|low",
      "category": "financial|operational|strategic",
      "expected_outcome": "Expected result"
    }}
  ]
}}

IMPORTANT:
- Be specific and actionable, grounded in the actual document content
- Include at least 3 insights, 2 risks, 2 opportunities, and 2 action items
- For financial fields, only include data you can calculate from the document (use null otherwise)
- Return ONLY valid JSON, no extra text"""

        try:
            client = get_llm_client()
            response = call_chat_completion(
                client,
                model=None,
                messages=[{"role": "user", "content": prompt}],
                description="consolidated_analysis",
                temperature=0.3,
            )

            raw_text = response.choices[0].message.content or ""
            data = extract_json_from_llm_response(raw_text, default=None)

            if not data:
                raise ValueError("LLM returned no parseable JSON for analysis")

            return self._parse_consolidated_result(data, metrics)

        except Exception as e:
            logger.error("Consolidated analysis failed: %s", e, exc_info=True)
            raise RuntimeError(f"AI analysis failed: {e}") from e

    def _parse_consolidated_result(
        self,
        data: Dict[str, Any],
        metrics: List[ExtractedMetric],
    ) -> Dict[str, Any]:
        """Parse the consolidated LLM response into typed structures."""
        result: Dict[str, Any] = {}

        # --- Summaries ---
        summaries: Dict[str, DocumentSummary] = {}
        for key, mode in [("executive_summary", SummaryMode.EXECUTIVE),
                          ("comprehensive_summary", SummaryMode.COMPREHENSIVE)]:
            s = data.get(key, {})
            if isinstance(s, dict):
                content = s.get("content", "")
                words = len(content.split())
                summaries[mode.value] = DocumentSummary(
                    mode=mode,
                    title=s.get("title", f"{mode.value.title()} Summary"),
                    content=content,
                    bullet_points=s.get("bullet_points", []),
                    word_count=words,
                    reading_time_minutes=max(1, words / 200),
                )
        result["summaries"] = summaries

        # --- Sentiment ---
        sent = data.get("sentiment", {})
        if isinstance(sent, dict):
            sentiment_map = {
                "very_positive": SentimentLevel.VERY_POSITIVE,
                "positive": SentimentLevel.POSITIVE,
                "neutral": SentimentLevel.NEUTRAL,
                "negative": SentimentLevel.NEGATIVE,
                "very_negative": SentimentLevel.VERY_NEGATIVE,
            }
            result["sentiment"] = SentimentAnalysis(
                overall_sentiment=sentiment_map.get(
                    str(sent.get("overall_sentiment", "neutral")).lower(),
                    SentimentLevel.NEUTRAL
                ),
                overall_score=float(sent.get("overall_score", 0)),
                confidence=float(sent.get("confidence", 0.8)),
                emotional_tone=sent.get("emotional_tone", "neutral"),
                urgency_level=sent.get("urgency_level", "normal"),
            )

        # --- Financial ---
        fin = data.get("financial", {})
        if isinstance(fin, dict):
            result["financial_analysis"] = FinancialAnalysis(
                metrics_found=len(metrics),
                currency=fin.get("currency", "USD"),
                gross_margin=fin.get("gross_margin"),
                operating_margin=fin.get("operating_margin"),
                net_margin=fin.get("net_margin"),
                revenue_growth=fin.get("revenue_growth"),
                profit_growth=fin.get("profit_growth"),
                yoy_comparison=fin.get("yoy_comparison", {}),
                variance_analysis=fin.get("variance_analysis", []),
                insights=fin.get("insights", []),
                warnings=fin.get("warnings", []),
            )

        # --- Insights ---
        priority_map = {"critical": Priority.CRITICAL, "high": Priority.HIGH,
                        "medium": Priority.MEDIUM, "low": Priority.LOW}
        result["insights"] = []
        for item in data.get("insights", []):
            if isinstance(item, dict):
                result["insights"].append(Insight(
                    id=f"ins_{uuid.uuid4().hex[:8]}",
                    type=item.get("type", "finding"),
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    priority=priority_map.get(str(item.get("priority", "medium")).lower(), Priority.MEDIUM),
                    confidence=float(item.get("confidence", 0.8)),
                    supporting_data=item.get("supporting_data", []),
                    actionable=bool(item.get("actionable", False)),
                    suggested_actions=item.get("suggested_actions", []),
                ))

        # --- Risks ---
        risk_map = {"critical": RiskLevel.CRITICAL, "high": RiskLevel.HIGH,
                    "medium": RiskLevel.MEDIUM, "low": RiskLevel.LOW, "minimal": RiskLevel.MINIMAL}
        result["risks"] = []
        for item in data.get("risks", []):
            if isinstance(item, dict):
                prob = float(item.get("probability", 0.5))
                impact = float(item.get("impact", 0.5))
                result["risks"].append(RiskItem(
                    id=f"risk_{uuid.uuid4().hex[:8]}",
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    risk_level=risk_map.get(str(item.get("risk_level", "medium")).lower(), RiskLevel.MEDIUM),
                    category=item.get("category", "general"),
                    probability=prob,
                    impact=impact,
                    risk_score=prob * impact,
                    mitigation_suggestions=item.get("mitigation_suggestions", []),
                ))

        # --- Opportunities ---
        result["opportunities"] = []
        for item in data.get("opportunities", []):
            if isinstance(item, dict):
                result["opportunities"].append(OpportunityItem(
                    id=f"opp_{uuid.uuid4().hex[:8]}",
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    opportunity_type=item.get("opportunity_type", "growth"),
                    potential_value=item.get("potential_value"),
                    confidence=float(item.get("confidence", 0.7)),
                    requirements=item.get("requirements", []),
                    suggested_actions=item.get("suggested_actions", []),
                ))

        # --- Action Items ---
        result["action_items"] = []
        for item in data.get("action_items", []):
            if isinstance(item, dict):
                result["action_items"].append(ActionItem(
                    id=f"act_{uuid.uuid4().hex[:8]}",
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    priority=priority_map.get(str(item.get("priority", "medium")).lower(), Priority.MEDIUM),
                    category=item.get("category", "general"),
                    expected_outcome=item.get("expected_outcome"),
                ))

        return result
