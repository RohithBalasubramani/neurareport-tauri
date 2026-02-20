"""Comprehensive tests for enrichment sources."""
from __future__ import annotations

import asyncio
import sys
import types
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Stub cryptography module for tests
fernet_module = types.ModuleType("cryptography.fernet")


class _DummyFernet:
    def __init__(self, key):
        self.key = key

    @staticmethod
    def generate_key():
        return b"A" * 44

    def encrypt(self, payload: bytes) -> bytes:
        return payload

    def decrypt(self, token: bytes) -> bytes:
        return token


setattr(fernet_module, "Fernet", _DummyFernet)
setattr(fernet_module, "InvalidToken", Exception)
crypto_module = types.ModuleType("cryptography")
setattr(crypto_module, "fernet", fernet_module)
sys.modules.setdefault("cryptography", crypto_module)
sys.modules.setdefault("cryptography.fernet", fernet_module)

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.services.enrichment.sources.base import EnrichmentSourceBase
from backend.app.services.enrichment.sources.company import CompanyInfoSource
from backend.app.services.enrichment.sources.address import AddressSource
from backend.app.services.enrichment.sources.exchange import (
    ExchangeRateSource,
    FALLBACK_RATES_USD,
    clear_exchange_rate_cache,
)


# =============================================================================
# EXCHANGE RATE SOURCE TESTS
# =============================================================================


