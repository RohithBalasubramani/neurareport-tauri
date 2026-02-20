"""Company information enrichment source using LLM."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from backend.app.services.utils.llm import extract_json_from_llm_response
from .base import EnrichmentSourceBase

logger = logging.getLogger("neura.domain.enrichment.company")


class CompanyInfoSource(EnrichmentSourceBase):
    """
    Enrichment source for company information.

    Uses LLM to lookup company details like industry, size, location, etc.
    """

    source_type = "company_info"
    supported_fields = [
        "industry",
        "sector",
        "company_size",
        "founded_year",
        "headquarters_city",
        "headquarters_country",
        "website",
        "description",
    ]

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._llm_client = None

    def _get_llm_client(self):
        """Get or create LLM client."""
        if self._llm_client is None:
            from backend.app.services.llm.client import get_llm_client
            self._llm_client = get_llm_client()
        return self._llm_client

    async def lookup(self, value: Any) -> Optional[Dict[str, Any]]:
        """
        Look up company information.

        Args:
            value: Company name to look up

        Returns:
            Dictionary of company information
        """
        if not value or not isinstance(value, str):
            return None

        company_name = value.strip()
        if not company_name:
            return None

        try:
            client = self._get_llm_client()

            prompt = f"""Provide information about the company "{company_name}".

Return a JSON object with the following fields (use null for unknown values):
{{
  "industry": "Primary industry/sector",
  "sector": "Business sector",
  "company_size": "small/medium/large/enterprise",
  "founded_year": 1900,
  "headquarters_city": "City name",
  "headquarters_country": "Country name",
  "website": "https://example.com",
  "description": "Brief company description"
}}

Return ONLY the JSON object, no other text."""

            response = client.complete(
                messages=[{"role": "user", "content": prompt}],
                description="company_enrichment",
                temperature=0.0,
            )

            content = response["choices"][0]["message"]["content"]

            # Parse JSON from response (handles markdown code blocks from Claude)
            result = extract_json_from_llm_response(content, default=None)
            return result

        except Exception as exc:
            # Check for critical errors that should be re-raised
            exc_str = str(exc).lower()
            is_critical = any(indicator in exc_str for indicator in [
                "authentication", "api_key", "invalid_api_key", "unauthorized",
                "quota", "rate_limit", "insufficient_quota",
            ])

            if is_critical:
                logger.error(
                    f"Company lookup critical error for '{company_name}': {exc}",
                    exc_info=True,
                    extra={"event": "company_enrichment_critical_error", "company_name": company_name},
                )
                raise  # Re-raise critical errors (auth, quota, rate limit)

            # Non-critical errors: log with details but return None
            logger.warning(
                f"Company lookup failed for '{company_name}': {exc}",
                exc_info=True,  # Include stack trace for debugging
                extra={"event": "company_enrichment_failed", "company_name": company_name, "error_type": type(exc).__name__},
            )
            return None

    def get_supported_fields(self) -> List[str]:
        return self.supported_fields

    def get_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence based on how many fields are populated."""
        if not result:
            return 0.0

        populated = sum(1 for v in result.values() if v is not None)
        return min(populated / len(self.supported_fields), 1.0)
