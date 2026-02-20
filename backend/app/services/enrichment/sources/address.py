"""Address normalization and enrichment source."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from backend.app.services.utils.llm import extract_json_from_llm_response
from .base import EnrichmentSourceBase

logger = logging.getLogger("neura.domain.enrichment.address")


class AddressSource(EnrichmentSourceBase):
    """
    Enrichment source for address normalization and geocoding.

    Uses LLM to parse and normalize addresses.
    """

    source_type = "address"
    supported_fields = [
        "street_address",
        "city",
        "state_province",
        "postal_code",
        "country",
        "country_code",
        "formatted_address",
        "address_type",  # residential, commercial, po_box
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
        Parse and normalize an address.

        Args:
            value: Raw address string

        Returns:
            Dictionary of parsed address components
        """
        if not value or not isinstance(value, str):
            return None

        address = value.strip()
        if not address:
            return None

        try:
            client = self._get_llm_client()

            prompt = f"""Parse and normalize this address into components:

Address: "{address}"

Return a JSON object with the following fields (use null for unknown/missing):
{{
  "street_address": "123 Main St, Suite 100",
  "city": "City name",
  "state_province": "State or province name",
  "postal_code": "12345",
  "country": "Country name",
  "country_code": "US",
  "formatted_address": "Complete formatted address",
  "address_type": "residential|commercial|po_box|unknown"
}}

Return ONLY the JSON object, no other text."""

            response = client.complete(
                messages=[{"role": "user", "content": prompt}],
                description="address_enrichment",
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
                    f"Address lookup critical error for '{address[:50]}...': {exc}",
                    exc_info=True,
                    extra={"event": "address_enrichment_critical_error", "address_preview": address[:50]},
                )
                raise  # Re-raise critical errors (auth, quota, rate limit)

            # Non-critical errors: log with details but return None
            logger.warning(
                f"Address lookup failed for '{address[:50]}...': {exc}",
                exc_info=True,  # Include stack trace for debugging
                extra={"event": "address_enrichment_failed", "address_preview": address[:50], "error_type": type(exc).__name__},
            )
            return None

    def get_supported_fields(self) -> List[str]:
        return self.supported_fields

    def get_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence based on how many fields are populated."""
        if not result:
            return 0.0

        # Weight important fields more heavily
        weights = {
            "city": 0.2,
            "country": 0.2,
            "postal_code": 0.15,
            "street_address": 0.15,
            "state_province": 0.1,
            "country_code": 0.1,
            "formatted_address": 0.1,
        }

        score = 0.0
        for field, weight in weights.items():
            if result.get(field):
                score += weight

        return min(score, 1.0)
