"""Finding Fusion and Multi-Source Evidence Correlation Layer.

Intelligently combines deterministic static findings (Ruff, Bandit, AST rules) with
contextual LLM insights, elevates corroborated issues to DetectionSource.HYBRID,
resolves severity conflicts safely, and preserves full multi-tool provenance.
"""

import uuid
from typing import List, Optional, Set, Tuple

from backend.app.models.domain import Evidence, ReviewFinding, StaticFinding
from backend.app.models.enums import Category, DetectionSource, Severity

# Semantic keywords for correlating static checks with LLM reasoning
SEMANTIC_CORRELATION_KEYWORDS = [
    "eval",
    "exec",
    "system",
    "subprocess",
    "pickle",
    "yaml",
    "sql",
    "injection",
    "password",
    "credential",
    "secret",
    "token",
    "except",
    "bare except",
    "mutable",
    "default argument",
    "complexity",
    "nesting",
    "parameter",
    "loop",
    "quadratic",
    "performance",
]


def _get_higher_severity(s1: Severity, s2: Severity) -> Severity:
    """Return the higher severity level between two options."""
    order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    idx1 = order.index(s1) if s1 in order else 99
    idx2 = order.index(s2) if s2 in order else 99
    return s1 if idx1 <= idx2 else s2


def _classify_confidence_level(score: float) -> str:
    """Classify numerical confidence into human-readable level."""
    if score >= 0.85:
        return "HIGH"
    elif score >= 0.70:
        return "MEDIUM"
    return "LOW"


def _are_findings_corroborated(static_f: ReviewFinding, llm_f: ReviewFinding) -> bool:
    """
    Determine if a static finding and an LLM finding describe the same underlying issue.
    Criteria:
    1. Same category (e.g. both SECURITY or both BUG).
    2. Line proximity: |line1 - line2| <= 2 (or both have no line).
    3. Keyword / semantic intent overlap.
    """
    if static_f.category != llm_f.category:
        return False

    # Check line proximity
    if static_f.line_number is not None and llm_f.line_number is not None:
        if abs(static_f.line_number - llm_f.line_number) > 2:
            return False
    elif static_f.line_number != llm_f.line_number:
        # One has line, one does not -> only match if strong keyword overlap
        pass

    # Keyword overlap in titles, rule IDs, and descriptions
    static_text = f"{static_f.rule_id} {static_f.title} {static_f.description}".lower()
    llm_text = f"{llm_f.title} {llm_f.description} {llm_f.explanation}".lower()

    for kw in SEMANTIC_CORRELATION_KEYWORDS:
        if kw in static_text and kw in llm_text:
            return True

    return False


class FindingFusion:
    """Fuses multi-tool static findings and LLM reasoning into unified, evidence-rich review findings."""

    def fuse_findings(
        self,
        static_findings: List[StaticFinding],
        llm_findings: List[ReviewFinding],
    ) -> List[ReviewFinding]:
        """
        Merge static evidence and LLM findings with provenance preservation and severity conflict resolution.
        """
        # 1. Convert raw StaticFinding entities into baseline ReviewFinding records
        converted_static: List[ReviewFinding] = []
        for sf in static_findings:
            tools = [t.strip() for t in sf.analyzer_name.split(",") if t.strip()]
            converted_static.append(
                ReviewFinding(
                    id=sf.id,
                    category=sf.category,
                    severity=sf.severity,
                    title=f"[{sf.rule_id}] {sf.message[:100]}",
                    description=sf.message,
                    line_number=sf.line_number,
                    end_line=sf.end_line,
                    code_evidence=sf.code_evidence,
                    explanation=f"Identified by deterministic static analyzer(s): {', '.join(tools)}.",
                    recommendation="Review code structure against security and style guidelines.",
                    confidence=0.90,
                    confidence_level="HIGH",
                    detection_source=DetectionSource.STATIC_ANALYSIS,
                    detected_by=tools,
                    rule_id=sf.rule_id,
                    rule_ids=[sf.rule_id] if sf.rule_id else [],
                    supporting_evidence=[
                        Evidence(
                            source_tool=sf.analyzer_name,
                            rule_id=sf.rule_id,
                            line_number=sf.line_number,
                            end_line=sf.end_line,
                            snippet=sf.code_evidence,
                            raw_message=sf.message,
                        )
                    ],
                )
            )

        # 2. Correlate Static and LLM Findings
        matched_llm_indices: Set[int] = set()
        fused_findings: List[ReviewFinding] = []

        for s_finding in converted_static:
            matched_llm_idx: Optional[int] = None
            for idx, l_finding in enumerate(llm_findings):
                if idx not in matched_llm_indices and _are_findings_corroborated(s_finding, l_finding):
                    matched_llm_idx = idx
                    break

            if matched_llm_idx is not None:
                matched_llm_indices.add(matched_llm_idx)
                l_finding = llm_findings[matched_llm_idx]

                # Merge into HYBRID finding
                all_tools = sorted(list(set(s_finding.detected_by + ["llm"])))
                all_rules = sorted(list(set(s_finding.rule_ids + ([l_finding.rule_id] if l_finding.rule_id else []))))

                # Severity Resolution Policy:
                # Retain higher severity (static security evidence cannot be downgraded)
                resolved_severity = _get_higher_severity(s_finding.severity, l_finding.severity)

                # Confidence elevation for multi-source agreement
                hybrid_confidence = min(0.98, max(s_finding.confidence, l_finding.confidence) + 0.05)

                # Combine supporting evidence
                combined_evidence = list(s_finding.supporting_evidence)
                if l_finding.explanation:
                    combined_evidence.append(
                        Evidence(
                            source_tool="llm",
                            rule_id=None,
                            line_number=l_finding.line_number,
                            end_line=l_finding.end_line,
                            snippet=l_finding.code_evidence,
                            raw_message=l_finding.explanation,
                        )
                    )

                fused = ReviewFinding(
                    id=s_finding.id,
                    category=s_finding.category,
                    severity=resolved_severity,
                    title=l_finding.title or s_finding.title,
                    description=l_finding.description or s_finding.description,
                    line_number=s_finding.line_number or l_finding.line_number,
                    end_line=s_finding.end_line or l_finding.end_line,
                    code_evidence=s_finding.code_evidence or l_finding.code_evidence,
                    explanation=l_finding.explanation or s_finding.explanation,
                    recommendation=l_finding.recommendation or s_finding.recommendation,
                    suggested_fix=l_finding.suggested_fix or s_finding.suggested_fix,
                    confidence=round(hybrid_confidence, 2),
                    confidence_level="HIGH",
                    detection_source=DetectionSource.HYBRID,
                    detected_by=all_tools,
                    rule_id=s_finding.rule_id,
                    rule_ids=all_rules,
                    supporting_evidence=combined_evidence,
                )
                fused_findings.append(fused)
            else:
                # Unmatched static finding remains as STATIC_ANALYSIS
                fused_findings.append(s_finding)

        # 3. Add remaining unmatched LLM findings
        for idx, l_finding in enumerate(llm_findings):
            if idx not in matched_llm_indices:
                conf = l_finding.confidence or 0.85
                l_finding.confidence_level = _classify_confidence_level(conf)
                l_finding.detected_by = ["llm"]
                fused_findings.append(l_finding)

        return fused_findings
