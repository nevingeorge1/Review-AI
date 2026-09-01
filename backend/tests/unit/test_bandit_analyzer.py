"""Unit tests for BanditAnalyzer adapter (availability, JSON parsing, severity mapping, timeout)."""

from unittest.mock import AsyncMock, patch
import pytest
from backend.app.analyzers.bandit_analyzer import BanditAnalyzer
from backend.app.analyzers.safe_process import SafeProcessResult
from backend.app.core.config import Settings
from backend.app.models.domain import SourceFile
from backend.app.models.enums import Category, Language, Severity


@pytest.fixture
def bandit_analyzer() -> BanditAnalyzer:
    settings = Settings(ENABLE_BANDIT=True, STATIC_ANALYZER_TIMEOUT=5)
    return BanditAnalyzer(settings=settings)


@pytest.mark.asyncio
async def test_bandit_disabled_returns_empty():
    settings = Settings(ENABLE_BANDIT=False)
    analyzer = BanditAnalyzer(settings=settings)
    sf = SourceFile(content="import os", language=Language.PYTHON)
    findings = await analyzer.analyze(sf)
    assert findings == []


@pytest.mark.asyncio
async def test_bandit_json_output_parsing(bandit_analyzer: BanditAnalyzer):
    mock_json = """
    {
        "results": [
            {
                "test_id": "B605",
                "issue_text": "Starting a process with a shell: possible injection vulnerability.",
                "issue_severity": "HIGH",
                "issue_confidence": "HIGH",
                "line_number": 3,
                "line_range": [3],
                "code": "os.system('ls')"
            },
            {
                "test_id": "B105",
                "issue_text": "Possible hardcoded password: 'secret'",
                "issue_severity": "LOW",
                "issue_confidence": "MEDIUM",
                "line_number": 1,
                "line_range": [1],
                "code": "password = 'secret'"
            }
        ]
    }
    """
    mock_process_result = SafeProcessResult(
        exit_code=1,
        stdout=mock_json,
        stderr="",
        duration_ms=45.0,
        timed_out=False,
    )

    with patch("backend.app.analyzers.bandit_analyzer.run_tool_safely", new=AsyncMock(return_value=(mock_process_result, None))):
        with patch.object(bandit_analyzer, "is_available", return_value=True):
            sf = SourceFile(content="password = 'secret'\nimport os\nos.system('ls')\n", language=Language.PYTHON)
            findings = await bandit_analyzer.analyze(sf)

            assert len(findings) == 2
            f1 = next(f for f in findings if f.rule_id == "B605")
            assert f1.category == Category.SECURITY
            assert f1.severity == Severity.HIGH
            assert f1.line_number == 3

            f2 = next(f for f in findings if f.rule_id == "B105")
            assert f2.category == Category.SECURITY
            assert f2.severity == Severity.LOW
            assert f2.line_number == 1


@pytest.mark.asyncio
async def test_bandit_timeout_handling(bandit_analyzer: BanditAnalyzer):
    mock_timeout_result = SafeProcessResult(
        exit_code=-1,
        stdout="",
        stderr="Process timed out",
        duration_ms=5000.0,
        timed_out=True,
    )

    with patch("backend.app.analyzers.bandit_analyzer.run_tool_safely", new=AsyncMock(return_value=(mock_timeout_result, None))):
        with patch.object(bandit_analyzer, "is_available", return_value=True):
            sf = SourceFile(content="print('timeout')", language=Language.PYTHON)
            findings = await bandit_analyzer.analyze(sf)
            assert findings == []
