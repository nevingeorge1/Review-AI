"""Integration unit tests for LLMReviewService (end-to-end pipeline and static fallback)."""

import pytest
from backend.app.core.config import Settings
from backend.app.llm.mock import MockLLMProvider
from backend.app.llm.service import LLMReviewService
from backend.app.models.domain import SourceFile
from backend.app.models.enums import Category, Language, Severity
from backend.app.preprocessing.python_preprocessor import PythonPreprocessor


@pytest.mark.asyncio
async def test_llm_service_successful_review():
    settings = Settings(ENABLE_LLM=True, ALLOW_STATIC_FALLBACK=True)
    provider = MockLLMProvider()
    service = LLMReviewService(provider=provider, settings=settings)

    code = "def process(items=[]):\n    return eval('1+1')\n"
    sf = SourceFile(content=code, language=Language.PYTHON, filename="process.py", line_count=2, byte_size=len(code))

    prep = PythonPreprocessor(settings=settings)
    prep_res = prep.analyze_source(code, filename="process.py")

    result = await service.review_code(source_file=sf, preprocessing_result=prep_res)

    assert result.success is True
    assert result.status == "COMPLETED"
    assert len(result.findings) >= 2
    assert result.provider == "mock"
    assert result.duration_ms > 0.0


@pytest.mark.asyncio
async def test_llm_service_disabled_fallback():
    settings = Settings(ENABLE_LLM=False, ALLOW_STATIC_FALLBACK=True)
    service = LLMReviewService(settings=settings)

    code = "x = 10\n"
    sf = SourceFile(content=code, language=Language.PYTHON, filename="test.py", line_count=1, byte_size=len(code))

    result = await service.review_code(source_file=sf)

    assert result.success is True
    assert result.status == "FALLBACK"
    assert result.findings == []


@pytest.mark.asyncio
async def test_llm_service_unavailable_graceful_fallback():
    settings = Settings(ENABLE_LLM=True, ALLOW_STATIC_FALLBACK=True)
    provider = MockLLMProvider(simulate_unavailable=True)
    service = LLMReviewService(provider=provider, settings=settings)

    code = "x = 10\n"
    sf = SourceFile(content=code, language=Language.PYTHON, filename="test.py", line_count=1, byte_size=len(code))

    result = await service.review_code(source_file=sf)

    assert result.success is False
    assert result.status == "FALLBACK"
    assert "LLM inference unavailable" in result.executive_summary
