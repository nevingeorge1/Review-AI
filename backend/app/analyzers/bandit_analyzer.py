"""Bandit Static Analysis Adapter for Python security vulnerability inspection."""

import json
import shutil
import uuid
from typing import Any, Dict, List, Optional

from backend.app.analyzers.base import StaticAnalyzer
from backend.app.analyzers.safe_process import run_tool_safely
from backend.app.core.config import Settings, get_settings
from backend.app.core.logging import logger
from backend.app.models.domain import SourceFile, StaticFinding
from backend.app.models.enums import Category, Language, Severity
from backend.app.preprocessing.models import PreprocessingResult


class BanditAnalyzer(StaticAnalyzer):
    """Integrates Bandit for dedicated security flaw and vulnerability pattern detection."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()

    @property
    def name(self) -> str:
        return "bandit"

    @property
    def supported_languages(self) -> List[Language]:
        return [Language.PYTHON]

    def is_available(self) -> bool:
        """Check if Bandit binary is installed and enabled in configuration."""
        return bool(self.settings.ENABLE_BANDIT and shutil.which("bandit"))

    def _map_bandit_severity(self, bandit_sev: str) -> Severity:
        """Map Bandit severity string (HIGH, MEDIUM, LOW) to domain Severity enum."""
        mapping = {
            "HIGH": Severity.HIGH,
            "MEDIUM": Severity.MEDIUM,
            "LOW": Severity.LOW,
        }
        return mapping.get(bandit_sev.upper(), Severity.MEDIUM)

    async def analyze(
        self,
        source_file: SourceFile,
        preprocessing_result: Optional[PreprocessingResult] = None,
    ) -> List[StaticFinding]:
        """Execute Bandit safely via subprocess in json mode."""
        if not self.is_available():
            logger.debug("BanditAnalyzer skipped (not available or disabled)")
            return []

        cmd = ["bandit", "-f", "json", "-q", "{file}"]
        result, _ = await run_tool_safely(
            command_args=cmd,
            source_content=source_file.content,
            filename_hint=source_file.filename,
            timeout_seconds=self.settings.STATIC_ANALYZER_TIMEOUT,
        )

        if result.timed_out:
            logger.warning("Bandit static analysis timed out after %ds", self.settings.STATIC_ANALYZER_TIMEOUT)
            return []

        if not result.stdout.strip():
            return []

        findings: List[StaticFinding] = []
        try:
            report = json.loads(result.stdout)
            issues = report.get("results", [])
            for issue in issues:
                test_id = issue.get("test_id", "BANDIT")
                sev_str = issue.get("issue_severity", "MEDIUM")
                severity = self._map_bandit_severity(sev_str)
                msg = issue.get("issue_text", "Security issue detected")
                line_no = issue.get("line_number")
                line_range = issue.get("line_range", [])
                end_line = line_range[-1] if line_range else line_no

                snippet = issue.get("code", "").strip() or None
                if not snippet and preprocessing_result and line_no:
                    snippet = preprocessing_result.get_snippet(line_no, end_line)

                finding = StaticFinding(
                    id=str(uuid.uuid4()),
                    analyzer_name="bandit",
                    rule_id=test_id,
                    category=Category.SECURITY,
                    severity=severity,
                    message=msg,
                    line_number=line_no,
                    end_line=end_line,
                    code_evidence=snippet,
                )
                findings.append(finding)
        except json.JSONDecodeError as err:
            logger.warning("Failed to parse JSON output from Bandit: %s", err)

        return findings
