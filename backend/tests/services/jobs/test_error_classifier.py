"""
Tests for the error classifier module.

Tests cover:
1. Transient error detection (should retry)
2. Permanent error detection (should not retry)
3. Edge cases and unknown errors
4. Backoff multiplier recommendations
"""
import pytest

from backend.app.services.jobs.error_classifier import (
    ErrorClassifier,
    ErrorCategory,
    ClassifiedError,
    is_retriable_error,
    classify_error,
)


class TestErrorClassifier:
    """Tests for the ErrorClassifier class."""

    # ========================================
    # Transient Error Tests (Should Retry)
    # ========================================

    @pytest.mark.parametrize("error_message", [
        "Connection refused",
        "connection reset by peer",
        "Connection timed out",
        "Request timeout",
        "Temporary failure in name resolution",
        "Resource temporarily unavailable",
        "Service unavailable",
        "503 Service Unavailable",
        "502 Bad Gateway",
        "504 Gateway Timeout",
        "Too many connections",
        "Database is locked",
        "Deadlock detected",
        "Lock wait timeout exceeded",
        "Could not connect to server",
        "Playwright error: Browser closed",
        "Chromium process terminated",
        "Target page closed unexpectedly",
        "Page crashed",
        "No space left on device",
        "Disk quota exceeded",
        "Rate limit exceeded",
        "429 Too Many Requests",
        "Request was throttled",
    ])
    def test_transient_errors_are_retriable(self, error_message: str):
        """Transient errors should be classified as retriable."""
        result = ErrorClassifier.classify(error_message)
        assert result.is_retriable is True, f"Expected '{error_message}' to be retriable"
        assert result.category in {
            ErrorCategory.TRANSIENT,
            ErrorCategory.TIMEOUT,
            ErrorCategory.RESOURCE,
        }

    # ========================================
    # Permanent Error Tests (Should NOT Retry)
    # ========================================

    @pytest.mark.parametrize("error_message", [
        "Template not found",
        "template_id 'abc123' not found",
        "Contract missing",
        "Connection not found",
        "File not found: report.html",
        "Template does not exist",
        "Authentication failed",
        "Permission denied",
        "Unauthorized access",
        "Forbidden: Access denied",
        "401 Unauthorized",
        "403 Forbidden",
        "Invalid template format",
        "Invalid template_id",
        "Validation failed: missing field",
        "Schema validation invalid",
        "Malformed JSON in contract",
        "Missing required field 'template_id'",
        "Configuration error: invalid settings",
    ])
    def test_permanent_errors_are_not_retriable(self, error_message: str):
        """Permanent errors should NOT be classified as retriable."""
        result = ErrorClassifier.classify(error_message)
        assert result.is_retriable is False, f"Expected '{error_message}' to NOT be retriable"
        assert result.category == ErrorCategory.PERMANENT

    # ========================================
    # Unknown Error Tests (Default Behavior)
    # ========================================

    def test_unknown_error_defaults_to_retriable(self):
        """Unknown errors should default to retriable (optimistic)."""
        result = ErrorClassifier.classify("Some random error that doesn't match any pattern")
        assert result.is_retriable is True
        assert result.category == ErrorCategory.UNKNOWN

    def test_empty_error_is_retriable(self):
        """Empty error strings should be treated as retriable."""
        result = ErrorClassifier.classify("")
        assert result.is_retriable is True

    def test_none_coercion(self):
        """None should be coerced to string and handled gracefully."""
        # This tests robustness against bad input
        result = ErrorClassifier.classify(None)  # type: ignore
        assert result.is_retriable is True

    # ========================================
    # Exception Object Tests
    # ========================================

    def test_exception_object_classification(self):
        """Exception objects should be classified by their message."""
        exc = ConnectionError("Connection refused by server")
        result = ErrorClassifier.classify(exc)
        assert result.is_retriable is True
        assert "Connection refused" in result.original_message

    def test_timeout_exception_classification(self):
        """TimeoutError should be classified as retriable."""
        exc = TimeoutError("Operation timed out")
        result = ErrorClassifier.classify(exc)
        assert result.is_retriable is True
        assert result.category == ErrorCategory.TIMEOUT

    def test_file_not_found_exception(self):
        """FileNotFoundError with 'template' should be permanent."""
        exc = FileNotFoundError("Template file not found")
        result = ErrorClassifier.classify(exc)
        assert result.is_retriable is False
        assert result.category == ErrorCategory.PERMANENT

    # ========================================
    # Backoff Multiplier Tests
    # ========================================

    def test_resource_errors_have_higher_backoff(self):
        """Resource exhaustion errors should suggest longer backoff."""
        # Rate limit error
        result = ErrorClassifier.classify("Rate limit exceeded, please try again later")
        assert result.suggested_backoff_multiplier > 1.0

        # Disk quota error
        result = ErrorClassifier.classify("Disk quota exceeded")
        assert result.suggested_backoff_multiplier > 1.0

    def test_transient_errors_have_normal_backoff(self):
        """Regular transient errors should use normal backoff."""
        result = ErrorClassifier.classify("Connection refused")
        assert result.suggested_backoff_multiplier == 1.0

    def test_permanent_errors_have_normal_backoff(self):
        """Permanent errors should have normal backoff (doesn't matter)."""
        result = ErrorClassifier.classify("Template not found")
        assert result.suggested_backoff_multiplier == 1.0

    # ========================================
    # ClassifiedError Structure Tests
    # ========================================

    def test_classified_error_contains_original_message(self):
        """ClassifiedError should preserve the original error message."""
        original = "Connection refused to database server"
        result = ErrorClassifier.classify(original)
        assert result.original_message == original

    def test_classified_error_has_normalized_message(self):
        """ClassifiedError should have a normalized message with category prefix."""
        result = ErrorClassifier.classify("Connection refused")
        assert "[transient]" in result.normalized_message.lower()

    # ========================================
    # Convenience Function Tests
    # ========================================

    def test_is_retriable_error_function(self):
        """is_retriable_error() should work as a quick check."""
        assert is_retriable_error("Connection timeout") is True
        assert is_retriable_error("Template not found") is False

    def test_classify_error_function(self):
        """classify_error() should return a ClassifiedError."""
        result = classify_error("Connection refused")
        assert isinstance(result, ClassifiedError)
        assert result.is_retriable is True

    # ========================================
    # Case Sensitivity Tests
    # ========================================

    def test_case_insensitive_matching(self):
        """Pattern matching should be case-insensitive."""
        assert is_retriable_error("CONNECTION REFUSED") is True
        assert is_retriable_error("Connection Refused") is True
        assert is_retriable_error("TEMPLATE NOT FOUND") is False
        assert is_retriable_error("Template Not Found") is False


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_error_with_mixed_patterns(self):
        """Error containing both permanent and transient patterns."""
        # Permanent pattern should take precedence
        error = "Connection refused while looking for template not found"
        result = ErrorClassifier.classify(error)
        # Permanent patterns are checked first
        assert result.is_retriable is False

    def test_error_with_numbers(self):
        """Errors with HTTP status codes should be recognized."""
        assert is_retriable_error("HTTP 503 error") is True
        assert is_retriable_error("Server returned 429") is True
        assert is_retriable_error("Error 401: Unauthorized") is False
        assert is_retriable_error("HTTP 403 Forbidden") is False

    def test_very_long_error_message(self):
        """Very long error messages should be handled."""
        long_error = "Connection refused " * 1000
        result = ErrorClassifier.classify(long_error)
        assert result.is_retriable is True

    def test_unicode_in_error_message(self):
        """Unicode characters in error messages should be handled."""
        error = "连接被拒绝 (Connection refused)"
        result = ErrorClassifier.classify(error)
        assert result.is_retriable is True

    def test_newlines_in_error_message(self):
        """Newlines in error messages should be handled."""
        error = "Error:\nConnection refused\nPlease try again"
        result = ErrorClassifier.classify(error)
        assert result.is_retriable is True


