"""Comprehensive unit tests for all 15 Custom AST Rules (Positive & Negative Cases)."""

import pytest
from backend.app.analyzers.ast_rules.rules import (
    Rule001Eval,
    Rule002Exec,
    Rule003DynamicImport,
    Rule004OsSystem,
    Rule005UnsafeSubprocess,
    Rule006UnsafePickle,
    Rule007BroadException,
    Rule008MutableDefaultArg,
    Rule009BareExcept,
    Rule010ExcessiveComplexity,
    Rule011ExcessiveNesting,
    Rule012TooManyParameters,
    Rule013HardcodedCredentials,
    Rule014SqlInjectionSignal,
    Rule015NestedLoopPerformance,
)
from backend.app.core.config import Settings
from backend.app.models.domain import SourceFile
from backend.app.models.enums import Category, Language, Severity
from backend.app.preprocessing.python_preprocessor import PythonPreprocessor


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        MAX_FUNCTION_COMPLEXITY=5,
        MAX_NESTING_DEPTH=3,
        MAX_FUNCTION_PARAMETERS=4,
    )


@pytest.fixture
def preprocessor(test_settings: Settings) -> PythonPreprocessor:
    return PythonPreprocessor(settings=test_settings)


def evaluate_rule(rule, code: str, preprocessor: PythonPreprocessor):
    sf = SourceFile(content=code, language=Language.PYTHON, filename="test.py")
    res = preprocessor.analyze_source(code, filename="test.py")
    assert res.syntax_valid is True, f"Code failed to parse: {res.syntax_error}"
    return rule.evaluate(source_file=sf, context=res.context)


