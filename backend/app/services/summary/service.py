"""Service for executive summary generation using AI."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from backend.app.services.llm.client import get_llm_client
from backend.app.repositories.state import store as state_store_module

logger = logging.getLogger("neura.domain.summary")


def _state_store():
    return state_store_module.state_store


class SummaryService:
    """Service for executive summary generation."""

    def __init__(self):
        self._llm_client = None

    def _get_llm_client(self):
        if self._llm_client is None:
            self._llm_client = get_llm_client()
        return self._llm_client

    def generate_summary(
        self,
        content: str,
        tone: str = "formal",
        max_sentences: int = 5,
        focus_areas: Optional[List[str]] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate an executive summary from content.

        Args:
            content: The content to summarize
            tone: Style of summary (formal, conversational, technical)
            max_sentences: Maximum sentences in summary
            focus_areas: Optional areas to focus on
            correlation_id: Request correlation ID

        Returns:
            Summary with key findings and metrics
        """
        logger.info("Generating executive summary", extra={"correlation_id": correlation_id})

        prompt = f"""Generate an executive summary of the following content.

CONTENT:
{content[:8000]}  # Limit content length

REQUIREMENTS:
- Tone: {tone}
- Maximum sentences: {max_sentences}
- Style: Professional, data-driven
{f"- Focus on: {', '.join(focus_areas)}" if focus_areas else ""}

Return a JSON object:
{{
  "executive_summary": "2-3 sentence overview",
  "key_findings": ["finding 1", "finding 2", "finding 3"],
  "metrics": [
    {{"name": "metric_name", "value": "123", "unit": "USD", "trend": "up"}}
  ],
  "recommendations": ["action 1", "action 2"],
  "confidence": 0.9
}}

Return ONLY the JSON object."""

        try:
            client = self._get_llm_client()
            response = client.complete(
                messages=[{"role": "user", "content": prompt}],
                description="executive_summary",
                temperature=0.3,
            )

            import json
            import re
            content_response = response["choices"][0]["message"]["content"]
            json_match = re.search(r"\{[\s\S]*\}", content_response)
            if json_match:
                return json.loads(json_match.group())

        except Exception as exc:
            logger.error(f"Summary generation failed: {exc}")
            error_message = "Summary generation failed"
        else:
            error_message = "Unknown error"

        return {
            "executive_summary": "Summary generation failed",
            "key_findings": [],
            "metrics": [],
            "recommendations": [],
            "confidence": 0.0,
            "error": error_message,
        }

    def generate_report_summary(
        self,
        report_id: str,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate summary for a specific report."""
        # Get report data from state store
        store = _state_store()
        with store.transaction() as state:
            runs = state.get("runs", {})
        report = runs.get(report_id)

        if not report:
            return {"error": "Report not found"}

        # Extract content from report
        content = str(report)
        return self.generate_summary(content, correlation_id=correlation_id)
