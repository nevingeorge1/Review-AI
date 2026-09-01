"""Code Health Score and Category Distribution Calculator.

Provides a transparent, explainable 0-100 code health scoring algorithm
grounded on finding severities, category weights, and multi-tool confidence ratings.
"""

from typing import Dict, List
from backend.app.models.domain import QualityScore, ReviewFinding
from backend.app.models.enums import Category, Severity


class ScoreCalculator:
    """Calculates overall and category-specific code health scores with letter grades."""

    SEVERITY_DEDUCTIONS = {
        Severity.CRITICAL: 25.0,
        Severity.HIGH: 15.0,
        Severity.MEDIUM: 8.0,
        Severity.LOW: 3.0,
        Severity.INFO: 0.5,
    }

    # Weight distribution across categories in overall code health (Sum = 1.0)
    CATEGORY_WEIGHTS = {
        Category.SECURITY: 0.30,
        Category.BUG: 0.30,
        Category.MAINTAINABILITY: 0.20,
        Category.PERFORMANCE: 0.10,
        Category.STYLE: 0.10,
    }

    def calculate_quality_score(self, findings: List[ReviewFinding]) -> QualityScore:
        """
        Calculate composite quality score (0.0 to 100.0) based on weighted finding deductions.

        Args:
            findings: Consolidated and deduplicated review findings.

        Returns:
            QualityScore containing overall score, sub-scores per category, and letter grade.
        """
        # Baseline 100 points per category
        category_penalties: Dict[Category, float] = {
            cat: 0.0 for cat in Category
        }

        for finding in findings:
            weight = self.SEVERITY_DEDUCTIONS.get(finding.severity, 2.0)
            confidence_factor = max(0.5, min(1.0, finding.confidence))
            penalty = weight * confidence_factor
            category_penalties[finding.category] += penalty

        # Compute bounded category sub-scores (0.0 to 100.0)
        category_scores: Dict[str, float] = {}
        for cat in Category:
            score = max(0.0, min(100.0, 100.0 - category_penalties[cat]))
            category_scores[cat.value] = round(score, 1)

        # Weighted aggregate overall score
        overall = sum(
            category_scores[cat.value] * self.CATEGORY_WEIGHTS[cat]
            for cat in Category
        )
        overall_score = round(max(0.0, min(100.0, overall)), 1)

        # Letter grade classification
        if overall_score >= 95.0:
            grade = "A+"
        elif overall_score >= 90.0:
            grade = "A"
        elif overall_score >= 80.0:
            grade = "B"
        elif overall_score >= 70.0:
            grade = "C"
        elif overall_score >= 60.0:
            grade = "D"
        else:
            grade = "F"

        return QualityScore(
            overall_score=overall_score,
            security_score=category_scores.get("security", 100.0),
            reliability_score=category_scores.get("bug", 100.0),
            performance_score=category_scores.get("performance", 100.0),
            maintainability_score=category_scores.get("maintainability", 100.0),
            style_score=category_scores.get("style", 100.0),
            category_scores=category_scores,
            grade=grade,
        )
