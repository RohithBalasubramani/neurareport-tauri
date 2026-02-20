"""Dropbox Cloud Storage Connector.

Connector for Dropbox using dropbox SDK.
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


class DropboxConnector(ConnectorBase):
    """Dropbox cloud storage connector."""

    connector_id = "dropbox"
    connector_name = "Dropbox"
    connector_type = ConnectorType.CLOUD_STORAGE
    auth_types = [AuthType.OAUTH2, AuthType.API_KEY]
    capabilities = [
        ConnectorCapability.READ,
        ConnectorCapability.WRITE,
        ConnectorCapability.STREAM,
    ]
    free_tier = True

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._client = None

    async def connect(self) -> bool:
        """Establish connection to Dropbox."""
        try:
            import dropbox

            access_token = self.config.get("access_token")
            refresh_token = self.config.get("refresh_token")
            app_key = self.config.get("app_key")
            app_secret = self.config.get("app_secret")

            if refresh_token and app_key and app_secret:
                self._client = dropbox.Dropbox(
                    oauth2_refresh_token=refresh_token,
                    app_key=app_key,
                    app_secret=app_secret,
                )
            elif access_token:
                self._client = dropbox.Dropbox(access_token)
            else:
                raise ValueError("Access token or refresh token required")

            self._connected = True
            return True
        except Exception as e:
            self._connected = False
            raise ConnectionError("Failed to connect to Dropbox") from e

    async def disconnect(self) -> None:
        """Close the connection."""
        self._client = None
        self._connected = False

    async def test_connection(self) -> ConnectionTest:
        """Test the connection."""
        start_time = time.time()
        try:
            if not self._connected:
                await self.connect()

            account = self._client.users_get_current_account()
            latency = (time.time() - start_time) * 1000

            return ConnectionTest(
                success=True,
                latency_ms=latency,
                details={"email": account.email},
            )
        except Exception as e:
            logger.warning("connection_test_failed", exc_info=True)
            return ConnectionTest(success=False, error="Connection test failed")

    async def list_files(
        self,
        path: str = "",
        recursive: bool = False,
    ) -> list[FileInfo]:
        """List files in Dropbox."""
        if not self._connected:
            await self.connect()

        import dropbox

        files: list[FileInfo] = []
        folder_path = path if path else ""

        result = self._client.files_list_folder(folder_path, recursive=recursive)

        while True:
            for entry in result.entries:
                is_folder = isinstance(entry, dropbox.files.FolderMetadata)
                files.append(FileInfo(
                    id=entry.id if hasattr(entry, "id") else entry.path_display,
                    name=entry.name,
                    path=entry.path_display,
                    size_bytes=getattr(entry, "size", 0),
                    modified_at=getattr(entry, "server_modified", None),
                    is_folder=is_folder,
                ))

            if not result.has_more:
                break
            result = self._client.files_list_folder_continue(result.cursor)

        return files

    async def download_file(
        self,
        file_id: str,
        destination: Optional[str] = None,
    ) -> bytes:
        """Download a file from Dropbox."""
        if not self._connected:
            await self.connect()

        # file_id can be either an ID or a path
        metadata, response = self._client.files_download(file_id)
        content = response.content

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
        """Upload a file to Dropbox."""
        if not self._connected:
            await self.connect()

        import dropbox

        upload_path = f"{path}/{filename}" if path else f"/{filename}"

        metadata = self._client.files_upload(
            content,
            upload_path,
            mode=dropbox.files.WriteMode.overwrite,
        )

        return FileInfo(
            id=metadata.id,
            name=metadata.name,
            path=metadata.path_display,
            size_bytes=metadata.size,
            modified_at=str(metadata.server_modified) if metadata.server_modified else None,
            is_folder=False,
        )

    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from Dropbox."""
        if not self._connected:
            await self.connect()

        try:
            self._client.files_delete_v2(file_id)
            return True
        except Exception:
            logger.warning("delete_file_failed", exc_info=True)
            return False

    async def get_shared_link(self, file_id: str) -> str:
        """Get a shared link for a file."""
        if not self._connected:
            await self.connect()

        try:
            shared_link = self._client.sharing_create_shared_link_with_settings(file_id)
            return shared_link.url
        except Exception:
            # Link might already exist
            links = self._client.sharing_list_shared_links(path=file_id)
            if links.links:
                return links.links[0].url
            raise

    def get_oauth_url(self, redirect_uri: str, state: str) -> Optional[str]:
        """Get OAuth authorization URL."""
        import dropbox

        flow = dropbox.DropboxOAuth2Flow(
            consumer_key=self.config.get("app_key"),
            consumer_secret=self.config.get("app_secret"),
            redirect_uri=redirect_uri,
            session={},
            csrf_token_session_key="dropbox-csrf-token",
            token_access_type="offline",
        )

        return flow.start(state=state)

    def handle_oauth_callback(
        self,
        code: str,
        redirect_uri: str,
    ) -> dict[str, Any]:
        """Handle OAuth callback."""
        import dropbox

        flow = dropbox.DropboxOAuth2Flow(
            consumer_key=self.config.get("app_key"),
            consumer_secret=self.config.get("app_secret"),
            redirect_uri=redirect_uri,
            session={},
            csrf_token_session_key="dropbox-csrf-token",
            token_access_type="offline",
        )

        # In a real implementation, you would use flow.finish() with the query params
        # For now, we'll do a manual token exchange
        import requests
        response = requests.post(
            "https://api.dropboxapi.com/oauth2/token",
            data={
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
                "client_id": self.config.get("app_key"),
                "client_secret": self.config.get("app_secret"),
            },
        )
        result = response.json()

        return {
            "access_token": result.get("access_token"),
            "refresh_token": result.get("refresh_token"),
            "expires_in": result.get("expires_in"),
            "token_type": result.get("token_type"),
        }

    @classmethod
    def get_config_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "app_key": {"type": "string", "description": "Dropbox App Key"},
                "app_secret": {"type": "string", "format": "password", "description": "Dropbox App Secret"},
                "access_token": {"type": "string", "description": "OAuth access token"},
                "refresh_token": {"type": "string", "description": "OAuth refresh token"},
            },
            "required": ["app_key", "app_secret"],
        }
