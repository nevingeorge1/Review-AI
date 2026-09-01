"""Security tests verifying that submitted source code is strictly treated as static DATA and NEVER executed."""

import os
import tempfile
import pytest
from backend.app.preprocessing.python_preprocessor import PythonPreprocessor


@pytest.fixture
def preprocessor() -> PythonPreprocessor:
    return PythonPreprocessor()


def test_malicious_code_never_executes_filesystem_side_effects(preprocessor: PythonPreprocessor):
    """
    Verify that submitted source code attempting to create or delete files
    is parsed statically without triggering side effects.
    """
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        temp_path = tf.name

    try:
        assert os.path.exists(temp_path)

        # Dangerous code string that would delete the file IF executed
        malicious_code = (
            "import os\n"
            f"os.remove({repr(temp_path)})\n"
            "def malicious_fn():\n"
            f"    os.system('echo dangerous > {temp_path}')\n"
        )

        # Parse with preprocessor
        result = preprocessor.analyze_source(malicious_code)

        # Verification: File MUST still exist because code was NEVER executed
        assert os.path.exists(temp_path), "CRITICAL SECURITY BREACH: Submitted code was executed!"
        assert result.success is True
        assert len(result.context.interesting_signals) >= 2
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_malicious_eval_and_exec_never_run(preprocessor: PythonPreprocessor):
    """Verify eval and exec in submitted code are detected as signals without running."""
    dangerous_code = (
        "eval('__import__(\"sys\").exit(1)')\n"
        "exec('open(\"hacked.txt\", \"w\").write(\"danger\")')\n"
    )
    result = preprocessor.analyze_source(dangerous_code)
    assert result.success is True
    signals = result.context.interesting_signals
    assert len(signals) == 2
    assert all(s.category == "code_execution" for s in signals)
    assert not os.path.exists("hacked.txt"), "CRITICAL: exec() was run during analysis!"
