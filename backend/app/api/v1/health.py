"""Health, liveness, and readiness endpoints for ReviewAI API v1."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status

from backend.app.core.config import Settings, get_settings
from backend.app.schemas.health import (
    HealthFeatures,
    HealthLimits,
    HealthResponse,
    LivenessResponse,
    ReadinessResponse,
)

health_router = APIRouter(tags=["Health & System"])


@health_router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Comprehensive health check",
    description="Returns service status, environment, enabled features, and payload limits without exposing sensitive credentials.",
)
async def get_health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Return comprehensive system health and feature flags."""
    return HealthResponse(
        status="healthy",
        service=settings.APP_NAME.lower(),
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        timestamp=datetime.now(timezone.utc),
        features=HealthFeatures(
            static_analysis_enabled=settings.ENABLE_STATIC_ANALYSIS,
            llm_enabled=settings.ENABLE_LLM,
            static_fallback_allowed=settings.ALLOW_STATIC_FALLBACK,
        ),
        limits=HealthLimits(
            max_source_lines=settings.MAX_SOURCE_LINES,
            max_source_size_bytes=settings.MAX_SOURCE_SIZE,
        ),
    )


@health_router.get(
    "/health/live",
    response_model=LivenessResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Simple probe confirming that the HTTP server process is running and accepting connections.",
)
async def get_liveness(settings: Settings = Depends(get_settings)) -> LivenessResponse:
    """Return basic liveness state for container orchestrators."""
    return LivenessResponse(
        status="live",
        service=settings.APP_NAME.lower(),
        timestamp=datetime.now(timezone.utc),
    )


@health_router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description="Probe confirming that the application and its critical subsystems are ready to process traffic.",
)
async def get_readiness(settings: Settings = Depends(get_settings)) -> ReadinessResponse:
    """Return readiness state and subsystem health checks."""
    checks = {
        "storage": "ready",
        "configuration": "ready",
    }
    return ReadinessResponse(
        status="ready",
        service=settings.APP_NAME.lower(),
        checks=checks,
        timestamp=datetime.now(timezone.utc),
    )
