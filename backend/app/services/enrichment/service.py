"""Service layer for Data Enrichment feature."""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type

from backend.app.utils.errors import AppError
from backend.app.repositories.state import store as state_store_module

from .cache import EnrichmentCache
from backend.app.schemas.enrichment import (
    EnrichmentSource,
    EnrichmentSourceCreate,
    EnrichmentSourceType,
    EnrichmentRequest,
    EnrichmentResult,
    EnrichedField,
    EnrichmentResponse,
    EnrichmentFieldMapping,
)
from .sources.base import EnrichmentSourceBase
from .sources.company import CompanyInfoSource
from .sources.address import AddressSource
from .sources.exchange import ExchangeRateSource

logger = logging.getLogger("neura.domain.enrichment")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _state_store():
    return state_store_module.state_store


# Registry of enrichment source types to their implementations
SOURCE_REGISTRY: Dict[EnrichmentSourceType, Type[EnrichmentSourceBase]] = {
    EnrichmentSourceType.COMPANY_INFO: CompanyInfoSource,
    EnrichmentSourceType.ADDRESS: AddressSource,
    EnrichmentSourceType.EXCHANGE_RATE: ExchangeRateSource,
}


class EnrichmentService:
    """Service for data enrichment operations."""

    def __init__(self):
        self._cache = EnrichmentCache(_state_store())
        self._source_instances: Dict[str, EnrichmentSourceBase] = {}

    def _get_source_instance(self, source: EnrichmentSource) -> EnrichmentSourceBase:
        """Get or create a source instance."""
        if source.id in self._source_instances:
            return self._source_instances[source.id]

        source_class = SOURCE_REGISTRY.get(source.type)
        if not source_class:
            raise AppError(
                code="unknown_source_type",
                message=f"Unknown enrichment source type: {source.type}",
                status_code=400,
            )

        instance = source_class(source.config)
        self._source_instances[source.id] = instance
        return instance

    def create_source(
        self,
        request: EnrichmentSourceCreate,
        correlation_id: Optional[str] = None,
    ) -> EnrichmentSource:
        """Create a new enrichment source."""
        logger.info(f"Creating enrichment source: {request.name}", extra={"correlation_id": correlation_id})

        source_id = str(uuid.uuid4())[:8]
        now = _now_iso()

        source = EnrichmentSource(
            id=source_id,
            name=request.name,
            type=request.type,
            description=request.description,
            config=request.config,
            cache_ttl_hours=request.cache_ttl_hours,
            created_at=now,
            updated_at=now,
        )

        # Persist to state store
        store = _state_store()
        with store.transaction() as state:
            state.setdefault("enrichment_sources", {})[source_id] = source.model_dump()

        return source

    def list_sources(self) -> List[EnrichmentSource]:
        """List all enrichment sources."""
        store = _state_store()
        with store.transaction() as state:
            sources = state.get("enrichment_sources", {})
        return [EnrichmentSource(**s) for s in sources.values()]

    def get_source(self, source_id: str) -> Optional[EnrichmentSource]:
        """Get an enrichment source by ID."""
        store = _state_store()
        with store.transaction() as state:
            source = state.get("enrichment_sources", {}).get(source_id)
        return EnrichmentSource(**source) if source else None

    def delete_source(self, source_id: str) -> bool:
        """Delete an enrichment source."""
        store = _state_store()
        with store.transaction() as state:
            sources = state.get("enrichment_sources", {})
            if source_id not in sources:
                return False
            del sources[source_id]

        # Clear cached instances
        self._source_instances.pop(source_id, None)

        # Invalidate cache for this source
        self._cache.invalidate(source_id)

        return True

    async def enrich(
        self,
        request: EnrichmentRequest,
        correlation_id: Optional[str] = None,
    ) -> EnrichmentResponse:
        """
        Enrich data with additional information.

        Args:
            request: Enrichment request with data and mappings
            correlation_id: Request correlation ID

        Returns:
            Enrichment response with results
        """
        logger.info(
            f"Enriching {len(request.data)} rows with {len(request.mappings)} mappings",
            extra={"correlation_id": correlation_id},
        )

        started = time.time()
        results: List[EnrichmentResult] = []
        cache_hits = 0
        cache_misses = 0
        enriched_count = 0

        # Build source lookup
        sources: Dict[str, EnrichmentSource] = {}
        for mapping in request.mappings:
            if mapping.enrichment_source_id not in sources:
                source = self.get_source(mapping.enrichment_source_id)
                if not source:
                    raise AppError(
                        code="source_not_found",
                        message=f"Enrichment source not found: {mapping.enrichment_source_id}",
                        status_code=404,
                    )
                if not source.enabled:
                    raise AppError(
                        code="source_disabled",
                        message=f"Enrichment source is disabled: {source.name}",
                        status_code=400,
                    )
                sources[mapping.enrichment_source_id] = source

        # Process each row
        for row_index, row in enumerate(request.data):
            enriched_fields: List[EnrichedField] = []
            errors: List[str] = []

            for mapping in request.mappings:
                source = sources[mapping.enrichment_source_id]
                source_instance = self._get_source_instance(source)

                # Get the lookup value
                lookup_value = row.get(mapping.source_field)
                if lookup_value is None:
                    continue

                # Check cache first
                cached_data = None
                if request.use_cache:
                    cached_data = self._cache.get(
                        source.id,
                        lookup_value,
                        max_age_hours=source.cache_ttl_hours,
                    )

                if cached_data:
                    cache_hits += 1
                    enrichment_data = cached_data
                    from_cache = True
                else:
                    cache_misses += 1
                    try:
                        enrichment_data = await source_instance.lookup(lookup_value)
                        if enrichment_data and request.use_cache:
                            self._cache.set(
                                source.id,
                                lookup_value,
                                enrichment_data,
                                ttl_hours=source.cache_ttl_hours,
                            )
                    except Exception as exc:
                        logger.warning("Enrichment lookup failed for %s: %s", mapping.source_field, exc)
                        errors.append(f"Lookup failed for {mapping.source_field}")
                        enrichment_data = None
                    from_cache = False

                if enrichment_data:
                    confidence = source_instance.get_confidence(enrichment_data)
                    for target_field in mapping.target_fields:
                        if target_field in enrichment_data:
                            enriched_fields.append(
                                EnrichedField(
                                    field=target_field,
                                    original_value=lookup_value,
                                    enriched_value=enrichment_data[target_field],
                                    confidence=confidence,
                                    source=source.name,
                                    cached=from_cache,
                                )
                            )

            if enriched_fields:
                enriched_count += 1

            results.append(
                EnrichmentResult(
                    row_index=row_index,
                    enriched_fields=enriched_fields,
                    errors=errors,
                )
            )

        processing_time_ms = int((time.time() - started) * 1000)

        return EnrichmentResponse(
            total_rows=len(request.data),
            enriched_rows=enriched_count,
            results=results,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            processing_time_ms=processing_time_ms,
        )

    async def preview_enrichment(
        self,
        sample_data: List[Dict[str, Any]],
        mappings: List[EnrichmentFieldMapping],
        correlation_id: Optional[str] = None,
    ) -> EnrichmentResponse:
        """
        Preview enrichment without caching results.

        Args:
            sample_data: Sample data rows
            mappings: Field mappings
            correlation_id: Request correlation ID

        Returns:
            Enrichment preview results
        """
        request = EnrichmentRequest(
            data=sample_data,
            mappings=mappings,
            use_cache=False,  # Don't cache preview results
        )
        return await self.enrich(request, correlation_id)

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self._cache.get_stats()

    def clear_cache(self, source_id: Optional[str] = None) -> int:
        """Clear enrichment cache."""
        return self._cache.invalidate(source_id)

    def get_available_source_types(self) -> List[Dict[str, Any]]:
        """Get list of available source types with their supported fields."""
        result = []
        for source_type, source_class in SOURCE_REGISTRY.items():
            instance = source_class({})
            result.append({
                "type": source_type.value,
                "name": source_type.value.replace("_", " ").title(),
                "supported_fields": instance.get_supported_fields(),
            })
        return result

    @staticmethod
    def get_builtin_sources() -> List[Dict[str, Any]]:
        """Return the catalog of built-in enrichment sources."""
        return [
            {
                "id": "company",
                "name": "Company Information",
                "type": EnrichmentSourceType.COMPANY_INFO.value,
                "description": "Enrich with company details (industry, size, revenue)",
                "required_fields": ["company_name"],
                "output_fields": ["industry", "company_size", "estimated_revenue", "founded_year"],
            },
            {
                "id": "address",
                "name": "Address Standardization",
                "type": EnrichmentSourceType.ADDRESS.value,
                "description": "Standardize and validate addresses",
                "required_fields": ["address"],
                "output_fields": ["formatted_address", "city", "state", "postal_code", "country"],
            },
            {
                "id": "exchange",
                "name": "Currency Exchange",
                "type": EnrichmentSourceType.EXCHANGE_RATE.value,
                "description": "Convert currencies to target currency",
                "required_fields": ["amount", "currency"],
                "output_fields": ["converted_amount", "exchange_rate", "target_currency"],
            },
        ]

    async def simple_enrich(
        self,
        data: List[Dict[str, Any]],
        sources: List[str],
        options: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Simplified enrichment for frontend.

        Args:
            data: List of data rows to enrich
            sources: List of source type IDs (e.g., ["company", "address"])
            options: Additional options (target_currency, etc.)
            correlation_id: Request correlation ID

        Returns:
            Dict with enriched_data, total_rows, enriched_rows, processing_time_ms
        """
        logger.info(
            f"Simple enrichment: {len(data)} rows with sources {sources}",
            extra={"correlation_id": correlation_id},
        )

        started = time.time()
        enriched_data = []
        enriched_count = 0

        # Map source IDs to source types (support multiple aliases)
        source_type_map = {
            "company": EnrichmentSourceType.COMPANY_INFO,
            "company_info": EnrichmentSourceType.COMPANY_INFO,
            "address": EnrichmentSourceType.ADDRESS,
            "exchange": EnrichmentSourceType.EXCHANGE_RATE,
            "exchange_rate": EnrichmentSourceType.EXCHANGE_RATE,
        }

        for row in data:
            enriched_row = dict(row)  # Copy original row
            row_enriched = False

            for source_id in sources:
                source_type = source_type_map.get(source_id)
                if not source_type:
                    continue

                source_class = SOURCE_REGISTRY.get(source_type)
                if not source_class:
                    continue

                # Create config with options
                config = dict(options) if options else {}
                source_instance = source_class(config)

                # Determine lookup field based on source type
                lookup_value = None
                if source_type == EnrichmentSourceType.COMPANY_INFO:
                    lookup_value = row.get("company_name") or row.get("company")
                elif source_type == EnrichmentSourceType.ADDRESS:
                    lookup_value = row.get("address")
                elif source_type == EnrichmentSourceType.EXCHANGE_RATE:
                    lookup_value = row.get("amount")
                    if lookup_value is not None:
                        # Pass as dict for proper parsing by ExchangeRateSource
                        from_currency = row.get("currency") or row.get("from_currency") or "USD"
                        target_currency = config.get("target_currency", "USD")
                        lookup_value = {
                            "amount": lookup_value,
                            "from_currency": from_currency,
                            "to_currency": target_currency,
                        }

                if lookup_value is None:
                    continue

                try:
                    # Pass lookup_value directly (can be string, dict, or number)
                    enrichment_result = await source_instance.lookup(lookup_value)
                    if enrichment_result:
                        enriched_row.update(enrichment_result)
                        row_enriched = True
                except Exception as exc:
                    logger.warning(f"Enrichment lookup failed: {exc}")

            enriched_data.append(enriched_row)
            if row_enriched:
                enriched_count += 1

        processing_time_ms = int((time.time() - started) * 1000)

        return {
            "enriched_data": enriched_data,
            "total_rows": len(data),
            "enriched_rows": enriched_count,
            "processing_time_ms": processing_time_ms,
        }

    async def simple_preview(
        self,
        data: List[Dict[str, Any]],
        sources: List[str],
        sample_size: int = 5,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Preview enrichment on a sample of data.

        Args:
            data: List of data rows
            sources: List of source type IDs
            sample_size: Number of rows to preview
            correlation_id: Request correlation ID

        Returns:
            Dict with preview results
        """
        # Take only sample_size rows
        sample_data = data[:sample_size]

        result = await self.simple_enrich(
            data=sample_data,
            sources=sources,
            options={},
            correlation_id=correlation_id,
        )

        return {
            "preview": result["enriched_data"],
            "total_rows": len(data),
            "enriched_rows": result["enriched_rows"],
            "processing_time_ms": result["processing_time_ms"],
        }
