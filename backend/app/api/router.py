"""Top-level API router aggregating all API versions."""

from fastapi import APIRouter
from backend.app.api.v1.router import api_v1_router

api_router = APIRouter()
api_router.include_router(api_v1_router, prefix="/v1")
