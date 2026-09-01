"""Domain and application exception hierarchy for ReviewAI."""

from typing import Any, Dict, Optional


class ReviewAIError(Exception):
    """Base exception for all ReviewAI domain and system errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to safe API response payload."""
        payload: Dict[str, Any] = {
            "error": {
                "code": self.error_code,
                "message": self.message,
            }
        }
        if self.details:
            payload["error"]["details"] = self.details
        return payload


# --- Input & Preprocessing Errors ---

class InvalidSourceCodeError(ReviewAIError):
    """Raised when source code is empty, invalid UTF-8, or malformed."""

    def __init__(self, message: str = "Source code contains invalid characters or format", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="INVALID_SOURCE_CODE", status_code=400, details=details)


class UnsupportedLanguageError(ReviewAIError):
    """Raised when the requested programming language is not supported."""

    def __init__(self, language: str, supported: Optional[list] = None):
        details = {"requested_language": language, "supported_languages": supported or ["python"]}
        super().__init__(
            f"Language '{language}' is not currently supported",
            error_code="UNSUPPORTED_LANGUAGE",
            status_code=400,
            details=details,
        )


class SourceCodeTooLargeError(ReviewAIError):
    """Raised when source code exceeds line limit or byte limit."""

    def __init__(self, line_count: Optional[int] = None, max_lines: Optional[int] = None, size_bytes: Optional[int] = None, max_bytes: Optional[int] = None):
        details: Dict[str, Any] = {}
        if line_count is not None and max_lines is not None:
            details.update({"line_count": line_count, "max_lines": max_lines})
            msg = f"Source code exceeds maximum allowed lines ({line_count} > {max_lines})"
        elif size_bytes is not None and max_bytes is not None:
            details.update({"size_bytes": size_bytes, "max_bytes": max_bytes})
            msg = f"Source code exceeds maximum allowed payload size ({size_bytes} bytes > {max_bytes} bytes)"
        else:
            msg = "Source code payload is too large"
        super().__init__(msg, error_code="SOURCE_TOO_LARGE", status_code=413, details=details)


class ParserSyntaxError(ReviewAIError):
    """Raised when the source code fails static AST parsing."""

    def __init__(self, message: str, line: Optional[int] = None, column: Optional[int] = None):
        details: Dict[str, Any] = {}
        if line is not None:
            details["line"] = line
        if column is not None:
            details["column"] = column
        super().__init__(f"Syntax error during parsing: {message}", error_code="SYNTAX_ERROR", status_code=422, details=details)


# --- Static Analysis Errors ---

class StaticAnalyzerError(ReviewAIError):
    """Raised when a static analyzer fails execution."""

    def __init__(self, analyzer_name: str, message: str):
        super().__init__(
            f"Static analyzer '{analyzer_name}' failed: {message}",
            error_code="ANALYZER_FAILURE",
            status_code=500,
            details={"analyzer": analyzer_name},
        )


class StaticAnalyzerUnavailableError(ReviewAIError):
    """Raised when a configured static analyzer tool is missing or uninstalled."""

    def __init__(self, analyzer_name: str):
        super().__init__(
            f"Static analyzer '{analyzer_name}' is not installed or available on this system",
            error_code="ANALYZER_UNAVAILABLE",
            status_code=503,
            details={"analyzer": analyzer_name},
        )


# --- LLM Provider Errors ---

class LLMProviderError(ReviewAIError):
    """Base exception for LLM provider errors."""

    def __init__(self, provider: str, message: str, error_code: str = "LLM_ERROR", status_code: int = 502):
        super().__init__(
            f"LLM Provider '{provider}' error: {message}",
            error_code=error_code,
            status_code=status_code,
            details={"provider": provider},
        )


class LLMUnavailableError(LLMProviderError):
    """Raised when the local LLM instance (e.g. Ollama) is unreachable."""

    def __init__(self, provider: str = "ollama", url: str = "http://localhost:11434"):
        super().__init__(
            provider=provider,
            message=f"LLM service is unreachable at {url}. Ensure Ollama is running.",
            error_code="LLM_UNAVAILABLE",
            status_code=503,
        )


class LLMTimeoutError(LLMProviderError):
    """Raised when LLM inference exceeds configured timeout limit."""

    def __init__(self, provider: str, timeout_seconds: int):
        super().__init__(
            provider=provider,
            message=f"LLM reasoning timed out after {timeout_seconds} seconds",
            error_code="LLM_TIMEOUT",
            status_code=504,
        )


class InvalidStructuredOutputError(LLMProviderError):
    """Raised when LLM output cannot be parsed into validated domain models."""

    def __init__(self, provider: str, message: str = "LLM generated invalid or unparseable structured response"):
        super().__init__(
            provider=provider,
            message=message,
            error_code="INVALID_STRUCTURED_OUTPUT",
            status_code=502,
        )


# --- Storage / Entity Errors ---

class ReviewNotFoundError(ReviewAIError):
    """Raised when a requested review ID does not exist."""

    def __init__(self, review_id: str):
        super().__init__(
            f"Code review with ID '{review_id}' was not found",
            error_code="REVIEW_NOT_FOUND",
            status_code=404,
            details={"review_id": review_id},
        )
