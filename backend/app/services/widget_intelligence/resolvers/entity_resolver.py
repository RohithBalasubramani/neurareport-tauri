"""
Deterministic entity resolution with plural handling and DB discovery.

Improvements over original V6:
1. Plural handling: "all pumps", "cooling towers" → discovers ALL instances from DB
2. DB instance discovery: queries information_schema for actual tables
3. Broad query detection: "power distribution across the plant" → multiple entity types
4. Better metric inference: "vibration or bearing issues" → pump (not motor)
"""

from __future__ import annotations

import logging
import re
from typing import Any

from backend.app.services.widget_intelligence.config import ENTITY_PREFIX_MAP, NUMBER_WORDS
from backend.app.services.widget_intelligence.models.intent import ResolvedEntity

logger = logging.getLogger(__name__)

# Default metrics per equipment prefix
_DEFAULT_METRICS: dict[str, tuple[str, str]] = {
    "trf": ("active_power_kw", "kW"),
    "dg": ("active_power_kw", "kW"),
    "ups": ("load_percent", "%"),
    "chiller": ("power_consumption_kw", "kW"),
    "ahu": ("supply_air_temp_c", "°C"),
    "ct": ("fan_motor_power_kw", "kW"),
    "pump": ("motor_power_kw", "kW"),
    "compressor": ("discharge_pressure_bar", "bar"),
    "motor": ("active_power_kw", "kW"),
    "em": ("active_power_total_kw", "kW"),
    "lt_db": ("active_power_kw", "kW"),
    "lt_mcc": ("active_power_kw", "kW"),
    "lt_pcc": ("active_power_kw", "kW"),
    "lt_vfd": ("output_frequency_hz", "Hz"),
    "lt_apfc": ("power_factor", ""),
    "lt_bd": ("active_power_kw", "kW"),
    "lt_feeder": ("active_power_kw", "kW"),
    "lt_incomer": ("active_power_kw", "kW"),
    "em_solar": ("active_power_kw", "kW"),
    "bms": ("battery_charge_pct", "%"),
    "fire": ("status", ""),
    "wtp": ("flow_rate_m3h", "m³/h"),
    "stp": ("flow_rate_m3h", "m³/h"),
    "boiler": ("steam_pressure_bar", "bar"),
}

# Words that signal "all instances" (plural / fleet-level queries)
_ALL_SIGNALS = frozenset({
    "all", "every", "each", "fleet", "entire", "across", "overall",
    "plant", "facility", "factory", "site",
})

# Plural forms → singular equipment name
_PLURAL_MAP: dict[str, str] = {
    "transformers": "transformer",
    "generators": "generator",
    "gensets": "genset",
    "chillers": "chiller",
    "ahus": "ahu",
    "cooling towers": "cooling tower",
    "pumps": "pump",
    "compressors": "compressor",
    "motors": "motor",
    "meters": "meter",
    "energy meters": "energy meter",
    "batteries": "battery",
    "boilers": "boiler",
    "feeders": "feeder",
    "incomers": "incomer",
}

# Broad query keywords that imply multiple equipment types
_BROAD_QUERY_MAP: dict[str, list[str]] = {
    "power distribution": ["trf", "chiller", "pump", "ct", "em", "lt_db"],
    "power across": ["trf", "chiller", "pump", "ct", "em", "lt_db"],
    "power distributed": ["trf", "chiller", "pump", "ct", "em", "lt_db"],
    "energy consumption": ["em", "trf", "chiller", "pump", "ct"],
    "fleet health": ["trf", "chiller", "pump", "ct"],
    "plant overview": ["trf", "em", "chiller", "pump", "ct"],
    "overall status": ["trf", "em", "chiller", "pump"],
    "equipment health": ["trf", "chiller", "pump", "motor"],
    "hvac": ["chiller", "ahu", "ct", "pump"],
    "electrical": ["trf", "em", "lt_db", "dg", "ups"],
    "cooling": ["chiller", "ct", "pump"],
}


