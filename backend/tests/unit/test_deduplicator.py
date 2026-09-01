"""Unit tests for finding deduplication, multi-tool provenance merging, and separation of distinct issues."""

from backend.app.analyzers.deduplicator import deduplicate_and_merge_static_findings
from backend.app.models.domain import StaticFinding
from backend.app.models.enums import Category, Severity


def test_deduplicate_identical_findings_from_different_tools():
    """Verify Bandit and AST rule finding same eval issue are merged with combined provenance."""
    f1 = StaticFinding(
        analyzer_name="bandit",
        rule_id="B307",
        category=Category.SECURITY,
        severity=Severity.HIGH,
        message="Use of possibly insecure function - eval detected.",
        line_number=5,
        code_evidence="eval(user_code)",
    )
    f2 = StaticFinding(
        analyzer_name="ast_rules",
        rule_id="RULE-001",
        category=Category.SECURITY,
        severity=Severity.HIGH,
        message="Direct invocation of eval() detected.",
        line_number=5,
        code_evidence="eval(user_code)",
    )

    merged = deduplicate_and_merge_static_findings([f1, f2])
    assert len(merged) == 1
    m = merged[0]
    assert "bandit" in m.analyzer_name
    assert "ast_rules" in m.analyzer_name
    assert m.category == Category.SECURITY
    assert m.severity == Severity.HIGH
    assert m.line_number == 5


def test_different_categories_at_same_line_not_merged():
    """Verify distinct issues at the same line (e.g. style vs security) are preserved independently."""
    f1 = StaticFinding(
        analyzer_name="ruff",
        rule_id="E501",
        category=Category.STYLE,
        severity=Severity.LOW,
        message="Line too long (110 > 100)",
        line_number=10,
    )
    f2 = StaticFinding(
        analyzer_name="ast_rules",
        rule_id="RULE-004",
        category=Category.SECURITY,
        severity=Severity.HIGH,
        message="Invocation of os.system() detected.",
        line_number=10,
    )

    merged = deduplicate_and_merge_static_findings([f1, f2])
    assert len(merged) == 2
    categories = [f.category for f in merged]
    assert Category.STYLE in categories
    assert Category.SECURITY in categories


def test_higher_severity_preserved_on_merge():
    """Verify when merging findings with differing severities, the higher severity wins."""
    f1 = StaticFinding(
        analyzer_name="tool_a",
        rule_id="R1",
        category=Category.SECURITY,
        severity=Severity.MEDIUM,
        message="Potential subprocess risk",
        line_number=12,
    )
    f2 = StaticFinding(
        analyzer_name="tool_b",
        rule_id="R2",
        category=Category.SECURITY,
        severity=Severity.HIGH,
        message="Dangerous subprocess execution with shell=True",
        line_number=12,
    )

    merged = deduplicate_and_merge_static_findings([f1, f2])
    assert len(merged) == 1
    assert merged[0].severity == Severity.HIGH
    assert "shell=True" in merged[0].message
