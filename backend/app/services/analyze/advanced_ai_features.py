# mypy: ignore-errors
"""
Advanced AI Features - Multi-modal understanding, cross-document intelligence, and predictive analytics.

Features:
8.1 Multi-Modal Understanding (images, handwriting, logos)
8.2 Cross-Document Intelligence (knowledge graphs, citations, contradictions)
8.3 Predictive Analytics (forecasting, anomaly prediction, growth modeling)
"""
from __future__ import annotations

import json
import logging
import math
import re
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

from backend.app.schemas.analyze.enhanced_analysis import (
    EnhancedChartSpec,
    EnhancedExtractedTable,
    ExtractedEntity,
    ExtractedMetric,
    Insight,
    Priority,
)
from backend.app.services.utils.llm import call_chat_completion, extract_json_from_llm_response
from backend.app.services.llm.client import get_llm_client

logger = logging.getLogger("neura.analyze.advanced_ai")


# =============================================================================
# 8.1 MULTI-MODAL UNDERSTANDING
# =============================================================================

@dataclass
class ImageAnalysisResult:
    """Result of image analysis within a document."""
    image_type: str  # chart, diagram, photo, logo, signature, handwriting
    description: str
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.8
    location: Optional[str] = None  # page number or position


@dataclass
class ChartDataExtraction:
    """Extracted data from a chart image."""
    chart_type: str
    title: Optional[str]
    x_axis: Dict[str, Any]
    y_axis: Dict[str, Any]
    data_series: List[Dict[str, Any]]
    insights: List[str]


def analyze_document_images(
    images: List[Any],
    document_context: str = "",
) -> List[ImageAnalysisResult]:
    """Analyze images found in a document using VLM."""
    results = []
    if not images:
        return results

    vlm = None
    try:
        from backend.app.services.llm.vision import VisionLanguageModel
        vlm = VisionLanguageModel()
    except Exception as exc:
        logger.warning(f"Vision model unavailable for image analysis: {exc}")

    # For each image, determine type and extract relevant data
    for img in images:
        img_data = None
        page = None
        if isinstance(img, dict):
            img_data = img.get("data") or img.get("bytes") or img.get("image")
            page = img.get("page")
        else:
            img_data = img

        if not img_data:
            continue

        prompt = f"""Analyze this image from a document.

Document context: {document_context[:500]}

Determine:
1. Image type (chart, diagram, photo, logo, signature, handwriting, table, other)
2. Detailed description of content
3. Any extractable data (for charts: data points, for forms: field values, etc.)

Return JSON:
```json
{{
  "image_type": "chart|diagram|photo|logo|signature|handwriting|table|other",
  "description": "Detailed description",
  "extracted_data": {{
    "chart_type": "bar",
    "data_points": [{{"label": "Q1", "value": 100}}],
    "title": "Revenue by Quarter"
  }},
  "confidence": 0.85,
  "key_information": ["Item 1", "Item 2"]
}}
```"""

        try:
            parsed: Dict[str, Any] = {}
            if vlm:
                response = vlm.client.complete_with_vision(
                    text=prompt,
                    images=[img_data],
                    model=vlm.model,
                    description="vlm_image_analysis",
                )
                raw_content = response["choices"][0]["message"]["content"]
                parsed = _extract_json_payload(raw_content, {})

            image_type = parsed.get("image_type", "unknown")
            description = parsed.get("description", "Analyzed image")
            extracted_data = parsed.get("extracted_data", {}) or {}
            confidence = float(parsed.get("confidence", 0.7) or 0.7)

            # Optional sub-analyses
            if image_type in ("chart", "diagram"):
                chart_data = extract_chart_data_from_image(img_data)
                if chart_data:
                    extracted_data["chart_data"] = chart_data.__dict__
            if image_type in ("handwriting", "signature"):
                extracted_data["handwriting"] = detect_handwriting(img_data)
            if image_type == "logo":
                extracted_data["logos"] = detect_logos(img_data)

            results.append(ImageAnalysisResult(
                image_type=image_type,
                description=description,
                extracted_data=extracted_data,
                confidence=confidence,
                location=f"Page {page}" if page else None,
            ))
        except Exception as e:
            logger.warning(f"Image analysis failed: {e}")

    return results


