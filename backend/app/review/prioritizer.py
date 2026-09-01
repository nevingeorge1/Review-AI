"""Finding Prioritizer ranking review issues by impact, severity, and evidence strength."""

from typing import List
from backend.app.models.domain import ReviewFinding
from backend.app.models.enums import Category, Severity


class FindingPrioritizer:
    """Prioritizes and ranks code review findings deterministically."""

    SEVERITY_ORDER = {
        Severity.CRITICAL: 0,
        Severity.HIGH: 1,
        Severity.MEDIUM: 2,
        Severity.LOW: 3,
        Severity.INFO: 4,
    }

    CATEGORY_ORDER = {
        Category.SECURITY: 0,
        Category.BUG: 1,
        Category.PERFORMANCE: 2,
        Category.MAINTAINABILITY: 3,
        Category.STYLE: 4,
    }

    def prioritize_findings(self, findings: List[ReviewFinding]) -> List[ReviewFinding]:
        """
        Sort findings deterministically by impact:
        1. Severity (CRITICAL -> HIGH -> MEDIUM -> LOW -> INFO)
        2. Category (SECURITY -> BUG -> PERFORMANCE -> MAINTAINABILITY -> STYLE)
        3. Confidence score (Descending: higher confidence first)
        4. Line number (Ascending: top-to-bottom within source)
        """
        if not findings:
            return []

        def sort_key(f: ReviewFinding):
            sev_rank = self.SEVERITY_ORDER.get(f.severity, 99)
            cat_rank = self.CATEGORY_ORDER.get(f.category, 99)
            conf_rank = -f.confidence  # Higher confidence first
            line_rank = f.line_number if f.line_number is not None else 99999
            return (sev_rank, cat_rank, conf_rank, line_rank)

        sorted_findings = list(findings)
        sorted_findings.sort(key=sort_key)
        return sorted_findings
