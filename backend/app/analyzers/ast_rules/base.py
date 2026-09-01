"""Base contract and infrastructure for custom AST rules."""

import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

from backend.app.core.config import Settings, get_settings
from backend.app.models.domain import Evidence, SourceFile, StaticFinding
from backend.app.models.enums import Category, Severity
from backend.app.preprocessing.models import CodeContext


class ASTRule(ABC):
    """Abstract Base Class for AST-based static code analysis rules."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique rule identifier (e.g. 'RULE-001')."""
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        """Short descriptive title."""
        pass

    @property
    @abstractmethod
    def category(self) -> Category:
        """Primary issue category."""
        pass

    @property
    @abstractmethod
    def severity(self) -> Severity:
        """Baseline severity level."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Detailed explanation of why this code pattern is flagged."""
        pass

    @property
    @abstractmethod
    def recommendation(self) -> str:
        """Actionable remediation guidance."""
        pass

    @abstractmethod
    def evaluate(self, source_file: SourceFile, context: CodeContext) -> List[StaticFinding]:
        """
        Evaluate rule logic against source file and extracted AST CodeContext.

        Args:
            source_file: Validated SourceFile entity.
            context: Extracted AST CodeContext from Module 3.

        Returns:
            List of StaticFinding records discovered by this rule.
        """
        pass

    def create_finding(
        self,
        message: str,
        line_number: Optional[int] = None,
        end_line: Optional[int] = None,
        code_evidence: Optional[str] = None,
        severity_override: Optional[Severity] = None,
    ) -> StaticFinding:
        """Helper to construct a normalized StaticFinding record."""
        return StaticFinding(
            id=str(uuid.uuid4()),
            analyzer_name="ast_rules",
            rule_id=self.rule_id,
            category=self.category,
            severity=severity_override or self.severity,
            message=message,
            line_number=line_number,
            end_line=end_line or line_number,
            code_evidence=code_evidence,
        )
