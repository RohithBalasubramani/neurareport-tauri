"""
Domain-aware column resolution with diversity tracking.

Replaces V5's per-widget LLM column selection with a deterministic system
that knows WHICH columns are meaningful for WHICH equipment type and
WHICH scenario.

Key improvements over the original V7 column resolver:
1. EQUIPMENT_METRIC_MAP — domain-aware column selection (ported from V5)
2. Diversity tracking — never picks the same column twice across a dashboard
3. Scenario awareness — KPI needs a scalar, trend needs timeseries, etc.
4. 5-tier fallback: question keywords → domain map → semantic match → name parts → default
5. Multi-column support for multi-entity scenarios (comparison, distribution, etc.)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from backend.app.services.widget_intelligence.models.catalog import ColumnStats

logger = logging.getLogger(__name__)


@dataclass
class ColumnMatch:
    """Result of column resolution."""
    table: str
    column: str
    unit: str
    confidence: float  # 0-1


# ── Domain-Aware Metric Map (ported from V5 data_collector.py) ───────────────
# Maps equipment prefix → {metric_keyword: (column_name, unit)}
# The "default" key is used when no keyword matches.

EQUIPMENT_METRIC_MAP: dict[str, dict[str, tuple[str, str]]] = {
    "trf": {
        "power": ("active_power_kw", "kW"), "load": ("load_percent", "%"),
        "power_factor": ("power_factor", "PF"), "pf": ("power_factor", "PF"),
        "voltage": ("secondary_voltage_r", "V"),
        "primary_voltage": ("primary_voltage_r", "V"),
        "secondary_voltage": ("secondary_voltage_r", "V"),
        "oil_temp": ("oil_temperature_top_c", "°C"),
        "winding_temp": ("winding_temperature_hv_c", "°C"), "temperature": ("oil_temperature_top_c", "°C"),
        "frequency": ("frequency_hz", "Hz"), "current": ("current_r", "A"),
        "health": ("load_percent", "%"), "efficiency": ("power_factor", "PF"),
        "default": ("active_power_kw", "kW"),
    },
    "dg": {
        "power": ("active_power_kw", "kW"), "load": ("load_percent", "%"),
        "voltage": ("output_voltage_r", "V"), "frequency": ("frequency_hz", "Hz"),
        "coolant": ("coolant_temperature_c", "°C"), "temperature": ("coolant_temperature_c", "°C"),
        "fuel": ("fuel_level_pct", "%"), "fuel_level": ("fuel_level_pct", "%"),
        "rpm": ("engine_rpm", "RPM"), "runtime": ("engine_rpm", "RPM"),
        "status": ("engine_rpm", "RPM"), "operational": ("load_percent", "%"),
        "default": ("active_power_kw", "kW"),
    },
    "ups": {
        "power": ("output_power_kw", "kW"), "load": ("load_percent", "%"),
        "voltage": ("output_voltage_r", "V"), "battery": ("battery_charge_pct", "%"),
        "battery_status": ("battery_charge_pct", "%"), "battery_health": ("battery_health_pct", "%"),
        "battery_voltage": ("battery_voltage_v", "V"), "runtime": ("battery_time_remaining_min", "min"),
        "temperature": ("battery_temperature_c", "°C"),
        "default": ("output_power_kw", "kW"),
    },
    "chiller": {
        "power": ("power_consumption_kw", "kW"), "load": ("load_percent", "%"),
        "cop": ("current_cop", "COP"), "efficiency": ("current_cop", "COP"),
        "eer": ("eer", "EER"),
        "capacity": ("cooling_capacity_kw", "kW"), "energy": ("energy_kwh", "kWh"),
        "consumption": ("power_consumption_kw", "kW"),
        "temperature": ("chw_supply_temp_c", "°C"), "flow": ("chw_flow_rate_m3h", "m³/h"),
        "delta_t": ("chw_delta_t_c", "°C"), "condenser": ("cw_inlet_temp_c", "°C"),
        "compressor": ("compressor_1_current_a", "A"),
        "current": ("compressor_1_current_a", "A"),
        "vibration": ("vibration_mm_s", "mm/s"),
        "cooling": ("chw_supply_temp_c", "°C"),
        "performance": ("current_cop", "COP"),
        "default": ("power_consumption_kw", "kW"),
    },
    "ahu": {
        "power": ("fan_motor_power_kw", "kW"), "temperature": ("supply_air_temp_c", "°C"),
        "flow": ("supply_air_flow_cfm", "CFM"), "humidity": ("supply_air_humidity_pct", "%"),
        "co2": ("return_air_co2_ppm", "ppm"), "air_quality": ("return_air_co2_ppm", "ppm"),
        "fan_speed": ("fan_speed_pct", "%"), "pressure": ("supply_air_pressure_pa", "Pa"),
        "default": ("fan_motor_power_kw", "kW"),
    },
    "ct": {
        "power": ("fan_motor_power_kw", "kW"), "temperature": ("inlet_water_temp_c", "°C"),
        "outlet_temp": ("outlet_water_temp_c", "°C"), "flow": ("water_flow_rate_m3h", "m³/h"),
        "vibration": ("fan_vibration_mm_s", "mm/s"),
        "cooling": ("outlet_water_temp_c", "°C"), "performance": ("effectiveness_pct", "%"),
        "approach": ("approach_temp_c", "°C"), "effectiveness": ("effectiveness_pct", "%"),
        "range": ("range_temp_c", "°C"), "ph": ("ph_value", ""),
        "conductivity": ("conductivity_us_cm", "uS/cm"),
        "water_level": ("water_level_pct", "%"),
        "default": ("fan_motor_power_kw", "kW"),
    },
    "pump": {
        "power": ("motor_power_kw", "kW"), "flow": ("flow_rate_m3h", "m³/h"),
        "pressure": ("discharge_pressure_bar", "bar"),
        "vibration": ("vibration_axial_mm_s", "mm/s"),
        "vibration_axial": ("vibration_axial_mm_s", "mm/s"),
        "vibration_de": ("vibration_de_mm_s", "mm/s"),
        "bearing": ("bearing_temp_de_c", "°C"), "bearing_temperature": ("bearing_temp_de_c", "°C"),
        "bearing_temp": ("bearing_temp_de_c", "°C"),
        "temperature": ("fluid_temperature_c", "°C"),
        "current": ("motor_current_r", "A"), "voltage": ("motor_voltage_r", "V"),
        "efficiency": ("pump_efficiency_pct", "%"),
        "default": ("motor_power_kw", "kW"),
    },
    "compressor": {
        "power": ("motor_power_kw", "kW"), "consumption": ("power_consumption_kw", "kW"),
        "pressure": ("discharge_pressure_bar", "bar"),
        "temperature": ("discharge_temperature_c", "°C"),
        "vibration": ("vibration_mm_s", "mm/s"),
        "bearing": ("motor_bearing_temp_de_c", "°C"),
        "oil_temp": ("oil_temperature_c", "°C"), "oil": ("oil_pressure_bar", "bar"),
        "load": ("load_percent", "%"),
        "dew_point": ("dew_point_c", "°C"),
        "flow": ("discharge_flow_cfm", "CFM"),
        "energy": ("energy_kwh", "kWh"),
        "specific_power": ("specific_power_kw_per_cfm", "kW/CFM"),
        "efficiency": ("specific_power_kw_per_cfm", "kW/CFM"),
        "current": ("motor_current_r", "A"), "speed": ("motor_speed_rpm", "RPM"),
        "default": ("motor_power_kw", "kW"),
    },
    "motor": {
        "power": ("active_power_kw", "kW"), "consumption": ("power_consumption_kw", "kW"),
        "load": ("load_percent", "%"),
        "temperature": ("winding_temp_r_c", "°C"), "winding_temp": ("winding_temp_r_c", "°C"),
        "vibration": ("vibration_de_h_mm_s", "mm/s"),
        "vibration_de": ("vibration_de_h_mm_s", "mm/s"),
        "vibration_nde": ("vibration_nde_h_mm_s", "mm/s"),
        "speed": ("speed_rpm", "RPM"), "rpm": ("speed_rpm", "RPM"),
        "current": ("current_r", "A"), "voltage": ("voltage_r", "V"),
        "bearing": ("bearing_temp_de_c", "°C"), "bearing_temperature": ("bearing_temp_de_c", "°C"),
        "efficiency": ("efficiency_pct", "%"), "torque": ("torque_nm", "Nm"),
        "frequency": ("frequency_hz", "Hz"), "slip": ("slip_pct", "%"),
        "insulation": ("insulation_resistance_mohm", "MΩ"),
        "energy": ("energy_kwh", "kWh"),
        "default": ("active_power_kw", "kW"),
    },
    "em": {
        "power": ("active_power_total_kw", "kW"), "voltage": ("voltage_avg", "V"),
        "current": ("current_avg", "A"),
        "power_factor": ("power_factor_total", "PF"), "pf": ("power_factor_total", "PF"),
        "frequency": ("frequency_hz", "Hz"),
        "energy": ("active_energy_import_kwh", "kWh"),
        "consumption": ("active_power_total_kw", "kW"),
        "demand": ("current_demand_kw", "kW"), "max_demand": ("max_demand_kw", "kW"),
        "harmonic": ("thd_voltage_r_pct", "%"), "thd": ("thd_voltage_r_pct", "%"),
        "voltage_unbalance": ("voltage_unbalance_pct", "%"),
        "default": ("active_power_total_kw", "kW"),
    },
    "lt_db": {
        "power": ("active_power_total_kw", "kW"), "voltage": ("voltage_r_n", "V"),
        "current": ("current_r", "A"),
        "power_factor": ("power_factor_total", "PF"), "pf": ("power_factor_total", "PF"),
        "frequency": ("frequency_hz", "Hz"),
        "energy": ("active_energy_import_kwh", "kWh"),
        "load": ("load_percent", "%"),
        "temperature": ("busbar_temp_r_c", "°C"), "busbar": ("busbar_temp_r_c", "°C"),
        "insulation": ("insulation_resistance_mohm", "MΩ"),
        "harmonic": ("thd_voltage_r_pct", "%"), "thd": ("thd_voltage_r_pct", "%"),
        "earth_leakage": ("current_earth_leakage_ma", "mA"),
        "default": ("active_power_total_kw", "kW"),
    },
    "lt_mcc": {
        "power": ("active_power_total_kw", "kW"), "voltage": ("voltage_r_n", "V"),
        "current": ("current_r", "A"),
        "power_factor": ("power_factor_total", "PF"), "pf": ("power_factor_total", "PF"),
        "frequency": ("frequency_hz", "Hz"),
        "energy": ("active_energy_import_kwh", "kWh"),
        "load": ("load_percent", "%"),
        "temperature": ("busbar_temp_r_c", "°C"), "busbar": ("busbar_temp_r_c", "°C"),
        "insulation": ("insulation_resistance_mohm", "MΩ"),
        "harmonic": ("thd_voltage_r_pct", "%"), "thd": ("thd_voltage_r_pct", "%"),
        "earth_leakage": ("current_earth_leakage_ma", "mA"),
        "default": ("active_power_total_kw", "kW"),
    },
    "boiler": {
        "power": ("power_consumption_kw", "kW"), "pressure": ("steam_pressure_bar", "bar"),
        "temperature": ("steam_temperature_c", "°C"), "flow": ("steam_flow_tph", "TPH"),
        "load": ("load_percent", "%"), "efficiency": ("efficiency_pct", "%"),
        "fuel": ("fuel_consumption_lph", "L/h"), "exhaust": ("exhaust_temp_c", "°C"),
        "water": ("feed_water_temp_c", "°C"), "emission": ("nox_ppm", "ppm"),
        "default": ("steam_pressure_bar", "bar"),
    },
    # ── Electrical panels (share lt_db-style schema) ─────────────────────────
    "lt_pcc": {
        "power": ("active_power_total_kw", "kW"), "load": ("load_percent", "%"),
        "power_factor": ("power_factor_total", "PF"), "pf": ("power_factor_total", "PF"),
        "voltage": ("voltage_ry", "V"), "current": ("current_r", "A"),
        "frequency": ("frequency_hz", "Hz"),
        "temperature": ("busbar_temp_r_c", "°C"), "busbar": ("busbar_temp_r_c", "°C"),
        "thd": ("thd_voltage_r_pct", "%"), "harmonic": ("thd_voltage_r_pct", "%"),
        "demand": ("max_demand_kw", "kW"), "energy": ("active_energy_import_kwh", "kWh"),
        "insulation": ("insulation_resistance_mohm", "MΩ"),
        "earth_leakage": ("current_earth_leakage_ma", "mA"),
        "efficiency": ("power_factor_total", "PF"),
        "default": ("active_power_total_kw", "kW"),
    },
    "lt_vfd": {
        "power": ("active_power_kw", "kW"), "load": ("load_percent", "%"),
        "power_factor": ("power_factor_total", "PF"), "pf": ("power_factor_total", "PF"),
        "voltage": ("drive_output_voltage", "V"),
        "current": ("drive_output_current_a", "A"),
        "frequency": ("drive_output_frequency_hz", "Hz"),
        "speed": ("motor_speed_rpm", "RPM"), "rpm": ("motor_speed_rpm", "RPM"),
        "torque": ("motor_torque_pct", "%"),
        "temperature": ("drive_heatsink_temp_c", "°C"),
        "thd": ("thd_voltage_r_pct", "%"), "harmonic": ("thd_voltage_r_pct", "%"),
        "energy": ("active_energy_import_kwh", "kWh"),
        "efficiency": ("power_factor_total", "PF"),
        "default": ("active_power_kw", "kW"),
    },
    "lt_apfc": {
        "power": ("active_power_total_kw", "kW"),
        "power_factor": ("achieved_power_factor", "PF"), "pf": ("achieved_power_factor", "PF"),
        "voltage": ("voltage_ry", "V"), "current": ("current_r", "A"),
        "frequency": ("frequency_hz", "Hz"),
        "temperature": ("capacitor_bank_temp_c", "°C"),
        "load": ("capacitor_steps_active", ""),
        "thd": ("thd_voltage_r_pct", "%"), "harmonic": ("thd_voltage_r_pct", "%"),
        "energy": ("reactive_energy_import_kvarh", "kVARh"),
        "efficiency": ("achieved_power_factor", "PF"),
        "default": ("power_factor_total", "PF"),
    },
    "lt_bd": {
        "power": ("active_power_total_kw", "kW"), "voltage": ("voltage_r_n", "V"),
        "current": ("current_r", "A"),
        "power_factor": ("power_factor_total", "PF"), "pf": ("power_factor_total", "PF"),
        "frequency": ("frequency_hz", "Hz"),
        "energy": ("active_energy_import_kwh", "kWh"),
        "load": ("load_percent", "%"),
        "temperature": ("busbar_temp_r_c", "°C"), "busbar": ("busbar_temp_r_c", "°C"),
        "insulation": ("insulation_resistance_mohm", "MΩ"),
        "harmonic": ("thd_voltage_r_pct", "%"), "thd": ("thd_voltage_r_pct", "%"),
        "earth_leakage": ("current_earth_leakage_ma", "mA"),
        "default": ("active_power_total_kw", "kW"),
    },
    "lt_feeder": {
        "power": ("active_power_total_kw", "kW"), "voltage": ("voltage_r_n", "V"),
        "current": ("current_r", "A"),
        "power_factor": ("power_factor_total", "PF"), "pf": ("power_factor_total", "PF"),
        "frequency": ("frequency_hz", "Hz"),
        "energy": ("active_energy_import_kwh", "kWh"),
        "load": ("load_percent", "%"),
        "temperature": ("busbar_temp_r_c", "°C"), "busbar": ("busbar_temp_r_c", "°C"),
        "insulation": ("insulation_resistance_mohm", "MΩ"),
        "harmonic": ("thd_voltage_r_pct", "%"), "thd": ("thd_voltage_r_pct", "%"),
        "earth_leakage": ("current_earth_leakage_ma", "mA"),
        "default": ("active_power_total_kw", "kW"),
    },
    "lt_incomer": {
        "power": ("active_power_total_kw", "kW"), "voltage": ("voltage_r_n", "V"),
        "current": ("current_r", "A"),
        "power_factor": ("power_factor_total", "PF"), "pf": ("power_factor_total", "PF"),
        "frequency": ("frequency_hz", "Hz"),
        "energy": ("active_energy_import_kwh", "kWh"),
        "load": ("load_percent", "%"),
        "temperature": ("busbar_temp_r_c", "°C"), "busbar": ("busbar_temp_r_c", "°C"),
        "insulation": ("insulation_resistance_mohm", "MΩ"),
        "harmonic": ("thd_voltage_r_pct", "%"), "thd": ("thd_voltage_r_pct", "%"),
        "earth_leakage": ("current_earth_leakage_ma", "mA"),
        "default": ("active_power_total_kw", "kW"),
    },
    # ── Specialized systems ──────────────────────────────────────────────────
    "em_solar": {
        "power": ("active_power_kw", "kW"), "energy": ("active_energy_import_kwh", "kWh"),
        "voltage": ("voltage_ry", "V"), "current": ("current_r", "A"),
        "frequency": ("frequency_hz", "Hz"),
        "power_factor": ("power_factor_total", "PF"), "pf": ("power_factor_total", "PF"),
        "default": ("active_power_kw", "kW"),
    },
    "bms": {
        "temperature": ("temperature_actual_c", "°C"),
        "humidity": ("humidity_actual_pct", "%"),
        "air_quality": ("co2_level_ppm", "ppm"), "co2": ("co2_level_ppm", "ppm"),
        "pressure": ("differential_pressure_pa", "Pa"),
        "lighting": ("lighting_level_lux", "lux"),
        "default": ("temperature_actual_c", "°C"),
    },
    "fire": {
        "pressure": ("sprinkler_pressure_bar", "bar"),
        "default": ("sprinkler_pressure_bar", "bar"),
    },
    "wtp": {
        "flow": ("flow_rate_m3h", "m³/h"), "pressure": ("pressure_bar", "bar"),
        "temperature": ("water_temp_c", "°C"),
        "ph": ("ph_value", ""), "conductivity": ("conductivity_us_cm", "µS/cm"),
        "default": ("flow_rate_m3h", "m³/h"),
    },
    "stp": {
        "flow": ("flow_rate_m3h", "m³/h"), "pressure": ("pressure_bar", "bar"),
        "temperature": ("water_temp_c", "°C"),
        "ph": ("ph_value", ""), "conductivity": ("conductivity_us_cm", "µS/cm"),
        "default": ("flow_rate_m3h", "m³/h"),
    },
}

# Metric keyword aliases — maps user-friendly terms to canonical metric keywords
_METRIC_ALIASES: dict[str, str] = {
    "power_kw": "power", "consumption": "power", "energy": "power",
    "power_consumption": "power", "power_output": "power",
    "demand": "power", "kw": "power", "watt": "power", "draw": "power",
    "power_factor": "power_factor", "pf": "power_factor",
    "voltage_avg": "voltage", "volt": "voltage", "v": "voltage",
    "primary_voltage": "primary_voltage", "primary voltage": "primary_voltage",
    "secondary_voltage": "secondary_voltage", "secondary voltage": "secondary_voltage",
    "current_avg": "current", "amp": "current", "ampere": "current",
    "freq": "frequency", "hz": "frequency",
    "temp": "temperature", "thermal": "temperature", "heat": "temperature",
    "water_temperature": "temperature", "water_temp": "temperature",
    "oil_temp": "oil_temp", "oil_temperature": "oil_temp",
    "vibration_level": "vibration", "vibration_levels": "vibration",
    "shaking": "vibration", "oscillation": "vibration",
    "pressure_reading": "pressure", "pressure_level": "pressure",
    "flow_rate": "flow", "humidity_level": "humidity",
    "battery_level": "battery", "battery_charge": "battery",
    "charge": "battery", "backup": "battery",
    "current_load": "load", "load_percent": "load", "loading": "load",
    "cop_value": "cop", "efficiency_value": "efficiency",
    "performance": "efficiency",
    "issue": "vibration", "issues": "vibration",  # "issues" in pumps usually means vibration/bearing
    # VFD-specific
    "speed": "speed", "torque": "torque", "drive": "speed",
    "rpm": "speed", "motor_speed": "speed",
    # APFC-specific
    "capacitor": "power_factor", "kvar": "power_factor", "reactive": "power_factor",
    # BMS-specific
    "co2": "air_quality", "air": "air_quality", "particle": "air_quality",
    "lighting": "lighting", "lux": "lighting", "occupancy": "temperature",
    # Boiler-specific
    "steam": "pressure", "boiler_pressure": "pressure",
    "fuel_consumption": "fuel", "emission": "exhaust", "nox": "exhaust",
    # Water treatment
    "ph": "ph", "conductivity": "conductivity", "tds": "conductivity", "turbidity": "flow",
}


# ── Metric Domain Classification ───────────────────────────────────────────────
# Groups related physical quantities so dashboard metric coherence can be
# enforced at assembly time. When a query focuses on "power", widgets showing
# "voltage" or "current" are off-topic. Generic — works for ANY metric domain.

METRIC_DOMAINS: dict[str, set[str]] = {
    "power":       {"power", "energy", "consumption", "demand", "load"},
    "voltage":     {"voltage"},
    "current":     {"current"},
    "temperature": {"temperature", "oil_temp", "winding_temp", "bearing",
                    "cooling", "delta_t", "coolant", "exhaust"},
    "vibration":   {"vibration"},
    "pressure":    {"pressure"},
    "flow":        {"flow"},
    "frequency":   {"frequency", "speed", "rpm"},
}

# Reverse index: canonical metric keyword → domain name
_KEYWORD_TO_DOMAIN: dict[str, str] = {}
for _dom, _kws in METRIC_DOMAINS.items():
    for _kw in _kws:
        _KEYWORD_TO_DOMAIN[_kw] = _dom

# Unit string → domain (fallback when metric name alone is ambiguous)
_UNIT_TO_DOMAIN: dict[str, str] = {
    "kw": "power", "kva": "power", "w": "power", "mw": "power", "kwh": "power",
    "v": "voltage", "kv": "voltage",
    "a": "current", "ma": "current",
    "°c": "temperature", "°f": "temperature",
    "mm/s": "vibration",
    "bar": "pressure", "psi": "pressure", "pa": "pressure", "kpa": "pressure",
    "m³/h": "flow", "cfm": "flow", "tph": "flow", "l/s": "flow",
    "hz": "frequency", "rpm": "frequency",
}

# Domains where cumulative (SUM over time) is physically meaningful.
# Power→energy, flow→volume are integrable. Voltage, current, temperature
# are instantaneous — cumulative makes no physical sense.
CUMULATIVE_ELIGIBLE_DOMAINS: frozenset[str] = frozenset({
    "power", "flow",
})


def classify_metric_domain(text: str, unit: str = "") -> str | None:
    """Classify a metric name or column label into its measurement domain.

    Returns "power", "voltage", "current", "temperature", etc., or None
    if the metric cannot be classified (e.g. COP, power factor, efficiency).
    Unclassified metrics are always kept by the coherence gate.
    """
    text_lower = text.lower()

    # Compound override: "power factor" is NOT in the "power" domain
    if "power factor" in text_lower or "power_factor" in text_lower:
        return None

    tokens = set(re.findall(r'[a-z]+', text_lower))
    for token in tokens:
        if token in _KEYWORD_TO_DOMAIN:
            return _KEYWORD_TO_DOMAIN[token]
        canonical = _METRIC_ALIASES.get(token)
        if canonical and canonical in _KEYWORD_TO_DOMAIN:
            return _KEYWORD_TO_DOMAIN[canonical]

    # Unit-based fallback
    if unit:
        u = unit.lower().strip()
        if u in _UNIT_TO_DOMAIN:
            return _UNIT_TO_DOMAIN[u]

    return None


def classify_query_domain(query: str) -> str | None:
    """Classify a natural-language query into its primary metric domain.

    Uses _extract_metric_keyword (with "current"-as-adjective disambiguation)
    then maps to domain. Returns None for generic queries with no specific
    metric focus — the coherence gate skips filtering in that case.
    """
    keyword = ColumnResolver()._extract_metric_keyword(query.lower())
    if not keyword:
        return None
    if keyword in _KEYWORD_TO_DOMAIN:
        return _KEYWORD_TO_DOMAIN[keyword]
    canonical = _METRIC_ALIASES.get(keyword)
    if canonical and canonical in _KEYWORD_TO_DOMAIN:
        return _KEYWORD_TO_DOMAIN[canonical]
    return None


# Scenario-specific metric preferences — which metrics are most meaningful per scenario
_SCENARIO_METRIC_ORDER: dict[str, list[str]] = {
    "kpi": ["power", "load", "temperature", "cop", "efficiency", "flow", "pressure", "vibration"],
    "trend": ["power", "temperature", "load", "cop", "vibration", "flow", "pressure"],
    "comparison": ["power", "load", "efficiency", "cop", "temperature"],
    "distribution": ["power", "load", "efficiency", "flow"],
    "composition": ["power", "load", "efficiency", "flow"],
    "category-bar": ["power", "load", "efficiency", "flow", "temperature"],
    "flow-sankey": ["power", "energy", "load"],
    "matrix-heatmap": ["power", "temperature", "load", "vibration"],
    "alerts": ["vibration", "temperature", "load", "pressure"],
    "timeline": ["power", "load", "temperature", "vibration"],
    "trend-multi-line": ["power", "temperature", "load", "vibration"],
    "trends-cumulative": ["power", "energy", "flow"],
    "eventlogstream": ["power", "vibration", "temperature", "load"],
}

# Numeric PG data types
_NUMERIC_TYPES = {"double precision", "real", "numeric", "float8", "integer", "bigint", "smallint"}


class ColumnResolver:
    """
    Domain-aware column resolver with diversity tracking.

    5-tier resolution strategy:
    1. Extract metric keywords from the question
    2. Look up in EQUIPMENT_METRIC_MAP for the equipment type (domain-aware)
    3. Semantic matching: score columns by question keyword overlap
    4. Column name part matching: break column name into parts
    5. Fallback to default metric for equipment type

    Diversity is enforced by accepting a `used_columns` set that prevents
    the same column from being picked for multiple widgets.
    """

    def resolve(
        self,
        question: str,
        table: str,
        available_columns: list[ColumnStats],
        equipment_prefix: str = "",
        scenario: str = "",
        used_columns: set[str] | None = None,
    ) -> ColumnMatch | None:
        """
        Match a question to the best column in a table.

        Args:
            question: The analytical question this widget answers
            table: The PG table name
            available_columns: Column metadata from catalog scan
            equipment_prefix: Equipment type prefix (e.g. "trf", "pump")
            scenario: Widget scenario type (e.g. "kpi", "trend")
            used_columns: Set of "table.column" strings already used —
                          will be avoided for diversity unless no alternative exists

        Returns ColumnMatch or None.
        """
        question_lower = question.lower()
        numeric_cols = [c for c in available_columns if c.dtype in _NUMERIC_TYPES]

        if not numeric_cols:
            return None

        # Infer equipment prefix from table name if not provided
        if not equipment_prefix and "_" in table:
            equipment_prefix = table.rsplit("_", 1)[0]
            # Handle multi-part prefixes like lt_mcc
            if equipment_prefix not in EQUIPMENT_METRIC_MAP:
                equipment_prefix = table.split("_")[0]

        available_col_names = {c.name for c in numeric_cols}
        used = used_columns or set()

        # ── Tier 1: Extract metric keywords from question → domain map lookup ──
        metric_keyword = self._extract_metric_keyword(question_lower)
        if metric_keyword and equipment_prefix in EQUIPMENT_METRIC_MAP:
            metric_map = EQUIPMENT_METRIC_MAP[equipment_prefix]
            if metric_keyword in metric_map:
                col_name, unit = metric_map[metric_keyword]
                if col_name in available_col_names:
                    key = f"{table}.{col_name}"
                    if key not in used:
                        return ColumnMatch(table=table, column=col_name, unit=unit, confidence=0.95)
                    # Keyword matched but column already used — try alternate columns below

            # Phase-aware fallback: if question mentions a specific phase (r/y/b),
            # try that phase suffix even if the base keyword mapped elsewhere
            phase_match = re.search(r'\b(phase\s+)?([ryb])\b', question_lower)
            if phase_match and col_name:
                phase = phase_match.group(2)
                base = re.sub(r'_[ryb]$', '', col_name)
                phase_col = f"{base}_{phase}"
                if phase_col in available_col_names:
                    key = f"{table}.{phase_col}"
                    if key not in used:
                        return ColumnMatch(table=table, column=phase_col, unit=unit, confidence=0.93)

        # ── Tier 2: Scenario-specific ordered preferences ──
        if equipment_prefix in EQUIPMENT_METRIC_MAP:
            metric_map = EQUIPMENT_METRIC_MAP[equipment_prefix]
            preference_order = _SCENARIO_METRIC_ORDER.get(scenario, [])
            for metric_key in preference_order:
                if metric_key in metric_map:
                    col_name, unit = metric_map[metric_key]
                    key = f"{table}.{col_name}"
                    if col_name in available_col_names and key not in used:
                        return ColumnMatch(table=table, column=col_name, unit=unit, confidence=0.80)

        # ── Tier 3: Score all columns by question relevance ──
        scored: list[tuple[ColumnStats, float]] = []
        for col in numeric_cols:
            if col.name == "timestamp":
                continue
            score = self._score_column(question_lower, col, equipment_prefix)
            key = f"{table}.{col.name}"
            # Penalize already-used columns but don't exclude them entirely
            if key in used:
                score *= 0.3
            scored.append((col, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        if scored and scored[0][1] > 0.1:
            best = scored[0][0]
            return ColumnMatch(
                table=table, column=best.name,
                unit=best.unit or self._infer_unit(best.name),
                confidence=min(scored[0][1], 1.0),
            )

        # ── Tier 4: Default metric for equipment type ──
        if equipment_prefix in EQUIPMENT_METRIC_MAP:
            metric_map = EQUIPMENT_METRIC_MAP[equipment_prefix]
            col_name, unit = metric_map.get("default", ("active_power_kw", "kW"))
            if col_name in available_col_names:
                key = f"{table}.{col_name}"
                if key not in used:
                    return ColumnMatch(table=table, column=col_name, unit=unit, confidence=0.60)

        # ── Tier 5: Any unused numeric column with data ──
        for col in numeric_cols:
            if col.name == "timestamp":
                continue
            key = f"{table}.{col.name}"
            if key not in used and col.avg_val is not None:
                return ColumnMatch(
                    table=table, column=col.name,
                    unit=col.unit or self._infer_unit(col.name),
                    confidence=0.40,
                )

        # Last resort: any numeric column at all (even if used)
        for col in numeric_cols:
            if col.name == "timestamp":
                continue
            return ColumnMatch(
                table=table, column=col.name,
                unit=col.unit or self._infer_unit(col.name),
                confidence=0.20,
            )

        return None

    def resolve_multi(
        self,
        question: str,
        tables: list[tuple[str, list[ColumnStats]]],
        equipment_prefix: str = "",
        scenario: str = "",
        used_columns: set[str] | None = None,
        n: int = 5,
    ) -> list[ColumnMatch]:
        """Resolve a question across multiple tables with diversity tracking."""
        matches = []
        used = set(used_columns) if used_columns else set()

        for table_name, columns in tables:
            match = self.resolve(
                question, table_name, columns,
                equipment_prefix=equipment_prefix,
                scenario=scenario,
                used_columns=used,
            )
            if match:
                matches.append(match)
                used.add(f"{match.table}.{match.column}")

        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches[:n]

    def resolve_diverse_columns(
        self,
        questions: list[str],
        table: str,
        available_columns: list[ColumnStats],
        equipment_prefix: str = "",
        scenarios: list[str] | None = None,
    ) -> list[ColumnMatch]:
        """
        Resolve multiple questions to diverse columns in the same table.
        Ensures each question gets a DIFFERENT column when possible.
        """
        used: set[str] = set()
        results = []
        scenario_list = scenarios or [""] * len(questions)

        for i, question in enumerate(questions):
            scenario = scenario_list[i] if i < len(scenario_list) else ""
            match = self.resolve(
                question, table, available_columns,
                equipment_prefix=equipment_prefix,
                scenario=scenario,
                used_columns=used,
            )
            if match:
                results.append(match)
                used.add(f"{match.table}.{match.column}")
            else:
                results.append(None)

        return results

    def _extract_metric_keyword(self, question: str) -> str:
        """Extract the primary metric keyword from a question string.

        Handles ambiguity: "current" can mean "present/latest" (adjective) or
        "electrical current" (noun). Disambiguate by checking if it precedes
        another metric noun like "power", "load", "status".
        """
        # Direct keyword matches (ordered by specificity — more specific first)
        direct_keywords = [
            "bearing", "vibration", "oil_temp", "winding_temp", "battery",
            "power_factor", "pf", "cop", "eer", "delta_t",
            "pressure", "flow", "humidity", "rpm", "speed",
            "primary_voltage", "secondary_voltage",  # Before generic "voltage"
            "voltage", "current", "frequency",
            "temperature", "load", "power", "efficiency",
            "energy", "consumption", "cooling", "performance",
        ]

        # Disambiguate "current" — skip if used as adjective before another metric
        _METRIC_NOUNS = {"power", "load", "status", "state", "value", "reading",
                         "level", "consumption", "output", "capacity", "factor",
                         "motor power", "active power"}

        for keyword in direct_keywords:
            if keyword.replace("_", " ") in question or keyword in question:
                if keyword == "current":
                    # Check if "current" precedes another metric noun
                    after_current = question[question.index("current") + 7:].strip()
                    if any(after_current.startswith(noun) for noun in _METRIC_NOUNS):
                        continue  # Skip — "current" is an adjective here
                # Check aliases
                canonical = _METRIC_ALIASES.get(keyword, keyword)
                return canonical

        # Check word-level aliases
        words = re.findall(r'\b\w+\b', question)
        for word in words:
            if word in _METRIC_ALIASES:
                return _METRIC_ALIASES[word]

        return ""

    def _score_column(self, question: str, col: ColumnStats, equipment_prefix: str) -> float:
        """Score how well a column matches a question, with domain awareness.

        Uses RapidFuzz token_sort_ratio (when available) for better affinity
        scoring: "active power kw" scores higher than "current r" against
        query "how is power distributed". Falls back to substring matching.
        """
        score = 0.0
        col_lower = col.name.lower()
        col_label = col_lower.replace("_", " ")

        # Fuzzy token matching (RapidFuzz) or substring fallback
        try:
            from rapidfuzz import fuzz
            token_score = fuzz.token_sort_ratio(col_label, question) / 100.0
            if token_score > 0.4:
                score += token_score * 0.6  # Scale to max ~0.6
        except ImportError:
            # Fallback: direct column name parts in question
            col_parts = col_label.split()
            for part in col_parts:
                if len(part) > 2 and part in question:
                    score += 0.4

        # Unit match — word-boundary aware to prevent single-letter units
        # (e.g. "A" for Amps) from matching inside words like "across" or "plant"
        if col.unit:
            unit_lower = col.unit.lower()
            if len(unit_lower) <= 2:
                # Short units need word-boundary matching
                if re.search(r'\b' + re.escape(unit_lower) + r'\b', question):
                    score += 0.2
            else:
                if unit_lower in question:
                    score += 0.2

        # Domain relevance: boost if column is a known metric for this equipment
        if equipment_prefix in EQUIPMENT_METRIC_MAP:
            metric_map = EQUIPMENT_METRIC_MAP[equipment_prefix]
            for metric_key, (mapped_col, _) in metric_map.items():
                if mapped_col == col_lower and metric_key != "default":
                    # This column IS a known metric — small boost for being domain-relevant
                    score += 0.15
                    break

        # Penalize non-useful columns
        if col_lower == "timestamp":
            score -= 10.0
        if col_lower.endswith(("_status", "_state", "_mode")):
            score -= 2.0

        return score

    @staticmethod
    def _infer_unit(column_name: str) -> str:
        """Infer physical unit from column name suffix."""
        name_lower = column_name.lower()
        # Multi-part suffixes first
        multi_suffixes = {
            "_mm_s": "mm/s", "_m3h": "m³/h", "_m3_h": "m³/h",
            "_nm3_hr": "Nm³/h", "_kl_hr": "kL/h", "_us_cm": "µS/cm",
            "_g_kwh": "g/kWh", "_kw_per_cfm": "kW/CFM",
            "_kvarh": "kVARh", "_kvah": "kVAh",
        }
        for suffix, unit in multi_suffixes.items():
            if name_lower.endswith(suffix):
                return unit
        suffixes = {
            "_kw": "kW", "_kvar": "kVAR", "_kva": "kVA",
            "_kwh": "kWh", "_mwh": "MWh",
            "_c": "°C", "_f": "°F",
            "_pct": "%", "_percent": "%",
            "_hz": "Hz",
            "_a": "A", "_v": "V", "_kv": "kV",
            "_bar": "bar", "_psi": "psi", "_mbar": "mbar",
            "_pa": "Pa",
            "_rpm": "RPM",
            "_ppm": "ppm",
            "_ma": "mA", "_mohm": "MΩ",
            "_cfm": "CFM",
            "_lph": "L/h", "_lpm": "L/min", "_lps": "L/s",
            "_nm": "Nm", "_min": "min", "_kl": "kL",
            "_lux": "lux", "_um": "µm",
        }
        for suffix, unit in suffixes.items():
            if name_lower.endswith(suffix):
                return unit
        if "power_factor" in name_lower:
            return "PF"
        return ""
