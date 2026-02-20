# mypy: ignore-errors
"""
Vision-Language Model Integration for Document Understanding.

Provides specialized document analysis using VLMs:
- Qwen-VL (via Ollama or API)
- DeepSeek-VL
- LLaVA
- GPT-5 Vision
- Claude 3 Vision
- Gemini Vision

Features:
- OCR with layout understanding
- Table extraction from images
- Document structure analysis
- Multi-page document processing
"""
from __future__ import annotations

import base64
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .client import LLMClient, get_llm_client
from .config import LLMConfig, LLMProvider, VISION_MODELS

logger = logging.getLogger("neura.llm.vision")


@dataclass
class DocumentAnalysisResult:
    """Result of VLM document analysis."""
    text_content: str
    tables: List[Dict[str, Any]]
    structure: Dict[str, Any]
    metadata: Dict[str, Any]
    raw_response: str


@dataclass
class TableExtractionResult:
    """Result of table extraction from image."""
    tables: List[Dict[str, Any]]
    confidence: float
    raw_response: str


class VisionLanguageModel:
    """
    Vision-Language Model service for document understanding.

    Provides high-level methods for:
    - Document OCR with structure understanding
    - Table extraction from images
    - Form field extraction
    - Chart/graph analysis
    """

    def __init__(
        self,
        client: Optional[LLMClient] = None,
        model: Optional[str] = None,
    ):
        self.client = client or get_llm_client()
        self._model = model

    @property
    def model(self) -> str:
        """Get the vision model to use."""
        if self._model:
            return self._model
        return self.client.config.get_vision_model()

    def analyze_document(
        self,
        image: Union[str, bytes, Path],
        analysis_type: str = "comprehensive",
        language: str = "auto",
    ) -> DocumentAnalysisResult:
        """
        Analyze a document image using VLM.

        Args:
            image: Image path, bytes, or base64 string
            analysis_type: Type of analysis (comprehensive, text_only, tables_only, structure)
            language: Expected document language

        Returns:
            DocumentAnalysisResult with extracted content
        """
        prompt = self._build_document_analysis_prompt(analysis_type, language)

        response = self.client.complete_with_vision(
            text=prompt,
            images=[image],
            model=self.model,
            description=f"vlm_document_analysis_{analysis_type}",
        )

        raw_content = response["choices"][0]["message"]["content"]
        return self._parse_document_analysis(raw_content, analysis_type)

    def extract_tables(
        self,
        image: Union[str, bytes, Path],
        expected_columns: Optional[List[str]] = None,
    ) -> TableExtractionResult:
        """
        Extract tables from a document image.

        Args:
            image: Image path, bytes, or base64 string
            expected_columns: Optional list of expected column names

        Returns:
            TableExtractionResult with extracted tables
        """
        prompt = self._build_table_extraction_prompt(expected_columns)

        response = self.client.complete_with_vision(
            text=prompt,
            images=[image],
            model=self.model,
            description="vlm_table_extraction",
        )

        raw_content = response["choices"][0]["message"]["content"]
        return self._parse_table_extraction(raw_content)

    def extract_text_with_layout(
        self,
        image: Union[str, bytes, Path],
        preserve_formatting: bool = True,
    ) -> Dict[str, Any]:
        """
        Extract text from image while preserving layout structure.

        Args:
            image: Image path, bytes, or base64 string
            preserve_formatting: Whether to preserve original formatting

        Returns:
            Dict with text blocks, their positions, and hierarchy
        """
        prompt = f"""Analyze this document image and extract all text content.

{"Preserve the original formatting, spacing, and layout as much as possible." if preserve_formatting else "Extract the text content in reading order."}

Return your response in the following JSON format:
```json
{{
  "title": "Document title if present",
  "sections": [
    {{
      "type": "header|paragraph|list|table|footer",
      "level": 1,
      "content": "Text content",
      "formatting": {{
        "bold": false,
        "italic": false,
        "alignment": "left|center|right"
      }}
    }}
  ],
  "page_number": null,
  "reading_order_text": "Full text in reading order"
}}
```

Analyze the image carefully and extract all visible text."""

        response = self.client.complete_with_vision(
            text=prompt,
            images=[image],
            model=self.model,
            description="vlm_text_extraction",
        )

        raw_content = response["choices"][0]["message"]["content"]
        return self._parse_json_response(raw_content, {
            "title": None,
            "sections": [],
            "page_number": None,
            "reading_order_text": raw_content,
        })

    def analyze_chart(
        self,
        image: Union[str, bytes, Path],
    ) -> Dict[str, Any]:
        """
        Analyze a chart/graph image and extract data.

        Args:
            image: Chart image path, bytes, or base64 string

        Returns:
            Dict with chart type, data points, labels, and insights
        """
        prompt = """Analyze this chart/graph image and extract the data.

Return your response in the following JSON format:
```json
{
  "chart_type": "bar|line|pie|scatter|area|other",
  "title": "Chart title if visible",
  "x_axis": {
    "label": "X axis label",
    "values": ["value1", "value2"]
  },
  "y_axis": {
    "label": "Y axis label",
    "min": 0,
    "max": 100
  },
  "data_series": [
    {
      "name": "Series name",
      "values": [10, 20, 30],
      "color": "blue"
    }
  ],
  "legend": ["Item 1", "Item 2"],
  "insights": "Brief description of what the chart shows"
}
```

Extract as much data as you can accurately determine from the image."""

        response = self.client.complete_with_vision(
            text=prompt,
            images=[image],
            model=self.model,
            description="vlm_chart_analysis",
        )

        raw_content = response["choices"][0]["message"]["content"]
        return self._parse_json_response(raw_content, {
            "chart_type": "unknown",
            "data_series": [],
            "insights": raw_content,
        })

    def extract_form_fields(
        self,
        image: Union[str, bytes, Path],
    ) -> Dict[str, Any]:
        """
        Extract form fields and their values from an image.

        Args:
            image: Form image path, bytes, or base64 string

        Returns:
            Dict with field labels and their filled values
        """
        prompt = """Analyze this form image and extract all form fields with their values.

Return your response in the following JSON format:
```json
{
  "form_title": "Form title if visible",
  "fields": [
    {
      "label": "Field label",
      "value": "Filled value or null if empty",
      "type": "text|checkbox|radio|date|signature|other",
      "required": true
    }
  ],
  "sections": [
    {
      "name": "Section name",
      "fields": ["field_label_1", "field_label_2"]
    }
  ]
}
```

Extract all visible form fields, whether filled or empty."""

        response = self.client.complete_with_vision(
            text=prompt,
            images=[image],
            model=self.model,
            description="vlm_form_extraction",
        )

        raw_content = response["choices"][0]["message"]["content"]
        return self._parse_json_response(raw_content, {
            "form_title": None,
            "fields": [],
        })

    def compare_documents(
        self,
        image1: Union[str, bytes, Path],
        image2: Union[str, bytes, Path],
    ) -> Dict[str, Any]:
        """
        Compare two document images and identify differences.

        Args:
            image1: First document image
            image2: Second document image

        Returns:
            Dict with comparison results and differences
        """
        prompt = """Compare these two document images and identify any differences.

The first image is the reference, and the second is the version to compare.

Return your response in the following JSON format:
```json
{
  "identical": false,
  "similarity_score": 0.95,
  "differences": [
    {
      "type": "text_change|layout_change|missing_element|added_element",
      "location": "Description of where the difference is",
      "reference_content": "Content in first image",
      "compared_content": "Content in second image"
    }
  ],
  "summary": "Brief summary of the comparison"
}
```

Be thorough but focus on meaningful differences, not minor formatting variations."""

        response = self.client.complete_with_vision(
            text=prompt,
            images=[image1, image2],
            model=self.model,
            description="vlm_document_comparison",
        )

        raw_content = response["choices"][0]["message"]["content"]
        return self._parse_json_response(raw_content, {
            "identical": False,
            "differences": [],
            "summary": raw_content,
        })

    def _build_document_analysis_prompt(
        self,
        analysis_type: str,
        language: str,
    ) -> str:
        """Build the prompt for document analysis."""
        base_prompt = """Analyze this document image comprehensively.

"""
        if analysis_type == "text_only":
            base_prompt += """Focus on extracting all text content accurately.

Return your response in JSON format:
```json
{
  "text_content": "Full extracted text",
  "paragraphs": ["paragraph 1", "paragraph 2"],
  "headers": ["header 1"],
  "language": "detected language"
}
```"""
        elif analysis_type == "tables_only":
            base_prompt += """Focus on extracting any tables present in the document.

Return your response in JSON format:
```json
{
  "tables": [
    {
      "id": 1,
      "title": "Table title if present",
      "headers": ["Column 1", "Column 2"],
      "rows": [
        ["Value 1", "Value 2"],
        ["Value 3", "Value 4"]
      ]
    }
  ]
}
```"""
        elif analysis_type == "structure":
            base_prompt += """Focus on understanding the document structure and layout.

Return your response in JSON format:
```json
{
  "document_type": "invoice|report|form|letter|other",
  "sections": [
    {"name": "Section name", "type": "header|body|footer|sidebar"}
  ],
  "has_tables": true,
  "has_images": false,
  "layout": "single_column|multi_column|mixed"
}
```"""
        else:  # comprehensive
            base_prompt += """Extract all content including text, tables, and structure.

Return your response in JSON format:
```json
{
  "document_type": "invoice|report|form|letter|other",
  "title": "Document title if present",
  "text_content": "Full text content in reading order",
  "tables": [
    {
      "id": 1,
      "title": "Table title",
      "headers": ["Col1", "Col2"],
      "rows": [["Val1", "Val2"]]
    }
  ],
  "structure": {
    "sections": ["Section 1", "Section 2"],
    "has_headers": true,
    "has_footers": true
  },
  "metadata": {
    "language": "en",
    "date_found": "2024-01-01",
    "page_number": 1
  }
}
```"""

        if language != "auto":
            base_prompt += f"\n\nThe document is in {language}."

        return base_prompt

    def _build_table_extraction_prompt(
        self,
        expected_columns: Optional[List[str]],
    ) -> str:
        """Build the prompt for table extraction."""
        prompt = """Extract all tables from this document image.

Return your response in JSON format:
```json
{
  "tables": [
    {
      "id": 1,
      "title": "Table title if visible",
      "headers": ["Column 1", "Column 2", "Column 3"],
      "rows": [
        ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
        ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"]
      ],
      "notes": "Any footnotes or notes about the table"
    }
  ],
  "confidence": 0.95
}
```

Be accurate with the data extraction. If a cell is empty, use an empty string.
If you cannot read a value clearly, indicate it with "[unclear]".
"""

        if expected_columns:
            prompt += f"\n\nExpected columns: {', '.join(expected_columns)}"
            prompt += "\nMap extracted columns to these expected names if they match."

        return prompt

    def _parse_document_analysis(
        self,
        raw_content: str,
        analysis_type: str,
    ) -> DocumentAnalysisResult:
        """Parse the document analysis response."""
        parsed = self._parse_json_response(raw_content, {})

        text_content = parsed.get("text_content", "")
        if not text_content and "paragraphs" in parsed:
            text_content = "\n\n".join(parsed.get("paragraphs", []))

        tables = parsed.get("tables", [])
        structure = parsed.get("structure", {})

        if "document_type" in parsed:
            structure["document_type"] = parsed["document_type"]
        if "title" in parsed:
            structure["title"] = parsed["title"]

        metadata = parsed.get("metadata", {})
        if "language" in parsed:
            metadata["language"] = parsed["language"]

        return DocumentAnalysisResult(
            text_content=text_content or raw_content,
            tables=tables,
            structure=structure,
            metadata=metadata,
            raw_response=raw_content,
        )

    def _parse_table_extraction(
        self,
        raw_content: str,
    ) -> TableExtractionResult:
        """Parse the table extraction response."""
        parsed = self._parse_json_response(raw_content, {"tables": [], "confidence": 0.5})

        return TableExtractionResult(
            tables=parsed.get("tables", []),
            confidence=parsed.get("confidence", 0.5),
            raw_response=raw_content,
        )

    def _parse_json_response(
        self,
        raw_content: str,
        default: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Extract JSON from LLM response."""
        # Try to find JSON in code blocks
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_content)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            # Try to find raw JSON
            json_str = raw_content.strip()

        # Find the JSON object
        start = json_str.find("{")
        if start == -1:
            return default

        # Use bracket counting to find the matching close brace
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
        except json.JSONDecodeError as e:
            logger.warning(
                "vlm_json_parse_failed",
                extra={
                    "event": "vlm_json_parse_failed",
                    "error": str(e),
                    "snippet": json_str[:200],
                }
            )
            return default


# Convenience functions

def get_vlm(model: Optional[str] = None) -> VisionLanguageModel:
    """Get a VisionLanguageModel instance."""
    return VisionLanguageModel(model=model)


def analyze_document_image(
    image: Union[str, bytes, Path],
    analysis_type: str = "comprehensive",
) -> DocumentAnalysisResult:
    """Quick function to analyze a document image."""
    vlm = get_vlm()
    return vlm.analyze_document(image, analysis_type)


def extract_tables_from_image(
    image: Union[str, bytes, Path],
) -> TableExtractionResult:
    """Quick function to extract tables from an image."""
    vlm = get_vlm()
    return vlm.extract_tables(image)
