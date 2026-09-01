"""Ruff Static Analysis Adapter for linting, style, and code quality inspection."""

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


class RuffAnalyzer(StaticAnalyzer):
    """Integrates Ruff for high-speed deterministic linting and code quality analysis."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()

    @property
    def name(self) -> str:
        return "ruff"

    @property
    def supported_languages(self) -> List[Language]:
        return [Language.PYTHON]

    def is_available(self) -> bool:
        """Check if Ruff binary is installed on system and enabled in config."""
        return bool(self.settings.ENABLE_RUFF and shutil.which("ruff"))

    def _map_ruff_code_to_category_and_severity(self, code: str) -> tuple[Category, Severity]:
        """
        Map Ruff diagnostic rule codes to normalized Category and Severity.
        Policy:
        - 'F' (Pyflakes): BUG, MEDIUM (HIGH for undefined names/syntax)
        - 'E' / 'W' (pycodestyle): STYLE, LOW
        - 'B' (flake8-bugbear): BUG, MEDIUM
        - 'S' (flake8-bandit in ruff): SECURITY, HIGH
        - 'PERF' / 'C4': PERFORMANCE, LOW
        - 'SIM' / 'UP' / 'ARG': MAINTAINABILITY, INFO
        """
        prefix = code.upper()

        if prefix.startswith("F821") or prefix.startswith("F822") or prefix.startswith("F7"):
            return Category.BUG, Severity.HIGH
        elif prefix.startswith("F"):
            return Category.BUG, Severity.MEDIUM
        elif prefix.startswith("S") or prefix.startswith("B1"):
            return Category.SECURITY, Severity.HIGH
        elif prefix.startswith("B"):
            return Category.BUG, Severity.MEDIUM
        elif prefix.startswith("PERF") or prefix.startswith("C4"):
            return Category.PERFORMANCE, Severity.LOW
        elif prefix.startswith("SIM") or prefix.startswith("UP") or prefix.startswith("ARG"):
            return Category.MAINTAINABILITY, Severity.INFO
        elif prefix.startswith("E") or prefix.startswith("W") or prefix.startswith("I"):
            return Category.STYLE, Severity.LOW
        else:
            return Category.STYLE, Severity.INFO

    async def analyze(
        self,
        source_file: SourceFile,
        preprocessing_result: Optional[PreprocessingResult] = None,
    ) -> List[StaticFinding]:
        """Execute Ruff safely via subprocess in json mode."""
        if not self.is_available():
            logger.debug("RuffAnalyzer skipped (not available or disabled)")
            return []

        cmd = ["ruff", "check", "--output-format=json", "--no-cache", "{file}"]
        result, _ = await run_tool_safely(
            command_args=cmd,
            source_content=source_file.content,
            filename_hint=source_file.filename,
            timeout_seconds=self.settings.STATIC_ANALYZER_TIMEOUT,
        )

        if result.timed_out:
            logger.warning("Ruff static analysis timed out after %ds", self.settings.STATIC_ANALYZER_TIMEOUT)
            return []

        if not result.stdout.strip():
            return []

        findings: List[StaticFinding] = []
        try:
            items = json.loads(result.stdout)
            for item in items:
                rule_id = item.get("code", "RUFF")
                category, severity = self._map_ruff_code_to_category_and_severity(rule_id)
                msg = item.get("message", "Linter diagnostic")
                loc = item.get("location", {})
                end_loc = item.get("end_location", {})

                start_line = loc.get("row")
                end_line = end_loc.get("row", start_line)

                # Extract code snippet if preprocessor result is available
                snippet = None
                if preprocessing_result and start_line:
                    snippet = preprocessing_result.get_snippet(start_line, end_line)

                finding = StaticFinding(
                    id=str(uuid.uuid4()),
                    analyzer_name="ruff",
                    rule_id=rule_id,
                    category=category,
                    severity=severity,
                    message=msg,
                    line_number=start_line,
                    end_line=end_line,
                    code_evidence=snippet,
                )
                findings.append(finding)
        except json.JSONDecodeError as err:
            logger.warning("Failed to parse JSON output from Ruff: %s", err)

        return findings
