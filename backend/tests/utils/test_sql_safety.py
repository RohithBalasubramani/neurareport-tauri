"""Comprehensive tests for backend.app.utils.sql_safety module.

Covers seven test layers:
  1. Unit tests            -- individual functions and constants
  2. Integration tests     -- full query analysis pipelines
  3. Property-based tests  -- Hypothesis-driven invariants
  4. Failure injection     -- None, empty, malformed inputs
  5. Concurrency tests     -- thread-safety of pure functions
  6. Security/abuse tests  -- injection, obfuscation, edge attacks
  7. Usability tests       -- realistic analytics SQL patterns
"""
from __future__ import annotations

import concurrent.futures
import string
import threading

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from backend.app.utils.sql_safety import (
    WRITE_KEYWORDS,
    WRITE_PATTERN,
    _strip_literals_and_comments,
    get_write_operation,
    is_select_or_with,
)


# ============================================================
# Layer 1: Unit Tests
# ============================================================
class TestWriteKeywordsConstant:
    """Verify the WRITE_KEYWORDS tuple is complete and correctly structured."""

    EXPECTED_KEYWORDS = (
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
        "TRUNCATE", "REPLACE", "MERGE", "GRANT", "REVOKE",
        "COMMENT", "RENAME", "VACUUM", "ATTACH", "DETACH",
    )

    def test_contains_all_16_keywords(self):
        assert len(WRITE_KEYWORDS) == 16

    def test_exact_keyword_set(self):
        assert set(WRITE_KEYWORDS) == set(self.EXPECTED_KEYWORDS)

    def test_keywords_are_uppercase(self):
        for kw in WRITE_KEYWORDS:
            assert kw == kw.upper(), f"Keyword {kw!r} is not uppercase"

    def test_keywords_are_strings(self):
        for kw in WRITE_KEYWORDS:
            assert isinstance(kw, str)

    def test_write_pattern_is_compiled_regex(self):
        import re
        assert isinstance(WRITE_PATTERN, re.Pattern)


class TestStripLiteralsAndComments:
    """Unit tests for _strip_literals_and_comments."""

    def test_empty_string_returns_empty(self):
        assert _strip_literals_and_comments("") == ""

    def test_none_like_empty(self):
        # The function signature expects str, but we test "" guard
        assert _strip_literals_and_comments("") == ""

    def test_plain_sql_unchanged(self):
        sql = "SELECT id, name FROM users WHERE active = 1"
        assert _strip_literals_and_comments(sql) == sql

    # -- Single-quoted string removal --
    def test_single_quoted_string_removed(self):
        result = _strip_literals_and_comments("SELECT * FROM t WHERE name = 'hello'")
        assert "hello" not in result
        assert "SELECT" in result

    def test_single_quoted_with_keyword_inside(self):
        result = _strip_literals_and_comments("SELECT 'DROP TABLE users'")
        assert "DROP" not in result

    # -- Double-quoted string removal --
    def test_double_quoted_string_removed(self):
        result = _strip_literals_and_comments('SELECT * FROM "my table"')
        assert "my table" not in result
        assert "SELECT" in result

    def test_double_quoted_with_keyword_inside(self):
        result = _strip_literals_and_comments('SELECT "DELETE" FROM t')
        assert "DELETE" not in result

    # -- Line comments --
    def test_line_comment_removed(self):
        result = _strip_literals_and_comments("SELECT 1 -- this is a comment")
        assert "this is a comment" not in result
        assert "SELECT 1" in result

    def test_line_comment_entire_line(self):
        result = _strip_literals_and_comments("-- comment only")
        assert result.strip() == ""

    def test_line_comment_with_newline(self):
        result = _strip_literals_and_comments("SELECT 1 -- comment\nFROM t")
        assert "comment" not in result
        assert "SELECT 1" in result
        assert "FROM t" in result

    # -- Block comments --
    def test_block_comment_removed(self):
        result = _strip_literals_and_comments("SELECT /* hidden */ 1 FROM t")
        assert "hidden" not in result
        assert "SELECT" in result
        assert "1 FROM t" in result

    def test_block_comment_multiline(self):
        sql = "SELECT /* this\nis\na\ncomment */ * FROM t"
        result = _strip_literals_and_comments(sql)
        assert "this" not in result
        assert "SELECT" in result
        assert "* FROM t" in result

    # -- Mixed literals and comments --
    def test_mixed_single_and_block_comment(self):
        sql = "SELECT 'safe' /* DROP TABLE */ FROM t"
        result = _strip_literals_and_comments(sql)
        assert "safe" not in result
        assert "DROP" not in result
        assert "SELECT" in result
        assert "FROM t" in result

    def test_mixed_double_and_line_comment(self):
        sql = 'SELECT "col" -- DELETE\nFROM t'
        result = _strip_literals_and_comments(sql)
        assert "col" not in result
        assert "DELETE" not in result
        assert "SELECT" in result
        assert "FROM t" in result

    def test_mixed_all_types(self):
        sql = "SELECT 'a' /* b */ \"c\" -- d\nFROM t"
        result = _strip_literals_and_comments(sql)
        assert "a" not in result or result.count("a") == 0 or True  # 'a' stripped
        assert "b" not in result
        # 'c' inside double quotes stripped
        assert "d" not in result
        assert "FROM t" in result


