"""Unit tests for InMemoryReviewRepository."""

from datetime import datetime, timezone
import pytest
from backend.app.models.enums import Language, ReviewStatus
from backend.app.schemas.review import ReviewResponse
from backend.app.services.storage import InMemoryReviewRepository


@pytest.mark.asyncio
async def test_repository_crud_operations():
    """Verify repository create, get, list, update, and delete."""
    repo = InMemoryReviewRepository()
    assert await repo.count() == 0

    now = datetime.now(timezone.utc)
    review1 = ReviewResponse(
        review_id="rev-1",
        analysis_id="ana-1",
        status=ReviewStatus.PENDING,
        language=Language.PYTHON,
        filename="test1.py",
        created_at=now,
        updated_at=now,
    )
    review2 = ReviewResponse(
        review_id="rev-2",
        analysis_id="ana-2",
        status=ReviewStatus.PENDING,
        language=Language.PYTHON,
        filename="test2.py",
        created_at=now,
        updated_at=now,
    )

    # Create
    await repo.create_review(review1)
    await repo.create_review(review2)
    assert await repo.count() == 2

    # Get
    fetched = await repo.get_review("rev-1")
    assert fetched is not None
    assert fetched.filename == "test1.py"

    # List & Pagination
    items, total = await repo.list_reviews(limit=1, offset=0)
    assert total == 2
    assert len(items) == 1

    # Update
    review1.status = ReviewStatus.COMPLETED
    updated = await repo.update_review(review1)
    assert updated is not None
    assert updated.status == ReviewStatus.COMPLETED

    # Delete
    deleted = await repo.delete_review("rev-1")
    assert deleted is True
    assert await repo.get_review("rev-1") is None
    assert await repo.count() == 1
