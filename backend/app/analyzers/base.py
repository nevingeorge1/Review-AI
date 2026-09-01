"""Abstract base classes and contracts for Language and Static Analyzers.

Extensibility Foundation:
- LanguageAnalyzer provides language-specific syntax and parsing hooks.
- StaticAnalyzer provides pluggable deterministic analyzers (AST, Ruff, Bandit, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from backend.app.models.domain import SourceFile, StaticFinding
from backend.app.models.enums import Language


class LanguageAnalyzer(ABC):
    """Abstract interface for language-specific syntax analysis and parsing.

    Enables adding support for JavaScript, TypeScript, Java, etc. in future modules
    without altering core review engine logic.
    """

    @property
    @abstractmethod
    def language(self) -> Language:
        """Return the target programming language."""
        pass

    @abstractmethod
    def validate_syntax(self, source_file: SourceFile) -> bool:
        """
        Validate source code syntax deterministically.
        Returns True if code parses without syntax errors, False otherwise.
        """
        pass

    @abstractmethod
    def parse_ast(self, source_file: SourceFile) -> Optional[Any]:
        """
        Parse source code into an Abstract Syntax Tree (AST) node or representation.
        Raises ParserSyntaxError if syntax is invalid.
        """
        pass


class StaticAnalyzer(ABC):
    """Abstract interface for deterministic static code analysis tools.

    Future implementations (Module 4) will include:
    - ASTAnalyzer (custom AST rules)
    - RuffAnalyzer (linting & formatting errors)
    - BanditAnalyzer (security vulnerabilities)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the static analyzer (e.g. 'bandit', 'ruff')."""
        pass

    @property
    @abstractmethod
    def supported_languages(self) -> List[Language]:
        """List of languages this static analyzer can process."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the underlying tool/binary is installed and accessible."""
        pass

    @abstractmethod
    async def analyze(self, source_file: SourceFile) -> List[StaticFinding]:
        """
        Execute deterministic static analysis on the source file.

        Args:
            source_file: The validated source file entity.

        Returns:
            List of normalized StaticFinding instances.
        """
        pass


class AnalyzerRegistry:
    """Registry managing available static and language analyzers."""

    def __init__(self) -> None:
        self._language_analyzers: Dict[Language, LanguageAnalyzer] = {}
        self._static_analyzers: Dict[str, StaticAnalyzer] = {}

    def register_language_analyzer(self, analyzer: LanguageAnalyzer) -> None:
        """Register a language analyzer for its specified language."""
        self._language_analyzers[analyzer.language] = analyzer

    def get_language_analyzer(self, language: Language) -> Optional[LanguageAnalyzer]:
        """Retrieve language analyzer for the given language."""
        return self._language_analyzers.get(language)

    def register_static_analyzer(self, analyzer: StaticAnalyzer) -> None:
        """Register a static analyzer."""
        self._static_analyzers[analyzer.name] = analyzer

    def get_static_analyzers_for_language(self, language: Language) -> List[StaticAnalyzer]:
        """Return all registered static analyzers that support the specified language."""
        return [
            analyzer
            for analyzer in self._static_analyzers.values()
            if language in analyzer.supported_languages and analyzer.is_available()
        ]