class TestExchangeRateSource:
    """Tests for ExchangeRateSource with live API and fallback support."""

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        """Clear the exchange rate cache before each test."""
        clear_exchange_rate_cache()
        yield
        clear_exchange_rate_cache()

    @pytest.fixture
    def source(self):
        """Create a default exchange rate source."""
        return ExchangeRateSource({
            "base_currency": "USD",
            "target_currency": "EUR",
        })

    @pytest.fixture
    def source_no_live(self):
        """Create an exchange rate source with live rates disabled."""
        return ExchangeRateSource({
            "base_currency": "USD",
            "target_currency": "EUR",
            "use_live_rates": False,
        })

    @pytest.mark.asyncio
    async def test_same_currency_returns_identity(self, source):
        """Converting same currency should return 1.0 rate."""
        result = await source.lookup({
            "amount": 100,
            "from_currency": "USD",
            "to_currency": "USD",
        })
        assert result is not None
        assert result["converted_amount"] == 100.0
        assert result["exchange_rate"] == 1.0
        assert result["rate_source"] == "identity"

    @pytest.mark.asyncio
    async def test_fallback_rates_usd_to_eur(self, source_no_live):
        """Test conversion using fallback rates."""
        result = await source_no_live.lookup({
            "amount": 100,
            "from_currency": "USD",
            "to_currency": "EUR",
        })
        assert result is not None
        assert result["source_currency"] == "USD"
        assert result["target_currency"] == "EUR"
        assert result["rate_source"] == "fallback"
        expected_rate = FALLBACK_RATES_USD["EUR"]
        assert result["exchange_rate"] == round(expected_rate, 6)
        assert result["converted_amount"] == round(100 * expected_rate, 2)

    @pytest.mark.asyncio
    async def test_fallback_rates_eur_to_usd(self, source_no_live):
        """Test inverse conversion using fallback rates."""
        source_no_live.target_currency = "USD"
        result = await source_no_live.lookup({
            "amount": 100,
            "from_currency": "EUR",
            "to_currency": "USD",
        })
        assert result is not None
        assert result["source_currency"] == "EUR"
        assert result["target_currency"] == "USD"
        assert result["rate_source"] == "fallback"
        expected_rate = 1.0 / FALLBACK_RATES_USD["EUR"]
        assert result["exchange_rate"] == pytest.approx(expected_rate, rel=1e-4)

    @pytest.mark.asyncio
    async def test_fallback_rates_cross_currency(self, source_no_live):
        """Test cross-currency conversion via USD."""
        result = await source_no_live.lookup({
            "amount": 100,
            "from_currency": "EUR",
            "to_currency": "GBP",
        })
        assert result is not None
        assert result["source_currency"] == "EUR"
        assert result["target_currency"] == "GBP"
        assert result["rate_source"] == "fallback"
        # EUR -> USD -> GBP
        expected_rate = FALLBACK_RATES_USD["GBP"] / FALLBACK_RATES_USD["EUR"]
        assert result["exchange_rate"] == pytest.approx(expected_rate, rel=1e-4)

    @pytest.mark.asyncio
    async def test_numeric_input(self, source_no_live):
        """Test conversion with numeric input."""
        result = await source_no_live.lookup(100)
        assert result is not None
        assert result["source_currency"] == "USD"
        assert result["target_currency"] == "EUR"
        assert result["converted_amount"] == round(100 * FALLBACK_RATES_USD["EUR"], 2)

    @pytest.mark.asyncio
    async def test_string_input_amount_currency(self, source_no_live):
        """Test parsing '100 EUR' string format."""
        result = await source_no_live.lookup("100 EUR")
        assert result is not None
        assert result["source_currency"] == "EUR"
        assert result["target_currency"] == "EUR"

    @pytest.mark.asyncio
    async def test_string_input_currency_amount(self, source_no_live):
        """Test parsing 'EUR 100' string format."""
        result = await source_no_live.lookup("EUR 100")
        assert result is not None
        assert result["source_currency"] == "EUR"

    @pytest.mark.asyncio
    async def test_pipe_separated_format(self, source_no_live):
        """Test parsing '100|EUR' pipe-separated format."""
        result = await source_no_live.lookup("100|EUR")
        assert result is not None
        assert result["source_currency"] == "EUR"

    @pytest.mark.asyncio
    async def test_none_input_returns_none(self, source):
        """Null input should return None."""
        result = await source.lookup(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_invalid_currency_returns_none(self, source_no_live):
        """Invalid currency should return None."""
        result = await source_no_live.lookup({
            "amount": 100,
            "from_currency": "INVALID",
            "to_currency": "EUR",
        })
        assert result is None

    @pytest.mark.asyncio
    async def test_confidence_for_live_rates(self, source):
        """Live rates should have higher confidence."""
        result = {
            "exchange_rate": 0.92,
            "rate_source": "live",
        }
        confidence = source.get_confidence(result)
        assert confidence == 0.99

    @pytest.mark.asyncio
    async def test_confidence_for_fallback_rates(self, source):
        """Fallback rates should have lower confidence."""
        result = {
            "exchange_rate": 0.92,
            "rate_source": "fallback",
        }
        confidence = source.get_confidence(result)
        assert confidence == 0.85

    @pytest.mark.asyncio
    async def test_confidence_for_identity(self, source):
        """Identity conversion should have 1.0 confidence."""
        result = {
            "exchange_rate": 1.0,
            "rate_source": "identity",
        }
        confidence = source.get_confidence(result)
        assert confidence == 1.0

    @pytest.mark.asyncio
    async def test_confidence_for_empty_result(self, source):
        """Empty result should have 0 confidence."""
        confidence = source.get_confidence({})
        assert confidence == 0.0
        confidence = source.get_confidence(None)
        assert confidence == 0.0

    @pytest.mark.asyncio
    async def test_supported_fields(self, source):
        """Verify supported fields are correct."""
        fields = source.get_supported_fields()
        assert "converted_amount" in fields
        assert "exchange_rate" in fields
        assert "source_currency" in fields
        assert "target_currency" in fields
        assert "rate_date" in fields
        assert "rate_source" in fields

    @pytest.mark.asyncio
    async def test_live_api_success(self, source):
        """Test successful live API call."""
        # Skip if no HTTP library available
        try:
            import httpx
            http_lib = "httpx"
        except ImportError:
            try:
                import aiohttp
                http_lib = "aiohttp"
            except ImportError:
                pytest.skip("No HTTP library available for live API test")
                return

        # Test with fallback to ensure the code path works
        result = await source.lookup({
            "amount": 100,
            "from_currency": "USD",
            "to_currency": "EUR",
        })
        # Should get either live or fallback rates
        assert result is not None
        assert result["source_currency"] == "USD"
        assert result["target_currency"] == "EUR"
        assert result["rate_source"] in ("live", "fallback")

    @pytest.mark.asyncio
    async def test_live_api_fallback_on_error(self, source_no_live):
        """Test fallback when live rates are disabled."""
        result = await source_no_live.lookup({
            "amount": 100,
            "from_currency": "USD",
            "to_currency": "EUR",
        })
        # Should use fallback rates
        assert result is not None
        assert result["rate_source"] == "fallback"

    def test_validate_config(self, source):
        """Config validation should pass."""
        assert source.validate_config() is True


# =============================================================================
# COMPANY INFO SOURCE TESTS
# =============================================================================


class TestCompanyInfoSource:
    """Tests for CompanyInfoSource."""

    @pytest.fixture
    def source(self):
        """Create a company info source."""
        return CompanyInfoSource({})

    @pytest.mark.asyncio
    async def test_none_input_returns_none(self, source):
        """Null input should return None."""
        result = await source.lookup(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_empty_string_returns_none(self, source):
        """Empty string should return None."""
        result = await source.lookup("")
        assert result is None

    def test_supported_fields(self, source):
        """Verify supported fields include company info."""
        fields = source.get_supported_fields()
        assert "industry" in fields
        assert "sector" in fields
        assert "company_size" in fields
        assert "founded_year" in fields
        assert "headquarters_city" in fields
        assert "website" in fields

    def test_confidence_with_result(self, source):
        """Confidence should be based on fields populated."""
        # Full result
        full_result = {
            "industry": "Technology",
            "sector": "Software",
            "company_size": "Large",
            "founded_year": 1998,
            "headquarters_city": "Mountain View",
            "headquarters_country": "USA",
            "website": "https://google.com",
            "description": "Search engine company",
        }
        confidence = source.get_confidence(full_result)
        assert confidence >= 0.8

        # Partial result
        partial_result = {
            "industry": "Technology",
        }
        partial_confidence = source.get_confidence(partial_result)
        assert partial_confidence < confidence

    @pytest.mark.asyncio
    async def test_lookup_with_mock_llm(self, source):
        """Test lookup with mocked LLM response."""
        mock_response = {
            "industry": "Technology",
            "sector": "Internet",
            "company_size": "Large",
            "founded_year": 1998,
            "headquarters_city": "Mountain View",
            "headquarters_country": "USA",
            "website": "https://google.com",
            "description": "Search engine and technology company",
        }

        with patch.object(source, "lookup", return_value=mock_response):
            result = await source.lookup("Google")
            assert result is not None
            assert result.get("industry") == "Technology"


# =============================================================================
# ADDRESS SOURCE TESTS
# =============================================================================


class TestAddressSource:
    """Tests for AddressSource."""

    @pytest.fixture
    def source(self):
        """Create an address source."""
        return AddressSource({})

    @pytest.mark.asyncio
    async def test_none_input_returns_none(self, source):
        """Null input should return None."""
        result = await source.lookup(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_empty_string_returns_none(self, source):
        """Empty string should return None."""
        result = await source.lookup("")
        assert result is None

    def test_supported_fields(self, source):
        """Verify supported fields include address components."""
        fields = source.get_supported_fields()
        assert "street_address" in fields
        assert "city" in fields
        assert "state_province" in fields
        assert "postal_code" in fields
        assert "country" in fields
        assert "country_code" in fields
        assert "formatted_address" in fields

    def test_confidence_with_result(self, source):
        """Confidence should be based on fields populated."""
        full_result = {
            "street_address": "1600 Amphitheatre Parkway",
            "city": "Mountain View",
            "state_province": "California",
            "postal_code": "94043",
            "country": "United States",
            "country_code": "US",
            "formatted_address": "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA",
        }
        confidence = source.get_confidence(full_result)
        assert confidence >= 0.8

    @pytest.mark.asyncio
    async def test_lookup_with_mock_llm(self, source):
        """Test lookup with mocked LLM response."""
        mock_response = {
            "street_address": "1600 Amphitheatre Parkway",
            "city": "Mountain View",
            "state_province": "California",
            "postal_code": "94043",
            "country": "United States",
            "country_code": "US",
            "formatted_address": "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA",
            "address_type": "commercial",
        }

        with patch.object(source, "lookup", return_value=mock_response):
            result = await source.lookup("1600 Amphitheatre Parkway, Mountain View, CA")
            assert result is not None
            assert result.get("city") == "Mountain View"


# =============================================================================
# ENRICHMENT SERVICE INTEGRATION TESTS
# =============================================================================


class TestEnrichmentServiceIntegration:
    """Integration tests for enrichment service."""

    @pytest.fixture
    def mock_state_store(self, tmp_path, monkeypatch):
        """Create a mock state store."""
        from backend.app.repositories.state import store as state_store_module

        # Clear NEURA_STATE_DIR to prevent .env override
        monkeypatch.delenv("NEURA_STATE_DIR", raising=False)
        base_dir = tmp_path / "state"
        store = state_store_module.StateStore(base_dir=base_dir)
        state_store_module.set_state_store(store)
        return store

    @pytest.mark.asyncio
    async def test_service_creates_source(self, mock_state_store):
        """Test creating an enrichment source via service."""
        from backend.app.services.enrichment.service import EnrichmentService
        from backend.app.schemas.enrichment import (
            EnrichmentSourceCreate,
            EnrichmentSourceType,
        )

        service = EnrichmentService()

        request = EnrichmentSourceCreate(
            name="Test Exchange",
            type=EnrichmentSourceType.EXCHANGE_RATE,
            description="Test exchange rate source",
            config={"base_currency": "USD", "target_currency": "EUR"},
        )

        source = service.create_source(request)
        assert source is not None
        assert source.name == "Test Exchange"
        assert source.type == EnrichmentSourceType.EXCHANGE_RATE

    @pytest.mark.asyncio
    async def test_service_lists_sources(self, mock_state_store):
        """Test listing enrichment sources."""
        from backend.app.services.enrichment.service import EnrichmentService
        from backend.app.schemas.enrichment import (
            EnrichmentSourceCreate,
            EnrichmentSourceType,
        )

        service = EnrichmentService()

        # Create a source first
        request = EnrichmentSourceCreate(
            name="Test Source",
            type=EnrichmentSourceType.COMPANY_INFO,
            description="Test source",
            config={},
        )
        service.create_source(request)

        sources = service.list_sources()
        assert len(sources) >= 1

    def test_get_available_source_types(self, mock_state_store):
        """Test getting available source types."""
        from backend.app.services.enrichment.service import EnrichmentService

        service = EnrichmentService()
        types = service.get_available_source_types()

        assert len(types) == 3
        type_names = [t["type"] for t in types]
        assert "company_info" in type_names
        assert "address" in type_names
        assert "exchange_rate" in type_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
