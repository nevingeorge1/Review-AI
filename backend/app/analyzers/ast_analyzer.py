"""Custom AST Rule Analyzer executing AST-based rules against CodeContext."""

from typing import List, Optional

from backend.app.analyzers.ast_rules.rules import get_all_ast_rules
from backend.app.analyzers.base import StaticAnalyzer
from backend.app.core.config import Settings, get_settings
from backend.app.core.logging import logger
from backend.app.models.domain import SourceFile, StaticFinding
from backend.app.models.enums import Language
from backend.app.preprocessing.models import PreprocessingResult
from backend.app.preprocessing.python_preprocessor import PythonPreprocessor


class ASTRuleAnalyzer(StaticAnalyzer):
    """Static Analyzer executing 15 high-value custom AST inspection rules."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        preprocessor: Optional[PythonPreprocessor] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.preprocessor = preprocessor or PythonPreprocessor(settings=self.settings)
        self.rules = get_all_ast_rules(settings=self.settings)

    @property
    def name(self) -> str:
        return "ast_rules"

    @property
    def supported_languages(self) -> List[Language]:
        return [Language.PYTHON]

    def is_available(self) -> bool:
        """AST rule engine is built-in and always available."""
        return self.settings.ENABLE_AST_RULES

    async def analyze(
        self,
        source_file: SourceFile,
        preprocessing_result: Optional[PreprocessingResult] = None,
    ) -> List[StaticFinding]:
        """
        Evaluate all active AST rules against the source file.

        Args:
            source_file: Validated SourceFile entity.
            preprocessing_result: Optional pre-computed result to avoid re-parsing.

        Returns:
            List of StaticFinding records.
        """
        # Ensure we have a valid CodeContext
        if preprocessing_result and preprocessing_result.context:
            context = preprocessing_result.context
        else:
            prep = self.preprocessor.analyze_source(
                code=source_file.content,
                filename=source_file.filename,
            )
            if not prep.syntax_valid or not prep.context:
                logger.info("ASTRuleAnalyzer skipped due to syntax errors in source")
                return []
            context = prep.context

        all_findings: List[StaticFinding] = []

        for rule in self.rules:
            try:
                findings = rule.evaluate(source_file=source_file, context=context)
                all_findings.extend(findings)
            except Exception as err:
                logger.warning("Error evaluating AST rule %s: %s", rule.rule_id, err, exc_info=True)

        return all_findings
