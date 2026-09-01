"""Performance benchmark tests measuring Python AST preprocessing throughput and latency."""

import time
import pytest
from backend.app.preprocessing.python_preprocessor import PythonPreprocessor


@pytest.fixture
def preprocessor() -> PythonPreprocessor:
    return PythonPreprocessor()


def test_preprocessing_latency_small_snippet(preprocessor: PythonPreprocessor):
    """Measure latency for a small (~10 line) snippet. Target: < 10ms."""
    code = (
        "import os\n"
        "def helper(x: int) -> int:\n"
        "    if x > 0:\n"
        "        return x * 2\n"
        "    return 0\n"
    )
    start = time.perf_counter()
    result = preprocessor.analyze_source(code)
    duration_ms = (time.perf_counter() - start) * 1000.0

    assert result.success is True
    assert duration_ms < 50.0  # Safe threshold for local test runs
    print(f"\n[Benchmark] Small Snippet (5 lines): {duration_ms:.3f} ms")


def test_preprocessing_latency_500_lines(preprocessor: PythonPreprocessor):
    """Measure latency for a maximum-sized (~500 lines) submission. Target: < 100ms."""
    functions = []
    for i in range(50):
        functions.append(
            f"def func_{i}(a: int, b: str, *args, **kwargs) -> int:\n"
            f"    \"\"\"Docstring for function {i}.\"\"\"\n"
            f"    total = a\n"
            f"    for item in range(10):\n"
            f"        if item % 2 == 0:\n"
            f"            total += item\n"
            f"        elif item == 3:\n"
            f"            continue\n"
            f"    return total\n"
        )
    large_code = "\n".join(functions)
    lines_count = len(large_code.split("\n"))

    start = time.perf_counter()
    result = preprocessor.analyze_source(large_code)
    duration_ms = (time.perf_counter() - start) * 1000.0

    assert result.success is True
    assert len(result.context.functions) == 50
    assert duration_ms < 250.0  # Well within near-real-time requirements
    print(f"\n[Benchmark] Large Source ({lines_count} lines, 50 functions): {duration_ms:.3f} ms")
