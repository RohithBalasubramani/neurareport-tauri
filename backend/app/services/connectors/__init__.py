# Connector Services
"""
Services for database and cloud storage connectors.
"""

from .base import ConnectorBase, ConnectorType, AuthType, ConnectorCapability
from .registry import get_connector, list_connectors, register_connector
from .resilience import (
    with_retry,
    retry_on_connection_error,
    retry_with_longer_backoff,
    is_transient_error,
    is_permanent_error,
    ConnectionHealth,
    TRANSIENT_ERRORS,
    PERMANENT_ERRORS,
)

# Database Connectors
from .databases import (
    PostgreSQLConnector,
    MySQLConnector,
    MongoDBConnector,
    SQLServerConnector,
    BigQueryConnector,
    SnowflakeConnector,
    ElasticsearchConnector,
    DuckDBConnector,
)

# Storage Connectors
from .storage import (
    AWSS3Connector,
    AzureBlobConnector,
    DropboxConnector,
    GoogleDriveConnector,
    OneDriveConnector,
    SFTPConnector,
)

__all__ = [
    # Base
    "ConnectorBase",
    "ConnectorType",
    "AuthType",
    "ConnectorCapability",
    "get_connector",
    "list_connectors",
    "register_connector",
    # Resilience
    "with_retry",
    "retry_on_connection_error",
    "retry_with_longer_backoff",
    "is_transient_error",
    "is_permanent_error",
    "ConnectionHealth",
    "TRANSIENT_ERRORS",
    "PERMANENT_ERRORS",
    # Database Connectors
    "PostgreSQLConnector",
    "MySQLConnector",
    "MongoDBConnector",
    "SQLServerConnector",
    "BigQueryConnector",
    "SnowflakeConnector",
    "ElasticsearchConnector",
    "DuckDBConnector",
    # Storage Connectors
    "AWSS3Connector",
    "AzureBlobConnector",
    "DropboxConnector",
    "GoogleDriveConnector",
    "OneDriveConnector",
    "SFTPConnector",
]