def extract_chart_data_from_image(image_data: bytes) -> Optional[ChartDataExtraction]:
    """Extract structured data from a chart image."""
    prompt = """Analyze this chart image and extract all data.

Return JSON:
```json
{
  "chart_type": "bar|line|pie|scatter|area|other",
  "title": "Chart title if visible",
  "x_axis": {
    "label": "X axis label",
    "values": ["Jan", "Feb", "Mar"],
    "type": "category|numeric|date"
  },
  "y_axis": {
    "label": "Y axis label",
    "min": 0,
    "max": 100,
    "type": "numeric"
  },
  "data_series": [
    {
      "name": "Series 1",
      "values": [10, 20, 30],
      "color": "blue"
    }
  ],
  "insights": [
    "Key observation 1",
    "Key observation 2"
  ]
}
```

Extract as much data as you can accurately determine from the image."""

    try:
        from backend.app.services.llm.vision import VisionLanguageModel
        vlm = VisionLanguageModel()
        result = vlm.analyze_chart(image_data)
        return ChartDataExtraction(
            chart_type=result.get("chart_type", "unknown"),
            title=result.get("title"),
            x_axis=result.get("x_axis", {}),
            y_axis=result.get("y_axis", {}),
            data_series=result.get("data_series", []),
            insights=result.get("insights", []) if isinstance(result.get("insights"), list) else [str(result.get("insights"))],
        )
    except Exception as exc:
        logger.warning(f"Chart extraction failed: {exc}")
        return None


def detect_handwriting(image_data: bytes) -> Dict[str, Any]:
    """Detect and transcribe handwritten text."""
    prompt = """Analyze this image for handwritten text.

Return JSON:
```json
{
  "has_handwriting": true,
  "transcribed_text": "Full transcription of handwritten content",
  "confidence": 0.75,
  "words": [
    {"text": "word", "confidence": 0.8, "position": {"x": 100, "y": 50}}
  ],
  "is_signature": false
}
```

Transcribe all visible handwritten text accurately."""

    try:
        from backend.app.services.llm.vision import VisionLanguageModel
        vlm = VisionLanguageModel()
        response = vlm.client.complete_with_vision(
            text=prompt,
            images=[image_data],
            model=vlm.model,
            description="vlm_handwriting_detection",
        )
        raw_content = response["choices"][0]["message"]["content"]
        parsed = _extract_json_payload(raw_content, {})
        if parsed:
            return parsed
    except Exception as exc:
        logger.warning(f"Handwriting detection failed: {exc}")
    return {
        "has_handwriting": False,
        "transcribed_text": "",
        "confidence": 0.0,
        "words": [],
        "is_signature": False,
    }


def detect_logos(image_data: bytes) -> List[Dict[str, Any]]:
    """Detect and identify logos in an image."""
    prompt = """Analyze this image and detect any logos or brand marks.

Return JSON:
```json
{
  "logos": [
    {
      "name": "Brand or company name if known",
      "confidence": 0.85,
      "description": "Brief description of the logo",
      "position": {"x": 0, "y": 0, "width": 0, "height": 0}
    }
  ]
}
```"""

    try:
        from backend.app.services.llm.vision import VisionLanguageModel
        vlm = VisionLanguageModel()
        response = vlm.client.complete_with_vision(
            text=prompt,
            images=[image_data],
            model=vlm.model,
            description="vlm_logo_detection",
        )
        raw_content = response["choices"][0]["message"]["content"]
        parsed = _extract_json_payload(raw_content, {})
        logos = parsed.get("logos", [])
        return logos if isinstance(logos, list) else []
    except Exception as exc:
        logger.warning(f"Logo detection failed: {exc}")
        return []


