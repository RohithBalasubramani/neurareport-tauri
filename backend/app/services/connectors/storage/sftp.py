"""SFTP Cloud Storage Connector.

Connector for SFTP/FTP servers using paramiko.
"""
from __future__ import annotations

import logging
import posixpath
import stat
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
from backend.app.utils.ssrf_guard import validate_hostname, SSRFError


class SFTPConnector(ConnectorBase):
    """SFTP/FTP cloud storage connector."""

    connector_id = "sftp"
    connector_name = "SFTP/FTP"
    connector_type = ConnectorType.CLOUD_STORAGE
    auth_types = [AuthType.BASIC, AuthType.API_KEY]  # API_KEY for key-based auth
    capabilities = [
        ConnectorCapability.READ,
        ConnectorCapability.WRITE,
        ConnectorCapability.STREAM,
    ]
    free_tier = True

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._transport = None
        self._sftp = None

    async def connect(self) -> bool:
        """Establish connection to SFTP server."""
        try:
            import paramiko

            host = self.config.get("host")
            port = self.config.get("port", 22)
            validate_hostname(host, port)
            username = self.config.get("username")
            password = self.config.get("password")
            private_key_path = self.config.get("private_key_path")
            private_key_string = self.config.get("private_key")

            self._transport = paramiko.Transport((host, port))

            if private_key_string:
                import io
                key_file = io.StringIO(private_key_string)
                pkey = paramiko.RSAKey.from_private_key(key_file)
                self._transport.connect(username=username, pkey=pkey)
            elif private_key_path:
                pkey = paramiko.RSAKey.from_private_key_file(private_key_path)
                self._transport.connect(username=username, pkey=pkey)
            else:
                self._transport.connect(username=username, password=password)

            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
            self._connected = True
            return True
        except Exception as e:
            self._connected = False
            raise ConnectionError("Failed to connect to SFTP server") from e

    async def disconnect(self) -> None:
        """Close the connection."""
        if self._sftp:
            self._sftp.close()
            self._sftp = None
        if self._transport:
            self._transport.close()
            self._transport = None
        self._connected = False

    async def test_connection(self) -> ConnectionTest:
        """Test the connection."""
        start_time = time.time()
        try:
            if not self._connected:
                await self.connect()

            # Try to list current directory
            self._sftp.listdir(".")
            latency = (time.time() - start_time) * 1000

            return ConnectionTest(
                success=True,
                latency_ms=latency,
                details={"cwd": self._sftp.getcwd() or "/"},
            )
        except Exception as e:
            logger.warning("connection_test_failed", exc_info=True)
            return ConnectionTest(success=False, error="Connection test failed")

    async def list_files(
        self,
        path: str = ".",
        recursive: bool = False,
    ) -> list[FileInfo]:
        """List files in SFTP directory."""
        if not self._connected:
            await self.connect()

        files: list[FileInfo] = []
        path = path or "."

        def _list_dir(dir_path: str) -> None:
            try:
                entries = self._sftp.listdir_attr(dir_path)
                for entry in entries:
                    full_path = f"{dir_path}/{entry.filename}".replace("//", "/")
                    is_folder = stat.S_ISDIR(entry.st_mode)

                    files.append(FileInfo(
                        id=full_path,
                        name=entry.filename,
                        path=full_path,
                        size_bytes=entry.st_size or 0,
                        modified_at=str(entry.st_mtime) if entry.st_mtime else None,
                        is_folder=is_folder,
                    ))

                    if recursive and is_folder:
                        _list_dir(full_path)
            except PermissionError:
                pass  # Skip directories we can't access

        _list_dir(path)
        return files

    async def download_file(
        self,
        file_id: str,
        destination: Optional[str] = None,
    ) -> bytes:
        """Download a file from SFTP."""
        normalized = posixpath.normpath(file_id)
        if '..' in normalized.split('/'):
            raise ValueError("Path traversal not allowed")

        if not self._connected:
            await self.connect()

        import io
        buffer = io.BytesIO()
        self._sftp.getfo(file_id, buffer)
        content = buffer.getvalue()

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
        """Upload a file to SFTP."""
        normalized = posixpath.normpath(f"{path}/{filename}" if path else filename)
        if '..' in normalized.split('/'):
            raise ValueError("Path traversal not allowed")

        if not self._connected:
            await self.connect()

        import io

        remote_path = f"{path}/{filename}" if path else filename
        remote_path = remote_path.replace("//", "/")

        buffer = io.BytesIO(content)
        self._sftp.putfo(buffer, remote_path)

        # Get file info
        try:
            file_stat = self._sftp.stat(remote_path)
            size = file_stat.st_size
        except Exception:
            size = len(content)

        return FileInfo(
            id=remote_path,
            name=filename,
            path=remote_path,
            size_bytes=size,
            is_folder=False,
        )

    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from SFTP."""
        normalized = posixpath.normpath(file_id)
        if '..' in normalized.split('/'):
            raise ValueError("Path traversal not allowed")

        if not self._connected:
            await self.connect()

        try:
            self._sftp.remove(file_id)
            return True
        except Exception:
            logger.warning("delete_file_failed", exc_info=True)
            return False

    async def mkdir(self, path: str) -> bool:
        """Create a directory."""
        if not self._connected:
            await self.connect()

        try:
            self._sftp.mkdir(path)
            return True
        except Exception:
            return False

    async def rmdir(self, path: str) -> bool:
        """Remove a directory."""
        if not self._connected:
            await self.connect()

        try:
            self._sftp.rmdir(path)
            return True
        except Exception:
            return False

    @classmethod
    def get_config_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "host": {"type": "string", "description": "SFTP server hostname"},
                "port": {"type": "integer", "default": 22, "description": "SFTP port"},
                "username": {"type": "string", "description": "Username"},
                "password": {"type": "string", "format": "password", "description": "Password"},
                "private_key_path": {"type": "string", "description": "Path to private key file"},
                "private_key": {"type": "string", "description": "Private key content"},
            },
            "required": ["host", "username"],
        }
