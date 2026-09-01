"""Unit tests for FindingPrioritizer ranking logic."""

from backend.app.models.domain import ReviewFinding
from backend.app.models.enums import Category, DetectionSource, Severity
from backend.app.review.prioritizer import FindingPrioritizer


def test_prioritizer_ranks_critical_security_first():
    f_style = ReviewFinding(
        category=Category.STYLE,
        severity=Severity.LOW,
        title="Bad indent",
        description="Indentation issue.",
        line_number=1,
        detection_source=DetectionSource.STATIC_ANALYSIS,
    )
    f_bug = ReviewFinding(
        category=Category.BUG,
        severity=Severity.MEDIUM,
        title="Possible off-by-one",
        description="Index might overflow.",
        line_number=5,
        detection_source=DetectionSource.LLM,
    )
    f_sec = ReviewFinding(
        category=Category.SECURITY,
        severity=Severity.CRITICAL,
        title="Remote Code Execution",
        description="eval on untrusted input.",
        line_number=10,
        detection_source=DetectionSource.HYBRID,
    )

    prioritizer = FindingPrioritizer()
    sorted_findings = prioritizer.prioritize_findings([f_style, f_bug, f_sec])

    assert len(sorted_findings) == 3
    # Critical security must be at index 0
    assert sorted_findings[0].severity == Severity.CRITICAL
    assert sorted_findings[0].category == Category.SECURITY
    # Medium bug at index 1
    assert sorted_findings[1].severity == Severity.MEDIUM
    # Low style at index 2
    assert sorted_findings[2].severity == Severity.LOW
