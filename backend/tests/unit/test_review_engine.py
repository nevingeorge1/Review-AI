"""Integration tests for ReviewEngine (full pipeline, static-only mode, hybrid mode, syntax failure)."""

import pytest
from backend.app.core.config import Settings
from backend.app.llm.mock import MockLLMProvider
from backend.app.llm.service import LLMReviewService
from backend.app.models.domain import AnalysisRequest, CodeSubmission
from backend.app.models.enums import Category, DetectionSource, Language, ReviewStatus, Severity
from backend.app.preprocessing.python_preprocessor import PythonPreprocessor
from backend.app.review.engine import ReviewEngine


@pytest.fixture
def mock_review_engine() -> ReviewEngine:
    settings = Settings(ENABLE_LLM=True, ENABLE_AST_RULES=True, ENABLE_RUFF=False, ENABLE_BANDIT=False)
    prep = PythonPreprocessor(settings=settings)
    mock_provider = MockLLMProvider()
    llm_service = LLMReviewService(provider=mock_provider, settings=settings)
    return ReviewEngine(settings=settings, preprocessor=prep, llm_service=llm_service)


@pytest.mark.asyncio
async def test_review_engine_hybrid_pipeline(mock_review_engine: ReviewEngine):
    code = (
        "import os\n"
        "def run_command(user_input, items=[]):\n"
        "    return eval(user_input)\n"
    )
    req = AnalysisRequest(
        submission=CodeSubmission(code=code, language=Language.PYTHON, filename="test.py"),
        enable_static_analysis=True,
        enable_llm=True,
    )

    response = await mock_review_engine.review_code(req)

    assert response.status == ReviewStatus.COMPLETED
    assert response.summary.review_mode == "HYBRID"
    assert len(response.findings) >= 2

    # Check that eval() was elevated to HYBRID
    eval_finding = next((f for f in response.findings if "eval" in f.title.lower() or "eval" in f.description.lower()), None)
    assert eval_finding is not None
    assert eval_finding.detection_source == DetectionSource.HYBRID
    assert eval_finding.severity == Severity.HIGH

    # Check scores
    assert response.quality_score.overall_score < 100.0
    assert response.quality_score.grade in ["A", "B", "C", "D", "F"]

    # Check stage timings
    assert "preprocessing" in response.metadata.stage_durations_ms
    assert "static_analysis" in response.metadata.stage_durations_ms
    assert "llm_reasoning" in response.metadata.stage_durations_ms
    assert response.metadata.total_duration_ms > 0.0


@pytest.mark.asyncio
async def test_review_engine_static_only_when_llm_disabled():
    settings = Settings(ENABLE_LLM=False, ENABLE_AST_RULES=True, ENABLE_RUFF=False, ENABLE_BANDIT=False)
    engine = ReviewEngine(settings=settings)

    code = "import os\nos.system('ls')\n"
    req = AnalysisRequest(
        submission=CodeSubmission(code=code, language=Language.PYTHON, filename="test.py"),
        enable_static_analysis=True,
        enable_llm=False,
    )

    response = await engine.review_code(req)
    assert response.status == ReviewStatus.COMPLETED
    assert response.summary.review_mode == "STATIC_ONLY"
    assert response.metadata.static_only_mode is True
    assert len(response.findings) >= 1
    assert response.findings[0].detection_source == DetectionSource.STATIC_ANALYSIS


@pytest.mark.asyncio
async def test_review_engine_syntax_error_graceful_handling():
    engine = ReviewEngine()
    broken_code = "def broken(\n    pass"
    req = AnalysisRequest(
        submission=CodeSubmission(code=broken_code, language=Language.PYTHON, filename="broken.py"),
    )

    response = await engine.review_code(req)
    assert response.status == ReviewStatus.FAILED
    assert response.quality_score.overall_score == 0.0
    assert response.quality_score.grade == "F"
    assert len(response.findings) == 1
    assert "Syntax Error" in response.findings[0].title
