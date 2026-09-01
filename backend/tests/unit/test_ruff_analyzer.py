"""Unit tests for RuffAnalyzer adapter (availability, JSON parsing, mapping, failure isolation)."""

from unittest.mock import AsyncMock, patch
import pytest
from backend.app.analyzers.ruff_analyzer import RuffAnalyzer
from backend.app.analyzers.safe_process import SafeProcessResult
from backend.app.core.config import Settings
from backend.app.models.domain import SourceFile
from backend.app.models.enums import Category, Language, Severity


@pytest.fixture
def ruff_analyzer() -> RuffAnalyzer:
    settings = Settings(ENABLE_RUFF=True, STATIC_ANALYZER_TIMEOUT=5)
    return RuffAnalyzer(settings=settings)


@pytest.mark.asyncio
async def test_ruff_disabled_returns_empty():
    settings = Settings(ENABLE_RUFF=False)
    analyzer = RuffAnalyzer(settings=settings)
    sf = SourceFile(content="import os", language=Language.PYTHON)
    findings = await analyzer.analyze(sf)
    assert findings == []


@pytest.mark.asyncio
async def test_ruff_json_output_parsing(ruff_analyzer: RuffAnalyzer):
    mock_json = """
    [
        {
            "code": "F401",
            "message": "'os' imported but unused",
            "location": {"row": 1, "column": 1},
            "end_location": {"row": 1, "column": 10},
            "filename": "submission.py"
        },
        {
            "code": "E501",
            "message": "Line too long (120 > 100)",
            "location": {"row": 5, "column": 1},
            "end_location": {"row": 5, "column": 120},
            "filename": "submission.py"
        }
    ]
    """
    mock_process_result = SafeProcessResult(
        exit_code=1,
        stdout=mock_json,
        stderr="",
        duration_ms=12.0,
        timed_out=False,
    )

    with patch("backend.app.analyzers.ruff_analyzer.run_tool_safely", new=AsyncMock(return_value=(mock_process_result, None))):
        with patch.object(ruff_analyzer, "is_available", return_value=True):
            sf = SourceFile(content="import os\n\n\n\nline = 'long' * 50\n", language=Language.PYTHON)
            findings = await ruff_analyzer.analyze(sf)

            assert len(findings) == 2
            f1 = next(f for f in findings if f.rule_id == "F401")
            assert f1.category == Category.BUG
            assert f1.severity == Severity.MEDIUM
            assert f1.line_number == 1

            f2 = next(f for f in findings if f.rule_id == "E501")
            assert f2.category == Category.STYLE
            assert f2.severity == Severity.LOW
            assert f2.line_number == 5


@pytest.mark.asyncio
async def test_ruff_timeout_handling(ruff_analyzer: RuffAnalyzer):
    mock_timeout_result = SafeProcessResult(
        exit_code=-1,
        stdout="",
        stderr="Process timed out",
        duration_ms=5000.0,
        timed_out=True,
    )

    with patch("backend.app.analyzers.ruff_analyzer.run_tool_safely", new=AsyncMock(return_value=(mock_timeout_result, None))):
        with patch.object(ruff_analyzer, "is_available", return_value=True):
            sf = SourceFile(content="print('timeout')", language=Language.PYTHON)
            findings = await ruff_analyzer.analyze(sf)
            assert findings == []
