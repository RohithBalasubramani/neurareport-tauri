"""
HashiCorp Vault secrets client.

Reads secrets from Vault KV v2 store with caching and fallback to env vars.
Supports AppRole authentication for production and token auth for development.

Based on: hashicorp/vault-examples patterns
"""
from __future__ import annotations
import os
import logging
from typing import Any, Optional
from functools import lru_cache

logger = logging.getLogger("neura.secrets")


class VaultSecretClient:
    """Read secrets from HashiCorp Vault with env var fallback."""

    def __init__(
        self,
        vault_addr: Optional[str] = None,
        vault_token: Optional[str] = None,
        role_id: Optional[str] = None,
        secret_id: Optional[str] = None,
        mount_point: str = "secret",
    ):
        self.vault_addr = vault_addr or os.getenv("VAULT_ADDR")
        self.mount_point = mount_point
        self._client = None
        self._token = vault_token or os.getenv("VAULT_TOKEN")
        self._role_id = role_id or os.getenv("VAULT_ROLE_ID")
        self._secret_id = secret_id or os.getenv("VAULT_SECRET_ID")
        self._cache: dict[str, dict[str, Any]] = {}

    @property
    def is_configured(self) -> bool:
        return bool(self.vault_addr)

    def _get_client(self):
        if self._client is None:
            try:
                import hvac
                self._client = hvac.Client(url=self.vault_addr, token=self._token)
                if self._role_id and self._secret_id:
                    result = self._client.auth.approle.login(
                        role_id=self._role_id,
                        secret_id=self._secret_id,
                    )
                    self._client.token = result["auth"]["client_token"]
                    logger.info("vault_approle_authenticated", extra={"event": "vault_approle_authenticated"})
                if not self._client.is_authenticated():
                    logger.warning("vault_not_authenticated", extra={"event": "vault_not_authenticated"})
                    self._client = None
            except ImportError:
                logger.warning("hvac_not_installed", extra={"event": "hvac_not_installed"})
                self._client = None
            except Exception as exc:
                logger.warning("vault_connect_failed", extra={"event": "vault_connect_failed", "error": str(exc)})
                self._client = None
        return self._client

    def read_secret(self, path: str, key: Optional[str] = None, default: Any = None) -> Any:
        """Read a secret from Vault KV v2, with caching and env var fallback."""
        # Check cache first
        if path in self._cache:
            data = self._cache[path]
            return data.get(key, default) if key else data

        # Try Vault
        if self.is_configured:
            client = self._get_client()
            if client:
                try:
                    response = client.secrets.kv.v2.read_secret_version(
                        path=path, mount_point=self.mount_point, raise_on_deleted_version=True,
                    )
                    data = response["data"]["data"]
                    self._cache[path] = data
                    logger.info("vault_secret_read", extra={"event": "vault_secret_read", "path": path})
                    return data.get(key, default) if key else data
                except Exception as exc:
                    logger.warning("vault_read_failed", extra={"event": "vault_read_failed", "path": path, "error": str(exc)})

        # Fallback to environment variable
        env_key = f"NEURA_{path.upper().replace('/', '_')}_{key.upper()}" if key else None
        if env_key:
            env_val = os.getenv(env_key)
            if env_val is not None:
                return env_val

        return default

    def write_secret(self, path: str, data: dict[str, Any]) -> bool:
        """Write a secret to Vault KV v2. Returns True on success."""
        if not self.is_configured:
            logger.warning("vault_write_skipped", extra={"event": "vault_write_skipped", "reason": "not configured"})
            return False
        client = self._get_client()
        if not client:
            return False
        try:
            client.secrets.kv.v2.create_or_update_secret(
                path=path, secret=data, mount_point=self.mount_point,
            )
            # Invalidate cache for this path
            self._cache.pop(path, None)
            logger.info("vault_secret_written", extra={"event": "vault_secret_written", "path": path})
            return True
        except Exception as exc:
            logger.warning("vault_write_failed", extra={"event": "vault_write_failed", "path": path, "error": str(exc)})
            return False

    def clear_cache(self) -> None:
        self._cache.clear()


_vault_client: Optional[VaultSecretClient] = None


def get_vault_client() -> VaultSecretClient:
    global _vault_client
    if _vault_client is None:
        _vault_client = VaultSecretClient()
    return _vault_client
