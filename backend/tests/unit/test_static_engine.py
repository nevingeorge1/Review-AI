"""Integration tests for StaticAnalysisEngine (composite orchestration, failure isolation, summary counts)."""

import pytest
from backend.app.analyzers.composite import StaticAnalysisEngine
from backend.app.core.config import Settings
from backend.app.models.domain import SourceFile
from backend.app.models.enums import Category, Language, Severity
from backend.app.preprocessing.python_preprocessor import PythonPreprocessor


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        ENABLE_AST_RULES=True,
        ENABLE_RUFF=False,  # Isolated unit test
        ENABLE_BANDIT=False,  # Isolated unit test
        MAX_FUNCTION_COMPLEXITY=5,
    )


@pytest.fixture
def static_engine(test_settings: Settings) -> StaticAnalysisEngine:
    prep = PythonPreprocessor(settings=test_settings)
    return StaticAnalysisEngine(settings=test_settings, preprocessor=prep)


@pytest.mark.asyncio
async def test_static_engine_e2e_flow(static_engine: StaticAnalysisEngine):
    """Verify full pipeline from SourceFile to StaticAnalysisResult."""
    code = (
        "import os\n"
        "API_SECRET = 'sk_live_12345678901234567890'\n\n"
        "def run_command(cmd, items=[]):\n"
        "    eval(cmd)\n"
        "    os.system('echo ' + cmd)\n"
    )
    sf = SourceFile(content=code, language=Language.PYTHON, filename="vulnerable.py")

    result = await static_engine.analyze_source(sf)

    assert result.success is True
    assert "ast_rules" in result.analyzers_run
    assert len(result.findings) >= 3

    # Check summary counts
    assert result.summary.total == len(result.findings)
    assert result.summary.high >= 2  # eval, os.system, API_SECRET
    assert result.summary.by_category.get("security", 0) >= 2
    assert result.summary.by_category.get("bug", 0) >= 1  # mutable default items=[]


@pytest.mark.asyncio
async def test_static_engine_clean_source(static_engine: StaticAnalysisEngine):
    """Verify clean source produces 0 findings."""
    code = (
        "def add(x: int, y: int) -> int:\n"
        "    return x + y\n"
    )
    sf = SourceFile(content=code, language=Language.PYTHON, filename="clean.py")
    result = await static_engine.analyze_source(sf)

    assert result.success is True
    assert len(result.findings) == 0
    assert result.summary.total == 0
