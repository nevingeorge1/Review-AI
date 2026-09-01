"""Static analysis and evidence layer package for ReviewAI."""

from backend.app.analyzers.ast_analyzer import ASTRuleAnalyzer
from backend.app.analyzers.bandit_analyzer import BanditAnalyzer
from backend.app.analyzers.base import (
    AnalyzerRegistry,
    LanguageAnalyzer,
    StaticAnalyzer,
)
from backend.app.analyzers.composite import StaticAnalysisEngine
from backend.app.analyzers.deduplicator import (
    deduplicate_and_merge_static_findings,
    merge_two_findings,
)
from backend.app.analyzers.models import (
    AnalyzerExecutionInfo,
    StaticAnalysisResult,
    StaticSummaryCounts,
)
from backend.app.analyzers.python import PythonLanguageAnalyzer
from backend.app.analyzers.ruff_analyzer import RuffAnalyzer

__all__ = [
    # Contracts & Base Classes
    "AnalyzerRegistry",
    "LanguageAnalyzer",
    "StaticAnalyzer",
    # Concrete Analyzers
    "ASTRuleAnalyzer",
    "BanditAnalyzer",
    "PythonLanguageAnalyzer",
    "RuffAnalyzer",
    "StaticAnalysisEngine",
    # Models & DTOs
    "AnalyzerExecutionInfo",
    "StaticAnalysisResult",
    "StaticSummaryCounts",
    # Deduplication Utilities
    "deduplicate_and_merge_static_findings",
    "merge_two_findings",
]
