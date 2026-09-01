"""Unit tests for domain models, validation constraints, and enums."""

import pytest
from pydantic import ValidationError

from backend.app.models.domain import (
    AnalysisMetadata,
    AnalysisRequest,
    AnalysisResponse,
    CodeSubmission,
    Evidence,
    QualityScore,
    ReviewFinding,
    ReviewSummary,
    SourceFile,
    StaticFinding,
    SuggestedFix,
)
from backend.app.models.enums import (
    Category,
    DetectionSource,
    Language,
    ReviewStatus,
    Severity,
)


class TestDomainEnums:
    """Test enum definitions and properties."""

    def test_language_values(self):
        assert Language.PYTHON.value == "python"
        assert Language.JAVASCRIPT.value == "javascript"
        assert Language.TYPESCRIPT.value == "typescript"
        assert Language.JAVA.value == "java"

    def test_category_values(self):
        assert Category.BUG.value == "bug"
        assert Category.SECURITY.value == "security"
        assert Category.STYLE.value == "style"
        assert Category.PERFORMANCE.value == "performance"
        assert Category.MAINTAINABILITY.value == "maintainability"

    def test_severity_penalties(self):
        assert Severity.CRITICAL.score_penalty == 25.0
        assert Severity.HIGH.score_penalty == 15.0
        assert Severity.MEDIUM.score_penalty == 8.0
        assert Severity.LOW.score_penalty == 3.0
        assert Severity.INFO.score_penalty == 0.5


class TestDomainModels:
    """Test domain model validation and serialization."""

    def test_code_submission_creation(self, sample_code: str):
        submission = CodeSubmission(
            code=sample_code,
            language=Language.PYTHON,
            filename="test.py",
        )
        assert submission.code == sample_code
        assert submission.language == Language.PYTHON
        assert submission.filename == "test.py"

    def test_code_submission_empty_rejected(self):
        with pytest.raises(ValidationError):
            CodeSubmission(code="", language=Language.PYTHON)

    def test_review_finding_validation(self, sample_review_finding: ReviewFinding):
        assert sample_review_finding.category == Category.SECURITY
        assert sample_review_finding.severity == Severity.HIGH
        assert sample_review_finding.detection_source == DetectionSource.HYBRID
        assert sample_review_finding.suggested_fix is not None
        assert sample_review_finding.confidence >= 0.0 and sample_review_finding.confidence <= 1.0

    def test_review_finding_end_line_validation(self):
        # Invalid when end_line < line_number
        with pytest.raises(ValidationError):
            ReviewFinding(
                category=Category.BUG,
                severity=Severity.MEDIUM,
                title="Invalid Line Range",
                description="End line cannot precede start line.",
                line_number=10,
                end_line=5,
                detection_source=DetectionSource.STATIC_ANALYSIS,
            )

    def test_quality_score_bounds(self):
        qs = QualityScore(overall_score=85.5, grade="B", category_scores={"security": 90.0})
        assert qs.overall_score == 85.5
        assert qs.grade == "B"

        with pytest.raises(ValidationError):
            QualityScore(overall_score=150.0, grade="Invalid")

        with pytest.raises(ValidationError):
            QualityScore(overall_score=-5.0, grade="Invalid")

    def test_analysis_response_serialization(self, sample_review_finding: ReviewFinding):
        response = AnalysisResponse(
            id="test-review-123",
            status=ReviewStatus.COMPLETED,
            findings=[sample_review_finding],
            summary=ReviewSummary(
                total_findings=1,
                high_count=1,
                executive_summary="Found 1 high severity issue.",
            ),
            quality_score=QualityScore(overall_score=85.0, grade="B"),
            metadata=AnalysisMetadata(
                analysis_id="test-review-123",
                language=Language.PYTHON,
                line_count=10,
                byte_size=200,
                total_duration_ms=125.5,
            ),
        )
        data = response.model_dump()
        assert data["id"] == "test-review-123"
        assert len(data["findings"]) == 1
        assert data["summary"]["high_count"] == 1
