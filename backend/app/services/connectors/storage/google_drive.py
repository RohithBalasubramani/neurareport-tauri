"""Google Drive Cloud Storage Connector.

Connector for Google Drive using google-api-python-client.
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


class GoogleDriveConnector(ConnectorBase):
    """Google Drive cloud storage connector."""

    connector_id = "google_drive"
    connector_name = "Google Drive"
    connector_type = ConnectorType.CLOUD_STORAGE
    auth_types = [AuthType.OAUTH2, AuthType.SERVICE_ACCOUNT]
    capabilities = [
        ConnectorCapability.READ,
        ConnectorCapability.WRITE,
        ConnectorCapability.STREAM,
    ]
    free_tier = True

    # OAuth scopes
    SCOPES = [
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.file",
    ]

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._service = None
        self._credentials = None

    async def connect(self) -> bool:
        """Establish connection to Google Drive."""
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            credentials_json = self.config.get("credentials_json")
            credentials_path = self.config.get("credentials_path")

            if credentials_json:
                import json
                if isinstance(credentials_json, str):
                    credentials_json = json.loads(credentials_json)
                self._credentials = service_account.Credentials.from_service_account_info(
                    credentials_json,
                    scopes=self.SCOPES,
                )
            elif credentials_path:
                self._credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=self.SCOPES,
                )
            else:
                # Use OAuth tokens if available
                from google.oauth2.credentials import Credentials
                self._credentials = Credentials(
                    token=self.config.get("access_token"),
                    refresh_token=self.config.get("refresh_token"),
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=self.config.get("client_id"),
                    client_secret=self.config.get("client_secret"),
                )

            self._service = build("drive", "v3", credentials=self._credentials)
            self._connected = True
            return True
        except Exception as e:
            self._connected = False
            raise ConnectionError("Failed to connect to Google Drive") from e

    async def disconnect(self) -> None:
        """Close the connection."""
        self._service = None
        self._credentials = None
        self._connected = False

    async def test_connection(self) -> ConnectionTest:
        """Test the connection."""
        start_time = time.time()
        try:
            if not self._connected:
                await self.connect()

            # Get about info
            about = self._service.about().get(fields="user").execute()
            latency = (time.time() - start_time) * 1000

            return ConnectionTest(
                success=True,
                latency_ms=latency,
                details={"user": about.get("user", {}).get("emailAddress")},
            )
        except Exception as e:
            logger.warning("connection_test_failed", exc_info=True)
            return ConnectionTest(success=False, error="Connection test failed")

    async def list_files(
        self,
        path: str = "root",
        recursive: bool = False,
    ) -> list[FileInfo]:
        """List files in Google Drive."""
        if not self._connected:
            await self.connect()

        files: list[FileInfo] = []
        parent_id = path if path != "/" else "root"

        query = f"'{parent_id}' in parents and trashed = false"
        fields = "nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, webContentLink)"

        page_token = None
        while True:
            response = self._service.files().list(
                q=query,
                pageSize=100,
                fields=fields,
                pageToken=page_token,
            ).execute()

            for item in response.get("files", []):
                is_folder = item["mimeType"] == "application/vnd.google-apps.folder"
                files.append(FileInfo(
                    id=item["id"],
                    name=item["name"],
                    path=f"/{item['name']}",
                    size_bytes=int(item.get("size", 0)),
                    mime_type=item["mimeType"],
                    created_at=item.get("createdTime"),
                    modified_at=item.get("modifiedTime"),
                    is_folder=is_folder,
                    download_url=item.get("webContentLink"),
                ))

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return files

    async def download_file(
        self,
        file_id: str,
        destination: Optional[str] = None,
    ) -> bytes:
        """Download a file from Google Drive."""
        if not self._connected:
            await self.connect()

        from googleapiclient.http import MediaIoBaseDownload
        import io

        request = self._service.files().get_media(fileId=file_id)
        file_buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        content = file_buffer.getvalue()

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
        """Upload a file to Google Drive."""
        if not self._connected:
            await self.connect()

        from googleapiclient.http import MediaInMemoryUpload

        file_metadata = {"name": filename}
        if path and path != "/":
            file_metadata["parents"] = [path]

        media = MediaInMemoryUpload(
            content,
            mimetype=mime_type or "application/octet-stream",
        )

        file = self._service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, name, mimeType, size, createdTime, webContentLink",
        ).execute()

        return FileInfo(
            id=file["id"],
            name=file["name"],
            path=f"/{file['name']}",
            size_bytes=len(content),
            mime_type=file.get("mimeType"),
            created_at=file.get("createdTime"),
            is_folder=False,
            download_url=file.get("webContentLink"),
        )

    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from Google Drive."""
        if not self._connected:
            await self.connect()

        try:
            self._service.files().delete(fileId=file_id).execute()
            return True
        except Exception:
            logger.warning("delete_file_failed", exc_info=True)
            return False

    def get_oauth_url(self, redirect_uri: str, state: str) -> Optional[str]:
        """Get OAuth authorization URL."""
        from google_auth_oauthlib.flow import Flow

        client_config = {
            "web": {
                "client_id": self.config.get("client_id"),
                "client_secret": self.config.get("client_secret"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

        flow = Flow.from_client_config(client_config, scopes=self.SCOPES)
        flow.redirect_uri = redirect_uri

        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            state=state,
        )

        return auth_url

    def handle_oauth_callback(
        self,
        code: str,
        redirect_uri: str,
    ) -> dict[str, Any]:
        """Handle OAuth callback."""
        from google_auth_oauthlib.flow import Flow

        client_config = {
            "web": {
                "client_id": self.config.get("client_id"),
                "client_secret": self.config.get("client_secret"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

        flow = Flow.from_client_config(client_config, scopes=self.SCOPES)
        flow.redirect_uri = redirect_uri

        flow.fetch_token(code=code)
        credentials = flow.credentials

        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
        }

    @classmethod
    def get_config_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "OAuth Client ID"},
                "client_secret": {"type": "string", "format": "password", "description": "OAuth Client Secret"},
                "credentials_path": {"type": "string", "description": "Path to service account JSON"},
                "credentials_json": {"type": "object", "description": "Service account credentials JSON"},
                "access_token": {"type": "string", "description": "OAuth access token"},
                "refresh_token": {"type": "string", "description": "OAuth refresh token"},
            },
            "required": [],
        }