def _extract_json_payload(raw_content: str, default: Dict[str, Any]) -> Dict[str, Any]:
    """Extract JSON from an LLM response (handles Claude's markdown code blocks)."""
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_content)
    if json_match:
        json_str = json_match.group(1).strip()
    else:
        json_str = raw_content.strip()

    start = json_str.find("{")
    if start == -1:
        return default

    depth = 0
    in_string = False
    escape_next = False
    for i, char in enumerate(json_str[start:], start):
        if escape_next:
            escape_next = False
            continue
        if char == "\\":
            escape_next = True
            continue
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                json_str = json_str[start:i + 1]
                break

    try:
        return json.loads(json_str)
    except Exception:
        return default


# =============================================================================
# 8.2 CROSS-DOCUMENT INTELLIGENCE
# =============================================================================

@dataclass
class KnowledgeGraphNode:
    """A node in the knowledge graph."""
    id: str
    label: str
    type: str  # entity, concept, metric, document
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeGraphEdge:
    """An edge in the knowledge graph."""
    source_id: str
    target_id: str
    relationship: str
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeGraph:
    """A knowledge graph built from document analysis."""
    nodes: List[KnowledgeGraphNode] = field(default_factory=list)
    edges: List[KnowledgeGraphEdge] = field(default_factory=list)

    def add_node(self, node: KnowledgeGraphNode) -> None:
        if not any(n.id == node.id for n in self.nodes):
            self.nodes.append(node)

    def add_edge(self, edge: KnowledgeGraphEdge) -> None:
        self.edges.append(edge)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [{"id": n.id, "label": n.label, "type": n.type, "properties": n.properties}
                      for n in self.nodes],
            "edges": [{"source": e.source_id, "target": e.target_id,
                       "relationship": e.relationship, "weight": e.weight}
                      for e in self.edges],
        }


def build_knowledge_graph(
    entities: List[ExtractedEntity],
    metrics: List[ExtractedMetric],
    document_id: str,
) -> KnowledgeGraph:
    """Build a knowledge graph from extracted entities and metrics."""
    graph = KnowledgeGraph()

    # Add document node
    doc_node = KnowledgeGraphNode(
        id=document_id,
        label=document_id,
        type="document",
    )
    graph.add_node(doc_node)

    # Add entity nodes
    for entity in entities:
        node = KnowledgeGraphNode(
            id=entity.id,
            label=entity.value,
            type=entity.type.value,
            properties={
                "normalized": entity.normalized_value,
                "confidence": entity.confidence,
            },
        )
        graph.add_node(node)

        # Connect to document
        graph.add_edge(KnowledgeGraphEdge(
            source_id=document_id,
            target_id=entity.id,
            relationship="contains",
            weight=entity.confidence,
        ))

    # Add metric nodes
    for metric in metrics:
        node = KnowledgeGraphNode(
            id=metric.id,
            label=metric.name,
            type="metric",
            properties={
                "value": metric.value,
                "raw_value": metric.raw_value,
                "metric_type": metric.metric_type.value,
                "period": metric.period,
            },
        )
        graph.add_node(node)

        # Connect to document
        graph.add_edge(KnowledgeGraphEdge(
            source_id=document_id,
            target_id=metric.id,
            relationship="reports",
            weight=metric.importance_score,
        ))

    # Find relationships between entities
    for i, e1 in enumerate(entities):
        for e2 in entities[i + 1:]:
            # If they appear in similar context, they might be related
            if e1.context and e2.context:
                # Simple proximity check
                if e1.value.lower() in (e2.context or "").lower() or e2.value.lower() in (e1.context or "").lower():
                    graph.add_edge(KnowledgeGraphEdge(
                        source_id=e1.id,
                        target_id=e2.id,
                        relationship="co_occurs",
                        weight=0.7,
                    ))

    return graph