class EntityResolver:
    """
    Deterministic entity resolver with plural handling and DB discovery.

    Resolution strategy:
    1. Check for broad/fleet-level queries ("power distribution across the plant")
    2. Check for plural equipment mentions ("all cooling towers")
    3. Check for specific equipment mentions ("transformer 1")
    4. Infer from metric keywords ("vibration" → pump/motor)
    5. Default to energy meter overview
    """

    def __init__(self, db: Any = None):
        self._db = db
        self._known_tables: set[str] | None = None

    def resolve(self, query: str) -> list[ResolvedEntity]:
        """
        Extract entities from query text.

        Resolution order (specific → general):
        1. Plural forms ("all cooling towers" → ct with all instances)
        2. Specific equipment mentions ("cooling tower 3" → ct_003)
        3. Broad query patterns ("power distribution" → trf, em, lt_db)
        4. Metric keyword inference ("vibration" → pump)
        5. Default to energy meter overview
        """
        query_lower = query.lower()
        entities: list[ResolvedEntity] = []
        seen_prefixes: set[str] = set()

        # Check if this is a broad/fleet-level query
        is_broad = any(signal in query_lower for signal in _ALL_SIGNALS)

        # ── Step 1: Plural forms → all instances (most specific) ──
        # Check longest plurals first to avoid "meter" matching before "energy meter"
        for plural, singular in sorted(_PLURAL_MAP.items(), key=lambda x: -len(x[0])):
            if plural in query_lower:
                prefix = ENTITY_PREFIX_MAP.get(singular)
                if prefix and prefix not in seen_prefixes:
                    metric, unit = _DEFAULT_METRICS.get(prefix, ("", ""))
                    entities.append(ResolvedEntity(
                        name=singular,
                        table_prefix=prefix,
                        default_metric=metric,
                        default_unit=unit,
                        instances=[],  # Will be discovered from DB in catalog stage
                        is_primary=len(entities) == 0,
                    ))
                    seen_prefixes.add(prefix)

        # ── Step 2: Specific equipment mentions ──
        # Check longest names first ("cooling tower" before "motor", "energy meter" before "meter")
        for name, prefix in sorted(ENTITY_PREFIX_MAP.items(), key=lambda x: -len(x[0])):
            if name in query_lower and prefix not in seen_prefixes:
                if is_broad:
                    # Broad query + entity mention → all instances
                    instances = []
                else:
                    instances = self._extract_instances(query_lower, name, prefix)
                metric, unit = _DEFAULT_METRICS.get(prefix, ("", ""))
                entities.append(ResolvedEntity(
                    name=name,
                    table_prefix=prefix,
                    default_metric=metric,
                    default_unit=unit,
                    instances=instances,
                    is_primary=len(entities) == 0,
                ))
                seen_prefixes.add(prefix)

        # If we found specific equipment, return early (don't dilute with broad patterns)
        if entities:
            return entities

        # ── Step 3: Broad query patterns (less specific, multi-entity) ──
        for pattern, prefixes in _BROAD_QUERY_MAP.items():
            if pattern in query_lower:
                for prefix in prefixes:
                    if prefix not in seen_prefixes:
                        metric, unit = _DEFAULT_METRICS.get(prefix, ("", ""))
                        name = self._prefix_to_name(prefix)
                        entities.append(ResolvedEntity(
                            name=name,
                            table_prefix=prefix,
                            default_metric=metric,
                            default_unit=unit,
                            instances=[],  # Will be discovered from DB in catalog stage
                            is_primary=len(entities) == 0,
                        ))
                        seen_prefixes.add(prefix)
                if entities:
                    return entities

        # ── Step 4: Infer from metric keywords ──
        if not entities:
            entities = self._infer_from_metrics(query_lower, is_broad)

        # ── Step 5: Default to general overview ──
        if not entities:
            entities = [ResolvedEntity(
                name="energy meter",
                table_prefix="em",
                default_metric="active_power_total_kw",
                default_unit="kW",
                instances=[],  # Will be discovered from DB
                is_primary=True,
            )]

        return entities

    def _extract_instances(self, query: str, name: str, prefix: str) -> list[str]:
        """Extract specific instance numbers from query."""
        instances = []

        patterns = [
            rf"{name}\s*[-_]?\s*(\d+)",
            rf"{name}\s+(one|two|three|four|five|six|seven|eight|nine|ten|first|second|third|fourth|fifth)",
            rf"{prefix}\s*[-_]?\s*(\d+)",
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, query, re.IGNORECASE):
                num_str = match.group(1).lower()
                num = NUMBER_WORDS.get(num_str, num_str)
                instance = f"{prefix}_{num.zfill(3)}"
                if instance not in instances:
                    instances.append(instance)

        # Default to _001 if entity mentioned but no number and no "all" signal
        if not instances:
            instances = [f"{prefix}_001"]

        return instances

    def _infer_from_metrics(self, query: str, is_broad: bool) -> list[ResolvedEntity]:
        """Infer entities from metric keywords."""
        metric_entity_map = {
            "power": ("trf", "transformer"),
            "voltage": ("trf", "transformer"),
            "current": ("trf", "transformer"),
            "frequency": ("trf", "transformer"),
            "temperature": ("chiller", "chiller"),
            "cop": ("chiller", "chiller"),
            "cooling": ("chiller", "chiller"),
            "flow": ("pump", "pump"),
            "pressure": ("compressor", "compressor"),
            "vibration": ("pump", "pump"),  # Pumps are the most common vibration subject
            "bearing": ("pump", "pump"),
            "battery": ("ups", "ups"),
            "load": ("trf", "transformer"),
            "energy": ("em", "energy meter"),
            "solar": ("em_solar", "solar"),
            "humidity": ("ahu", "ahu"),
            "air quality": ("ahu", "ahu"),
        }

        entities = []
        seen = set()
        for keyword, (prefix, name) in metric_entity_map.items():
            if keyword in query and prefix not in seen:
                metric, unit = _DEFAULT_METRICS.get(prefix, ("", ""))
                entities.append(ResolvedEntity(
                    name=name,
                    table_prefix=prefix,
                    default_metric=metric,
                    default_unit=unit,
                    instances=[] if is_broad else [f"{prefix}_001"],
                    is_primary=len(entities) == 0,
                ))
                seen.add(prefix)
                if not is_broad:
                    break  # For specific queries, take first match

        return entities

    def infer_domain(self, entities: list[ResolvedEntity]) -> str:
        """Infer domain from entity types."""
        electrical = {"trf", "em", "lt_db", "lt_mcc", "lt_pcc", "lt_vfd", "lt_apfc",
                      "lt_bd", "lt_feeder", "lt_incomer", "em_solar", "dg", "ups"}
        hvac = {"chiller", "ahu", "ct", "pump", "compressor"}
        safety = {"fire", "bms"}

        prefixes = {e.table_prefix for e in entities}

        if prefixes & electrical:
            return "electrical"
        if prefixes & hvac:
            return "hvac"
        if prefixes & safety:
            return "safety"
        return "general"

    @staticmethod
    def _prefix_to_name(prefix: str) -> str:
        """Convert prefix back to human-readable name."""
        for name, pfx in ENTITY_PREFIX_MAP.items():
            if pfx == prefix:
                return name
        return prefix
