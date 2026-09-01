"""Domain enumerations for ReviewAI."""

from enum import Enum


class Language(str, Enum):
    """Supported and planned programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"


class Category(str, Enum):
    """Categorization of code review findings."""
    BUG = "bug"
    SECURITY = "security"
    STYLE = "style"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"


class Severity(str, Enum):
    """Severity levels for review findings, ordered from highest to lowest impact."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

    @property
    def score_penalty(self) -> float:
        """Penalty points deducted from 100-point quality score."""
        penalties = {
            Severity.CRITICAL: 25.0,
            Severity.HIGH: 15.0,
            Severity.MEDIUM: 8.0,
            Severity.LOW: 3.0,
            Severity.INFO: 0.5,
        }
        return penalties.get(self, 1.0)


class DetectionSource(str, Enum):
    """The origin of a finding in the hybrid review pipeline."""
    STATIC_ANALYSIS = "static_analysis"
    LLM = "llm"
    HYBRID = "hybrid"


class ReviewStatus(str, Enum):
    """Lifecycle status of an analysis request."""
    PENDING = "pending"
    ANALYZING = "analyzing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
