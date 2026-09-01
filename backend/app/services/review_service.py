"""Review application service for ReviewAI.

Coordinates API request validation, repository persistence, and delegates
end-to-end review orchestration to ReviewEngine.
"""

import math
import uuid
from datetime import datetime, timezone
from typing import Optional

from backend.app.core.config import Settings, get_settings
from backend.app.core.errors import (
    ReviewNotFoundError,
    UnsupportedLanguageError,
)
from backend.app.core.logging import logger
from backend.app.core.security import sanitize_and_validate_source_code
from backend.app.models.domain import (
    AnalysisRequest,
    CodeSubmission,
)
from backend.app.models.enums import Language, ReviewStatus
from backend.app.review.engine import ReviewEngine
from backend.app.schemas.review import (
    ReviewCreateRequest,
    ReviewFindingListResponse,
    ReviewListResponse,
    ReviewResponse,
)
from backend.app.services.storage import ReviewRepository


class ReviewService:
    """Application service coordinating code review lifecycle, persistence, and review engine execution."""

    def __init__(
        self,
        repository: ReviewRepository,
        settings: Optional[Settings] = None,
        review_engine: Optional[ReviewEngine] = None,
    ) -> None:
        self.repository = repository
        self.settings = settings or get_settings()
        self.engine = review_engine or ReviewEngine(settings=self.settings)

    async def create_review(self, request: ReviewCreateRequest) -> ReviewResponse:
        """
        Validate submission, execute full ReviewEngine analysis pipeline, and persist review record.

        Args:
            request: The client code review request.

        Returns:
            ReviewResponse containing prioritized findings, summary metrics, and quality score.
        """
        # 1. Language validation (Python supported initially)
        if request.language != Language.PYTHON:
            raise UnsupportedLanguageError(
                language=request.language.value,
                supported=[Language.PYTHON.value],
            )

        # 2. Security validation & input limits enforcement
        sanitized_code, line_count, byte_size = sanitize_and_validate_source_code(
            code=request.code,
            max_lines=self.settings.MAX_SOURCE_LINES,
            max_bytes=self.settings.MAX_SOURCE_SIZE,
        )

        review_id = str(uuid.uuid4())
        analysis_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        submission = CodeSubmission(
            code=sanitized_code,
            language=request.language,
            filename=request.filename or "submission.py",
            context_notes=request.context_notes,
        )

        analysis_request = AnalysisRequest(
            id=analysis_id,
            submission=submission,
            enable_static_analysis=request.enable_static_analysis,
            enable_llm=request.enable_llm,
            created_at=now,
        )

        logger.info(
            "Executing review analysis pipeline: review_id=%s, analysis_id=%s, lines=%d, bytes=%d",
            review_id,
            analysis_id,
            line_count,
            byte_size,
        )

        # 3. Execute ReviewEngine Orchestration
        analysis_response = await self.engine.review_code(analysis_request)

        # 4. Map to ReviewResponse entity
        review = ReviewResponse(
            review_id=review_id,
            analysis_id=analysis_response.id,
            status=analysis_response.status,
            language=request.language,
            filename=submission.filename or "submission.py",
            line_count=line_count,
            byte_size=byte_size,
            created_at=now,
            updated_at=now,
            findings=analysis_response.findings,
            summary=analysis_response.summary,
            quality_score=analysis_response.quality_score,
            metadata=analysis_response.metadata,
            message=(
                f"Review completed successfully in {analysis_response.summary.review_mode} mode."
                if analysis_response.status == ReviewStatus.COMPLETED
                else f"Review analysis halted: {analysis_response.summary.executive_summary}"
            ),
        )

        # 5. Persist to repository
        await self.repository.create_review(review)
        return review

    async def get_review(self, review_id: str) -> ReviewResponse:
        """
        Retrieve review record by unique review ID.

        Raises:
            ReviewNotFoundError: If the review ID does not exist.
        """
        review = await self.repository.get_review(review_id)
        if not review:
            logger.warning("Review lookup failed: review_id=%s not found", review_id)
            raise ReviewNotFoundError(review_id=review_id)
        return review

    async def list_reviews(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> ReviewListResponse:
        """
        List reviews with pagination.

        Args:
            page: 1-indexed page number.
            page_size: Number of items per page (1 to 100).

        Returns:
            ReviewListResponse containing items and pagination metadata.
        """
        page = max(1, page)
        page_size = max(1, min(page_size, 100))
        offset = (page - 1) * page_size

        items, total = await self.repository.list_reviews(limit=page_size, offset=offset)
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return ReviewListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def delete_review(self, review_id: str) -> bool:
        """
        Delete review record by ID.

        Raises:
            ReviewNotFoundError: If the review ID does not exist.
        """
        deleted = await self.repository.delete_review(review_id)
        if not deleted:
            raise ReviewNotFoundError(review_id=review_id)
        logger.info("Deleted review: review_id=%s", review_id)
        return True

    async def get_review_findings(self, review_id: str) -> ReviewFindingListResponse:
        """
        Retrieve findings for a specific review record.

        Raises:
            ReviewNotFoundError: If the review ID does not exist.
        """
        review = await self.get_review(review_id)
        return ReviewFindingListResponse(
            review_id=review.review_id,
            total=len(review.findings),
            findings=review.findings,
        )