def merge_knowledge_graphs(graphs: List[KnowledgeGraph]) -> KnowledgeGraph:
    """Merge multiple knowledge graphs into one."""
    merged = KnowledgeGraph()

    # Collect all nodes
    node_map: Dict[str, KnowledgeGraphNode] = {}
    for graph in graphs:
        for node in graph.nodes:
            # Merge by label for same-type nodes
            key = f"{node.type}:{node.label.lower()}"
            if key not in node_map:
                node_map[key] = node
            else:
                # Merge properties
                node_map[key].properties.update(node.properties)

    merged.nodes = list(node_map.values())

    # Collect all edges
    edge_set = set()
    for graph in graphs:
        for edge in graph.edges:
            edge_key = (edge.source_id, edge.target_id, edge.relationship)
            if edge_key not in edge_set:
                edge_set.add(edge_key)
                merged.add_edge(edge)

    return merged


@dataclass
class CitationLink:
    """A citation or reference link between documents."""
    source_doc_id: str
    target_doc_id: str
    citation_text: str
    citation_type: str  # reference, quote, data_source
    confidence: float = 0.8


def detect_citations(text: str, document_id: str) -> List[CitationLink]:
    """Detect citations and references in text."""
    citations = []

    # Common citation patterns
    patterns = [
        r'\[(\d+)\]',  # [1], [2]
        r'\(([A-Za-z]+(?:\s+et\s+al\.?)?,?\s*\d{4})\)',  # (Smith, 2023), (Smith et al., 2023)
        r'(?:Source|Reference|See|cf\.?):\s*(.+?)(?:\.|$)',  # Source: document name
        r'(?:According to|As stated in|Per)\s+(.+?)(?:,|\.)',  # According to X
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            citations.append(CitationLink(
                source_doc_id=document_id,
                target_doc_id=f"ref_{uuid.uuid4().hex[:8]}",
                citation_text=match.group(0),
                citation_type="reference",
                confidence=0.7,
            ))

    return citations


@dataclass
class Contradiction:
    """A detected contradiction between statements or documents."""
    statement1: str
    statement2: str
    source1: str
    source2: str
    contradiction_type: str  # factual, numerical, temporal
    severity: str  # minor, moderate, major
    confidence: float = 0.7


def detect_contradictions(
    text1: str,
    text2: str,
    doc1_id: str = "doc1",
    doc2_id: str = "doc2",
) -> List[Contradiction]:
    """Detect contradictions between two texts using LLM."""
    prompt = f"""Compare these two texts and identify any contradictions, inconsistencies, or conflicting information.

Text 1:
{text1[:3000]}

Text 2:
{text2[:3000]}

Return JSON:
```json
{{
  "contradictions": [
    {{
      "statement1": "Quote or paraphrase from Text 1",
      "statement2": "Conflicting statement from Text 2",
      "type": "factual|numerical|temporal|logical",
      "severity": "minor|moderate|major",
      "explanation": "Why these are contradictory",
      "confidence": 0.8
    }}
  ],
  "overall_consistency": 0.85
}}
```

Only report genuine contradictions, not differences in scope or perspective."""

    try:
        client = get_llm_client()
        response = call_chat_completion(
            client,
            model=None,
            messages=[{"role": "user", "content": prompt}],
            description="contradiction_detection",
            temperature=0.2,
        )

        raw_text = response.choices[0].message.content or ""
        json_match = re.search(r'\{[\s\S]*\}', raw_text)

        if json_match:
            data = json.loads(json_match.group())
            contradictions = []

            for item in data.get("contradictions", []):
                contradictions.append(Contradiction(
                    statement1=item.get("statement1", ""),
                    statement2=item.get("statement2", ""),
                    source1=doc1_id,
                    source2=doc2_id,
                    contradiction_type=item.get("type", "factual"),
                    severity=item.get("severity", "moderate"),
                    confidence=item.get("confidence", 0.7),
                ))

            return contradictions

    except Exception as e:
        logger.warning(f"Contradiction detection failed: {e}")

    return []


# =============================================================================
# 8.3 PREDICTIVE ANALYTICS
# =============================================================================

@dataclass
class Forecast:
    """A forecast prediction."""
    metric_name: str
    current_value: float
    predictions: List[Dict[str, Any]]  # [{period, value, lower_bound, upper_bound}]
    trend: str  # increasing, decreasing, stable
    confidence: float
    method: str  # linear, exponential, seasonal
    factors: List[str] = field(default_factory=list)


@dataclass
class AnomalyPrediction:
    """Predicted anomaly or unusual pattern."""
    metric_name: str
    predicted_date: Optional[str]
    anomaly_type: str  # spike, dip, deviation
    probability: float
    expected_value: float
    threshold: float
    reasoning: str


@dataclass
class GrowthModel:
    """Growth model for a metric."""
    metric_name: str
    model_type: str  # linear, exponential, logistic, polynomial
    parameters: Dict[str, float]
    r_squared: float
    projected_values: List[Dict[str, Any]]
    saturation_point: Optional[float] = None


def forecast_time_series(
    data: List[Tuple[str, float]],  # [(date, value), ...]
    metric_name: str,
    periods: int = 6,
) -> Forecast:
    """Generate a forecast for time series data."""
    if len(data) < 3:
        return Forecast(
            metric_name=metric_name,
            current_value=data[-1][1] if data else 0,
            predictions=[],
            trend="unknown",
            confidence=0.3,
            method="insufficient_data",
        )

    values = [v for _, v in data]
    n = len(values)

    # Calculate trend using linear regression
    x = list(range(n))
    mean_x = sum(x) / n
    mean_y = sum(values) / n

    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, values))
    denominator = sum((xi - mean_x) ** 2 for xi in x)

    if denominator == 0:
        slope = 0
        intercept = mean_y
    else:
        slope = numerator / denominator
        intercept = mean_y - slope * mean_x

    # Calculate R-squared
    ss_tot = sum((yi - mean_y) ** 2 for yi in values)
    ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, values))
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    # Determine trend
    if slope > 0.05 * mean_y:
        trend = "increasing"
    elif slope < -0.05 * mean_y:
        trend = "decreasing"
    else:
        trend = "stable"

    # Generate predictions
    predictions = []
    std_error = math.sqrt(ss_res / max(n - 2, 1)) if n > 2 else mean_y * 0.1

    for i in range(1, periods + 1):
        x_pred = n - 1 + i
        y_pred = slope * x_pred + intercept

        # Confidence interval (approximate)
        margin = 1.96 * std_error * math.sqrt(1 + 1 / n + (x_pred - mean_x) ** 2 / denominator) if denominator > 0 else y_pred * 0.2

        predictions.append({
            "period": i,
            "value": round(y_pred, 2),
            "lower_bound": round(y_pred - margin, 2),
            "upper_bound": round(y_pred + margin, 2),
        })

    confidence = min(0.95, max(0.3, r_squared))

    return Forecast(
        metric_name=metric_name,
        current_value=values[-1],
        predictions=predictions,
        trend=trend,
        confidence=round(confidence, 2),
        method="linear",
        factors=[f"Based on {n} historical data points", f"R² = {r_squared:.3f}"],
    )


