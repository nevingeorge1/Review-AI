"""API v1 root router aggregating feature routers for ReviewAI."""

from fastapi import APIRouter

from backend.app.api.v1.health import health_router
from backend.app.api.v1.reviews import reviews_router

api_v1_router = APIRouter()

# Include health routes directly under /api/v1 (e.g. /api/v1/health, /api/v1/health/live, /api/v1/health/ready)
api_v1_router.include_router(health_router)

# Include review routes under /api/v1 (e.g. /api/v1/reviews, /api/v1/reviews/{id})
api_v1_router.include_router(reviews_router)
