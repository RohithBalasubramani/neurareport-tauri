"""
Logger Database Discovery Service.

Probes known Logger database locations (LoggerDeploy / LoggerFast) and returns
available connections that NeuraReport can register as data sources.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import create_engine, text

logger = logging.getLogger("neura.logger.discovery")

# Known Logger database configurations
LOGGER_DATABASES = [
    {
        "key": "logger_deploy",
        "name": "Logger Deploy (neuract_db)",
        "host": "localhost",
        "port": 5434,
        "database": "neuract_db",
        "username": "neuract",
        "password": "neuract123",
        "logger_type": "deploy",
    },
    {
        "key": "logger_fast",
        "name": "Logger Fast (meta_data_fast)",
        "host": "localhost",
        "port": 5432,
        "database": "meta_data_fast",
        "username": "postgres",
        "password": "",
        "logger_type": "fast",
    },
]


def _build_url(cfg: dict) -> str:
    user = cfg["username"]
    password = cfg.get("password") or ""
    host = cfg["host"]
    port = cfg["port"]
    database = cfg["database"]
    if password:
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    return f"postgresql://{user}@{host}:{port}/{database}"


def _can_connect(url: str) -> bool:
    """Test if a PostgreSQL database is reachable."""
    engine = create_engine(url, connect_args={"connect_timeout": 3})
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.debug(f"Cannot connect to {url}: {exc}")
        return False
    finally:
        engine.dispose()


def _count_tables(url: str) -> int:
    """Count user tables in a PostgreSQL database."""
    engine = create_engine(url, connect_args={"connect_timeout": 5})
    try:
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_type = 'BASE TABLE' "
                "AND table_schema NOT IN ('pg_catalog', 'information_schema')"
            ))
            return result.scalar() or 0
    except Exception:
        return 0
    finally:
        engine.dispose()


def _get_storage_targets(url: str) -> list[dict]:
    """Query app_storage_targets from a Logger database for additional data DBs."""
    engine = create_engine(url, connect_args={"connect_timeout": 5})
    try:
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT id, name, provider, connection_string, is_default, status "
                "FROM app_storage_targets ORDER BY name"
            ))
            targets = []
            for row in result:
                targets.append({
                    "id": str(row[0]),
                    "name": row[1],
                    "provider": row[2],
                    "connection_string": row[3],
                    "is_default": row[4],
                    "status": row[5],
                })
            return targets
    except Exception as exc:
        logger.debug(f"Could not query storage targets: {exc}")
        return []
    finally:
        engine.dispose()


def discover_logger_databases() -> list[dict[str, Any]]:
    """Probe for Logger databases and return discovered connections."""
    discovered = []

    for cfg in LOGGER_DATABASES:
        url = _build_url(cfg)
        if _can_connect(url):
            table_count = _count_tables(url)
            entry: dict[str, Any] = {
                "key": cfg["key"],
                "name": cfg["name"],
                "db_type": "postgresql",
                "host": cfg["host"],
                "port": cfg["port"],
                "database": cfg["database"],
                "db_url": url,
                "logger_type": cfg["logger_type"],
                "table_count": table_count,
                "status": "available",
            }

            # Try to discover storage targets from this Logger DB
            storage_targets = _get_storage_targets(url)
            if storage_targets:
                entry["storage_targets"] = storage_targets

            discovered.append(entry)
            logger.info(f"Discovered Logger database: {cfg['name']} ({table_count} tables)")

    return discovered