def predict_anomalies(
    data: List[Tuple[str, float]],
    metric_name: str,
    sensitivity: float = 2.0,
) -> List[AnomalyPrediction]:
    """Predict potential anomalies based on historical patterns."""
    if len(data) < 10:
        return []

    values = [v for _, v in data]
    mean = sum(values) / len(values)
    std = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))

    if std == 0:
        return []

    # Calculate moving average and detect patterns
    window = min(5, len(values) // 2)
    predictions = []

    # Check for cyclic patterns (simplified)
    recent_values = values[-window:]
    recent_mean = sum(recent_values) / len(recent_values)

    # If recent trend differs significantly from overall
    if abs(recent_mean - mean) > std:
        if recent_mean > mean + std:
            predictions.append(AnomalyPrediction(
                metric_name=metric_name,
                predicted_date=None,
                anomaly_type="spike",
                probability=0.6,
                expected_value=recent_mean,
                threshold=mean + sensitivity * std,
                reasoning="Recent values significantly above historical average",
            ))
        else:
            predictions.append(AnomalyPrediction(
                metric_name=metric_name,
                predicted_date=None,
                anomaly_type="dip",
                probability=0.6,
                expected_value=recent_mean,
                threshold=mean - sensitivity * std,
                reasoning="Recent values significantly below historical average",
            ))

    # Check for increasing volatility
    recent_std = math.sqrt(sum((v - recent_mean) ** 2 for v in recent_values) / len(recent_values))
    if recent_std > std * 1.5:
        predictions.append(AnomalyPrediction(
            metric_name=metric_name,
            predicted_date=None,
            anomaly_type="deviation",
            probability=0.5,
            expected_value=recent_mean,
            threshold=recent_std,
            reasoning="Increased volatility in recent data",
        ))

    return predictions


def build_growth_model(
    data: List[Tuple[str, float]],
    metric_name: str,
    model_type: str = "auto",
) -> GrowthModel:
    """Build a growth model for a metric."""
    if len(data) < 5:
        return GrowthModel(
            metric_name=metric_name,
            model_type="insufficient_data",
            parameters={},
            r_squared=0,
            projected_values=[],
        )

    values = [v for _, v in data]
    n = len(values)
    x = list(range(n))

    # Try linear model
    mean_x = sum(x) / n
    mean_y = sum(values) / n

    num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, values))
    den = sum((xi - mean_x) ** 2 for xi in x)

    if den == 0:
        slope = 0
        intercept = mean_y
    else:
        slope = num / den
        intercept = mean_y - slope * mean_x

    # Calculate R-squared for linear
    ss_tot = sum((yi - mean_y) ** 2 for yi in values)
    ss_res_linear = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, values))
    r2_linear = 1 - (ss_res_linear / ss_tot) if ss_tot > 0 else 0

    # Try exponential model (log-linear)
    positive_values = [max(0.01, v) for v in values]
    log_values = [math.log(v) for v in positive_values]
    mean_log_y = sum(log_values) / n

    num_exp = sum((xi - mean_x) * (yi - mean_log_y) for xi, yi in zip(x, log_values))
    if den > 0:
        exp_slope = num_exp / den
        exp_intercept = mean_log_y - exp_slope * mean_x

        predicted_exp = [math.exp(exp_slope * xi + exp_intercept) for xi in x]
        ss_res_exp = sum((yi - pi) ** 2 for yi, pi in zip(values, predicted_exp))
        r2_exp = 1 - (ss_res_exp / ss_tot) if ss_tot > 0 else 0
    else:
        r2_exp = 0
        exp_slope = 0
        exp_intercept = math.log(mean_y) if mean_y > 0 else 0

    # Choose best model
    if model_type == "auto":
        if r2_exp > r2_linear + 0.1 and exp_slope > 0:
            model_type = "exponential"
        else:
            model_type = "linear"

    if model_type == "exponential":
        parameters = {"growth_rate": exp_slope, "initial_value": math.exp(exp_intercept)}
        r_squared = r2_exp

        projected = []
        for i in range(1, 7):
            x_pred = n - 1 + i
            y_pred = math.exp(exp_slope * x_pred + exp_intercept)
            projected.append({"period": i, "value": round(y_pred, 2)})

        # Estimate saturation (if growth slowing)
        growth_rates = [values[i] / values[i - 1] if values[i - 1] > 0 else 1 for i in range(1, n)]
        if len(growth_rates) >= 3:
            recent_growth = sum(growth_rates[-3:]) / 3
            early_growth = sum(growth_rates[:3]) / 3
            if recent_growth < early_growth * 0.8:
                saturation = values[-1] * (1 / (1 - recent_growth)) if recent_growth < 1 else None
            else:
                saturation = None
        else:
            saturation = None

    else:  # linear
        parameters = {"slope": slope, "intercept": intercept}
        r_squared = r2_linear
        saturation = None

        projected = []
        for i in range(1, 7):
            x_pred = n - 1 + i
            y_pred = slope * x_pred + intercept
            projected.append({"period": i, "value": round(y_pred, 2)})

    return GrowthModel(
        metric_name=metric_name,
        model_type=model_type,
        parameters=parameters,
        r_squared=round(r_squared, 4),
        projected_values=projected,
        saturation_point=saturation,
    )


