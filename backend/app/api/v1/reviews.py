"""Review API endpoints for ReviewAI v1."""

from fastapi import APIRouter, Depends, Query, status

from backend.app.api.deps import get_review_service
from backend.app.schemas.error import ErrorResponse
from backend.app.schemas.review import (
    ReviewCreateRequest,
    ReviewFindingListResponse,
    ReviewListResponse,
    ReviewResponse,
)
from backend.app.services.review_service import ReviewService

reviews_router = APIRouter(prefix="/reviews", tags=["Reviews"])


@reviews_router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit code for review",
    description="Validates submitted source code, creates a new review job, and registers it in the system.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid source code or unsupported language"},
        413: {"model": ErrorResponse, "description": "Source code exceeds line or payload limit"},
        422: {"model": ErrorResponse, "description": "Request validation failure"},
    },
)
async def submit_code_review(
    request: ReviewCreateRequest,
    service: ReviewService = Depends(get_review_service),
) -> ReviewResponse:
    """Register and validate a code review submission."""
    return await service.create_review(request)


@reviews_router.get(
    "/{review_id}",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve review report",
    description="Fetches a completed or in-progress review record by its unique review UUID.",
    responses={
        404: {"model": ErrorResponse, "description": "Review record not found"},
    },
)
async def get_review_by_id(
    review_id: str,
    service: ReviewService = Depends(get_review_service),
) -> ReviewResponse:
    """Retrieve review by ID."""
    return await service.get_review(review_id)


@reviews_router.get(
    "",
    response_model=ReviewListResponse,
    status_code=status.HTTP_200_OK,
    summary="List historical reviews",
    description="Returns a paginated list of historical code reviews.",
    responses={
        422: {"model": ErrorResponse, "description": "Invalid pagination parameters"},
    },
)
async def list_reviews(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    service: ReviewService = Depends(get_review_service),
) -> ReviewListResponse:
    """List code review history with pagination."""
    return await service.list_reviews(page=page, page_size=page_size)


@reviews_router.get(
    "/{review_id}/findings",
    response_model=ReviewFindingListResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve review findings",
    description="Returns all prioritized findings discovered for a specific review.",
    responses={
        404: {"model": ErrorResponse, "description": "Review record not found"},
    },
)
async def get_review_findings(
    review_id: str,
    service: ReviewService = Depends(get_review_service),
) -> ReviewFindingListResponse:
    """Retrieve findings for a review."""
    return await service.get_review_findings(review_id)


@reviews_router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete review record",
    description="Deletes a code review record from the repository.",
    responses={
        404: {"model": ErrorResponse, "description": "Review record not found"},
    },
)
async def delete_review(
    review_id: str,
    service: ReviewService = Depends(get_review_service),
) -> None:
    """Delete a review by ID."""
    await service.delete_review(review_id)
