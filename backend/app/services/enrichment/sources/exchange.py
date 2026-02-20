"""Currency exchange rate enrichment source with live API support."""
from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .base import EnrichmentSourceBase

logger = logging.getLogger("neura.domain.enrichment.exchange")

# Common exchange rates (fallback when API is unavailable)
# These are approximate rates as of Jan 2025 and should be used only as fallback
FALLBACK_RATES_USD = {
    # Major currencies
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 149.50,
    "CAD": 1.36,
    "AUD": 1.53,
    "CHF": 0.88,
    "CNY": 7.24,
    # Asian currencies
    "INR": 83.12,
    "KRW": 1325.0,
    "SGD": 1.34,
    "HKD": 7.82,
    "TWD": 31.50,
    "THB": 34.50,
    "MYR": 4.45,
    "IDR": 15800.0,
    "PHP": 56.20,
    "VND": 24500.0,
    "PKR": 278.0,
    "BDT": 110.0,
    # European currencies
    "NOK": 10.65,
    "SEK": 10.42,
    "DKK": 6.87,
    "PLN": 4.02,
    "CZK": 23.20,
    "HUF": 365.0,
    "RON": 4.60,
    "BGN": 1.80,
    "HRK": 6.95,
    "UAH": 41.50,
    "RUB": 92.50,
    "TRY": 32.15,
    # Americas
    "MXN": 17.15,
    "BRL": 4.97,
    "ARS": 875.0,
    "CLP": 950.0,
    "COP": 4050.0,
    "PEN": 3.72,
    # Middle East & Africa
    "ILS": 3.70,
    "AED": 3.67,
    "SAR": 3.75,
    "QAR": 3.64,
    "KWD": 0.31,
    "BHD": 0.38,
    "OMR": 0.38,
    "EGP": 30.90,
    "ZAR": 18.75,
    "NGN": 1580.0,
    "KES": 153.0,
    # Oceania
    "NZD": 1.64,
    "FJD": 2.27,
}

# API configuration
EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY", "")
# Free tier APIs (in order of preference):
# 1. exchangerate.host - No API key needed for basic usage
# 2. open.er-api.com - Free tier available
# 3. frankfurter.app - Free ECB rates
EXCHANGE_API_URLS = [
    "https://api.exchangerate.host/latest",  # Free, no key needed
    "https://api.frankfurter.app/latest",    # Free ECB rates
]

# In-memory cache for API rates (refresh every 6 hours)
_RATES_CACHE: Dict[str, Any] = {}
_CACHE_TTL_SECONDS = 6 * 60 * 60  # 6 hours