def generate_ai_predictions(
    metrics: List[ExtractedMetric],
    tables: List[EnhancedExtractedTable],
) -> Dict[str, Any]:
    """Generate AI-powered predictions using LLM."""
    # Build context
    metrics_context = "\n".join([
        f"- {m.name}: {m.raw_value}" + (f" ({m.change}% change)" if m.change else "")
        for m in metrics[:15]
    ])

    prompt = f"""Based on these metrics, provide strategic predictions and insights.

Metrics:
{metrics_context}

Return JSON:
```json
{{
  "predictions": [
    {{
      "metric": "Revenue",
      "prediction": "Expected to grow 15-20% based on current trajectory",
      "confidence": "medium",
      "timeframe": "next 6 months",
      "factors": ["Market expansion", "New product launch"]
    }}
  ],
  "strategic_insights": [
    "Key strategic observation 1",
    "Key strategic observation 2"
  ],
  "risk_indicators": [
    {{
      "indicator": "Declining margins",
      "severity": "moderate",
      "recommendation": "Review cost structure"
    }}
  ],
  "growth_opportunities": [
    {{
      "opportunity": "Market segment X",
      "potential": "20% revenue increase",
      "requirements": ["Investment needed", "Timeline"]
    }}
  ]
}}
```

Be specific and data-driven in your predictions."""

    try:
        client = get_llm_client()
        response = call_chat_completion(
            client,
            model=None,
            messages=[{"role": "user", "content": prompt}],
            description="ai_predictions",
            temperature=0.4,
        )

        raw_text = response.choices[0].message.content or ""
        json_match = re.search(r'\{[\s\S]*\}', raw_text)

        if json_match:
            return json.loads(json_match.group())

    except Exception as e:
        logger.warning(f"AI predictions failed: {e}")

    return {"predictions": [], "strategic_insights": [], "risk_indicators": [], "growth_opportunities": []}


