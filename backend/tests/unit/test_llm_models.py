"""Unit tests for LLM data models, DTOs, and field validators."""

from backend.app.llm.models import (
    LLMRawFinding,
    LLMRawResponsePayload,
    LLMReviewResult,
    LLMSuggestedFix,
)
from backend.app.models.enums import Category, DetectionSource, Severity


def test_raw_finding_enum_normalization():
    """Verify that case-insensitive category and severity strings are normalized safely."""
    raw = LLMRawFinding(
        category="sEcUrItY",  # type: ignore
        severity="hIgH",  # type: ignore
        title="SQL Injection",
        description="Dynamic string formatting in query.",
        confidence=1.5,  # Should clamp to 1.0
    )
    assert raw.category == Category.SECURITY
    assert raw.severity == Severity.HIGH
    assert raw.confidence == 1.0


def test_raw_finding_fallback_on_unknown_enums():
    """Verify unknown category/severity defaults to BUG / MEDIUM without crashing."""
    raw = LLMRawFinding(
        category="unknown_category",  # type: ignore
        severity="apocalyptic",  # type: ignore
        title="Unknown Issue",
        description="Something happened.",
        confidence=-0.5,  # Should clamp to 0.0
    )
    assert raw.category == Category.BUG
    assert raw.severity == Severity.MEDIUM
    assert raw.confidence == 0.0


def test_raw_response_payload_parsing():
    """Verify full payload parsing into structured findings."""
    payload_dict = {
        "executive_summary": "Clean code with one minor performance concern.",
        "findings": [
            {
                "category": "performance",
                "severity": "low",
                "title": "Use list comprehension instead of loop",
                "description": "Building lists iteratively in for-loop can be optimized.",
                "line_number": 10,
                "end_line": 12,
                "confidence": 0.85,
                "suggested_fix": {
                    "original_snippet": "res = []\nfor x in items: res.append(x*2)",
                    "replacement_snippet": "res = [x * 2 for x in items]",
                    "explanation": "List comprehensions are vectorized in Python C-layer."
                }
            }
        ]
    }
    payload = LLMRawResponsePayload.model_validate(payload_dict)
    assert payload.executive_summary.startswith("Clean code")
    assert len(payload.findings) == 1
    f = payload.findings[0]
    assert f.category == Category.PERFORMANCE
    assert f.suggested_fix is not None
    assert "List comprehensions" in f.suggested_fix.explanation
