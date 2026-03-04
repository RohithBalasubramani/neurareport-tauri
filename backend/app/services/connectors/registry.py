"""
Connector Registry - Central registry for all connector types.
"""

from __future__ import annotations

import logging
from typing import Any, Type

from .base import ConnectorBase

logger = logging.getLogger("neura.connectors.registry")

# Global registry of connector classes
CONNECTOR_REGISTRY: dict[str, Type[ConnectorBase]] = {}


def register_connector(connector_class: Type[ConnectorBase]) -> Type[ConnectorBase]:
    """
    Decorator to register a connector class.

    Usage:
        @register_connector
        class PostgreSQLConnector(ConnectorBase):
            connector_id = "postgresql"
            ...
    """
    connector_id = connector_class.connector_id
    if not connector_id:
        raise ValueError(f"Connector class {connector_class.__name__} must have a connector_id")

    if connector_id in CONNECTOR_REGISTRY:
        logger.warning(f"Overwriting existing connector: {connector_id}")

    CONNECTOR_REGISTRY[connector_id] = connector_class
    logger.info(f"Registered connector: {connector_id}")
    return connector_class


def get_connector(connector_id: str, config: dict[str, Any]) -> ConnectorBase:
    """
    Factory function to create a connector instance.

    Args:
        connector_id: ID of the connector type
        config: Connector configuration

    Returns:
        Connector instance

    Raises:
        ValueError: If connector_id is not registered
    """
    if connector_id not in CONNECTOR_REGISTRY:
        available = ", ".join(CONNECTOR_REGISTRY.keys())
        raise ValueError(f"Unknown connector: {connector_id}. Available: {available}")

    connector_class = CONNECTOR_REGISTRY[connector_id]
    return connector_class(config)


def list_connectors() -> list[dict[str, Any]]:
    """
    List all registered connectors with their metadata.

    Returns:
        List of connector info dictionaries
    """
    return [
        connector_class.get_connector_info()
        for connector_class in CONNECTOR_REGISTRY.values()
    ]


def get_connector_info(connector_id: str) -> dict[str, Any] | None:
    """
    Get info for a specific connector.

    Args:
        connector_id: ID of the connector

    Returns:
        Connector info or None if not found
    """
    if connector_id not in CONNECTOR_REGISTRY:
        return None
    return CONNECTOR_REGISTRY[connector_id].get_connector_info()


def list_connectors_by_type(connector_type: str) -> list[dict[str, Any]]:
    """
    List connectors filtered by type.

    Args:
        connector_type: Type to filter by (database, cloud_storage, etc.)

    Returns:
        Filtered list of connector info
    """
    return [
        connector_class.get_connector_info()
        for connector_class in CONNECTOR_REGISTRY.values()
        if connector_class.connector_type.value == connector_type
    ]


# Auto-import all connector modules to trigger registration
def _auto_register_connectors():
    """Import all connector modules to register them."""
    import importlib
    import pkgutil
    from pathlib import Path

    # Get the package directory
    package_dir = Path(__file__).parent

    # Import database connectors
    databases_dir = package_dir / "databases"
    if databases_dir.exists():
        for _, module_name, _ in pkgutil.iter_modules([str(databases_dir)]):
            try:
                importlib.import_module(f".databases.{module_name}", __package__)
            except ImportError as e:
                logger.debug(f"Could not import database connector {module_name}: {e}")

    # Import cloud storage connectors
    cloud_dir = package_dir / "cloud_storage"
    if cloud_dir.exists():
        for _, module_name, _ in pkgutil.iter_modules([str(cloud_dir)]):
            try:
                importlib.import_module(f".cloud_storage.{module_name}", __package__)
            except ImportError as e:
                logger.debug(f"Could not import cloud storage connector {module_name}: {e}")

    # Import storage connectors (alternate folder)
    storage_dir = package_dir / "storage"
    if storage_dir.exists():
        for _, module_name, _ in pkgutil.iter_modules([str(storage_dir)]):
            try:
                importlib.import_module(f".storage.{module_name}", __package__)
            except ImportError as e:
                logger.debug(f"Could not import storage connector {module_name}: {e}")

    # Import productivity connectors
    productivity_dir = package_dir / "productivity"
    if productivity_dir.exists():
        for _, module_name, _ in pkgutil.iter_modules([str(productivity_dir)]):
            try:
                importlib.import_module(f".productivity.{module_name}", __package__)
            except ImportError as e:
                logger.debug(f"Could not import productivity connector {module_name}: {e}")


# Run auto-registration on module import
try:
    _auto_register_connectors()
except Exception as e:
    logger.warning(f"Error during connector auto-registration: {e}")
