"""Domain models, schemas, and enumerations for ReviewAI."""

from backend.app.models.enums import (
    Category,
    DetectionSource,
    Language,
    ReviewStatus,
    Severity,
)
from backend.app.models.domain import (
    AnalysisMetadata,
    AnalysisRequest,
    AnalysisResponse,
    CodeSubmission,
    Evidence,
    QualityScore,
    ReviewFinding,
    ReviewSummary,
    SourceFile,
    StaticFinding,
    SuggestedFix,
)

__all__ = [
    # Enums
    "Category",
    "DetectionSource",
    "Language",
    "ReviewStatus",
    "Severity",
    # Models
    "AnalysisMetadata",
    "AnalysisRequest",
    "AnalysisResponse",
    "CodeSubmission",
    "Evidence",
    "QualityScore",
    "ReviewFinding",
    "ReviewSummary",
    "SourceFile",
    "StaticFinding",
    "SuggestedFix",
]
