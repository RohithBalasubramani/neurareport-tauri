"""Base class for enrichment sources."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class EnrichmentSourceBase(ABC):
    """Abstract base class for enrichment sources."""

    source_type: str = "base"
    supported_fields: List[str] = []

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the enrichment source.

        Args:
            config: Source-specific configuration
        """
        self.config = config

    @abstractmethod
    async def lookup(self, value: Any) -> Optional[Dict[str, Any]]:
        """
        Look up enrichment data for a value.

        Args:
            value: The value to look up (e.g., company name, address)

        Returns:
            Dictionary of enriched fields, or None if not found
        """
        pass

    @abstractmethod
    def get_supported_fields(self) -> List[str]:
        """
        Get list of fields this source can provide.

        Returns:
            List of field names
        """
        pass

    def validate_config(self) -> bool:
        """
        Validate the source configuration.

        Returns:
            True if configuration is valid
        """
        return True

    def get_confidence(self, result: Dict[str, Any]) -> float:
        """
        Calculate confidence score for a result.

        Args:
            result: The enrichment result

        Returns:
            Confidence score between 0 and 1
        """
        return 1.0