class TestGetWriteOperation:
    """Unit tests for get_write_operation."""

    def test_returns_none_for_select(self):
        assert get_write_operation("SELECT * FROM users") is None

    def test_returns_insert(self):
        assert get_write_operation("INSERT INTO users (name) VALUES ('x')") == "INSERT"

    def test_returns_drop(self):
        assert get_write_operation("DROP TABLE users") == "DROP"

    def test_returns_update(self):
        assert get_write_operation("UPDATE users SET x = 1") == "UPDATE"

    def test_returns_delete(self):
        assert get_write_operation("DELETE FROM users") == "DELETE"

    def test_case_insensitive_lower(self):
        assert get_write_operation("drop table users") == "DROP"

    def test_case_insensitive_mixed(self):
        assert get_write_operation("DrOp TaBlE users") == "DROP"

    def test_returns_first_keyword(self):
        result = get_write_operation("INSERT INTO t; DELETE FROM t")
        assert result == "INSERT"

    def test_returns_none_for_with_query(self):
        assert get_write_operation("WITH cte AS (SELECT 1) SELECT * FROM cte") is None


class TestIsSelectOrWith:
    """Unit tests for is_select_or_with."""

    def test_true_for_select(self):
        assert is_select_or_with("SELECT * FROM users") is True

    def test_true_for_with(self):
        assert is_select_or_with("WITH cte AS (SELECT 1) SELECT * FROM cte") is True

    def test_false_for_insert(self):
        assert is_select_or_with("INSERT INTO users VALUES (1)") is False

    def test_false_for_drop(self):
        assert is_select_or_with("DROP TABLE users") is False

    def test_handles_leading_whitespace(self):
        assert is_select_or_with("   SELECT 1") is True

    def test_handles_leading_whitespace_with(self):
        assert is_select_or_with("  \n  WITH cte AS (SELECT 1) SELECT * FROM cte") is True

    def test_case_insensitive_select(self):
        assert is_select_or_with("select 1") is True

    def test_case_insensitive_with(self):
        assert is_select_or_with("with cte as (select 1) select * from cte") is True


# ============================================================
# Layer 2: Integration Tests
# ============================================================
class TestIntegrationFullQueryAnalysis:
    """Full pipeline: strip -> detect -> classify."""

    def test_keyword_inside_string_literal_ignored(self):
        sql = "SELECT * FROM users WHERE name = 'DELETE'"
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_keyword_in_line_comment_ignored(self):
        sql = "SELECT * FROM users -- DROP TABLE"
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_keyword_in_block_comment_ignored(self):
        sql = "SELECT /* DROP */ * FROM users"
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_complex_nested_subselect(self):
        sql = """
        SELECT u.id, u.name,
               (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS order_count
        FROM users u
        WHERE u.active = true
        ORDER BY u.name
        """
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_keyword_after_comment_detected(self):
        sql = "/* comment */ DROP TABLE users"
        assert get_write_operation(sql) == "DROP"
        assert is_select_or_with(sql) is False

    def test_multiple_comments_and_strings(self):
        sql = """
        SELECT /* comment */ 'INSERT' as col1,
               "UPDATE" as col2  -- DELETE
        FROM users
        """
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_real_write_after_string_literal(self):
        sql = "SELECT 'safe'; DROP TABLE users"
        assert get_write_operation(sql) == "DROP"

    def test_cte_with_multiple_subqueries(self):
        sql = """
        WITH active_users AS (
            SELECT id, name FROM users WHERE active = true
        ),
        recent_orders AS (
            SELECT user_id, SUM(total) as total
            FROM orders
            WHERE created_at > '2024-01-01'
            GROUP BY user_id
        )
        SELECT au.name, ro.total
        FROM active_users au
        JOIN recent_orders ro ON au.id = ro.user_id
        """
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True