class TestASTRules:
    """Test all 15 rules for precision and false-positive avoidance."""

    # RULE-001: eval
    def test_rule001_eval_positive(self, test_settings, preprocessor):
        rule = Rule001Eval(settings=test_settings)
        code = "def parse(x): return eval(x)"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 1
        assert findings[0].rule_id == "RULE-001"
        assert findings[0].category == Category.SECURITY

    def test_rule001_eval_negative(self, test_settings, preprocessor):
        rule = Rule001Eval(settings=test_settings)
        code = "def evaluate_score(score): return score * 2"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 0

    # RULE-002: exec
    def test_rule002_exec_positive(self, test_settings, preprocessor):
        rule = Rule002Exec(settings=test_settings)
        code = "def run(x): exec(x)"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 1
        assert findings[0].rule_id == "RULE-002"

    def test_rule002_exec_negative(self, test_settings, preprocessor):
        rule = Rule002Exec(settings=test_settings)
        code = "def execute_command(cmd): pass"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 0

    # RULE-003: __import__
    def test_rule003_dynamic_import_positive(self, test_settings, preprocessor):
        rule = Rule003DynamicImport(settings=test_settings)
        code = "mod = __import__('os')"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 1
        assert findings[0].rule_id == "RULE-003"

    def test_rule003_dynamic_import_negative(self, test_settings, preprocessor):
        rule = Rule003DynamicImport(settings=test_settings)
        code = "import os\nfrom pathlib import Path"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 0

    # RULE-004: os.system
    def test_rule004_os_system_positive(self, test_settings, preprocessor):
        rule = Rule004OsSystem(settings=test_settings)
        code = "import os\nos.system('ls ' + user_input)"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 1
        assert findings[0].rule_id == "RULE-004"

    def test_rule004_os_system_negative(self, test_settings, preprocessor):
        rule = Rule004OsSystem(settings=test_settings)
        code = "import os\npath = os.path.join('a', 'b')"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 0

    # RULE-005: subprocess
    def test_rule005_subprocess_shell_true_positive(self, test_settings, preprocessor):
        rule = Rule005UnsafeSubprocess(settings=test_settings)
        code = "import subprocess\nsubprocess.run('echo hello', shell=True)"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 1
        assert findings[0].rule_id == "RULE-005"
        assert findings[0].severity == Severity.HIGH

    def test_rule005_subprocess_safe_negative(self, test_settings, preprocessor):
        rule = Rule005UnsafeSubprocess(settings=test_settings)
        code = "import subprocess\nsubprocess.run(['echo', 'hello'], check=True)"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 0

    # RULE-006: pickle
    def test_rule006_pickle_positive(self, test_settings, preprocessor):
        rule = Rule006UnsafePickle(settings=test_settings)
        code = "import pickle\ndata = pickle.loads(raw_bytes)"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 1
        assert findings[0].rule_id == "RULE-006"

    def test_rule006_pickle_negative(self, test_settings, preprocessor):
        rule = Rule006UnsafePickle(settings=test_settings)
        code = "import json\ndata = json.loads(raw_text)"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 0

    # RULE-007: broad exception
    def test_rule007_broad_exception_positive(self, test_settings, preprocessor):
        rule = Rule007BroadException(settings=test_settings)
        code = "try:\n    x = 1 / 0\nexcept Exception:\n    pass"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 1
        assert findings[0].rule_id == "RULE-007"
        assert findings[0].category == Category.MAINTAINABILITY

    def test_rule007_broad_exception_negative(self, test_settings, preprocessor):
        rule = Rule007BroadException(settings=test_settings)
        code = "try:\n    x = 1 / 0\nexcept ZeroDivisionError:\n    pass"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 0

    # RULE-008: mutable default
    def test_rule008_mutable_default_positive(self, test_settings, preprocessor):
        rule = Rule008MutableDefaultArg(settings=test_settings)
        code = "def append_item(x, items=[]): items.append(x)"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 1
        assert findings[0].rule_id == "RULE-008"
        assert findings[0].category == Category.BUG

    def test_rule008_mutable_default_negative(self, test_settings, preprocessor):
        rule = Rule008MutableDefaultArg(settings=test_settings)
        code = "def append_item(x, items=None): items = items or []"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 0

    # RULE-009: bare except
    def test_rule009_bare_except_positive(self, test_settings, preprocessor):
        rule = Rule009BareExcept(settings=test_settings)
        code = "try:\n    do_something()\nexcept:\n    pass"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 1
        assert findings[0].rule_id == "RULE-009"

    def test_rule009_bare_except_negative(self, test_settings, preprocessor):
        rule = Rule009BareExcept(settings=test_settings)
        code = "try:\n    do_something()\nexcept ValueError:\n    pass"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 0

    # RULE-010: excessive complexity
    def test_rule010_complexity_positive(self, test_settings, preprocessor):
        rule = Rule010ExcessiveComplexity(settings=test_settings)
        # Threshold is set to 5 in fixture
        code = (
            "def complex_fn(a, b, c, d, e, f):\n"
            "    if a: pass\n"
            "    if b: pass\n"
            "    if c: pass\n"
            "    if d: pass\n"
            "    if e: pass\n"
            "    if f: pass\n"
        )
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 1
        assert findings[0].rule_id == "RULE-010"

    def test_rule010_complexity_negative(self, test_settings, preprocessor):
        rule = Rule010ExcessiveComplexity(settings=test_settings)
        code = "def simple_fn(x): return x + 1"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 0

    # RULE-011: excessive nesting
    def test_rule011_nesting_positive(self, test_settings, preprocessor):
        rule = Rule011ExcessiveNesting(settings=test_settings)
        # Threshold is set to 3 in fixture
        code = (
            "def deep_nested(data):\n"
            "    if data:\n"
            "        for row in data:\n"
            "            for item in row:\n"
            "                if item > 0:\n"
            "                    print(item)\n"
        )
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 1
        assert findings[0].rule_id == "RULE-011"

    def test_rule011_nesting_negative(self, test_settings, preprocessor):
        rule = Rule011ExcessiveNesting(settings=test_settings)
        code = "def shallow(data):\n    for item in data:\n        print(item)"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 0

    # RULE-012: too many parameters
    def test_rule012_parameters_positive(self, test_settings, preprocessor):
        rule = Rule012TooManyParameters(settings=test_settings)
        # Threshold is set to 4 in fixture
        code = "def func_with_many_params(a, b, c, d, e): pass"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 1
        assert findings[0].rule_id == "RULE-012"

    def test_rule012_parameters_negative(self, test_settings, preprocessor):
        rule = Rule012TooManyParameters(settings=test_settings)
        code = "def func_with_few_params(a, b): pass"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 0

    # RULE-013: hardcoded credentials
    def test_rule013_credentials_positive(self, test_settings, preprocessor):
        rule = Rule013HardcodedCredentials(settings=test_settings)
        code = "api_key = 'sk_live_99887766554433221100aabbcc'"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 1
        assert findings[0].rule_id == "RULE-013"

    def test_rule013_credentials_negative_placeholder(self, test_settings, preprocessor):
        rule = Rule013HardcodedCredentials(settings=test_settings)
        code = "api_key = os.getenv('API_KEY', 'placeholder')"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 0

    # RULE-014: SQL injection
    def test_rule014_sql_injection_positive(self, test_settings, preprocessor):
        rule = Rule014SqlInjectionSignal(settings=test_settings)
        code = "cursor.execute('SELECT * FROM users WHERE name = ' + user_input)"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 1
        assert findings[0].rule_id == "RULE-014"

    def test_rule014_sql_injection_negative(self, test_settings, preprocessor):
        rule = Rule014SqlInjectionSignal(settings=test_settings)
        code = "cursor.execute('SELECT * FROM users WHERE name = %s', (user_input,))"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 0

    # RULE-015: nested loops
    def test_rule015_nested_loops_positive(self, test_settings, preprocessor):
        rule = Rule015NestedLoopPerformance(settings=test_settings)
        code = "for a in list1:\n    for b in list2:\n        if a == b: pass"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 1
        assert findings[0].rule_id == "RULE-015"
        assert findings[0].category == Category.PERFORMANCE

    def test_rule015_nested_loops_negative(self, test_settings, preprocessor):
        rule = Rule015NestedLoopPerformance(settings=test_settings)
        code = "for a in list1: pass\nfor b in list2: pass"
        findings = evaluate_rule(rule, code, preprocessor)
        assert len(findings) == 0
