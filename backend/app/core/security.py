"""Security and input sanitation utilities for ReviewAI.

Fundamental Invariant:
ReviewAI is strictly a static/contextual analysis engine.
NEVER execute or evaluate submitted user code dynamically.
"""

from typing import Tuple
from backend.app.core.errors import InvalidSourceCodeError, SourceCodeTooLargeError


def sanitize_and_validate_source_code(
    code: str,
    max_lines: int = 500,
    max_bytes: int = 65536,
) -> Tuple[str, int, int]:
    """
    Validate and sanitize submitted source code before analysis.

    Returns:
        Tuple of (sanitized_code, line_count, byte_size)

    Raises:
        InvalidSourceCodeError: If code is empty, contains null bytes, or invalid UTF-8.
        SourceCodeTooLargeError: If code exceeds line count or byte size thresholds.
    """
    if code is None or not isinstance(code, str):
        raise InvalidSourceCodeError("Source code must be provided as a valid string")

    # Reject null bytes (potential C-string injection or binary files)
    if "\x00" in code:
        raise InvalidSourceCodeError("Source code contains prohibited null bytes (binary content detected)")

    # Normalize line endings to standard Unix LF
    normalized = code.replace("\r\n", "\n").replace("\r", "\n")

    # Check for empty content
    if not normalized.strip():
        raise InvalidSourceCodeError("Submitted source code cannot be empty")

    # Byte size check
    byte_size = len(normalized.encode("utf-8"))
    if byte_size > max_bytes:
        raise SourceCodeTooLargeError(size_bytes=byte_size, max_bytes=max_bytes)

    # Line count check
    lines = normalized.split("\n")
    line_count = len(lines)
    if line_count > max_lines:
        raise SourceCodeTooLargeError(line_count=line_count, max_lines=max_lines)

    return normalized, line_count, byte_size
