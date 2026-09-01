"""FastAPI application entrypoint for ReviewAI."""

import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.router import api_router
from backend.app.api.v1.health import health_router
from backend.app.core.config import get_settings
from backend.app.core.errors import ReviewAIError
from backend.app.core.logging import (
    analysis_id_ctx,
    logger,
    request_id_ctx,
    setup_logging,
)

settings = get_settings()
setup_logging(level=settings.LOG_LEVEL, json_format=settings.JSON_LOGS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    logger.info(
        "Starting %s v%s in [%s] mode",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.APP_ENV,
    )
    logger.info(
        "Limits: max_lines=%d, max_bytes=%d | Subsystems: static=%s, llm=%s",
        settings.MAX_SOURCE_LINES,
        settings.MAX_SOURCE_SIZE,
        settings.ENABLE_STATIC_ANALYSIS,
        settings.ENABLE_LLM,
    )
    yield
    logger.info("Shutting down %s...", settings.APP_NAME)


app = FastAPI(
    title="ReviewAI API",
    description=(
        "Production-quality backend foundation for ReviewAI — Intelligent Code Review "
        "& Engineering Insights combining deterministic static code analysis with LLM reasoning."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def tracing_and_timing_middleware(request: Request, call_next):
    """Inject request ID into context, log lifecycle, and measure processing latency."""
    raw_req_id = request.headers.get("X-Request-ID")
    request_id = raw_req_id if raw_req_id and len(raw_req_id) <= 64 else str(uuid.uuid4())
    token = request_id_ctx.set(request_id)
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
        process_time_ms = (time.perf_counter() - start_time) * 1000.0
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"
        return response
    finally:
        request_id_ctx.reset(token)
        analysis_id_ctx.set(None)


@app.exception_handler(ReviewAIError)
async def handle_reviewai_error(request: Request, exc: ReviewAIError) -> JSONResponse:
    """Handle domain-specific exceptions with structured, safe error payloads."""
    req_id = request_id_ctx.get() or ""
    logger.warning("Domain error: code=%s, msg='%s', request_id=%s", exc.error_code, exc.message, req_id)
    content = {
        "error": {
            "code": exc.error_code,
            "message": exc.message,
            "request_id": req_id,
        }
    }
    if exc.details:
        content["error"]["details"] = exc.details

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers={"X-Request-ID": req_id},
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request schema validation errors cleanly."""
    req_id = request_id_ctx.get() or ""
    logger.warning("Request validation error: request_id=%s, errors=%s", req_id, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The submitted request failed schema validation.",
                "request_id": req_id,
                "details": {"validation_errors": exc.errors()},
            }
        },
        headers={"X-Request-ID": req_id},
    )


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions."""
    req_id = request_id_ctx.get() or ""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
                "request_id": req_id,
            }
        },
        headers={"X-Request-ID": req_id},
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled server exceptions preventing stack trace leaks."""
    req_id = request_id_ctx.get() or ""
    logger.error("Unhandled exception: %s (request_id=%s)", str(exc), req_id, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal error occurred. Please reference the Request ID.",
                "request_id": req_id,
            }
        },
        headers={"X-Request-ID": req_id},
    )


# Root Health Routes (for container orchestrators and direct root probes)
app.include_router(health_router)


@app.get("/", tags=["System"], summary="API Root Metadata")
async def root() -> Dict[str, Any]:
    """Root metadata endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "ReviewAI: Intelligent Code Review & Engineering Insights API",
        "docs": "/docs",
        "health": "/health",
        "api_v1": settings.API_V1_PREFIX,
    }


# Mount Top-Level API Router (/api/v1)
app.include_router(api_router, prefix="/api")
