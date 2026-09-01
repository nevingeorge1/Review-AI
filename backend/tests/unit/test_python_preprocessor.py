"""Unit tests for PythonPreprocessor and AST intelligence extraction."""

import pytest
from backend.app.core.errors import InvalidSourceCodeError, SourceCodeTooLargeError
from backend.app.models.enums import Language
from backend.app.preprocessing.models import PreprocessingResult
from backend.app.preprocessing.python_preprocessor import PythonPreprocessor


@pytest.fixture
def preprocessor() -> PythonPreprocessor:
    return PythonPreprocessor()


class TestPythonPreprocessor:
    """Comprehensive test suite for AST structural extraction and metrics."""

    def test_valid_simple_code(self, preprocessor: PythonPreprocessor):
        code = "def hello():\n    return 'world'\n"
        result = preprocessor.analyze_source(code)
        assert result.success is True
        assert result.syntax_valid is True
        assert result.context is not None
        assert len(result.context.functions) == 1
        assert result.context.functions[0].name == "hello"
        assert result.context.metrics.logical_lines == 2

    def test_empty_code_rejection(self, preprocessor: PythonPreprocessor):
        with pytest.raises(InvalidSourceCodeError):
            preprocessor.analyze_source("   \n\t  ")

    def test_syntax_error_handling(self, preprocessor: PythonPreprocessor):
        code = "def broken(\n    return 42"
        result = preprocessor.analyze_source(code)
        assert result.success is False
        assert result.syntax_valid is False
        assert result.syntax_error is not None
        assert result.syntax_error.line is not None
        assert len(result.warnings) > 0

    def test_incomplete_code_graceful_response(self, preprocessor: PythonPreprocessor):
        code = "if x > 10:"
        result = preprocessor.analyze_source(code)
        assert result.success is False
        assert result.syntax_valid is False
        assert "expected an indented block" in result.syntax_error.message.lower() or "syntax" in result.syntax_error.message.lower()

    def test_import_extraction(self, preprocessor: PythonPreprocessor):
        code = (
            "import os\n"
            "import sys as system_lib\n"
            "from pathlib import Path, PurePath\n"
        )
        result = preprocessor.analyze_source(code)
        assert result.success is True
        imports = result.context.imports
        assert len(imports) == 4

        os_imp = next(i for i in imports if i.name == "os")
        assert os_imp.is_from_import is False

        sys_imp = next(i for i in imports if i.name == "sys")
        assert sys_imp.alias == "system_lib"

        path_imp = next(i for i in imports if i.name == "Path")
        assert path_imp.module == "pathlib"
        assert path_imp.is_from_import is True

    def test_function_and_parameter_extraction(self, preprocessor: PythonPreprocessor):
        code = (
            "@decorator_one\n"
            "@module.decorator_two\n"
            "def compute(a: int, b: str = 'default', *args, key_only: bool = True, **kwargs) -> int:\n"
            "    \"\"\"Compute docstring.\"\"\"\n"
            "    return a + len(b)\n"
        )
        result = preprocessor.analyze_source(code)
        assert result.success is True
        funcs = result.context.functions
        assert len(funcs) == 1
        fn = funcs[0]

        assert fn.name == "compute"
        assert fn.is_async is False
        assert fn.has_docstring is True
        assert "Compute docstring." in fn.docstring
        assert len(fn.decorators) == 2
        assert fn.parameter_count == 5
        assert fn.return_annotation == "int"

        param_names = [p.name for p in fn.parameters]
        assert param_names == ["a", "b", "args", "key_only", "kwargs"]

        vararg = next(p for p in fn.parameters if p.name == "args")
        assert vararg.is_args is True

        kwarg = next(p for p in fn.parameters if p.name == "kwargs")
        assert kwarg.is_kwargs is True

        kwonly = next(p for p in fn.parameters if p.name == "key_only")
        assert kwonly.is_keyword_only is True

    def test_async_function_extraction(self, preprocessor: PythonPreprocessor):
        code = (
            "async def fetch_data(url: str):\n"
            "    await helper()\n"
            "    return True\n"
        )
        result = preprocessor.analyze_source(code)
        assert result.success is True
        fn = result.context.functions[0]
        assert fn.name == "fetch_data"
        assert fn.is_async is True

    def test_class_extraction(self, preprocessor: PythonPreprocessor):
        code = (
            "class MyService(BaseService, Mixin):\n"
            "    \"\"\"Service docstring.\"\"\"\n"
            "    def method_one(self):\n"
            "        pass\n"
            "    async def method_two(self):\n"
            "        pass\n"
        )
        result = preprocessor.analyze_source(code)
        assert result.success is True
        classes = result.context.classes
        assert len(classes) == 1
        cls = classes[0]

        assert cls.name == "MyService"
        assert cls.base_classes == ["BaseService", "Mixin"]
        assert cls.has_docstring is True
        assert cls.method_count == 2
        assert "method_one" in cls.methods
        assert "method_two" in cls.methods

        # Verify parent_class in function records
        m1 = next(f for f in result.context.functions if f.name == "method_one")
        assert m1.parent_class == "MyService"

    def test_variable_extraction(self, preprocessor: PythonPreprocessor):
        code = (
            "GLOBAL_VAR = 100\n"
            "annotated_var: str = 'hello'\n"
            "GLOBAL_VAR += 1\n"
        )
        result = preprocessor.analyze_source(code)
        assert result.success is True
        vars_found = result.context.variables
        assert len(vars_found) == 3
        types = [v.assignment_type for v in vars_found]
        assert "Assign" in types
        assert "AnnAssign" in types
        assert "AugAssign" in types

    def test_function_call_and_attribute_chain_extraction(self, preprocessor: PythonPreprocessor):
        code = (
            "result = calculate(1, 2, mode='fast')\n"
            "os.path.join('a', 'b')\n"
        )
        result = preprocessor.analyze_source(code)
        assert result.success is True
        calls = result.context.calls
        assert len(calls) == 2

        c1 = calls[0]
        assert c1.name == "calculate"
        assert c1.arg_count == 2
        assert "mode" in c1.keyword_args

        c2 = calls[1]
        assert c2.full_attribute_chain == "os.path.join"

    def test_control_flow_and_nesting_depth(self, preprocessor: PythonPreprocessor):
        code = (
            "def nested_logic(data):\n"
            "    if data:\n"
            "        for item in data:\n"
            "            while item > 0:\n"
            "                try:\n"
            "                    if item == 5:\n"
            "                        break\n"
            "                except Exception:\n"
            "                    continue\n"
        )
        result = preprocessor.analyze_source(code)
        assert result.success is True
        cf = result.context.control_flow
        assert cf.if_count == 2
        assert cf.for_count == 1
        assert cf.while_count == 1
        assert cf.try_count == 1
        assert cf.except_count == 1
        assert cf.break_count == 1
        assert cf.continue_count == 1
        assert cf.max_nesting_depth >= 4

    def test_cyclomatic_complexity_calculation(self, preprocessor: PythonPreprocessor):
        # Function with 3 branches -> complexity = 1 (base) + 2 (if/elif) + 1 (for) = 4
        code = (
            "def branchy(x, items):\n"
            "    if x > 10:\n"
            "        return True\n"
            "    elif x < 0:\n"
            "        return False\n"
            "    for i in items:\n"
            "        pass\n"
            "    return True\n"
        )
        result = preprocessor.analyze_source(code)
        assert result.success is True
        fn = result.context.functions[0]
        assert fn.metrics.cyclomatic_complexity == 4

    def test_dangerous_interesting_calls_signals(self, preprocessor: PythonPreprocessor):
        code = (
            "import os\n"
            "import pickle\n"
            "eval(user_code)\n"
            "os.system('rm -rf /')\n"
            "pickle.loads(raw_data)\n"
        )
        result = preprocessor.analyze_source(code)
        assert result.success is True
        signals = result.context.interesting_signals
        assert len(signals) == 3

        categories = [s.category for s in signals]
        assert "code_execution" in categories
        assert "process_execution" in categories
        assert "deserialization" in categories

    def test_snippet_extraction(self, preprocessor: PythonPreprocessor):
        code = "line1\nline2\nline3\nline4\nline5\n"
        result = preprocessor.analyze_source(code)
        assert result.get_snippet(2, 4) == "line2\nline3\nline4"
        assert result.get_snippet(1, 1) == "line1"

    def test_unicode_source_handling(self, preprocessor: PythonPreprocessor):
        code = (
            "# Unicode comment: こんにちは世界 🚀\n"
            "def greet_unicode():\n"
            "    return '你好，世界'\n"
        )
        result = preprocessor.analyze_source(code)
        assert result.success is True
        assert result.context.functions[0].name == "greet_unicode"

    def test_comprehensions_and_lambda_extraction(self, preprocessor: PythonPreprocessor):
        code = (
            "squares = [x**2 for x in range(10)]\n"
            "lookup = {x: str(x) for x in range(5)}\n"
            "fn = lambda a, b: a + b\n"
        )
        result = preprocessor.analyze_source(code)
        assert result.success is True
        assert result.context.control_flow.comprehension_count == 2

    def test_deterministic_output(self, preprocessor: PythonPreprocessor):
        code = (
            "def func_a(x): return x * 2\n"
            "def func_b(y): return y + 1\n"
        )
        res1 = preprocessor.analyze_source(code).model_dump()
        res2 = preprocessor.analyze_source(code).model_dump()
        assert res1 == res2
