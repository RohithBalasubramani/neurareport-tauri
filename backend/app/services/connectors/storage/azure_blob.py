"""Azure Blob Storage Connector.

Connector for Azure Blob Storage using azure-storage-blob.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)

from backend.app.services.connectors.base import (
    AuthType,
    ConnectionTest,
    ConnectorBase,
    ConnectorCapability,
    ConnectorType,
    FileInfo,
)


class AzureBlobConnector(ConnectorBase):
    """Azure Blob Storage connector."""

    connector_id = "azure_blob"
    connector_name = "Azure Blob Storage"
    connector_type = ConnectorType.CLOUD_STORAGE
    auth_types = [AuthType.CONNECTION_STRING, AuthType.API_KEY]
    capabilities = [
        ConnectorCapability.READ,
        ConnectorCapability.WRITE,
        ConnectorCapability.STREAM,
    ]
    free_tier = True

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._blob_service_client = None
        self._container_client = None

    async def connect(self) -> bool:
        """Establish connection to Azure Blob Storage."""
        try:
            from azure.storage.blob import BlobServiceClient

            connection_string = self.config.get("connection_string")
            account_name = self.config.get("account_name")
            account_key = self.config.get("account_key")
            container_name = self.config.get("container")

            if connection_string:
                self._blob_service_client = BlobServiceClient.from_connection_string(
                    connection_string
                )
            elif account_name and account_key:
                account_url = f"https://{account_name}.blob.core.windows.net"
                self._blob_service_client = BlobServiceClient(
                    account_url=account_url,
                    credential=account_key,
                )
            else:
                raise ValueError("Connection string or account credentials required")

            if container_name:
                self._container_client = self._blob_service_client.get_container_client(
                    container_name
                )

            self._connected = True
            return True
        except Exception as e:
            self._connected = False
            raise ConnectionError("Failed to connect to Azure Blob Storage") from e

    async def disconnect(self) -> None:
        """Close the connection."""
        self._blob_service_client = None
        self._container_client = None
        self._connected = False

    async def test_connection(self) -> ConnectionTest:
        """Test the connection."""
        start_time = time.time()
        try:
            if not self._connected:
                await self.connect()

            # Try to get container properties
            if self._container_client:
                props = self._container_client.get_container_properties()
                container_info = {"container": props.name}
            else:
                # List containers
                containers = list(self._blob_service_client.list_containers(max_results=1))
                container_info = {"containers": len(containers)}

            latency = (time.time() - start_time) * 1000
            return ConnectionTest(
                success=True,
                latency_ms=latency,
                details=container_info,
            )
        except Exception as e:
            logger.warning("connection_test_failed", exc_info=True)
            return ConnectionTest(success=False, error="Connection test failed")

    async def list_files(
        self,
        path: str = "",
        recursive: bool = False,
    ) -> list[FileInfo]:
        """List files in Azure Blob container."""
        if not self._connected:
            await self.connect()

        files: list[FileInfo] = []
        prefix = path.strip("/") + "/" if path and not path.endswith("/") else path.lstrip("/")

        if recursive:
            blobs = self._container_client.list_blobs(name_starts_with=prefix or None)
        else:
            blobs = self._container_client.walk_blobs(name_starts_with=prefix or None)

        for blob in blobs:
            # Check if it's a prefix (folder)
            if hasattr(blob, "prefix"):
                files.append(FileInfo(
                    id=blob.prefix,
                    name=blob.prefix.rstrip("/").split("/")[-1],
                    path=blob.prefix,
                    size_bytes=0,
                    is_folder=True,
                ))
            else:
                files.append(FileInfo(
                    id=blob.name,
                    name=blob.name.split("/")[-1],
                    path=blob.name,
                    size_bytes=blob.size or 0,
                    mime_type=blob.content_settings.content_type if blob.content_settings else None,
                    created_at=str(blob.creation_time) if blob.creation_time else None,
                    modified_at=str(blob.last_modified) if blob.last_modified else None,
                    is_folder=False,
                ))

        return files

    async def download_file(
        self,
        file_id: str,
        destination: Optional[str] = None,
    ) -> bytes:
        """Download a file from Azure Blob Storage."""
        if not self._connected:
            await self.connect()

        blob_client = self._container_client.get_blob_client(file_id)
        content = blob_client.download_blob().readall()

        if destination:
            with open(destination, "wb") as f:
                f.write(content)

        return content

    async def upload_file(
        self,
        content: bytes,
        path: str,
        filename: str,
        mime_type: Optional[str] = None,
    ) -> FileInfo:
        """Upload a file to Azure Blob Storage."""
        if not self._connected:
            await self.connect()

        from azure.storage.blob import ContentSettings

        blob_name = f"{path.strip('/')}/{filename}" if path else filename

        blob_client = self._container_client.get_blob_client(blob_name)

        content_settings = None
        if mime_type:
            content_settings = ContentSettings(content_type=mime_type)

        blob_client.upload_blob(
            content,
            overwrite=True,
            content_settings=content_settings,
        )

        return FileInfo(
            id=blob_name,
            name=filename,
            path=blob_name,
            size_bytes=len(content),
            mime_type=mime_type,
            is_folder=False,
        )

    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from Azure Blob Storage."""
        if not self._connected:
            await self.connect()

        try:
            blob_client = self._container_client.get_blob_client(file_id)
            blob_client.delete_blob()
            return True
        except Exception:
            logger.warning("delete_file_failed", exc_info=True)
            return False

    async def get_sas_url(
        self,
        file_id: str,
        expires_in: int = 3600,
    ) -> str:
        """Generate a SAS URL for downloading."""
        if not self._connected:
            await self.connect()

        from datetime import datetime, timedelta, timezone
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions

        blob_client = self._container_client.get_blob_client(file_id)

        sas_token = generate_blob_sas(
            account_name=self._blob_service_client.account_name,
            container_name=self._container_client.container_name,
            blob_name=file_id,
            account_key=self.config.get("account_key"),
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(seconds=expires_in),
        )

        return f"{blob_client.url}?{sas_token}"

    @classmethod
    def get_config_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "connection_string": {"type": "string", "description": "Azure connection string"},
                "account_name": {"type": "string", "description": "Storage account name"},
                "account_key": {"type": "string", "format": "password", "description": "Storage account key"},
                "container": {"type": "string", "description": "Container name"},
            },
            "required": ["container"],
        }
