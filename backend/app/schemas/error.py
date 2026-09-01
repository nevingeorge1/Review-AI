"""Standard error response schemas for ReviewAI."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Structured error detail payload."""
    code: str = Field(..., description="Machine-readable error identifier (e.g. 'REVIEW_NOT_FOUND', 'SOURCE_TOO_LARGE')")
    message: str = Field(..., description="Human-readable safe explanation of the error")
    request_id: Optional[str] = Field(None, description="Unique correlation ID for tracing in server logs")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional context or validation metadata")


class ErrorResponse(BaseModel):
    """Standardized top-level API error envelope."""
    error: ErrorDetail = Field(..., description="Error detail container")
