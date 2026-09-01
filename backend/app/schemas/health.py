"""Health check and telemetry schemas for ReviewAI."""

from datetime import datetime, timezone
from typing import Any, Dict
from pydantic import BaseModel, Field


class HealthFeatures(BaseModel):
    """Subsystem feature enablement flags."""
    static_analysis_enabled: bool = Field(..., description="Deterministic static code analysis enabled")
    llm_enabled: bool = Field(..., description="LLM contextual reasoning enabled")
    static_fallback_allowed: bool = Field(..., description="Graceful fallback to static-only mode allowed")


class HealthLimits(BaseModel):
    """Configured input limits."""
    max_source_lines: int = Field(..., description="Maximum allowed lines per submission")
    max_source_size_bytes: int = Field(..., description="Maximum allowed source payload size in bytes")


class HealthResponse(BaseModel):
    """Detailed health check response model."""
    status: str = Field(default="healthy", description="Overall health status ('healthy', 'degraded', 'unhealthy')")
    service: str = Field(default="review-ai", description="Service identifier")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Deployment environment (development, staging, production, testing)")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Server UTC timestamp")
    features: HealthFeatures = Field(..., description="Active subsystem features")
    limits: HealthLimits = Field(..., description="Active payload limits")


class LivenessResponse(BaseModel):
    """Liveness probe response model."""
    status: str = Field(default="live", description="Liveness state")
    service: str = Field(default="review-ai", description="Service identifier")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Server UTC timestamp")


class ReadinessResponse(BaseModel):
    """Readiness probe response model."""
    status: str = Field(default="ready", description="Readiness state ('ready', 'not_ready')")
    service: str = Field(default="review-ai", description="Service identifier")
    checks: Dict[str, str] = Field(default_factory=dict, description="Status of individual dependencies")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Server UTC timestamp")
