"""Tests for backend adapters."""
from __future__ import annotations

import os
import sys
import tempfile
import types
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

# Stub cryptography module for tests
fernet_module = types.ModuleType("cryptography.fernet")


class _DummyFernet:
    def __init__(self, key):
        self.key = key

    @staticmethod
    def generate_key():
        return b"A" * 44

    def encrypt(self, payload: bytes) -> bytes:
        return payload

    def decrypt(self, token: bytes) -> bytes:
        return token


setattr(fernet_module, "Fernet", _DummyFernet)
setattr(fernet_module, "InvalidToken", Exception)
crypto_module = types.ModuleType("cryptography")
setattr(crypto_module, "fernet", fernet_module)
sys.modules.setdefault("cryptography", crypto_module)
sys.modules.setdefault("cryptography.fernet", fernet_module)


# =============================================================================
# SQLite Adapter Tests
# =============================================================================


class TestSQLiteConnectionPool:
    """Tests for SQLite connection pooling (now DataFrame-based)."""

    def test_pool_creation(self, tmp_path):
        """Connection pool should be created with proper size."""
        from backend.engine.adapters.databases.sqlite import SQLiteConnectionPool

        db_path = tmp_path / "test.db"
        # Create empty db
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        conn.close()

        pool = SQLiteConnectionPool(db_path, readonly=True, pool_size=3)

        status = pool.status()
        assert status["pool_size"] == 3
        assert status["tables_loaded"] == 1  # DataFrame-based pool loads tables
        assert not status["closed"]

        pool.close()

    def test_pool_acquire_and_release(self, tmp_path):
        """Connections should be acquired and released properly."""
        from backend.engine.adapters.databases.sqlite import SQLiteConnectionPool
        from backend.app.repositories.dataframes import sqlite_shim

        db_path = tmp_path / "test.db"
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'hello')")
        conn.commit()
        conn.close()

        pool = SQLiteConnectionPool(db_path, readonly=True, pool_size=2)

        with pool.acquire() as conn:
            conn.row_factory = sqlite_shim.Row
            cursor = conn.execute("SELECT id, value FROM test")
            rows = cursor.fetchall()
            assert len(rows) == 1
            assert rows[0]["value"] == "hello"

        # Pool tracks active connections (DataFrame-based)
        status = pool.status()
        assert status["active_connections"] == 0

        pool.close()

    def test_pool_concurrent_acquire(self, tmp_path):
        """Pool should handle concurrent connections (DataFrame-based)."""
        from backend.engine.adapters.databases.sqlite import SQLiteConnectionPool

        db_path = tmp_path / "test.db"
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        conn.close()

        pool = SQLiteConnectionPool(db_path, readonly=True, pool_size=1, max_overflow=2)

        # Acquire multiple connections - DataFrame-based pool creates new connections as needed
        with pool.acquire():
            with pool.acquire():
                status = pool.status()
                # Both connections active
                assert status["active_connections"] == 2

        pool.close()


class TestSQLiteDataSource:
    """Tests for SQLite data source."""

    def test_test_connection_success(self, tmp_path):
        """test_connection should return success for valid database."""
        from backend.engine.adapters.databases.sqlite import SQLiteDataSource

        db_path = tmp_path / "test.db"
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY)")
        conn.close()

        ds = SQLiteDataSource(db_path, readonly=True)
        result = ds.test_connection()

        assert result.success is True
        assert result.table_count == 2
        assert result.error is None
        assert result.latency_ms > 0

        ds.close()

    def test_test_connection_empty_database(self, tmp_path):
        """test_connection should succeed for empty database with 0 tables."""
        from backend.engine.adapters.databases.sqlite import SQLiteDataSource

        db_path = tmp_path / "empty.db"
        # Create empty database file
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.close()

        ds = SQLiteDataSource(db_path, readonly=True)
        result = ds.test_connection()

        # Empty database connects successfully but has no tables
        assert result.success is True
        assert result.table_count == 0
        assert result.error is None

        ds.close()

    def test_execute_query(self, tmp_path):
        """execute_query should return proper results."""
        from backend.engine.adapters.databases.sqlite import SQLiteDataSource

        db_path = tmp_path / "test.db"
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("INSERT INTO users VALUES (1, 'Alice')")
        conn.execute("INSERT INTO users VALUES (2, 'Bob')")
        conn.commit()
        conn.close()

        ds = SQLiteDataSource(db_path, readonly=True)
        result = ds.execute_query("SELECT id, name FROM users ORDER BY id")

        assert result.row_count == 2
        # DataFrame adds rowid columns, so check specific columns exist
        assert "id" in result.columns
        assert "name" in result.columns
        # Find the indices for id and name columns
        id_idx = result.columns.index("id")
        name_idx = result.columns.index("name")
        assert result.rows[0][id_idx] == 1
        assert result.rows[0][name_idx] == "Alice"
        assert result.rows[1][id_idx] == 2
        assert result.rows[1][name_idx] == "Bob"
        assert result.execution_time_ms > 0

        ds.close()

    def test_with_connection_pool(self, tmp_path):
        """DataSource should work with connection pooling enabled."""
        from backend.engine.adapters.databases.sqlite import SQLiteDataSource

        db_path = tmp_path / "test.db"
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        conn.close()

        ds = SQLiteDataSource(db_path, readonly=True, use_pool=True, pool_size=2)

        status = ds.pool_status()
        assert status is not None
        assert status["pool_size"] == 2

        result = ds.execute_query("SELECT 1 as value")
        assert result.rows[0][0] == 1

        ds.close()


