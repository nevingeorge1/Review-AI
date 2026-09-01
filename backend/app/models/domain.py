"""Core domain models for ReviewAI.

These models represent entities across the review pipeline and are independent
of any specific framework, database, or external tool.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

from backend.app.models.enums import (
    Category,
    DetectionSource,
    Language,
    ReviewStatus,
    Severity,
)


class Evidence(BaseModel):
    """Normalized evidence provided by a deterministic static analyzer or context."""
    source_tool: str = Field(..., description="Tool that generated this evidence (e.g. 'bandit', 'ruff', 'ast', 'llm')")
    rule_id: Optional[str] = Field(None, description="Original rule or check identifier")
    line_number: Optional[int] = Field(None, ge=1, description="1-indexed line number")
    end_line: Optional[int] = Field(None, ge=1, description="1-indexed end line number")
    snippet: Optional[str] = Field(None, description="Relevant code slice or AST node repr")
    raw_message: Optional[str] = Field(None, description="Raw message from the static analysis tool")


class SuggestedFix(BaseModel):
    """Specific actionable code modification suggested to resolve a finding."""
    original_snippet: str = Field(..., description="The code block targeted for replacement")
    replacement_snippet: str = Field(..., description="The corrected code block")
    explanation: Optional[str] = Field(None, description="Rationale for the suggested replacement")
    diff: Optional[str] = Field(None, description="Unified diff representation if available")


class SourceFile(BaseModel):
    """Representation of a source file submitted for analysis."""
    filename: str = Field(default="submission.py", description="Source filename with extension")
    content: str = Field(..., description="Source code text")
    language: Language = Field(default=Language.PYTHON, description="Programming language")
    line_count: int = Field(default=0, ge=0, description="Total number of lines")
    byte_size: int = Field(default=0, ge=0, description="Byte size of UTF-8 content")


class CodeSubmission(BaseModel):
    """Initial payload submitted by a client or user."""
    code: str = Field(..., min_length=1, description="Source code string to analyze")
    language: Language = Field(default=Language.PYTHON, description="Target programming language")
    filename: Optional[str] = Field(default="submission.py", description="Optional source file name")
    context_notes: Optional[str] = Field(None, max_length=1000, description="Optional developer context notes")


class AnalysisRequest(BaseModel):
    """Internal normalized request for the ReviewEngine."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique analysis job UUID")
    submission: CodeSubmission = Field(..., description="Source submission")
    enable_static_analysis: bool = Field(default=True, description="Run static analysis passes")
    enable_llm: bool = Field(default=True, description="Run LLM reasoning passes")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of submission")


class StaticFinding(BaseModel):
    """Deterministic finding discovered by a static analyzer tool."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Finding UUID")
    analyzer_name: str = Field(..., description="Name of the static analyzer (e.g., 'bandit', 'ruff', 'ast')")
    rule_id: str = Field(..., description="Linter rule or security vulnerability identifier")
    category: Category = Field(..., description="Classified category of the finding")
    severity: Severity = Field(..., description="Initial severity assessment")
    message: str = Field(..., description="Descriptive message from the analyzer")
    line_number: Optional[int] = Field(None, ge=1, description="1-indexed line number")
    end_line: Optional[int] = Field(None, ge=1, description="1-indexed end line number")
    code_evidence: Optional[str] = Field(None, description="Extracted code snippet")


class ReviewFinding(BaseModel):
    """Comprehensive, actionable finding presented in the final code review."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique finding ID")
    category: Category = Field(..., description="Issue category (BUG, SECURITY, STYLE, etc.)")
    severity: Severity = Field(..., description="Impact severity (CRITICAL, HIGH, MEDIUM, LOW, INFO)")
    title: str = Field(..., min_length=3, max_length=150, description="Concise finding headline")
    description: str = Field(..., min_length=5, description="Detailed explanation of the issue")
    line_number: Optional[int] = Field(None, ge=1, description="1-indexed starting line number")
    end_line: Optional[int] = Field(None, ge=1, description="1-indexed ending line number")
    column: Optional[int] = Field(None, ge=1, description="1-indexed starting column number")
    end_column: Optional[int] = Field(None, ge=1, description="1-indexed ending column number")
    code_evidence: Optional[str] = Field(None, description="Source code snippet demonstrating the issue")
    explanation: Optional[str] = Field(None, description="Contextual explanation of why this is problematic")
    recommendation: Optional[str] = Field(None, description="Actionable advice on how to resolve the issue")
    suggested_fix: Optional[SuggestedFix] = Field(None, description="Concrete proposed code replacement")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    confidence_level: str = Field(default="HIGH", description="Categorical confidence rating: HIGH, MEDIUM, LOW")
    detection_source: DetectionSource = Field(..., description="STATIC_ANALYSIS, LLM, or HYBRID")
    detected_by: List[str] = Field(default_factory=list, description="List of analyzers/models identifying this issue")
    rule_id: Optional[str] = Field(None, description="Primary rule or check ID")
    rule_ids: List[str] = Field(default_factory=list, description="All associated rule IDs across tools")
    supporting_evidence: List[Evidence] = Field(default_factory=list, description="Underlying static and AI evidence")
    status: str = Field(default="ACTIVE", description="Status: ACTIVE, SUPPRESSED, DISMISSED")

    @field_validator("end_line")
    @classmethod
    def validate_end_line(cls, v: Optional[int], info) -> Optional[int]:
        start = info.data.get("line_number")
        if v is not None and start is not None and v < start:
            raise ValueError(f"end_line ({v}) cannot be smaller than line_number ({start})")
        return v


