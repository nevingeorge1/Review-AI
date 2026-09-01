"""Data transfer objects and domain models for the LLM intelligence layer."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

from backend.app.models.domain import ReviewFinding, SuggestedFix
from backend.app.models.enums import Category, DetectionSource, Severity


class LLMSuggestedFix(BaseModel):
    """Suggested code fix proposed by the LLM."""
    original_snippet: str = Field(..., description="Target code to be replaced")
    replacement_snippet: str = Field(..., description="Proposed replacement code")
    explanation: Optional[str] = Field(None, description="Rationale for the fix")
    diff: Optional[str] = Field(None, description="Unified diff if generated")


class LLMRawFinding(BaseModel):
    """Raw finding format expected from the LLM JSON response."""
    category: Category = Field(default=Category.BUG, description="Finding category")
    severity: Severity = Field(default=Severity.MEDIUM, description="Impact severity")
    title: str = Field(..., min_length=3, max_length=200, description="Concise headline")
    description: str = Field(..., min_length=5, description="Detailed explanation")
    line_number: Optional[int] = Field(None, description="1-indexed line number")
    end_line: Optional[int] = Field(None, description="1-indexed end line number")
    code_evidence: Optional[str] = Field(None, description="Code snippet")
    explanation: Optional[str] = Field(None, description="Why this is problematic")
    recommendation: Optional[str] = Field(None, description="Remediation steps")
    suggested_fix: Optional[LLMSuggestedFix] = Field(None, description="Suggested code fix")
    reasoning: Optional[str] = Field(None, description="Chain of thought / rationale")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0, description="Model-reported confidence score")

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, v: Any) -> Category:
        if isinstance(v, str):
            v_lower = v.strip().lower()
            for cat in Category:
                if cat.value == v_lower:
                    return cat
        return Category.BUG

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, v: Any) -> Severity:
        if isinstance(v, str):
            v_lower = v.strip().lower()
            for sev in Severity:
                if sev.value == v_lower:
                    return sev
        return Severity.MEDIUM

    @field_validator("confidence", mode="before")
    @classmethod
    def clamp_confidence(cls, v: Any) -> float:
        try:
            val = float(v)
            return max(0.0, min(1.0, val))
        except (ValueError, TypeError):
            return 0.85


class LLMRawResponsePayload(BaseModel):
    """Root JSON structure expected from LLM output."""
    executive_summary: str = Field(default="No summary provided.", description="High-level assessment")
    findings: List[LLMRawFinding] = Field(default_factory=list, description="List of AI findings")


class LLMReviewResult(BaseModel):
    """Consolidated and validated LLM review output with full telemetry."""
    success: bool = Field(default=True, description="True if LLM inference and validation succeeded")
    executive_summary: str = Field(default="", description="High-level engineering overview")
    findings: List[ReviewFinding] = Field(default_factory=list, description="Validated ReviewFinding instances")
    raw_response: Optional[str] = Field(None, description="Raw model response text")
    provider: str = Field(..., description="Provider name (e.g. 'ollama', 'mock')")
    model_used: str = Field(..., description="Model identifier used")
    prompt_version: str = Field(default="1.0", description="Prompt template version")
    context_version: str = Field(default="1.0", description="Context schema version")
    duration_ms: float = Field(default=0.0, ge=0.0, description="Inference and parsing latency in ms")
    status: str = Field(default="COMPLETED", description="Status: COMPLETED, FAILED, TIMEOUT, FALLBACK")
    error_message: Optional[str] = Field(None, description="Error message if inference or parsing failed")
    model_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Model runtime information")
