"""Unit tests for LLMOutputParser (markdown stripping, defensive line clamping, invalid JSON)."""

import pytest
from backend.app.core.errors import InvalidStructuredOutputError
from backend.app.llm.parser import LLMOutputParser
from backend.app.models.enums import Category, Severity


@pytest.fixture
def parser() -> LLMOutputParser:
    return LLMOutputParser()


def test_parser_with_markdown_fences(parser: LLMOutputParser):
    raw_markdown = """
    Here is the review result:
    ```json
    {
        "executive_summary": "Solid implementation with no major flaws.",
        "findings": [
            {
                "category": "style",
                "severity": "info",
                "title": "Variable naming consistency",
                "description": "Consider using snake_case for local variables.",
                "line_number": 2,
                "end_line": 2
            }
        ]
    }
    ```
    I hope this helps!
    """
    summary, findings = parser.parse_and_validate(raw_markdown, total_source_lines=10)
    assert summary == "Solid implementation with no major flaws."
    assert len(findings) == 1
    f = findings[0]
    assert f.category == Category.STYLE
    assert f.severity == Severity.INFO
    assert f.line_number == 2


def test_parser_defensive_line_clamping(parser: LLMOutputParser):
    """Verify lines outside source bounds (e.g. line 999 for a 10-line file) are safely omitted."""
    raw_json = """
    {
        "executive_summary": "Summary",
        "findings": [
            {
                "category": "bug",
                "severity": "high",
                "title": "Out of range finding",
                "description": "Hallucinated line number.",
                "line_number": 999,
                "end_line": 1000
            },
            {
                "category": "security",
                "severity": "high",
                "title": "Valid finding",
                "description": "Valid line number.",
                "line_number": 5,
                "end_line": 6
            }
        ]
    }
    """
    summary, findings = parser.parse_and_validate(raw_json, total_source_lines=10)
    assert len(findings) == 2
    # First finding line should be omitted
    assert findings[0].line_number is None
    # Second finding line should be preserved
    assert findings[1].line_number == 5


def test_parser_empty_response_raises(parser: LLMOutputParser):
    with pytest.raises(InvalidStructuredOutputError):
        parser.parse_and_validate("   ", total_source_lines=10)


def test_parser_invalid_json_raises(parser: LLMOutputParser):
    with pytest.raises(InvalidStructuredOutputError):
        parser.parse_and_validate("This is not valid json { broken", total_source_lines=10)
