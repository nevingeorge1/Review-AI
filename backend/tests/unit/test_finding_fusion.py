"""Unit tests for FindingFusion layer (multi-tool correlation, severity resolution, provenance)."""

from backend.app.models.domain import ReviewFinding, StaticFinding, SuggestedFix
from backend.app.models.enums import Category, DetectionSource, Severity
from backend.app.review.fusion import FindingFusion


def test_fuse_static_and_llm_corroboration():
    """Verify Bandit + AST + LLM finding same eval vulnerability elevates to HYBRID."""
    sf = StaticFinding(
        analyzer_name="bandit,ast_rules",
        rule_id="B307/RULE-001",
        category=Category.SECURITY,
        severity=Severity.HIGH,
        message="Direct invocation of eval() detected.",
        line_number=5,
        code_evidence="eval(cmd)",
    )

    lf = ReviewFinding(
        category=Category.SECURITY,
        severity=Severity.HIGH,
        title="Critical Code Injection via eval()",
        description="User input is passed directly to eval() allowing arbitrary code execution.",
        line_number=5,
        end_line=5,
        explanation="eval() executes arbitrary code in current context.",
        recommendation="Use ast.literal_eval() instead.",
        suggested_fix=SuggestedFix(
            original_snippet="eval(cmd)",
            replacement_snippet="ast.literal_eval(cmd)",
            explanation="Safe evaluation of data literals.",
        ),
        confidence=0.95,
        detection_source=DetectionSource.LLM,
    )

    fusion = FindingFusion()
    fused = fusion.fuse_findings([sf], [lf])

    assert len(fused) == 1
    f = fused[0]
    assert f.detection_source == DetectionSource.HYBRID
    assert "bandit" in f.detected_by
    assert "ast_rules" in f.detected_by
    assert "llm" in f.detected_by
    assert f.confidence >= 0.95
    assert f.confidence_level == "HIGH"
    assert f.suggested_fix is not None
    assert len(f.supporting_evidence) >= 2


def test_severity_conflict_prefers_higher_severity():
    """Verify static HIGH security is not downgraded by an LLM MEDIUM rating."""
    sf = StaticFinding(
        analyzer_name="ast_rules",
        rule_id="RULE-004",
        category=Category.SECURITY,
        severity=Severity.HIGH,
        message="Invocation of os.system() detected.",
        line_number=10,
    )

    lf = ReviewFinding(
        category=Category.SECURITY,
        severity=Severity.MEDIUM,  # Lower severity
        title="os.system call detected",
        description="Consider using subprocess instead.",
        line_number=10,
        detection_source=DetectionSource.LLM,
    )

    fusion = FindingFusion()
    fused = fusion.fuse_findings([sf], [lf])

    assert len(fused) == 1
    assert fused[0].severity == Severity.HIGH  # Invariant: Static security severity is preserved


def test_unrelated_findings_remain_separate():
    """Verify findings with different categories on same line are NOT merged."""
    sf = StaticFinding(
        analyzer_name="ruff",
        rule_id="E501",
        category=Category.STYLE,
        severity=Severity.LOW,
        message="Line too long (120 > 100)",
        line_number=15,
    )

    lf = ReviewFinding(
        category=Category.BUG,
        severity=Severity.HIGH,
        title="Uncaught ZeroDivisionError",
        description="Denominator can be 0.",
        line_number=15,
        detection_source=DetectionSource.LLM,
    )

    fusion = FindingFusion()
    fused = fusion.fuse_findings([sf], [lf])

    assert len(fused) == 2
    cats = [f.category for f in fused]
    assert Category.STYLE in cats
    assert Category.BUG in cats