# =============================================================================
# ADVANCED AI SERVICE ORCHESTRATOR
# =============================================================================

class AdvancedAIService:
    """Orchestrates all advanced AI features."""

    def analyze_images(
        self,
        images: List[Any],
        document_context: str = "",
    ) -> List[ImageAnalysisResult]:
        """Analyze images in the document."""
        return analyze_document_images(images, document_context)

    def build_knowledge_graph(
        self,
        entities: List[ExtractedEntity],
        metrics: List[ExtractedMetric],
        document_id: str,
    ) -> KnowledgeGraph:
        """Build a knowledge graph from extracted data."""
        return build_knowledge_graph(entities, metrics, document_id)

    def detect_citations(self, text: str, document_id: str) -> List[CitationLink]:
        """Detect citations in text."""
        return detect_citations(text, document_id)

    def detect_contradictions(
        self,
        text1: str,
        text2: str,
        doc1_id: str = "doc1",
        doc2_id: str = "doc2",
    ) -> List[Contradiction]:
        """Detect contradictions between texts."""
        return detect_contradictions(text1, text2, doc1_id, doc2_id)

    def generate_forecasts(
        self,
        tables: List[EnhancedExtractedTable],
    ) -> List[Forecast]:
        """Generate forecasts for time series data in tables."""
        forecasts = []

        for table in tables:
            # Find datetime and numeric column pairs
            datetime_cols = [i for i, d in enumerate(table.data_types) if d == "datetime"]
            numeric_cols = [i for i, d in enumerate(table.data_types) if d == "numeric"]

            if not datetime_cols or not numeric_cols:
                continue

            date_idx = datetime_cols[0]

            for num_idx in numeric_cols[:3]:  # Limit to 3 numeric columns
                # Extract time series data
                data = []
                for row in table.rows:
                    if date_idx < len(row) and num_idx < len(row):
                        date_val = str(row[date_idx])
                        try:
                            num_val = float(str(row[num_idx]).replace(",", "").replace("$", "").replace("%", ""))
                            data.append((date_val, num_val))
                        except (ValueError, TypeError):
                            pass

                if len(data) >= 3:
                    forecast = forecast_time_series(
                        data,
                        table.headers[num_idx],
                        periods=6,
                    )
                    forecasts.append(forecast)

        return forecasts

    def predict_anomalies(
        self,
        tables: List[EnhancedExtractedTable],
    ) -> List[AnomalyPrediction]:
        """Predict anomalies in the data."""
        all_predictions = []

        for table in tables:
            for col_idx, (header, dtype) in enumerate(zip(table.headers, table.data_types)):
                if dtype != "numeric":
                    continue

                # Extract values
                data = []
                for i, row in enumerate(table.rows):
                    if col_idx < len(row):
                        try:
                            val = float(str(row[col_idx]).replace(",", "").replace("$", "").replace("%", ""))
                            data.append((str(i), val))
                        except (ValueError, TypeError):
                            pass

                if len(data) >= 10:
                    predictions = predict_anomalies(data, header)
                    all_predictions.extend(predictions)

        return all_predictions

    def build_growth_models(
        self,
        tables: List[EnhancedExtractedTable],
    ) -> List[GrowthModel]:
        """Build growth models for metrics."""
        models = []

        for table in tables:
            numeric_cols = [(i, h) for i, (h, d) in enumerate(zip(table.headers, table.data_types)) if d == "numeric"]

            for col_idx, header in numeric_cols[:3]:
                data = []
                for i, row in enumerate(table.rows):
                    if col_idx < len(row):
                        try:
                            val = float(str(row[col_idx]).replace(",", "").replace("$", "").replace("%", ""))
                            data.append((str(i), val))
                        except (ValueError, TypeError):
                            pass

                if len(data) >= 5:
                    model = build_growth_model(data, header)
                    if model.r_squared > 0.5:  # Only include models with reasonable fit
                        models.append(model)

        return models

    def generate_ai_predictions(
        self,
        metrics: List[ExtractedMetric],
        tables: List[EnhancedExtractedTable],
    ) -> Dict[str, Any]:
        """Generate AI-powered strategic predictions."""
        return generate_ai_predictions(metrics, tables)

    def run_all_advanced_features(
        self,
        text: str,
        entities: List[ExtractedEntity],
        metrics: List[ExtractedMetric],
        tables: List[EnhancedExtractedTable],
        document_id: str,
        images: Optional[List[Any]] = None,
        document_context: str = "",
    ) -> Dict[str, Any]:
        """Run all advanced AI features."""
        results = {
            "knowledge_graph": self.build_knowledge_graph(entities, metrics, document_id).to_dict(),
            "citations": [c.__dict__ for c in self.detect_citations(text, document_id)],
            "forecasts": [f.__dict__ for f in self.generate_forecasts(tables)],
            "anomaly_predictions": [a.__dict__ for a in self.predict_anomalies(tables)],
            "growth_models": [m.__dict__ for m in self.build_growth_models(tables)],
            "ai_predictions": self.generate_ai_predictions(metrics, tables),
        }
        if images:
            results["image_analysis"] = [
                r.__dict__ for r in self.analyze_images(images, document_context=document_context)
            ]
        return results
