"""Finding Deduplication and Evidence Merging Layer.

Identifies overlapping findings across Ruff, Bandit, and AST rules, merges them
while preserving multi-tool provenance, and prevents accidental merging of unrelated issues.
"""

from typing import List, Optional
from backend.app.models.domain import StaticFinding
from backend.app.models.enums import Category, Severity


def _are_findings_duplicates(f1: StaticFinding, f2: StaticFinding) -> bool:
    """
    Determine if two static findings describe the same underlying issue.
    Criteria:
    1. Same category (e.g. both SECURITY).
    2. Overlapping or adjacent line numbers (|line1 - line2| <= 1).
    3. Matching or highly similar rule intent (e.g. both relate to eval, os.system, subprocess, pickle).
    """
    if f1.category != f2.category:
        return False

    if f1.line_number is None or f2.line_number is None:
        return False

    if abs(f1.line_number - f2.line_number) > 1:
        return False

    # Check semantic keyword overlap in rule IDs or messages
    text1 = f"{f1.rule_id} {f1.message}".lower()
    text2 = f"{f2.rule_id} {f2.message}".lower()

    keywords = [
        "eval",
        "exec",
        "system",
        "subprocess",
        "pickle",
        "yaml",
        "sql",
        "password",
        "credential",
        "secret",
        "except",
        "mutable",
        "complexity",
        "nesting",
        "parameter",
    ]

    for kw in keywords:
        if kw in text1 and kw in text2:
            return True

    # Same rule ID exact match
    if f1.rule_id == f2.rule_id:
        return True

    return False


def _get_higher_severity(s1: Severity, s2: Severity) -> Severity:
    """Return the higher severity level between two options."""
    order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    idx1 = order.index(s1) if s1 in order else 99
    idx2 = order.index(s2) if s2 in order else 99
    return s1 if idx1 <= idx2 else s2


def merge_two_findings(primary: StaticFinding, secondary: StaticFinding) -> StaticFinding:
    """
    Merge two overlapping findings into a single consolidated finding with combined provenance.
    """
    # Combine analyzer names without duplication
    existing_analyzers = set(primary.analyzer_name.split(","))
    existing_analyzers.update(secondary.analyzer_name.split(","))
    combined_analyzers = ",".join(sorted(existing_analyzers))

    # Pick higher severity
    highest_sev = _get_higher_severity(primary.severity, secondary.severity)

    # Prefer the more descriptive message
    best_message = primary.message if len(primary.message) >= len(secondary.message) else secondary.message

    # Prefer non-empty code snippet
    snippet = primary.code_evidence or secondary.code_evidence

    return StaticFinding(
        id=primary.id,
        analyzer_name=combined_analyzers,
        rule_id=f"{primary.rule_id}/{secondary.rule_id}" if primary.rule_id != secondary.rule_id else primary.rule_id,
        category=primary.category,
        severity=highest_sev,
        message=best_message,
        line_number=primary.line_number or secondary.line_number,
        end_line=primary.end_line or secondary.end_line,
        code_evidence=snippet,
    )


def deduplicate_and_merge_static_findings(findings: List[StaticFinding]) -> List[StaticFinding]:
    """
    Deduplicate a list of static findings from multiple tools.
    Preserves unique findings while merging corroborated issues.
    """
    if not findings:
        return []

    merged_findings: List[StaticFinding] = []

    for finding in findings:
        matched_idx: Optional[int] = None
        for idx, existing in enumerate(merged_findings):
            if _are_findings_duplicates(existing, finding):
                matched_idx = idx
                break

        if matched_idx is not None:
            # Merge with existing
            merged_findings[matched_idx] = merge_two_findings(merged_findings[matched_idx], finding)
        else:
            merged_findings.append(finding)

    # Sort deterministically by line number then severity
    def sort_key(f: StaticFinding):
        sev_rank = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }.get(f.severity, 5)
        return (f.line_number or 0, sev_rank)

    merged_findings.sort(key=sort_key)
    return merged_findings
