"""Performance benchmark tests measuring static analysis latency across representative code sizes."""

import time
import pytest
from backend.app.analyzers.composite import StaticAnalysisEngine
from backend.app.core.config import Settings
from backend.app.models.domain import SourceFile
from backend.app.models.enums import Language
from backend.app.preprocessing.python_preprocessor import PythonPreprocessor


@pytest.fixture
def static_engine() -> StaticAnalysisEngine:
    settings = Settings(ENABLE_AST_RULES=True, ENABLE_RUFF=False, ENABLE_BANDIT=False)
    prep = PythonPreprocessor(settings=settings)
    return StaticAnalysisEngine(settings=settings, preprocessor=prep)


@pytest.mark.asyncio
async def test_static_engine_latency_small(static_engine: StaticAnalysisEngine):
    """Benchmark AST static analysis on small ~15-line code snippet. Target: < 20ms."""
    code = (
        "import os\n"
        "def process(cmd, config={}):\n"
        "    if cmd:\n"
        "        os.system(cmd)\n"
        "    return config\n"
    )
    sf = SourceFile(content=code, language=Language.PYTHON, filename="bench_small.py")

    start = time.perf_counter()
    result = await static_engine.analyze_source(sf)
    duration_ms = (time.perf_counter() - start) * 1000.0

    assert result.success is True
    assert duration_ms < 50.0
    print(f"\n[Benchmark] Small Snippet Static Analysis: {duration_ms:.3f} ms (Findings: {len(result.findings)})")


@pytest.mark.asyncio
async def test_static_engine_latency_500_lines(static_engine: StaticAnalysisEngine):
    """Benchmark AST static analysis on maximum 500-line submission. Target: < 150ms."""
    snippets = []
    for i in range(50):
        snippets.append(
            f"def func_{i}(arg_a, arg_b, items=[]):\n"
            f"    \"\"\"Function {i} docstring.\"\"\"\n"
            f"    if arg_a > 10:\n"
            f"        for item in items:\n"
            f"            if item == arg_b:\n"
            f"                return item\n"
            f"    return None\n"
        )
    large_code = "\n".join(snippets)
    lines_count = len(large_code.split("\n"))

    sf = SourceFile(content=large_code, language=Language.PYTHON, filename="bench_large.py")

    start = time.perf_counter()
    result = await static_engine.analyze_source(sf)
    duration_ms = (time.perf_counter() - start) * 1000.0

    assert result.success is True
    assert duration_ms < 300.0
    print(f"\n[Benchmark] 500-Line Static Analysis ({lines_count} lines, 50 functions): {duration_ms:.3f} ms (Findings: {len(result.findings)})")
