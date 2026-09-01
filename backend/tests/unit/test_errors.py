"""Unit tests for exception hierarchy and error code mappings."""

import pytest
from backend.app.core.errors import (
    InvalidSourceCodeError,
    LLMTimeoutError,
    LLMUnavailableError,
    ReviewAIError,
    SourceCodeTooLargeError,
    UnsupportedLanguageError,
)
from backend.app.core.security import sanitize_and_validate_source_code


class TestErrorHierarchy:
    """Test custom domain error handling."""

    def test_reviewai_error_to_dict(self):
        err = ReviewAIError(
            message="Database connection dropped",
            error_code="DB_ERROR",
            status_code=500,
            details={"host": "localhost"},
        )
        d = err.to_dict()
        assert d["error"]["code"] == "DB_ERROR"
        assert d["error"]["message"] == "Database connection dropped"
        assert d["error"]["details"]["host"] == "localhost"

    def test_source_code_too_large_error(self):
        err = SourceCodeTooLargeError(line_count=600, max_lines=500)
        assert err.status_code == 413
        assert err.error_code == "SOURCE_TOO_LARGE"
        assert err.details["line_count"] == 600

    def test_unsupported_language_error(self):
        err = UnsupportedLanguageError(language="cobol")
        assert err.status_code == 400
        assert err.error_code == "UNSUPPORTED_LANGUAGE"
        assert err.details["requested_language"] == "cobol"

    def test_llm_unavailable_error(self):
        err = LLMUnavailableError(provider="ollama")
        assert err.status_code == 503
        assert err.error_code == "LLM_UNAVAILABLE"


class TestSecurityValidation:
    """Test security sanitization and limits."""

    def test_clean_code_validation(self):
        code = "def hello():\n    return 'world'\n"
        sanitized, lines, bytes_count = sanitize_and_validate_source_code(code, max_lines=500, max_bytes=1000)
        assert lines == 3
        assert bytes_count > 0

    def test_reject_null_bytes(self):
        with pytest.raises(InvalidSourceCodeError, match="null bytes"):
            sanitize_and_validate_source_code("print('hello\x00world')")

    def test_reject_empty_code(self):
        with pytest.raises(InvalidSourceCodeError, match="empty"):
            sanitize_and_validate_source_code("   \n   \t  ")

    def test_reject_over_limit_lines(self):
        long_code = "\n".join([f"line_{i} = {i}" for i in range(100)])
        with pytest.raises(SourceCodeTooLargeError):
            sanitize_and_validate_source_code(long_code, max_lines=50)
