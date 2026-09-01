"""Review request and response DTO schemas for ReviewAI."""

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import AliasChoices, BaseModel, Field

from backend.app.models.domain import (
    AnalysisMetadata,
    QualityScore,
    ReviewFinding,
    ReviewSummary,
)
from backend.app.models.enums import Language, ReviewStatus


class ReviewCreateRequest(BaseModel):
    """Payload submitted to initiate a new code review."""
    code: str = Field(
        ...,
        min_length=1,
        description="Source code string to analyze",
        validation_alias=AliasChoices("code", "source_code"),
    )
    language: Language = Field(
        default=Language.PYTHON,
        description="Target programming language (currently Python supported)",
    )
    filename: Optional[str] = Field(
        default="submission.py",
        max_length=255,
        description="Optional source file name for context and reporting",
    )
    context_notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional developer context or instructions for the reviewer",
    )
    enable_static_analysis: bool = Field(
        default=True,
        description="Whether to run deterministic static analyzers",
    )
    enable_llm: bool = Field(
        default=True,
        description="Whether to run contextual LLM reasoning passes",
    )

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "code": "def divide(a, b):\n    return a / b\n",
                "language": "python",
                "filename": "math_utils.py",
                "context_notes": "Utility function for arithmetic.",
            }
        },
    }


class ReviewResponse(BaseModel):
    """Complete code review record and state representation."""
    review_id: str = Field(..., description="Unique public review UUID")
    analysis_id: str = Field(..., description="Unique processing run UUID")
    status: ReviewStatus = Field(default=ReviewStatus.PENDING, description="Review lifecycle status")
    language: Language = Field(..., description="Source code language")
    filename: str = Field(default="submission.py", description="Source code filename")
    line_count: int = Field(default=0, ge=0, description="Total line count of analyzed code")
    byte_size: int = Field(default=0, ge=0, description="Total byte size of analyzed code")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Submission timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")

    # The following fields are populated once analysis completes in future modules:
    summary: Optional[ReviewSummary] = Field(None, description="Executive summary and finding metrics")
    findings: List[ReviewFinding] = Field(default_factory=list, description="Prioritized list of review findings")
    quality_score: Optional[QualityScore] = Field(None, description="Calculated code quality score (0-100)")
    metadata: Optional[AnalysisMetadata] = Field(None, description="Detailed stage timings and execution metadata")
    message: Optional[str] = Field(
        default="Review request accepted and queued for analysis.",
        description="Human-readable status or guidance message",
    )


class ReviewListResponse(BaseModel):
    """Paginated collection of review records."""
    items: List[ReviewResponse] = Field(default_factory=list, description="List of review records")
    total: int = Field(..., ge=0, description="Total number of reviews available")
    page: int = Field(..., ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")


class ReviewFindingListResponse(BaseModel):
    """List of individual findings for a specific review."""
    review_id: str = Field(..., description="Parent review UUID")
    total: int = Field(..., ge=0, description="Total findings count")
    findings: List[ReviewFinding] = Field(default_factory=list, description="List of review findings")