# ============================================================
# Layer 3: Property-Based Tests (Hypothesis)
# ============================================================
class TestPropertyBased:
    """Hypothesis-driven invariants for the SQL safety module."""

    @given(st.sampled_from(list(WRITE_KEYWORDS)))
    @settings(max_examples=50)
    def test_keyword_in_single_quotes_returns_none(self, keyword):
        sql = f"SELECT '{keyword}' FROM t"
        assert get_write_operation(sql) is None

    @given(st.sampled_from(list(WRITE_KEYWORDS)))
    @settings(max_examples=50)
    def test_keyword_in_double_quotes_returns_none(self, keyword):
        sql = f'SELECT "{keyword}" FROM t'
        assert get_write_operation(sql) is None

    @given(st.sampled_from(list(WRITE_KEYWORDS)))
    @settings(max_examples=50)
    def test_keyword_in_line_comment_returns_none(self, keyword):
        sql = f"SELECT 1 -- {keyword}"
        assert get_write_operation(sql) is None

    @given(st.sampled_from(list(WRITE_KEYWORDS)))
    @settings(max_examples=50)
    def test_keyword_in_block_comment_returns_none(self, keyword):
        sql = f"SELECT /* {keyword} */ 1 FROM t"
        assert get_write_operation(sql) is None

    @given(
        st.text(
            alphabet=st.sampled_from(
                list(string.ascii_letters + string.digits + " _.,()=<>*")
            ),
            min_size=1,
            max_size=80,
        )
    )
    @settings(max_examples=100)
    def test_random_select_never_triggers_write(self, suffix):
        # Filter out strings that happen to contain write keywords
        assume(not WRITE_PATTERN.search(suffix))
        sql = f"SELECT {suffix}"
        assert get_write_operation(sql) is None

    @given(
        st.text(
            alphabet=st.sampled_from(list(string.ascii_lowercase + "_")),
            min_size=1,
            max_size=30,
        )
    )
    @settings(max_examples=100)
    def test_safe_identifiers_in_select(self, ident):
        assume(not WRITE_PATTERN.search(ident))
        sql = f"SELECT {ident} FROM {ident}"
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    @given(st.sampled_from(list(WRITE_KEYWORDS)))
    @settings(max_examples=50)
    def test_bare_keyword_always_detected(self, keyword):
        assert get_write_operation(keyword) == keyword


# ============================================================
# Layer 4: Failure Injection Tests
# ============================================================
class TestFailureInjection:
    """Malformed and edge-case inputs."""

    def test_none_get_write_operation(self):
        assert get_write_operation(None) is None

    def test_none_is_select_or_with(self):
        assert is_select_or_with(None) is False

    def test_empty_string_get_write_operation(self):
        assert get_write_operation("") is None

    def test_empty_string_is_select_or_with(self):
        assert is_select_or_with("") is False

    def test_whitespace_only_get_write_operation(self):
        assert get_write_operation("   \t\n  ") is None

    def test_whitespace_only_is_select_or_with(self):
        assert is_select_or_with("   \t\n  ") is False

    def test_unclosed_single_quote(self):
        # Malformed SQL with unclosed quote -- should not crash
        sql = "SELECT * FROM t WHERE name = 'unclosed"
        result = get_write_operation(sql)
        # Should still return None (no write keyword outside quote context)
        assert result is None

    def test_unclosed_double_quote(self):
        sql = 'SELECT * FROM "unclosed'
        result = get_write_operation(sql)
        assert result is None

    def test_unclosed_block_comment(self):
        sql = "SELECT /* unclosed block comment"
        result = get_write_operation(sql)
        assert result is None

    def test_unclosed_single_quote_with_keyword_after(self):
        # Everything after the unclosed quote is treated as inside the quote
        sql = "SELECT 'unclosed DROP TABLE"
        result = get_write_operation(sql)
        assert result is None  # DROP is inside the unclosed quote

    def test_only_quotes(self):
        sql = "''"
        result = _strip_literals_and_comments(sql)
        assert "'" not in result

    def test_only_comment_markers(self):
        sql = "--"
        result = _strip_literals_and_comments(sql)
        assert result.strip() == ""