class ExchangeRateSource(EnrichmentSourceBase):
    """
    Enrichment source for currency exchange rates.

    Converts amounts between currencies using live exchange rates from APIs,
    with fallback to cached/hardcoded rates when APIs are unavailable.
    """

    source_type = "exchange_rate"
    supported_fields = [
        "converted_amount",
        "exchange_rate",
        "source_currency",
        "target_currency",
        "rate_date",
        "rate_source",
    ]

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_currency = config.get("base_currency", "USD")
        self.target_currency = config.get("target_currency", "USD")
        self._use_live_rates = config.get("use_live_rates", True)

    @staticmethod
    def _build_api_params(api_url: str, base: str) -> Dict[str, str]:
        if "frankfurter" in api_url or "exchangerate.host" in api_url:
            return {"base": base}
        return {"from": base}

    async def _fetch_live_rates(self, base: str = "USD") -> Optional[Dict[str, float]]:
        """
        Fetch live exchange rates from API.

        Args:
            base: Base currency for rates

        Returns:
            Dictionary of currency -> rate mappings, or None if failed
        """
        global _RATES_CACHE

        cache_key = f"rates_{base}"
        cached = _RATES_CACHE.get(cache_key)
        if cached:
            cache_time = cached.get("_timestamp", 0)
            if time.time() - cache_time < _CACHE_TTL_SECONDS:
                rates = {k: v for k, v in cached.items() if k != "_timestamp"}
                return rates

        # Try httpx first (commonly available in FastAPI projects)
        try:
            import httpx
            return await self._fetch_with_httpx(base, cache_key)
        except ImportError:
            pass

        # Fall back to aiohttp
        try:
            import aiohttp
            return await self._fetch_with_aiohttp(base, cache_key)
        except ImportError:
            pass

        # Last resort: try synchronous requests
        try:
            import requests
            return self._fetch_with_requests_sync(base, cache_key)
        except ImportError:
            logger.warning("No HTTP library available for live rates")
            return None

    async def _fetch_with_httpx(self, base: str, cache_key: str) -> Optional[Dict[str, float]]:
        """Fetch rates using httpx (async)."""
        import httpx
        global _RATES_CACHE

        async with httpx.AsyncClient(timeout=10.0) as client:
            for api_url in EXCHANGE_API_URLS:
                try:
                    params = self._build_api_params(api_url, base)
                    response = await client.get(api_url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        rates = data.get("rates", {})
                        if rates:
                            _RATES_CACHE[cache_key] = {
                                **rates,
                                "_timestamp": time.time(),
                            }
                            logger.info(
                                f"Fetched live exchange rates from {api_url}",
                                extra={"currencies": len(rates), "base": base},
                            )
                            return rates
                except Exception as exc:
                    logger.debug(f"API {api_url} failed with httpx: {exc}")
                    continue

        logger.warning("All exchange rate APIs failed (httpx), using fallback rates")
        return None

    async def _fetch_with_aiohttp(self, base: str, cache_key: str) -> Optional[Dict[str, float]]:
        """Fetch rates using aiohttp."""
        import aiohttp
        global _RATES_CACHE

        for api_url in EXCHANGE_API_URLS:
            try:
                params = self._build_api_params(api_url, base)
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        api_url,
                        params=params,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            rates = data.get("rates", {})
                            if rates:
                                _RATES_CACHE[cache_key] = {
                                    **rates,
                                    "_timestamp": time.time(),
                                }
                                logger.info(
                                    f"Fetched live exchange rates from {api_url}",
                                    extra={"currencies": len(rates), "base": base},
                                )
                                return rates
            except Exception as exc:
                logger.debug(f"API {api_url} failed with aiohttp: {exc}")
                continue

        logger.warning("All exchange rate APIs failed (aiohttp), using fallback rates")
        return None

    def _fetch_with_requests_sync(self, base: str, cache_key: str) -> Optional[Dict[str, float]]:
        """Fetch rates using requests (sync, last resort)."""
        import requests
        global _RATES_CACHE

        for api_url in EXCHANGE_API_URLS:
            try:
                params = self._build_api_params(api_url, base)
                response = requests.get(api_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    rates = data.get("rates", {})
                    if rates:
                        _RATES_CACHE[cache_key] = {
                            **rates,
                            "_timestamp": time.time(),
                        }
                        logger.info(
                            f"Fetched live exchange rates from {api_url} (sync)",
                            extra={"currencies": len(rates), "base": base},
                        )
                        return rates
            except Exception as exc:
                logger.debug(f"API {api_url} failed with requests: {exc}")
                continue

        logger.warning("All exchange rate APIs failed (requests), using fallback rates")
        return None

    async def lookup(self, value: Any) -> Optional[Dict[str, Any]]:
        """
        Convert currency amount.

        Args:
            value: Can be:
                - A number (uses configured currencies)
                - A dict with 'amount', 'from_currency', 'to_currency'
                - A string like "100 EUR" or "EUR 100"

        Returns:
            Dictionary with converted amount and rate info
        """
        if value is None:
            return None

        try:
            amount: float
            from_currency: str
            to_currency: str

            if isinstance(value, dict):
                amount = float(value.get("amount", 0))
                from_currency = value.get("from_currency", self.base_currency).upper()
                to_currency = value.get("to_currency", self.target_currency).upper()
            elif isinstance(value, (int, float)):
                amount = float(value)
                from_currency = self.base_currency
                to_currency = self.target_currency
            elif isinstance(value, str):
                # Parse string like "100 EUR" or "EUR 100" or "100|EUR"
                if "|" in value:
                    parts = value.strip().split("|")
                    amount = float(parts[0].replace(",", ""))
                    from_currency = parts[1].upper() if len(parts) > 1 else self.base_currency
                else:
                    parts = value.strip().split()
                    if len(parts) == 2:
                        if parts[0].replace(".", "").replace(",", "").replace("-", "").isdigit():
                            amount = float(parts[0].replace(",", ""))
                            from_currency = parts[1].upper()
                        else:
                            from_currency = parts[0].upper()
                            amount = float(parts[1].replace(",", ""))
                    else:
                        amount = float(value.replace(",", ""))
                        from_currency = self.base_currency
                to_currency = self.target_currency
            else:
                return None

            # Get exchange rate (live or fallback)
            rate, source = await self._get_rate_async(from_currency, to_currency)
            if rate is None:
                return None

            converted = amount * rate

            return {
                "converted_amount": round(converted, 2),
                "exchange_rate": round(rate, 6),
                "source_currency": from_currency,
                "target_currency": to_currency,
                "rate_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "rate_source": source,
            }

        except Exception as exc:
            logger.warning(f"Exchange rate lookup failed for '{value}': {exc}")
            return None

    async def _get_rate_async(
        self, from_currency: str, to_currency: str
    ) -> tuple[Optional[float], str]:
        """
        Get exchange rate between two currencies asynchronously.

        Returns:
            Tuple of (rate, source) where source is 'live' or 'fallback'
        """
        if from_currency == to_currency:
            return 1.0, "identity"

        # Try live rates first
        if self._use_live_rates:
            live_rates = await self._fetch_live_rates(from_currency)
            if live_rates:
                rate = live_rates.get(to_currency)
                if rate:
                    return float(rate), "live"
                # Try inverse lookup
                inverse_rates = await self._fetch_live_rates(to_currency)
                if inverse_rates:
                    inverse_rate = inverse_rates.get(from_currency)
                    if inverse_rate:
                        return 1.0 / float(inverse_rate), "live"

        # Fall back to hardcoded rates
        return self._get_fallback_rate(from_currency, to_currency), "fallback"

    def _get_fallback_rate(
        self, from_currency: str, to_currency: str
    ) -> Optional[float]:
        """Get exchange rate from fallback hardcoded rates."""
        if from_currency == to_currency:
            return 1.0

        try:
            if from_currency == "USD":
                rate = FALLBACK_RATES_USD.get(to_currency)
                if rate:
                    return rate
            elif to_currency == "USD":
                rate = FALLBACK_RATES_USD.get(from_currency)
                if rate:
                    return 1.0 / rate
            else:
                # Convert via USD
                from_usd = FALLBACK_RATES_USD.get(from_currency)
                to_usd = FALLBACK_RATES_USD.get(to_currency)
                if from_usd and to_usd:
                    return to_usd / from_usd

            logger.warning(f"No fallback rate found for {from_currency} -> {to_currency}")
            return None

        except Exception as exc:
            logger.error(f"Fallback rate calculation error: {exc}")
            return None

    def get_supported_fields(self) -> List[str]:
        return self.supported_fields

    def get_confidence(self, result: Dict[str, Any]) -> float:
        """
        Exchange rates confidence based on data source.

        Live rates get higher confidence than fallback rates.
        """
        if not result or not result.get("exchange_rate"):
            return 0.0

        rate_source = result.get("rate_source", "fallback")
        if rate_source == "live":
            return 0.99  # High confidence for live API rates
        elif rate_source == "identity":
            return 1.0  # Same currency conversion
        else:
            return 0.85  # Lower confidence for fallback rates

    def validate_config(self) -> bool:
        """Validate source configuration."""
        # No required config for exchange rates
        return True


def clear_exchange_rate_cache() -> None:
    """Clear the in-memory exchange rate cache."""
    global _RATES_CACHE
    _RATES_CACHE.clear()
    logger.info("Exchange rate cache cleared")


def get_exchange_rate_cache_status() -> Dict[str, Any]:
    """Get current exchange rate cache status for monitoring."""
    cache_info = {}
    for key, value in _RATES_CACHE.items():
        if isinstance(value, dict) and "_timestamp" in value:
            cache_info[key] = {
                "currencies": len(value) - 1,  # Exclude _timestamp
                "age_seconds": int(time.time() - value.get("_timestamp", 0)),
                "is_stale": time.time() - value.get("_timestamp", 0) > _CACHE_TTL_SECONDS,
            }
    return {
        "cache_ttl_seconds": _CACHE_TTL_SECONDS,
        "cached_bases": list(cache_info.keys()),
        "cache_details": cache_info,
        "fallback_currencies": len(FALLBACK_RATES_USD),
    }


def get_supported_currencies() -> List[str]:
    """Get list of all supported currency codes."""
    return ["USD"] + sorted(FALLBACK_RATES_USD.keys())


async def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    use_live_rates: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Convenience function to convert currency amounts.

    Args:
        amount: Amount to convert
        from_currency: Source currency code (e.g., "USD")
        to_currency: Target currency code (e.g., "EUR")
        use_live_rates: Whether to try live API rates first

    Returns:
        Conversion result dict or None if failed
    """
    source = ExchangeRateSource({
        "base_currency": from_currency.upper(),
        "target_currency": to_currency.upper(),
        "use_live_rates": use_live_rates,
    })
    return await source.lookup(amount)
