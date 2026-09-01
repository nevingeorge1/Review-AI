"""Concrete Python Language Analyzer implementing Module 1 LanguageAnalyzer contract."""

import ast
from typing import Any, Optional

from backend.app.analyzers.base import LanguageAnalyzer
from backend.app.core.errors import ParserSyntaxError
from backend.app.models.domain import SourceFile
from backend.app.models.enums import Language
from backend.app.preprocessing.python_preprocessor import PythonPreprocessor


class PythonLanguageAnalyzer(LanguageAnalyzer):
    """Deterministic Python language analyzer utilizing Python's built-in AST parser."""

    def __init__(self, preprocessor: Optional[PythonPreprocessor] = None) -> None:
        self.preprocessor = preprocessor or PythonPreprocessor()

    @property
    def language(self) -> Language:
        return Language.PYTHON

    def validate_syntax(self, source_file: SourceFile) -> bool:
        """
        Validate Python code syntax deterministically.
        Returns True if code parses without syntax errors, False otherwise.
        """
        try:
            ast.parse(source_file.content, filename=source_file.filename)
            return True
        except (SyntaxError, ValueError):
            return False

    def parse_ast(self, source_file: SourceFile) -> Optional[ast.AST]:
        """
        Parse source code into an AST node.

        Raises:
            ParserSyntaxError: If the source code contains syntax errors.
        """
        try:
            return ast.parse(source_file.content, filename=source_file.filename)
        except SyntaxError as e:
            raise ParserSyntaxError(
                message=e.msg,
                line=e.lineno,
                column=e.offset,
            ) from e
