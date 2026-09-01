"""Unit tests for ReviewService end-to-end lifecycle and repository persistence."""

import pytest
from backend.app.core.config import Settings
from backend.app.llm.mock import MockLLMProvider
from backend.app.llm.service import LLMReviewService
from backend.app.models.enums import Language, ReviewStatus
from backend.app.preprocessing.python_preprocessor import PythonPreprocessor
from backend.app.review.engine import ReviewEngine
from backend.app.schemas.review import ReviewCreateRequest
from backend.app.services.review_service import ReviewService
from backend.app.services.storage import InMemoryReviewRepository


@pytest.fixture
def review_service() -> ReviewService:
    settings = Settings(ENABLE_LLM=True, ENABLE_AST_RULES=True, ENABLE_RUFF=False, ENABLE_BANDIT=False)
    repo = InMemoryReviewRepository()
    prep = PythonPreprocessor(settings=settings)
    mock_llm = MockLLMProvider()
    llm_service = LLMReviewService(provider=mock_llm, settings=settings)
    engine = ReviewEngine(settings=settings, preprocessor=prep, llm_service=llm_service)
    return ReviewService(repository=repo, settings=settings, review_engine=engine)


@pytest.mark.asyncio
async def test_review_service_create_and_retrieve(review_service: ReviewService):
    code = (
        "def compute(data: list = []):\n"
        "    return sum(data)\n"
    )
    req = ReviewCreateRequest(
        code=code,
        language=Language.PYTHON,
        filename="compute.py",
        enable_static_analysis=True,
        enable_llm=True,
    )

    created = await review_service.create_review(req)
    assert created.review_id is not None
    assert created.status == ReviewStatus.COMPLETED
    assert created.quality_score is not None
    assert created.quality_score.overall_score <= 100.0

    # Retrieve by ID
    retrieved = await review_service.get_review(created.review_id)
    assert retrieved.review_id == created.review_id
    assert len(retrieved.findings) == len(created.findings)

    # Findings endpoint
    findings_resp = await review_service.get_review_findings(created.review_id)
    assert findings_resp.total == len(created.findings)
