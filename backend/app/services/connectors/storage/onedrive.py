"""OneDrive Cloud Storage Connector.

Connector for Microsoft OneDrive using MSAL and Graph API.
"""
from __future__ import annotations

import logging
import posixpath
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


class OneDriveConnector(ConnectorBase):
    """Microsoft OneDrive cloud storage connector."""

    connector_id = "onedrive"
    connector_name = "Microsoft OneDrive"
    connector_type = ConnectorType.CLOUD_STORAGE
    auth_types = [AuthType.OAUTH2]
    capabilities = [
        ConnectorCapability.READ,
        ConnectorCapability.WRITE,
        ConnectorCapability.STREAM,
    ]
    free_tier = True

    GRAPH_API_URL = "https://graph.microsoft.com/v1.0"
    SCOPES = ["Files.ReadWrite.All", "User.Read", "offline_access"]

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._access_token = None
        self._session = None

    @staticmethod
    def _safe_path(path: str) -> str:
        """Normalise *path* and reject directory-traversal attempts.

        Strips leading/trailing slashes, collapses ``..`` via
        ``posixpath.normpath`` and raises ``ValueError`` if the result
        still escapes the root (i.e. starts with ``..``).
        """
        cleaned = path.strip("/")
        if not cleaned:
            return ""
        normalised = posixpath.normpath(cleaned)
        # normpath("../../x") → "../../x"  — still escapes root
        if normalised.startswith(".."):
            raise ValueError(
                f"Path traversal not allowed: {path!r}"
            )
        return normalised

    async def connect(self) -> bool:
        """Establish connection to OneDrive."""
        try:
            import httpx

            self._access_token = self.config.get("access_token")
            if not self._access_token:
                # Try to get token using client credentials
                await self._get_token_with_msal()

            self._session = httpx.AsyncClient(
                headers={"Authorization": f"Bearer {self._access_token}"}
            )
            self._connected = True
            return True
        except Exception as e:
            self._connected = False
            raise ConnectionError("Failed to connect to OneDrive") from e

    async def _get_token_with_msal(self) -> None:
        """Get access token using MSAL."""
        import msal

        app = msal.ConfidentialClientApplication(
            self.config.get("client_id"),
            authority=f"https://login.microsoftonline.com/{self.config.get('tenant_id', 'common')}",
            client_credential=self.config.get("client_secret"),
        )

        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

        if "access_token" in result:
            self._access_token = result["access_token"]
        else:
            raise ConnectionError(f"Failed to acquire token: {result.get('error_description')}")

    async def disconnect(self) -> None:
        """Close the connection."""
        if self._session:
            await self._session.aclose()
            self._session = None
        self._access_token = None
        self._connected = False

    async def test_connection(self) -> ConnectionTest:
        """Test the connection."""
        start_time = time.time()
        try:
            if not self._connected:
                await self.connect()

            response = await self._session.get(f"{self.GRAPH_API_URL}/me")
            response.raise_for_status()
            user = response.json()

            latency = (time.time() - start_time) * 1000
            return ConnectionTest(
                success=True,
                latency_ms=latency,
                details={"user": user.get("userPrincipalName")},
            )
        except Exception as e:
            logger.warning("connection_test_failed", exc_info=True)
            return ConnectionTest(success=False, error="Connection test failed")

    async def list_files(
        self,
        path: str = "/",
        recursive: bool = False,
    ) -> list[FileInfo]:
        """List files in OneDrive."""
        if not self._connected:
            await self.connect()

        files: list[FileInfo] = []

        if path == "/" or path == "root":
            url = f"{self.GRAPH_API_URL}/me/drive/root/children"
        else:
            safe = self._safe_path(path)
            url = f"{self.GRAPH_API_URL}/me/drive/root:/{safe}:/children"

        while url:
            response = await self._session.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get("value", []):
                is_folder = "folder" in item
                files.append(FileInfo(
                    id=item["id"],
                    name=item["name"],
                    path=item.get("parentReference", {}).get("path", "") + "/" + item["name"],
                    size_bytes=item.get("size", 0),
                    mime_type=item.get("file", {}).get("mimeType"),
                    created_at=item.get("createdDateTime"),
                    modified_at=item.get("lastModifiedDateTime"),
                    is_folder=is_folder,
                    download_url=item.get("@microsoft.graph.downloadUrl"),
                ))

            url = data.get("@odata.nextLink")

        return files

    async def download_file(
        self,
        file_id: str,
        destination: Optional[str] = None,
    ) -> bytes:
        """Download a file from OneDrive."""
        if not self._connected:
            await self.connect()

        response = await self._session.get(
            f"{self.GRAPH_API_URL}/me/drive/items/{file_id}/content"
        )
        response.raise_for_status()
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
        """Upload a file to OneDrive."""
        if not self._connected:
            await self.connect()

        safe_dir = self._safe_path(path) if path and path != "/" else ""
        upload_path = f"{safe_dir}/{filename}" if safe_dir else filename

        response = await self._session.put(
            f"{self.GRAPH_API_URL}/me/drive/root:/{upload_path}:/content",
            content=content,
            headers={"Content-Type": mime_type or "application/octet-stream"},
        )
        response.raise_for_status()
        item = response.json()

        return FileInfo(
            id=item["id"],
            name=item["name"],
            path=item.get("parentReference", {}).get("path", "") + "/" + item["name"],
            size_bytes=item.get("size", len(content)),
            mime_type=item.get("file", {}).get("mimeType"),
            created_at=item.get("createdDateTime"),
            is_folder=False,
        )

    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from OneDrive."""
        if not self._connected:
            await self.connect()

        try:
            response = await self._session.delete(
                f"{self.GRAPH_API_URL}/me/drive/items/{file_id}"
            )
            return response.status_code == 204
        except Exception:
            logger.warning("delete_file_failed", exc_info=True)
            return False

    def get_oauth_url(self, redirect_uri: str, state: str) -> Optional[str]:
        """Get OAuth authorization URL."""
        import urllib.parse

        params = {
            "client_id": self.config.get("client_id"),
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.SCOPES),
            "response_mode": "query",
            "state": state,
        }

        base_url = f"https://login.microsoftonline.com/{self.config.get('tenant_id', 'common')}/oauth2/v2.0/authorize"
        return f"{base_url}?{urllib.parse.urlencode(params)}"

    def handle_oauth_callback(
        self,
        code: str,
        redirect_uri: str,
    ) -> dict[str, Any]:
        """Handle OAuth callback."""
        import msal

        app = msal.ConfidentialClientApplication(
            self.config.get("client_id"),
            authority=f"https://login.microsoftonline.com/{self.config.get('tenant_id', 'common')}",
            client_credential=self.config.get("client_secret"),
        )

        result = app.acquire_token_by_authorization_code(
            code,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri,
        )

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
                "client_id": {"type": "string", "description": "Azure App Client ID"},
                "client_secret": {"type": "string", "format": "password", "description": "Azure App Client Secret"},
                "tenant_id": {"type": "string", "default": "common", "description": "Azure Tenant ID"},
                "access_token": {"type": "string", "description": "OAuth access token"},
                "refresh_token": {"type": "string", "description": "OAuth refresh token"},
            },
            "required": ["client_id", "client_secret"],
        }
