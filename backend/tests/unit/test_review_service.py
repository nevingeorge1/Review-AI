"""Unit tests for ReviewService business logic and orchestration."""

import pytest
from backend.app.core.errors import (
    InvalidSourceCodeError,
    ReviewNotFoundError,
    SourceCodeTooLargeError,
    UnsupportedLanguageError,
)
from backend.app.models.enums import Language, ReviewStatus
from backend.app.schemas.review import ReviewCreateRequest
from backend.app.services.review_service import ReviewService


@pytest.mark.asyncio
async def test_create_review_success(review_service: ReviewService):
    """Verify standard review registration."""
    req = ReviewCreateRequest(
        code="def add(x, y):\n    return x + y\n",
        language=Language.PYTHON,
        filename="calculator.py",
        context_notes="Simple math function",
    )
    result = await review_service.create_review(req)
    assert result.review_id is not None
    assert result.analysis_id is not None
    assert result.status == ReviewStatus.PENDING
    assert result.language == Language.PYTHON
    assert result.filename == "calculator.py"
    assert result.line_count == 3
    assert result.byte_size > 0
    assert len(result.findings) == 0


@pytest.mark.asyncio
async def test_create_review_unsupported_language(review_service: ReviewService):
    """Verify rejection of unsupported languages."""
    req = ReviewCreateRequest(
        code="fn main() { println!(\"hello\"); }",
        language=Language.RUST,
    )
    with pytest.raises(UnsupportedLanguageError) as exc_info:
        await review_service.create_review(req)
    assert exc_info.value.error_code == "UNSUPPORTED_LANGUAGE"


@pytest.mark.asyncio
async def test_create_review_empty_code(review_service: ReviewService):
    """Verify rejection of whitespace-only code."""
    req = ReviewCreateRequest(code="   \n   \t  ", language=Language.PYTHON)
    with pytest.raises(InvalidSourceCodeError):
        await review_service.create_review(req)


@pytest.mark.asyncio
async def test_create_review_oversized_code(review_service: ReviewService):
    """Verify rejection when code exceeds line limit."""
    long_code = "\n".join([f"var_{i} = {i}" for i in range(150)])
    req = ReviewCreateRequest(code=long_code, language=Language.PYTHON)
    with pytest.raises(SourceCodeTooLargeError):
        await review_service.create_review(req)


@pytest.mark.asyncio
async def test_get_review_by_id(review_service: ReviewService):
    """Verify retrieval of created review."""
    req = ReviewCreateRequest(code="print('test')", language=Language.PYTHON)
    created = await review_service.create_review(req)

    fetched = await review_service.get_review(created.review_id)
    assert fetched.review_id == created.review_id
    assert fetched.status == ReviewStatus.PENDING


@pytest.mark.asyncio
async def test_get_review_not_found(review_service: ReviewService):
    """Verify 404 domain error on non-existent review ID."""
    with pytest.raises(ReviewNotFoundError) as exc_info:
        await review_service.get_review("non-existent-uuid")
    assert exc_info.value.error_code == "REVIEW_NOT_FOUND"


@pytest.mark.asyncio
async def test_list_reviews_pagination(review_service: ReviewService):
    """Verify pagination calculation and ordering."""
    for i in range(5):
        await review_service.create_review(
            ReviewCreateRequest(code=f"x_{i} = {i}", language=Language.PYTHON)
        )

    # Page 1 with page_size 2
    page1 = await review_service.list_reviews(page=1, page_size=2)
    assert page1.total == 5
    assert len(page1.items) == 2
    assert page1.page == 1
    assert page1.total_pages == 3

    # Page 3 with page_size 2
    page3 = await review_service.list_reviews(page=3, page_size=2)
    assert len(page3.items) == 1


@pytest.mark.asyncio
async def test_delete_review(review_service: ReviewService):
    """Verify deletion of review records."""
    req = ReviewCreateRequest(code="print('temp')", language=Language.PYTHON)
    created = await review_service.create_review(req)

    deleted = await review_service.delete_review(created.review_id)
    assert deleted is True

    with pytest.raises(ReviewNotFoundError):
        await review_service.get_review(created.review_id)
