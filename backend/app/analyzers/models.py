"""Domain and DTO models for Static Analysis Engine and Evidence Normalization."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from backend.app.models.domain import Evidence, StaticFinding
from backend.app.models.enums import Category, DetectionSource, Severity


class AnalyzerExecutionInfo(BaseModel):
    """Execution telemetry for an individual static analyzer tool."""
    analyzer_name: str = Field(..., description="Tool name (e.g. 'ruff', 'bandit', 'ast')")
    status: str = Field(default="SUCCESS", description="SUCCESS, FAILED, TIMEOUT, UNAVAILABLE, or DISABLED")
    duration_ms: float = Field(default=0.0, ge=0.0, description="Execution duration in milliseconds")
    findings_count: int = Field(default=0, ge=0, description="Number of raw findings discovered")
    error_message: Optional[str] = Field(None, description="Error message if execution failed or timed out")


class StaticSummaryCounts(BaseModel):
    """Aggregate finding distribution across severities and categories."""
    total: int = Field(default=0, ge=0)
    critical: int = Field(default=0, ge=0)
    high: int = Field(default=0, ge=0)
    medium: int = Field(default=0, ge=0)
    low: int = Field(default=0, ge=0)
    info: int = Field(default=0, ge=0)
    by_category: Dict[str, int] = Field(default_factory=dict)
    by_analyzer: Dict[str, int] = Field(default_factory=dict)


class StaticAnalysisResult(BaseModel):
    """Consolidated, deduplicated static analysis output with evidence provenance."""
    success: bool = Field(default=True, description="True if at least one analyzer succeeded")
    findings: List[StaticFinding] = Field(default_factory=list, description="Deduplicated, normalized findings")
    analyzers_run: List[str] = Field(default_factory=list, description="List of analyzer names that executed successfully")
    analyzers_failed: List[str] = Field(default_factory=list, description="List of analyzer names that failed or timed out")
    analyzer_executions: List[AnalyzerExecutionInfo] = Field(default_factory=list)
    total_duration_ms: float = Field(default=0.0, ge=0.0, description="Total wall-clock static analysis duration in ms")
    summary: StaticSummaryCounts = Field(default_factory=StaticSummaryCounts)
