"""Unit tests for ScoreCalculator and quality score bounds."""

from backend.app.models.domain import ReviewFinding
from backend.app.models.enums import Category, DetectionSource, Severity
from backend.app.review.scorer import ScoreCalculator


def test_score_calculator_clean_code():
    scorer = ScoreCalculator()
    score = scorer.calculate_quality_score([])
    assert score.overall_score == 100.0
    assert score.grade == "A+"
    assert score.security_score == 100.0
    assert score.reliability_score == 100.0


def test_score_calculator_penalties_and_grading():
    findings = [
        ReviewFinding(
            category=Category.SECURITY,
            severity=Severity.HIGH,
            title="SQL Injection",
            description="Dynamic SQL query.",
            confidence=1.0,
            detection_source=DetectionSource.HYBRID,
        ),
        ReviewFinding(
            category=Category.BUG,
            severity=Severity.HIGH,
            title="Mutable default",
            description="Mutable default argument.",
            confidence=1.0,
            detection_source=DetectionSource.STATIC_ANALYSIS,
        ),
    ]

    scorer = ScoreCalculator()
    score = scorer.calculate_quality_score(findings)

    # Security deduction = 15.0 -> security_score = 85.0
    assert score.security_score == 85.0
    # Reliability deduction = 15.0 -> reliability_score = 85.0
    assert score.reliability_score == 85.0
    # Overall score = 0.3*85 + 0.3*85 + 0.2*100 + 0.1*100 + 0.1*100 = 25.5 + 25.5 + 20 + 10 + 10 = 91.0
    assert score.overall_score == 91.0
    assert score.grade == "A"


def test_score_calculator_bounded_floor():
    # Many critical findings to test 0.0 floor
    findings = [
        ReviewFinding(
            category=Category.SECURITY,
            severity=Severity.CRITICAL,
            title=f"Critical {i}",
            description="Critical exploit.",
            confidence=1.0,
            detection_source=DetectionSource.STATIC_ANALYSIS,
        )
        for i in range(10)
    ]

    scorer = ScoreCalculator()
    score = scorer.calculate_quality_score(findings)
    assert score.security_score == 0.0
    assert score.overall_score >= 0.0
    assert score.grade == "C" or score.grade == "D" or score.grade == "F"
