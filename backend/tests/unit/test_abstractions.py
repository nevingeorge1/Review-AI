"""Unit tests verifying abstraction contracts, registries, and in-memory storage."""

import pytest
from backend.app.analyzers.base import (
    AnalyzerRegistry,
    LanguageAnalyzer,
    StaticAnalyzer,
)
from backend.app.llm.base import LLMProvider, ModelMetadata
from backend.app.models.domain import (
    AnalysisMetadata,
    AnalysisResponse,
    QualityScore,
    ReviewSummary,
    SourceFile,
    StaticFinding,
)
from backend.app.models.enums import Language, ReviewStatus
from backend.app.services.storage import InMemoryReviewRepository


class DummyLanguageAnalyzer(LanguageAnalyzer):
    """Test implementation of LanguageAnalyzer."""

    @property
    def language(self) -> Language:
        return Language.PYTHON

    def validate_syntax(self, source_file: SourceFile) -> bool:
        return True

    def parse_ast(self, source_file: SourceFile):
        return None


class DummyStaticAnalyzer(StaticAnalyzer):
    """Test implementation of StaticAnalyzer."""

    @property
    def name(self) -> str:
        return "dummy_linter"

    @property
    def supported_languages(self) -> list[Language]:
        return [Language.PYTHON]

    def is_available(self) -> bool:
        return True

    async def analyze(self, source_file: SourceFile) -> list[StaticFinding]:
        return []


class TestAnalyzerRegistry:
    """Test registry managing language and static analyzers."""

    def test_registry_registration_and_retrieval(self):
        registry = AnalyzerRegistry()
        lang_analyzer = DummyLanguageAnalyzer()
        static_analyzer = DummyStaticAnalyzer()

        registry.register_language_analyzer(lang_analyzer)
        registry.register_static_analyzer(static_analyzer)

        assert registry.get_language_analyzer(Language.PYTHON) is lang_analyzer
        assert registry.get_language_analyzer(Language.JAVA) is None

        analyzers = registry.get_static_analyzers_for_language(Language.PYTHON)
        assert len(analyzers) == 1
        assert analyzers[0].name == "dummy_linter"


class TestInMemoryRepository:
    """Test in-memory storage abstraction."""

    @pytest.mark.asyncio
    async def test_save_and_retrieve_review(self):
        repo = InMemoryReviewRepository()
        review = AnalysisResponse(
            id="rev-001",
            status=ReviewStatus.COMPLETED,
            findings=[],
            summary=ReviewSummary(total_findings=0),
            quality_score=QualityScore(overall_score=100.0, grade="A+"),
            metadata=AnalysisMetadata(
                analysis_id="rev-001",
                language=Language.PYTHON,
                line_count=5,
                byte_size=100,
            ),
        )

        await repo.save_review(review)
        retrieved = await repo.get_review("rev-001")
        assert retrieved is not None
        assert retrieved.id == "rev-001"

        missing = await repo.get_review("non-existent")
        assert missing is None

        reviews_list = await repo.list_reviews()
        assert len(reviews_list) == 1

        deleted = await repo.delete_review("rev-001")
        assert deleted is True
        assert await repo.get_review("rev-001") is None
