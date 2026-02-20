"""AWS S3 Cloud Storage Connector.

Connector for Amazon S3 using boto3.
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


class AWSS3Connector(ConnectorBase):
    """AWS S3 cloud storage connector."""

    connector_id = "aws_s3"
    connector_name = "Amazon S3"
    connector_type = ConnectorType.CLOUD_STORAGE
    auth_types = [AuthType.API_KEY, AuthType.SERVICE_ACCOUNT]
    capabilities = [
        ConnectorCapability.READ,
        ConnectorCapability.WRITE,
        ConnectorCapability.STREAM,
    ]
    free_tier = True

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self._client = None
        self._bucket = None

    async def connect(self) -> bool:
        """Establish connection to AWS S3."""
        try:
            import boto3

            self._client = boto3.client(
                "s3",
                aws_access_key_id=self.config.get("access_key_id"),
                aws_secret_access_key=self.config.get("secret_access_key"),
                region_name=self.config.get("region", "us-east-1"),
            )
            self._bucket = self.config.get("bucket")
            self._connected = True
            return True
        except Exception as e:
            self._connected = False
            raise ConnectionError("Failed to connect to AWS S3") from e

    async def disconnect(self) -> None:
        """Close the connection."""
        self._client = None
        self._bucket = None
        self._connected = False

    async def test_connection(self) -> ConnectionTest:
        """Test the connection."""
        start_time = time.time()
        try:
            if not self._connected:
                await self.connect()

            # Try to list bucket contents (head bucket)
            self._client.head_bucket(Bucket=self._bucket)

            latency = (time.time() - start_time) * 1000
            return ConnectionTest(
                success=True,
                latency_ms=latency,
                details={"bucket": self._bucket},
            )
        except Exception as e:
            logger.warning("connection_test_failed", exc_info=True)
            return ConnectionTest(success=False, error="Connection test failed")

    async def list_files(
        self,
        path: str = "",
        recursive: bool = False,
    ) -> list[FileInfo]:
        """List files in S3 bucket."""
        if not self._connected:
            await self.connect()

        files: list[FileInfo] = []
        prefix = path.lstrip("/")

        paginator = self._client.get_paginator("list_objects_v2")
        params = {"Bucket": self._bucket, "Prefix": prefix}

        if not recursive:
            params["Delimiter"] = "/"

        for page in paginator.paginate(**params):
            # Add folders (common prefixes)
            for prefix_info in page.get("CommonPrefixes", []):
                folder_path = prefix_info["Prefix"]
                files.append(FileInfo(
                    id=folder_path,
                    name=folder_path.rstrip("/").split("/")[-1],
                    path=folder_path,
                    size_bytes=0,
                    is_folder=True,
                ))

            # Add files
            for obj in page.get("Contents", []):
                key = obj["Key"]
                files.append(FileInfo(
                    id=key,
                    name=key.split("/")[-1],
                    path=key,
                    size_bytes=obj["Size"],
                    modified_at=obj["LastModified"].isoformat() if obj.get("LastModified") else None,
                    is_folder=False,
                ))

        return files

    async def download_file(
        self,
        file_id: str,
        destination: Optional[str] = None,
    ) -> bytes:
        """Download a file from S3."""
        if not self._connected:
            await self.connect()

        response = self._client.get_object(Bucket=self._bucket, Key=file_id)
        content = response["Body"].read()

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
        """Upload a file to S3."""
        if not self._connected:
            await self.connect()

        key = f"{path.strip('/')}/{filename}" if path else filename
        extra_args = {}
        if mime_type:
            extra_args["ContentType"] = mime_type

        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=content,
            **extra_args,
        )

        return FileInfo(
            id=key,
            name=filename,
            path=key,
            size_bytes=len(content),
            mime_type=mime_type,
            is_folder=False,
        )

    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from S3."""
        if not self._connected:
            await self.connect()

        try:
            self._client.delete_object(Bucket=self._bucket, Key=file_id)
            return True
        except Exception:
            logger.warning("delete_file_failed", exc_info=True)
            return False

    async def get_presigned_url(
        self,
        file_id: str,
        expires_in: int = 3600,
    ) -> str:
        """Generate a presigned URL for downloading."""
        if not self._connected:
            await self.connect()

        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": file_id},
            ExpiresIn=expires_in,
        )

    @classmethod
    def get_config_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "access_key_id": {"type": "string", "description": "AWS Access Key ID"},
                "secret_access_key": {"type": "string", "format": "password", "description": "AWS Secret Access Key"},
                "region": {"type": "string", "default": "us-east-1", "description": "AWS Region"},
                "bucket": {"type": "string", "description": "S3 Bucket name"},
            },
            "required": ["access_key_id", "secret_access_key", "bucket"],
        }
