"""
Connector Base - Abstract base class for all connectors.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class ConnectorType(str, Enum):
    """Types of connectors."""

    DATABASE = "database"
    CLOUD_STORAGE = "cloud_storage"
    PRODUCTIVITY = "productivity"
    API = "api"


class AuthType(str, Enum):
    """Authentication types."""

    NONE = "none"
    BASIC = "basic"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    SERVICE_ACCOUNT = "service_account"
    CONNECTION_STRING = "connection_string"


class ConnectorCapability(str, Enum):
    """Connector capabilities."""

    READ = "read"
    WRITE = "write"
    STREAM = "stream"
    SCHEMA_DISCOVERY = "schema_discovery"
    QUERY = "query"
    SYNC = "sync"
    WEBHOOK = "webhook"


class ConnectionTest(BaseModel):
    """Result of connection test."""

    success: bool
    latency_ms: Optional[float] = None
    error: Optional[str] = None
    details: Optional[dict[str, Any]] = None


class SchemaInfo(BaseModel):
    """Database/storage schema information."""

    tables: list[TableInfo] = []
    views: list[TableInfo] = []
    schemas: list[str] = []


class TableInfo(BaseModel):
    """Table/collection information."""

    name: str
    schema_name: Optional[str] = None
    columns: list[ColumnInfo] = []
    row_count: Optional[int] = None
    size_bytes: Optional[int] = None


class ColumnInfo(BaseModel):
    """Column information."""

    name: str
    data_type: str
    nullable: bool = True
    primary_key: bool = False
    foreign_key: Optional[str] = None
    default_value: Optional[Any] = None


class QueryResult(BaseModel):
    """Result of a query execution."""

    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    execution_time_ms: float
    truncated: bool = False
    error: Optional[str] = None


class FileInfo(BaseModel):
    """File/object information for cloud storage."""

    id: str
    name: str
    path: str
    size_bytes: int
    mime_type: Optional[str] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
    is_folder: bool = False
    download_url: Optional[str] = None


class ConnectorBase(ABC):
    """
    Abstract base class for all connectors.

    All connectors must implement the core methods:
    - connect: Establish connection
    - disconnect: Clean up resources
    - test_connection: Verify connection health
    """

    # Class attributes to be overridden by subclasses
    connector_id: str = ""
    connector_name: str = ""
    connector_type: ConnectorType = ConnectorType.DATABASE
    auth_types: list[AuthType] = [AuthType.BASIC]
    capabilities: list[ConnectorCapability] = [ConnectorCapability.READ]
    free_tier: bool = True  # All connectors must be free

    def __init__(self, config: dict[str, Any]):
        """
        Initialize connector with configuration.

        Args:
            config: Connector-specific configuration dict
        """
        self.config = config
        self._connected = False
        self._credentials: Optional[dict] = None

    @property
    def is_connected(self) -> bool:
        """Check if connector is connected."""
        return self._connected

    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the data source.

        Returns:
            True if connection successful
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Clean up connection resources."""
        pass

    @abstractmethod
    async def test_connection(self) -> ConnectionTest:
        """
        Test if connection is healthy.

        Returns:
            ConnectionTest with success status and latency
        """
        pass

    async def discover_schema(self) -> SchemaInfo:
        """
        Discover available data structures (tables, collections, etc.).

        Returns:
            SchemaInfo with discovered structures
        """
        raise NotImplementedError(f"{self.connector_name} does not support schema discovery")

    async def execute_query(
        self,
        query: str,
        parameters: Optional[dict] = None,
        limit: int = 1000,
    ) -> QueryResult:
        """
        Execute a query and return results.

        Args:
            query: Query string (SQL, API path, etc.)
            parameters: Query parameters
            limit: Maximum rows to return

        Returns:
            QueryResult with data
        """
        raise NotImplementedError(f"{self.connector_name} does not support queries")

    async def list_files(
        self,
        path: str = "/",
        recursive: bool = False,
    ) -> list[FileInfo]:
        """
        List files in cloud storage.

        Args:
            path: Directory path
            recursive: Include subdirectories

        Returns:
            List of FileInfo objects
        """
        raise NotImplementedError(f"{self.connector_name} does not support file listing")

    async def download_file(
        self,
        file_id: str,
        destination: Optional[str] = None,
    ) -> bytes:
        """
        Download a file from cloud storage.

        Args:
            file_id: File identifier
            destination: Local path to save file

        Returns:
            File content as bytes
        """
        raise NotImplementedError(f"{self.connector_name} does not support file download")

    async def upload_file(
        self,
        content: bytes,
        path: str,
        filename: str,
        mime_type: Optional[str] = None,
    ) -> FileInfo:
        """
        Upload a file to cloud storage.

        Args:
            content: File content
            path: Destination path
            filename: File name
            mime_type: MIME type

        Returns:
            FileInfo of uploaded file
        """
        raise NotImplementedError(f"{self.connector_name} does not support file upload")

    def get_oauth_url(
        self,
        redirect_uri: str,
        state: str,
    ) -> Optional[str]:
        """
        Get OAuth authorization URL if applicable.

        Args:
            redirect_uri: OAuth callback URL
            state: State parameter for security

        Returns:
            Authorization URL or None
        """
        return None

    def handle_oauth_callback(
        self,
        code: str,
        redirect_uri: str,
    ) -> dict[str, Any]:
        """
        Handle OAuth callback and exchange code for tokens.

        Args:
            code: Authorization code
            redirect_uri: Same redirect_uri used in auth URL

        Returns:
            Token dictionary
        """
        raise NotImplementedError(f"{self.connector_name} does not support OAuth")

    async def refresh_token(self) -> dict[str, Any]:
        """
        Refresh OAuth access token.

        Returns:
            New token dictionary
        """
        raise NotImplementedError(f"{self.connector_name} does not support token refresh")

    @classmethod
    def get_config_schema(cls) -> dict[str, Any]:
        """
        Get JSON schema for connector configuration.

        Returns:
            JSON schema dictionary
        """
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    @classmethod
    def get_connector_info(cls) -> dict[str, Any]:
        """
        Get connector metadata.

        Returns:
            Connector information dictionary
        """
        return {
            "id": cls.connector_id,
            "name": cls.connector_name,
            "type": cls.connector_type.value,
            "auth_types": [at.value for at in cls.auth_types],
            "capabilities": [cap.value for cap in cls.capabilities],
            "free_tier": cls.free_tier,
            "config_schema": cls.get_config_schema(),
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.connector_id}, connected={self._connected})>"
