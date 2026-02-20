"""SQL Injection Validation Tests.

Tests for is_read_only_sql() — ensures only SELECT/WITH queries are allowed,
and blocks DDL, DML, and administrative SQL statements.
"""
import pytest

from backend.app.utils.validation import is_read_only_sql


class TestReadOnlySQL:
    """Tests for SQL injection prevention via is_read_only_sql()."""

    # --- Allowed queries ---

    def test_simple_select(self):
        ok, err = is_read_only_sql("SELECT * FROM users")
        assert ok is True
        assert err is None

    def test_select_with_where(self):
        ok, err = is_read_only_sql("SELECT name, email FROM users WHERE id = 1")
        assert ok is True

    def test_select_with_join(self):
        ok, err = is_read_only_sql(
            "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id"
        )
        assert ok is True

    def test_with_cte(self):
        ok, err = is_read_only_sql(
            "WITH active AS (SELECT * FROM users WHERE active = true) SELECT * FROM active"
        )
        assert ok is True

    def test_lowercase_select(self):
        ok, err = is_read_only_sql("select id from products")
        assert ok is True

    def test_mixed_case_select(self):
        ok, err = is_read_only_sql("SeLeCt * FrOm users")
        assert ok is True

    # --- Blocked queries ---

    def test_blocks_drop_table(self):
        ok, err = is_read_only_sql("DROP TABLE users")
        assert ok is False
        assert "SELECT" in err or "DROP" in err

    def test_blocks_delete(self):
        ok, err = is_read_only_sql("DELETE FROM users WHERE id = 1")
        assert ok is False

    def test_blocks_insert(self):
        ok, err = is_read_only_sql("INSERT INTO users (name) VALUES ('hacker')")
        assert ok is False

    def test_blocks_update(self):
        ok, err = is_read_only_sql("UPDATE users SET admin = true")
        assert ok is False

    def test_blocks_alter_table(self):
        ok, err = is_read_only_sql("ALTER TABLE users ADD COLUMN hack TEXT")
        assert ok is False

    def test_blocks_truncate(self):
        ok, err = is_read_only_sql("TRUNCATE TABLE users")
        assert ok is False

    def test_blocks_create_table(self):
        ok, err = is_read_only_sql("CREATE TABLE evil (id int)")
        assert ok is False

    def test_blocks_grant(self):
        ok, err = is_read_only_sql("GRANT ALL ON users TO public")
        assert ok is False

    def test_blocks_exec(self):
        ok, err = is_read_only_sql("EXEC sp_password 'old', 'new'")
        assert ok is False

    def test_blocks_drop_in_subquery(self):
        """Even if wrapped in SELECT, blocked keywords in the body should be caught."""
        ok, err = is_read_only_sql("SELECT * FROM users; DROP TABLE users")
        assert ok is False
        assert "DROP" in err

    # --- Edge cases ---

    def test_empty_query(self):
        ok, err = is_read_only_sql("")
        assert ok is False
        assert "empty" in err.lower()

    def test_whitespace_only(self):
        ok, err = is_read_only_sql("   ")
        assert ok is False

    def test_comment_only(self):
        ok, err = is_read_only_sql("-- just a comment")
        assert ok is False

    def test_select_with_line_comments_stripped(self):
        """Comments should be stripped before analysis."""
        ok, err = is_read_only_sql("-- this is a comment\nSELECT * FROM users")
        assert ok is True

    def test_select_with_block_comments_stripped(self):
        ok, err = is_read_only_sql("/* block */ SELECT * FROM users")
        assert ok is True

    def test_blocks_delete_hidden_in_comment(self):
        """DELETE after a SELECT should still be caught."""
        ok, err = is_read_only_sql("SELECT 1; DELETE FROM users")
        assert ok is False
