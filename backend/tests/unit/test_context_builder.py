"""Unit tests for ReviewContextBuilder and context determinism."""

from backend.app.analyzers.models import StaticAnalysisResult, StaticSummaryCounts
from backend.app.llm.context import CONTEXT_SCHEMA_VERSION, ReviewContextBuilder
from backend.app.models.domain import SourceFile, StaticFinding
from backend.app.models.enums import Category, Language, Severity
from backend.app.preprocessing.python_preprocessor import PythonPreprocessor


def test_context_builder_complete_flow():
    code = (
        "import os\n"
        "class Worker:\n"
        "    def run(self, cmd: str) -> None:\n"
        "        eval(cmd)\n"
    )
    sf = SourceFile(content=code, language=Language.PYTHON, filename="worker.py", line_count=4, byte_size=len(code))

    prep = PythonPreprocessor()
    prep_res = prep.analyze_source(code, filename="worker.py")

    static_finding = StaticFinding(
        analyzer_name="ast_rules",
        rule_id="RULE-001",
        category=Category.SECURITY,
        severity=Severity.HIGH,
        message="Direct invocation of eval() detected.",
        line_number=4,
    )
    static_res = StaticAnalysisResult(
        success=True,
        findings=[static_finding],
        analyzers_run=["ast_rules"],
        summary=StaticSummaryCounts(total=1, high=1),
    )

    builder = ReviewContextBuilder()
    ctx = builder.build_context(
        source_file=sf,
        preprocessing_result=prep_res,
        static_analysis_result=static_res,
        developer_notes="Critical service worker module.",
    )

    assert ctx.schema_version == CONTEXT_SCHEMA_VERSION
    assert ctx.source.filename == "worker.py"
    assert ctx.structure.class_count == 1
    assert "Worker" in ctx.structure.class_names
    assert len(ctx.structure.function_signatures) == 1
    assert len(ctx.static_evidence) == 1
    assert ctx.static_evidence[0].rule_id == "RULE-001"
    assert ctx.developer_notes == "Critical service worker module."


def test_context_builder_determinism():
    """Verify context construction is 100% deterministic across multiple runs."""
    code = "def add(a: int, b: int) -> int: return a + b\n"
    sf = SourceFile(content=code, language=Language.PYTHON, filename="math.py", line_count=1, byte_size=len(code))

    builder = ReviewContextBuilder()
    ctx1 = builder.build_context(source_file=sf).model_dump()
    ctx2 = builder.build_context(source_file=sf).model_dump()
    assert ctx1 == ctx2
