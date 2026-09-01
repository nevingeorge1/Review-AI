"""Strongly typed domain and DTO models for source code preprocessing and AST extraction."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.app.models.enums import Language


class SyntaxErrorInfo(BaseModel):
    """Detailed metadata for Python syntax errors."""
    message: str = Field(..., description="Parser syntax error message")
    line: Optional[int] = Field(None, ge=1, description="1-indexed line number")
    column: Optional[int] = Field(None, ge=1, description="1-indexed column offset")
    end_line: Optional[int] = Field(None, ge=1, description="1-indexed ending line number")
    end_column: Optional[int] = Field(None, ge=1, description="1-indexed ending column offset")
    text: Optional[str] = Field(None, description="Source line text where error occurred")


class ImportRecord(BaseModel):
    """Extracted module or symbol import."""
    module: Optional[str] = Field(None, description="Imported module root or path (e.g. 'os', 'pathlib')")
    name: str = Field(..., description="Imported symbol name or module name")
    alias: Optional[str] = Field(None, description="Optional 'as' alias name")
    is_from_import: bool = Field(default=False, description="True if 'from x import y' format")
    line_number: int = Field(..., ge=1, description="1-indexed line number")


class ParameterRecord(BaseModel):
    """Extracted function parameter metadata."""
    name: str = Field(..., description="Parameter identifier name")
    type_annotation: Optional[str] = Field(None, description="Static type annotation repr if provided")
    default_value_repr: Optional[str] = Field(None, description="Default value repr if provided")
    is_args: bool = Field(default=False, description="True if *args variable positional parameter")
    is_kwargs: bool = Field(default=False, description="True if **kwargs variable keyword parameter")
    is_keyword_only: bool = Field(default=False, description="True if keyword-only parameter")


class FunctionMetrics(BaseModel):
    """Complexity and structure metrics for an individual function."""
    line_count: int = Field(default=0, ge=0, description="Total physical lines spanned by function")
    parameter_count: int = Field(default=0, ge=0, description="Number of parameters")
    branching_count: int = Field(default=0, ge=0, description="Number of decision / branch points")
    loop_count: int = Field(default=0, ge=0, description="Number of loops (for, while)")
    nesting_depth: int = Field(default=0, ge=0, description="Maximum internal block nesting depth")
    cyclomatic_complexity: int = Field(default=1, ge=1, description="Estimated McCabe cyclomatic complexity")


class FunctionRecord(BaseModel):
    """Extracted function or method metadata."""
    name: str = Field(..., description="Function identifier name")
    line_number: int = Field(..., ge=1, description="1-indexed starting line number")
    end_line_number: int = Field(..., ge=1, description="1-indexed ending line number")
    is_async: bool = Field(default=False, description="True if async def")
    parameters: List[ParameterRecord] = Field(default_factory=list, description="Function parameters")
    parameter_count: int = Field(default=0, ge=0, description="Total parameter count")
    return_annotation: Optional[str] = Field(None, description="Return type annotation repr")
    decorators: List[str] = Field(default_factory=list, description="Decorator names applied")
    has_docstring: bool = Field(default=False, description="True if docstring is present")
    docstring: Optional[str] = Field(None, description="Extracted docstring text")
    is_nested: bool = Field(default=False, description="True if defined inside another function")
    parent_class: Optional[str] = Field(None, description="Enclosing class name if method")
    metrics: FunctionMetrics = Field(default_factory=FunctionMetrics, description="Function-level metrics")


class ClassRecord(BaseModel):
    """Extracted class definition metadata."""
    name: str = Field(..., description="Class identifier name")
    line_number: int = Field(..., ge=1, description="1-indexed starting line number")
    end_line_number: int = Field(..., ge=1, description="1-indexed ending line number")
    base_classes: List[str] = Field(default_factory=list, description="Explicit base class names")
    decorators: List[str] = Field(default_factory=list, description="Decorator names applied")
    methods: List[str] = Field(default_factory=list, description="Method names defined within class")
    method_count: int = Field(default=0, ge=0, description="Total method count")
    has_docstring: bool = Field(default=False, description="True if docstring is present")
    docstring: Optional[str] = Field(None, description="Extracted docstring text")


class VariableRecord(BaseModel):
    """Extracted variable assignment metadata."""
    name: str = Field(..., description="Variable identifier name")
    line_number: int = Field(..., ge=1, description="1-indexed line number")
    assignment_type: str = Field(default="Assign", description="Assign, AnnAssign, or AugAssign")
    type_annotation: Optional[str] = Field(None, description="Type annotation if AnnAssign")
    scope: str = Field(default="module", description="Scope: module, class, function")


class CallRecord(BaseModel):
    """Extracted function or method invocation."""
    name: str = Field(..., description="Short function or method name (e.g. 'system', 'run')")
    full_attribute_chain: str = Field(..., description="Full attribute path (e.g. 'os.system', 'self.helper')")
    line_number: int = Field(..., ge=1, description="1-indexed line number")
    arg_count: int = Field(default=0, ge=0, description="Positional arguments count")
    keyword_args: List[str] = Field(default_factory=list, description="Keyword argument names provided")


class PotentiallyInterestingCall(BaseModel):
    """Neutral signal of a function call that may warrant inspection by static analyzers."""
    name: str = Field(..., description="Function or method call expression")
    category: str = Field(..., description="Signal category: code_execution, process_execution, deserialization, etc.")
    line_number: int = Field(..., ge=1, description="1-indexed line number")
    description: str = Field(..., description="Explanation of why this call pattern is flagged for inspection")
    arguments_preview: Optional[str] = Field(None, description="Safe snippet preview of argument expressions")


class ControlFlowSummary(BaseModel):
    """Aggregate control-flow construct counts across the module."""
    if_count: int = Field(default=0, ge=0)
    for_count: int = Field(default=0, ge=0)
    while_count: int = Field(default=0, ge=0)
    try_count: int = Field(default=0, ge=0)
    except_count: int = Field(default=0, ge=0)
    with_count: int = Field(default=0, ge=0)
    return_count: int = Field(default=0, ge=0)
    raise_count: int = Field(default=0, ge=0)
    break_count: int = Field(default=0, ge=0)
    continue_count: int = Field(default=0, ge=0)
    comprehension_count: int = Field(default=0, ge=0)
    max_nesting_depth: int = Field(default=0, ge=0)


class CodeMetrics(BaseModel):
    """Overall structural and complexity metrics for a source file."""
    total_lines: int = Field(default=0, ge=0)
    logical_lines: int = Field(default=0, ge=0)
    comment_lines: int = Field(default=0, ge=0)
    blank_lines: int = Field(default=0, ge=0)
    function_count: int = Field(default=0, ge=0)
    class_count: int = Field(default=0, ge=0)
    import_count: int = Field(default=0, ge=0)
    call_count: int = Field(default=0, ge=0)
    max_nesting_depth: int = Field(default=0, ge=0)
    average_function_length: float = Field(default=0.0, ge=0.0)
    cyclomatic_complexity_total: int = Field(default=1, ge=1)


class CodeContext(BaseModel):
    """Normalized structural context ready for consumption by static analyzers and LLM layers."""
    language: Language = Field(default=Language.PYTHON)
    source_statistics: Dict[str, Any] = Field(default_factory=dict)
    imports: List[ImportRecord] = Field(default_factory=list)
    functions: List[FunctionRecord] = Field(default_factory=list)
    classes: List[ClassRecord] = Field(default_factory=list)
    calls: List[CallRecord] = Field(default_factory=list)
    interesting_signals: List[PotentiallyInterestingCall] = Field(default_factory=list)
    control_flow: ControlFlowSummary = Field(default_factory=ControlFlowSummary)
    metrics: CodeMetrics = Field(default_factory=CodeMetrics)
    syntax_valid: bool = Field(default=True)
    syntax_error: Optional[SyntaxErrorInfo] = Field(None)


class PreprocessingResult(BaseModel):
    """Unified result of source preprocessing and AST intelligence extraction."""
    success: bool = Field(..., description="True if preprocessing completed without fatal errors")
    language: Language = Field(default=Language.PYTHON)
    filename: str = Field(default="submission.py")
    source_lines: int = Field(default=0, ge=0)
    source_size: int = Field(default=0, ge=0)
    syntax_valid: bool = Field(default=True)
    syntax_error: Optional[SyntaxErrorInfo] = Field(None)
    context: Optional[CodeContext] = Field(None)
    warnings: List[str] = Field(default_factory=list)
    _raw_source: Optional[str] = None

    def set_raw_source(self, code: str) -> None:
        """Store original source text in memory for snippet referencing."""
        object.__setattr__(self, "_raw_source", code)

    def get_snippet(self, start_line: int, end_line: Optional[int] = None) -> str:
        """Extract a source code slice by line range (1-indexed, inclusive)."""
        raw = getattr(self, "_raw_source", None)
        if not raw:
            return ""
        lines = raw.split("\n")
        start_idx = max(0, start_line - 1)
        end_idx = end_line if end_line is not None else start_line
        end_idx = min(len(lines), end_idx)
        return "\n".join(lines[start_idx:end_idx])
