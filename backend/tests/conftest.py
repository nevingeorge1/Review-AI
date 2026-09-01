"""Pytest shared fixtures for ReviewAI test suite."""

import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import Settings
from backend.app.main import app
from backend.app.models.domain import (
    AnalysisRequest,
    CodeSubmission,
    Evidence,
    QualityScore,
    ReviewFinding,
    ReviewSummary,
    SourceFile,
    StaticFinding,
    SuggestedFix,
)
from backend.app.models.enums import (
    Category,
    DetectionSource,
    Language,
    ReviewStatus,
    Severity,
)
from backend.app.services.review_service import ReviewService
from backend.app.services.storage import InMemoryReviewRepository


@pytest.fixture
def test_settings() -> Settings:
    """Provide isolated testing settings with lower limits for boundary testing."""
    return Settings(
        APP_ENV="testing",
        LOG_LEVEL="DEBUG",
        MAX_SOURCE_LINES=100,
        MAX_SOURCE_SIZE=10000,
        ENABLE_LLM=True,
        ENABLE_STATIC_ANALYSIS=True,
    )


@pytest.fixture
def in_memory_repo() -> InMemoryReviewRepository:
    """Provide a fresh, isolated InMemoryReviewRepository."""
    return InMemoryReviewRepository()


@pytest.fixture
def review_service(in_memory_repo: InMemoryReviewRepository, test_settings: Settings) -> ReviewService:
    """Provide initialized ReviewService with isolated repository."""
    return ReviewService(repository=in_memory_repo, settings=test_settings)


@pytest.fixture
def client() -> TestClient:
    """Provide FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_code() -> str:
    """Sample Python snippet containing a security flaw and style issue."""
    return (
        "import os\n\n"
        "def run_command(user_input):\n"
        "    # Insecure shell command\n"
        "    os.system('echo ' + user_input)\n"
    )


@pytest.fixture
def sample_submission(sample_code: str) -> CodeSubmission:
    """Fixture providing a valid CodeSubmission."""
    return CodeSubmission(
        code=sample_code,
        language=Language.PYTHON,
        filename="command_runner.py",
        context_notes="Sample script for command execution.",
    )


@pytest.fixture
def sample_source_file(sample_code: str) -> SourceFile:
    """Fixture providing a valid SourceFile entity."""
    lines = sample_code.split("\n")
    return SourceFile(
        filename="command_runner.py",
        content=sample_code,
        language=Language.PYTHON,
        line_count=len(lines),
        byte_size=len(sample_code.encode("utf-8")),
    )


@pytest.fixture
def sample_review_finding() -> ReviewFinding:
    """Fixture providing a full ReviewFinding instance."""
    return ReviewFinding(
        category=Category.SECURITY,
        severity=Severity.HIGH,
        title="Command Injection Vulnerability via os.system",
        description="Passing unescaped user input directly into os.system allows arbitrary shell command execution.",
        line_number=5,
        end_line=5,
        code_evidence="os.system('echo ' + user_input)",
        explanation="Untrusted parameters can contain shell metacharacters that execute unintended commands.",
        recommendation="Replace os.system with the subprocess module using safe list-based arguments.",
        suggested_fix=SuggestedFix(
            original_snippet="os.system('echo ' + user_input)",
            replacement_snippet="subprocess.run(['echo', user_input], check=True)",
            explanation="Use subprocess.run with argument list to avoid shell parsing.",
        ),
        confidence=0.95,
        detection_source=DetectionSource.HYBRID,
        rule_id="B605",
        supporting_evidence=[
            Evidence(
                source_tool="bandit",
                rule_id="B605",
                line_number=5,
                snippet="os.system('echo ' + user_input)",
                raw_message="Possible shell injection",
            )
        ],
    )