class QualityScore(BaseModel):
    """Overall calculated code quality assessment."""
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Normalized score from 0 (poor) to 100 (clean)")
    security_score: float = Field(default=100.0, ge=0.0, le=100.0, description="Security sub-score (0-100)")
    reliability_score: float = Field(default=100.0, ge=0.0, le=100.0, description="Reliability/Bugs sub-score (0-100)")
    performance_score: float = Field(default=100.0, ge=0.0, le=100.0, description="Performance sub-score (0-100)")
    maintainability_score: float = Field(default=100.0, ge=0.0, le=100.0, description="Maintainability sub-score (0-100)")
    style_score: float = Field(default=100.0, ge=0.0, le=100.0, description="Code style sub-score (0-100)")
    category_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Individual scores per category (e.g. security: 95.0, style: 80.0)"
    )
    grade: str = Field(default="A", description="Letter grade: A+, A, B, C, D, F")


class AnalysisMetadata(BaseModel):
    """Execution telemetry and environment metadata for a review job."""
    analysis_id: str = Field(..., description="Unique job ID")
    language: Language = Field(..., description="Analyzed language")
    line_count: int = Field(..., ge=0, description="Total lines processed")
    byte_size: int = Field(..., ge=0, description="Total bytes processed")
    review_mode: str = Field(default="HYBRID", description="Review mode: HYBRID or STATIC_ONLY")
    static_analysis_enabled: bool = Field(default=True)
    llm_enabled: bool = Field(default=True)
    llm_model_used: Optional[str] = Field(None, description="LLM model identifier used (e.g. qwen2.5-coder:7b)")
    static_only_mode: bool = Field(default=False, description="True if review ran without LLM reasoning")
    analyzers_executed: List[str] = Field(default_factory=list, description="Static and AI analyzers executed")
    stage_durations_ms: Dict[str, float] = Field(
        default_factory=dict,
        description="Timing breakdown in milliseconds per pipeline stage"
    )
    total_duration_ms: float = Field(default=0.0, ge=0.0, description="Total end-to-end execution time in ms")


class ReviewSummary(BaseModel):
    """High-level summary of review results and finding distributions."""
    total_findings: int = Field(default=0, ge=0, description="Total count of findings")
    critical_count: int = Field(default=0, ge=0)
    high_count: int = Field(default=0, ge=0)
    medium_count: int = Field(default=0, ge=0)
    low_count: int = Field(default=0, ge=0)
    info_count: int = Field(default=0, ge=0)
    category_breakdown: Dict[str, int] = Field(default_factory=dict)
    review_mode: str = Field(default="HYBRID", description="Review mode: HYBRID or STATIC_ONLY")
    analyzers_used: List[str] = Field(default_factory=list, description="Analyzers contributing findings")
    llm_status: str = Field(default="COMPLETED", description="LLM execution status: COMPLETED, FALLBACK, DISABLED")
    executive_summary: str = Field(default="", description="High-level engineering overview of code quality")


class AnalysisResponse(BaseModel):
    """Complete code review report returned to clients."""
    id: str = Field(..., description="Unique review identifier")
    status: ReviewStatus = Field(default=ReviewStatus.COMPLETED, description="Status of the review")
    findings: List[ReviewFinding] = Field(default_factory=list, description="List of prioritized review findings")
    summary: ReviewSummary = Field(..., description="Summary statistics and executive assessment")
    quality_score: QualityScore = Field(..., description="Calculated quality scores")
    metadata: AnalysisMetadata = Field(..., description="Job execution metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
