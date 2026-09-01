"""Dependency injection providers for ReviewAI API layer."""

from fastapi import Depends

from backend.app.analyzers.composite import StaticAnalysisEngine
from backend.app.core.config import Settings, get_settings
from backend.app.llm.service import LLMReviewService
from backend.app.preprocessing.python_preprocessor import PythonPreprocessor
from backend.app.review.engine import ReviewEngine
from backend.app.review.fusion import FindingFusion
from backend.app.review.prioritizer import FindingPrioritizer
from backend.app.review.scorer import ScoreCalculator
from backend.app.services.review_service import ReviewService
from backend.app.services.storage import (
    InMemoryReviewRepository,
    ReviewRepository,
)

# Singleton instances for app lifecycle
_in_memory_repo = InMemoryReviewRepository()
_python_preprocessor = PythonPreprocessor()
_static_analysis_engine = StaticAnalysisEngine(preprocessor=_python_preprocessor)
_llm_review_service = LLMReviewService()
_finding_fusion = FindingFusion()
_finding_prioritizer = FindingPrioritizer()
_score_calculator = ScoreCalculator()

_review_engine = ReviewEngine(
    preprocessor=_python_preprocessor,
    static_engine=_static_analysis_engine,
    llm_service=_llm_review_service,
    fusion=_finding_fusion,
    prioritizer=_finding_prioritizer,
    scorer=_score_calculator,
)


def get_review_repository() -> ReviewRepository:
    """Provide the active review repository instance."""
    return _in_memory_repo


def get_review_engine(
    settings: Settings = Depends(get_settings),
) -> ReviewEngine:
    """Provide initialized ReviewEngine orchestrator instance."""
    return _review_engine


def get_review_service(
    repo: ReviewRepository = Depends(get_review_repository),
    settings: Settings = Depends(get_settings),
    review_engine: ReviewEngine = Depends(get_review_engine),
) -> ReviewService:
    """Provide initialized ReviewService instance."""
    return ReviewService(
        repository=repo,
        settings=settings,
        review_engine=review_engine,
    )
