"""Concrete Python source code preprocessor and AST intelligence engine."""

import ast
from typing import Optional

from backend.app.core.config import Settings, get_settings
from backend.app.core.errors import InvalidSourceCodeError, SourceCodeTooLargeError
from backend.app.core.logging import logger
from backend.app.core.security import sanitize_and_validate_source_code
from backend.app.models.domain import CodeSubmission, SourceFile
from backend.app.models.enums import Language
from backend.app.preprocessing.ast_visitor import PythonASTVisitor
from backend.app.preprocessing.base import Preprocessor
from backend.app.preprocessing.metrics import (
    calculate_line_metrics,
    estimate_node_cyclomatic_complexity,
)
from backend.app.preprocessing.models import (
    CodeContext,
    CodeMetrics,
    PreprocessingResult,
    SyntaxErrorInfo,
)


class PythonPreprocessor(Preprocessor):
    """Robust, deterministic Python source code preprocessor and AST intelligence extractor.

    Safety Invariant:
    NEVER executes, imports, or dynamically evaluates submitted source code.
    All inspection is performed strictly through static AST and source text parsing.
    """

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()

    def preprocess(self, submission: CodeSubmission) -> SourceFile:
        """
        Implementation of Module 1 Preprocessor contract:
        Sanitize and normalize a raw submission into an internal SourceFile.
        """
        sanitized, lines, bytes_count = sanitize_and_validate_source_code(
            code=submission.code,
            max_lines=self.settings.MAX_SOURCE_LINES,
            max_bytes=self.settings.MAX_SOURCE_SIZE,
        )
        return SourceFile(
            filename=submission.filename or "submission.py",
            content=sanitized,
            language=Language.PYTHON,
            line_count=lines,
            byte_size=bytes_count,
        )

    def analyze_source(
        self,
        code: str,
        filename: str = "submission.py",
    ) -> PreprocessingResult:
        """
        Execute comprehensive AST extraction and structural intelligence analysis.

        Args:
            code: Raw Python source code string.
            filename: Name of the file being processed.

        Returns:
            PreprocessingResult containing CodeContext, metrics, and AST data,
            or structured syntax error information if invalid.
        """
        # 1. Enforce safety and payload limits
        try:
            sanitized_code, line_count, byte_size = sanitize_and_validate_source_code(
                code=code,
                max_lines=self.settings.MAX_SOURCE_LINES,
                max_bytes=self.settings.MAX_SOURCE_SIZE,
            )
        except (InvalidSourceCodeError, SourceCodeTooLargeError) as exc:
            # Propagate system validation errors directly
            raise exc

        # 2. Compute text line statistics
        total_lines, logical_lines, comment_lines, blank_lines = calculate_line_metrics(sanitized_code)

        # 3. Parse AST safely without code execution
        try:
            tree = ast.parse(sanitized_code, filename=filename)
        except SyntaxError as e:
            logger.info("Syntax error encountered during AST parsing: line=%s, msg='%s'", e.lineno, e.msg)
            syntax_err = SyntaxErrorInfo(
                message=e.msg,
                line=e.lineno,
                column=e.offset,
                end_line=getattr(e, "end_lineno", e.lineno),
                end_column=getattr(e, "end_offset", e.offset),
                text=e.text.strip() if e.text else None,
            )
            result = PreprocessingResult(
                success=False,
                language=Language.PYTHON,
                filename=filename,
                source_lines=total_lines,
                source_size=byte_size,
                syntax_valid=False,
                syntax_error=syntax_err,
                context=None,
                warnings=["Source code contains syntax errors and could not be fully parsed into an AST."],
            )
            result.set_raw_source(sanitized_code)
            return result

        # 4. Traverse AST in a single pass
        visitor = PythonASTVisitor(source_code=sanitized_code)
        visitor.visit(tree)

        # 5. Aggregate overall metrics
        cyclomatic_total = estimate_node_cyclomatic_complexity(tree)
        func_count = len(visitor.functions)
        avg_func_len = (
            sum(f.metrics.line_count for f in visitor.functions) / func_count
            if func_count > 0
            else 0.0
        )

        metrics = CodeMetrics(
            total_lines=total_lines,
            logical_lines=logical_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            function_count=func_count,
            class_count=len(visitor.classes),
            import_count=len(visitor.imports),
            call_count=len(visitor.calls),
            max_nesting_depth=visitor.max_nesting_depth,
            average_function_length=round(avg_func_len, 2),
            cyclomatic_complexity_total=cyclomatic_total,
        )

        control_flow = visitor.get_control_flow_summary()

        # 6. Construct normalized CodeContext
        context = CodeContext(
            language=Language.PYTHON,
            source_statistics={
                "line_count": total_lines,
                "logical_lines": logical_lines,
                "byte_size": byte_size,
                "blank_lines": blank_lines,
                "comment_lines": comment_lines,
            },
            imports=visitor.imports,
            functions=visitor.functions,
            classes=visitor.classes,
            calls=visitor.calls,
            interesting_signals=visitor.interesting_signals,
            control_flow=control_flow,
            metrics=metrics,
            syntax_valid=True,
            syntax_error=None,
        )

        result = PreprocessingResult(
            success=True,
            language=Language.PYTHON,
            filename=filename,
            source_lines=total_lines,
            source_size=byte_size,
            syntax_valid=True,
            syntax_error=None,
            context=context,
            warnings=[],
        )
        result.set_raw_source(sanitized_code)
        return result