class TestRealWorldScenarios:
    """Tests based on real-world error scenarios."""

    def test_playwright_browser_crash(self):
        """Playwright browser crash should be retriable."""
        errors = [
            "Playwright error: browser has been closed",
            "Target page, context or browser has been closed",
            "Page crashed: Chromium render process exited",
            "Browser disconnected",
        ]
        for error in errors:
            assert is_retriable_error(error) is True, f"Failed for: {error}"

    def test_database_errors(self):
        """Common database errors should be classified correctly."""
        # Retriable
        assert is_retriable_error("OperationalError: database is locked") is True
        assert is_retriable_error("Cannot acquire lock on table") is True
        assert is_retriable_error("Too many connections to database") is True

        # Not retriable (schema/permission issues)
        # These would typically be "file not found" or "permission denied"
        assert is_retriable_error("PermissionError: Permission denied") is False

    def test_network_errors(self):
        """Network-related errors should be retriable."""
        errors = [
            "requests.exceptions.ConnectionError: Connection refused",
            "urllib3.exceptions.MaxRetryError",
            "socket.timeout: timed out",
            "ssl.SSLError: Connection reset",
        ]
        for error in errors:
            assert is_retriable_error(error) is True, f"Failed for: {error}"

    def test_template_validation_errors(self):
        """Template validation errors should not be retriable."""
        errors = [
            "Invalid template structure",
            "Contract validation failed: missing required fields",
            "Malformed HTML in template",
        ]
        for error in errors:
            assert is_retriable_error(error) is False, f"Should not retry: {error}"
