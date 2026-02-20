"""Configuration constants for the widget intelligence pipeline."""
from __future__ import annotations

# Grid layout constants
GRID_COLS = 12
GRID_ROWS = 12

# Widget size to grid span mapping
SIZE_COLS: dict[str, int] = {
    "compact": 3,
    "normal": 4,
    "expanded": 6,
    "hero": 12,
}

SIZE_ROWS: dict[str, int] = {
    "compact": 2,
    "normal": 3,
    "expanded": 4,
    "hero": 4,
}

# Entity prefix map — equipment name → table prefix
ENTITY_PREFIX_MAP: dict[str, str] = {
    "transformer": "trf",
    "generator": "dg",
    "genset": "dg",
    "ups": "ups",
    "chiller": "chiller",
    "ahu": "ahu",
    "cooling tower": "ct",
    "pump": "pump",
    "compressor": "compressor",
    "motor": "motor",
    "energy meter": "em",
    "meter": "em",
    "solar": "em_solar",
    "battery": "bms",
    "fire": "fire",
    "wtp": "wtp",
    "stp": "stp",
    "boiler": "boiler",
    "lt db": "lt_db",
    "lt mcc": "lt_mcc",
    "lt pcc": "lt_pcc",
    "lt vfd": "lt_vfd",
    "lt apfc": "lt_apfc",
    "lt bd": "lt_bd",
    "lt feeder": "lt_feeder",
    "lt incomer": "lt_incomer",
}

# Number words for instance extraction
NUMBER_WORDS: dict[str, str] = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "first": "1", "second": "2", "third": "3", "fourth": "4", "fifth": "5",
}

# vLLM base URL for DSPy reasoner
VLLM_BASE_URL = "http://localhost:8000/v1"