class TestSQLiteSchemaDiscovery:
    """Tests for SQLite schema discovery."""

    def test_discover_tables_batch(self, tmp_path):
        """Schema discovery should batch queries efficiently."""
        from backend.engine.adapters.databases.sqlite import SQLiteDataSource

        db_path = tmp_path / "test.db"
        import sqlite3
        conn = sqlite3.connect(db_path)
        # Create multiple tables
        for i in range(5):
            conn.execute(f"CREATE TABLE table_{i} (id INTEGER PRIMARY KEY, value TEXT)")
            conn.execute(f"INSERT INTO table_{i} VALUES (1, 'test')")
        conn.commit()
        conn.close()

        ds = SQLiteDataSource(db_path, readonly=True)
        schema = ds.discover_schema()

        # Should have discovered all 5 tables
        assert len(schema.tables) == 5
        for table in schema.tables:
            assert table.row_count == 1
            assert "id" in table.columns
            assert "value" in table.columns

        ds.close()


# =============================================================================
# OpenAI Adapter Tests
# =============================================================================


class TestOpenAIClient:
    """Tests for OpenAI LLM client."""

    def test_api_key_validation_missing(self, monkeypatch):
        """Client should raise error when API key is missing."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        from backend.engine.adapters.llm.openai import OpenAIClient

        client = OpenAIClient(api_key=None)

        with pytest.raises(ValueError, match="API key is required"):
            client._get_client()

    def test_api_key_validation_warning(self, monkeypatch, caplog):
        """Client should warn on invalid API key format."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        from backend.engine.adapters.llm.openai import OpenAIClient
        import logging

        with patch("openai.OpenAI"):
            caplog.set_level(logging.WARNING)
            client = OpenAIClient(api_key="invalid-key-format")
            client._get_client()

            # Should have logged a warning
            assert any("may be invalid" in r.message for r in caplog.records)

    def test_force_gpt5_enabled_by_default(self, monkeypatch):
        """GPT-5 forcing should be enabled by default."""
        monkeypatch.delenv("NEURA_FORCE_GPT5", raising=False)

        # Need to reimport to pick up env change
        import importlib
        from backend.engine.adapters.llm import openai
        importlib.reload(openai)

        # Default should now be true
        assert openai._FORCE_GPT5 is True

    def test_force_gpt5_can_be_enabled(self, monkeypatch):
        """GPT-5 forcing can be enabled via env var."""
        monkeypatch.setenv("NEURA_FORCE_GPT5", "true")

        import importlib
        from backend.engine.adapters.llm import openai
        importlib.reload(openai)

        assert openai._FORCE_GPT5 is True

    def test_model_not_overridden_when_disabled(self, monkeypatch):
        """Model should not be overridden when forcing is disabled."""
        monkeypatch.setenv("NEURA_FORCE_GPT5", "false")

        import importlib
        from backend.engine.adapters.llm import openai
        importlib.reload(openai)

        result = openai._force_gpt5("custom-model")
        assert result == "custom-model"

    def test_complete_prepares_messages(self, monkeypatch):
        """complete should prepare messages correctly."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("NEURA_FORCE_GPT5", "false")

        from backend.engine.adapters.llm.openai import OpenAIClient
        from backend.engine.adapters.llm.base import LLMMessage, LLMRole

        mock_response = {
            "output_text": "Test response",
            "model": "gpt-5",
            "usage": {"input_tokens": 10, "output_tokens": 5},
        }

        mock_client = MagicMock()
        mock_client.responses.create.return_value = mock_response

        with patch("openai.OpenAI", return_value=mock_client):
            client = OpenAIClient(api_key="sk-test-key", default_model="gpt-5")
            messages = [
                LLMMessage(role=LLMRole.SYSTEM, content="You are helpful"),
                LLMMessage(role=LLMRole.USER, content="Hello"),
            ]
            result = client.complete(messages, model="gpt-5")

            assert result.content == "Test response"
            assert result.model == "gpt-5"
            assert result.usage["total_tokens"] == 15


# =============================================================================
# Rate Limiter Tests (deprecated)
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