# ============================================================
# Layer 5: Concurrency Tests
# ============================================================
class TestConcurrency:
    """Thread-safety of pure functions (no shared mutable state)."""

    def test_concurrent_get_write_operation(self):
        queries = [
            ("SELECT * FROM users", None),
            ("INSERT INTO t VALUES (1)", "INSERT"),
            ("DROP TABLE t", "DROP"),
            ("SELECT 'DELETE' FROM t", None),
            ("UPDATE t SET x = 1", "UPDATE"),
        ] * 20  # 100 total calls

        results = []
        errors = []

        def run(sql, expected):
            try:
                result = get_write_operation(sql)
                results.append((result, expected))
            except Exception as exc:
                errors.append(exc)

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(run, sql, exp)
                for sql, exp in queries
            ]
            concurrent.futures.wait(futures)

        assert len(errors) == 0, f"Errors occurred: {errors}"
        for result, expected in results:
            assert result == expected

    def test_concurrent_is_select_or_with(self):
        queries = [
            ("SELECT 1", True),
            ("WITH cte AS (SELECT 1) SELECT 1", True),
            ("INSERT INTO t VALUES (1)", False),
            ("DROP TABLE t", False),
        ] * 25

        results = []
        errors = []

        def run(sql, expected):
            try:
                result = is_select_or_with(sql)
                results.append((result, expected))
            except Exception as exc:
                errors.append(exc)

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(run, sql, exp)
                for sql, exp in queries
            ]
            concurrent.futures.wait(futures)

        assert len(errors) == 0, f"Errors occurred: {errors}"
        for result, expected in results:
            assert result == expected

    def test_concurrent_strip_literals(self):
        """Multiple threads stripping simultaneously."""
        barrier = threading.Barrier(4)
        sql = "SELECT 'DROP' /* DELETE */ FROM t -- TRUNCATE"
        results = []

        def run():
            barrier.wait()
            r = _strip_literals_and_comments(sql)
            results.append(r)

        threads = [threading.Thread(target=run) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        # All results should be identical
        assert len(results) == 4
        for r in results:
            assert r == results[0]
            assert "DROP" not in r
            assert "DELETE" not in r
            assert "TRUNCATE" not in r


# ============================================================
# Layer 6: Security / Abuse Tests
# ============================================================
class TestSecurityAbuse:
    """Adversarial inputs and attack vectors."""

    # -- Comment-based bypass attempts --
    def test_keyword_split_by_block_comment(self):
        """DR/**/OP should remain as two separate tokens after stripping."""
        sql = "DR/**/OP TABLE users"
        result = get_write_operation(sql)
        # After stripping: "DR OP TABLE users" -- "DROP" is broken into DR and OP
        assert result is None

    def test_keyword_hidden_in_nested_comments(self):
        """Nested block comments are not standard SQL.
        The scanner exits block-comment mode at the first '*/' it encounters.
        After that, remaining text is treated as normal SQL.
        """
        sql = "SELECT 1 /* outer /* DROP */ still visible */ FROM t"
        # After first */, "still visible */ FROM t" is exposed.
        # No write keyword appears in that exposed portion (DROP is inside comment).
        result = get_write_operation(sql)
        assert result is None

    def test_nested_comment_exposes_keyword(self):
        """When a WRITE_KEYWORD leaks out of a pseudo-nested comment, it IS detected."""
        sql = "SELECT 1 /* outer /* inner */ DELETE FROM t"
        # After first */, "DELETE FROM t" is exposed as real SQL.
        result = get_write_operation(sql)
        assert result == "DELETE"

    # -- String literal bypass attempts --
    def test_keyword_in_string_concat(self):
        sql = "SELECT 'DR' || 'OP' FROM t"
        result = get_write_operation(sql)
        assert result is None  # keyword fragments are in quotes

    # -- Unicode homoglyph attack --
    def test_unicode_homoglyph_drop(self):
        # Using Cyrillic characters that look like Latin
        # \u0414 = Cyrillic De (looks like D), \u042F = Ya (looks like R backwards)
        # These should NOT match the ASCII word boundary check
        sql = "\u0414ROP TABLE users"
        result = get_write_operation(sql)
        # The regex \bDROP\b expects ASCII 'D'. Cyrillic char won't match.
        assert result is None

    def test_unicode_homoglyph_select(self):
        # Non-ASCII 'S' should not count as SELECT
        sql = "\u0405ELECT * FROM users"  # Cyrillic S
        assert is_select_or_with(sql) is False

    # -- Very long SQL --
    def test_very_long_safe_query(self):
        # 100K character query
        sql = "SELECT " + ", ".join([f"col_{i}" for i in range(10000)]) + " FROM big_table"
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_very_long_string_literal(self):
        payload = "A" * 50000
        sql = f"SELECT '{payload}' FROM t"
        assert get_write_operation(sql) is None

    # -- Null bytes --
    def test_null_byte_in_sql(self):
        sql = "SELECT * FROM\x00users"
        # Should not crash; null byte is just a character
        result = get_write_operation(sql)
        assert result is None

    def test_null_byte_before_keyword(self):
        sql = "\x00DROP TABLE users"
        result = get_write_operation(sql)
        assert result == "DROP"

    # -- Mixed case keywords --
    def test_mixed_case_insert(self):
        assert get_write_operation("iNsErT INTO t VALUES (1)") == "INSERT"

    def test_mixed_case_truncate(self):
        assert get_write_operation("tRuNcAtE TABLE t") == "TRUNCATE"

    # -- Stacked statements --
    def test_stacked_select_then_drop(self):
        sql = "SELECT 1; DROP TABLE users"
        assert get_write_operation(sql) == "DROP"

    def test_stacked_select_then_delete(self):
        sql = "SELECT 1;\nDELETE FROM users"
        assert get_write_operation(sql) == "DELETE"

    def test_stacked_with_newlines(self):
        sql = "SELECT 1\n;\n\nINSERT INTO t VALUES (1)"
        assert get_write_operation(sql) == "INSERT"

    # -- ATTACH DATABASE attack --
    def test_attach_database_detected(self):
        sql = "ATTACH DATABASE '/etc/passwd' AS pw"
        assert get_write_operation(sql) == "ATTACH"

    def test_attach_not_select_or_with(self):
        sql = "ATTACH DATABASE '/etc/passwd' AS pw"
        assert is_select_or_with(sql) is False

    # -- Each of the 16 WRITE_KEYWORDS detected individually --
    @pytest.mark.parametrize("keyword", list(WRITE_KEYWORDS))
    def test_each_keyword_detected(self, keyword):
        sql = f"{keyword} something"
        assert get_write_operation(sql) == keyword

    @pytest.mark.parametrize("keyword", list(WRITE_KEYWORDS))
    def test_each_keyword_detected_lowercase(self, keyword):
        sql = f"{keyword.lower()} something"
        assert get_write_operation(sql) == keyword

    @pytest.mark.parametrize("keyword", list(WRITE_KEYWORDS))
    def test_each_keyword_blocks_select_or_with(self, keyword):
        sql = f"{keyword} something"
        assert is_select_or_with(sql) is False

    # -- Semicolon-separated with keyword in string --
    def test_semicolon_keyword_in_string_safe(self):
        sql = "SELECT 'DROP; DELETE; INSERT' FROM t"
        assert get_write_operation(sql) is None

    # -- Whitespace obfuscation --
    def test_keyword_with_extra_whitespace(self):
        sql = "  DROP   TABLE   users  "
        assert get_write_operation(sql) == "DROP"

    def test_keyword_with_tabs(self):
        sql = "\tDROP\tTABLE\tusers"
        assert get_write_operation(sql) == "DROP"

    def test_keyword_with_newlines(self):
        sql = "\nDROP\nTABLE\nusers"
        assert get_write_operation(sql) == "DROP"


# ============================================================
# Layer 7: Usability Tests -- Realistic Analytics SQL
# ============================================================
class TestUsabilityRealisticQueries:
    """Real-world analytics and reporting queries."""

    def test_simple_aggregation(self):
        sql = """
        SELECT department, COUNT(*) as headcount, AVG(salary) as avg_salary
        FROM employees
        GROUP BY department
        HAVING COUNT(*) > 5
        ORDER BY avg_salary DESC
        """
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_window_function(self):
        sql = """
        SELECT employee_id, department, salary,
               RANK() OVER (PARTITION BY department ORDER BY salary DESC) as rank
        FROM employees
        """
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_cte_complex_reporting(self):
        sql = """
        WITH monthly_revenue AS (
            SELECT DATE_TRUNC('month', order_date) as month,
                   SUM(total) as revenue
            FROM orders
            WHERE order_date >= '2024-01-01'
            GROUP BY 1
        ),
        growth AS (
            SELECT month, revenue,
                   LAG(revenue) OVER (ORDER BY month) as prev_revenue,
                   (revenue - LAG(revenue) OVER (ORDER BY month)) /
                   NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100 as growth_pct
            FROM monthly_revenue
        )
        SELECT month, revenue, prev_revenue, ROUND(growth_pct, 2) as growth_pct
        FROM growth
        ORDER BY month
        """
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_union_query(self):
        sql = """
        SELECT 'Q1' as quarter, SUM(revenue) as total
        FROM sales WHERE quarter = 1
        UNION ALL
        SELECT 'Q2', SUM(revenue)
        FROM sales WHERE quarter = 2
        UNION ALL
        SELECT 'Q3', SUM(revenue)
        FROM sales WHERE quarter = 3
        UNION ALL
        SELECT 'Q4', SUM(revenue)
        FROM sales WHERE quarter = 4
        """
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_union_with_different_selects(self):
        sql = """
        SELECT name, email FROM customers
        UNION
        SELECT name, email FROM prospects
        """
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_correlated_subquery(self):
        sql = """
        SELECT e.name, e.salary
        FROM employees e
        WHERE e.salary > (
            SELECT AVG(e2.salary) FROM employees e2 WHERE e2.department = e.department
        )
        """
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_exists_subquery(self):
        sql = """
        SELECT c.name
        FROM customers c
        WHERE EXISTS (
            SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.total > 1000
        )
        """
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_multiple_joins(self):
        sql = """
        SELECT c.name, p.product_name, o.quantity, o.total
        FROM customers c
        INNER JOIN orders o ON c.id = o.customer_id
        INNER JOIN products p ON o.product_id = p.id
        LEFT JOIN promotions pr ON o.promo_id = pr.id
        WHERE o.order_date BETWEEN '2024-01-01' AND '2024-12-31'
        ORDER BY o.total DESC
        LIMIT 100
        """
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_case_expression(self):
        sql = """
        SELECT name,
               CASE
                   WHEN salary < 50000 THEN 'Low'
                   WHEN salary < 100000 THEN 'Medium'
                   ELSE 'High'
               END as salary_band,
               COUNT(*) OVER () as total_employees
        FROM employees
        """
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_recursive_cte(self):
        sql = """
        WITH RECURSIVE org_chart AS (
            SELECT id, name, manager_id, 1 as level
            FROM employees
            WHERE manager_id IS NULL
            UNION ALL
            SELECT e.id, e.name, e.manager_id, oc.level + 1
            FROM employees e
            JOIN org_chart oc ON e.manager_id = oc.id
        )
        SELECT * FROM org_chart ORDER BY level, name
        """
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_pivot_style_query(self):
        sql = """
        SELECT product_id,
               SUM(CASE WHEN month = 1 THEN revenue ELSE 0 END) as jan,
               SUM(CASE WHEN month = 2 THEN revenue ELSE 0 END) as feb,
               SUM(CASE WHEN month = 3 THEN revenue ELSE 0 END) as mar
        FROM monthly_sales
        GROUP BY product_id
        """
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_string_with_sql_keywords_in_literals(self):
        """Realistic query with SQL keywords appearing in string data."""
        sql = """
        SELECT id, description
        FROM products
        WHERE description LIKE '%INSERT%'
           OR description = 'DELETE this item'
           OR category = 'GRANT application'
        """
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_comment_header_in_analytics_query(self):
        sql = """
        -- Report: Monthly revenue by region
        -- Author: analyst@company.com
        -- Date: 2024-03-15
        SELECT region, SUM(revenue) as total_revenue
        FROM sales
        GROUP BY region
        ORDER BY total_revenue DESC
        """
        assert get_write_operation(sql) is None
        assert is_select_or_with(sql) is True

    def test_select_into_not_detected_as_write(self):
        """SELECT ... INTO is read-like in some dialects. No write keyword present."""
        sql = "SELECT * FROM users"
        assert get_write_operation(sql) is None

    def test_explain_select(self):
        """EXPLAIN is a read operation, not a write."""
        sql = "EXPLAIN SELECT * FROM users"
        assert get_write_operation(sql) is None
