"""Composite Static Analysis Engine coordinating AST, Ruff, and Bandit analyzers."""

import time
from typing import List, Optional

from backend.app.analyzers.ast_analyzer import ASTRuleAnalyzer
from backend.app.analyzers.bandit_analyzer import BanditAnalyzer
from backend.app.analyzers.base import StaticAnalyzer
from backend.app.analyzers.deduplicator import deduplicate_and_merge_static_findings
from backend.app.analyzers.models import (
    AnalyzerExecutionInfo,
    StaticAnalysisResult,
    StaticSummaryCounts,
)
from backend.app.analyzers.ruff_analyzer import RuffAnalyzer
from backend.app.core.config import Settings, get_settings
from backend.app.core.logging import logger
from backend.app.models.domain import SourceFile, StaticFinding
from backend.app.models.enums import Severity
from backend.app.preprocessing.models import PreprocessingResult
from backend.app.preprocessing.python_preprocessor import PythonPreprocessor


class StaticAnalysisEngine:
    """Orchestrates multi-tool static code analysis, evidence normalization, and deduplication."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        preprocessor: Optional[PythonPreprocessor] = None,
        analyzers: Optional[List[StaticAnalyzer]] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.preprocessor = preprocessor or PythonPreprocessor(settings=self.settings)

        if analyzers is not None:
            self.analyzers = analyzers
        else:
            # Register standard multi-tool suite
            self.analyzers = [
                ASTRuleAnalyzer(settings=self.settings, preprocessor=self.preprocessor),
                RuffAnalyzer(settings=self.settings),
                BanditAnalyzer(settings=self.settings),
            ]

    async def analyze_source(
        self,
        source_file: SourceFile,
        preprocessing_result: Optional[PreprocessingResult] = None,
    ) -> StaticAnalysisResult:
        """
        Execute static analysis across all active tools with failure isolation and deduplication.

        Args:
            source_file: Validated SourceFile entity.
            preprocessing_result: Optional pre-computed AST PreprocessingResult.

        Returns:
            Consolidated StaticAnalysisResult.
        """
        start_time = time.perf_counter()
        raw_findings: List[StaticFinding] = []
        analyzers_run: List[str] = []
        analyzers_failed: List[str] = []
        execution_infos: List[AnalyzerExecutionInfo] = []

        # Run each analyzer with failure isolation
        for analyzer in self.analyzers:
            tool_name = analyzer.name
            t0 = time.perf_counter()

            if not analyzer.is_available():
                execution_infos.append(
                    AnalyzerExecutionInfo(
                        analyzer_name=tool_name,
                        status="UNAVAILABLE",
                        duration_ms=0.0,
                        findings_count=0,
                        error_message=f"Analyzer '{tool_name}' is disabled or not installed on host.",
                    )
                )
                continue

            try:
                logger.info("Executing static analyzer: %s", tool_name)
                tool_findings = await analyzer.analyze(
                    source_file=source_file,
                    preprocessing_result=preprocessing_result,
                )
                duration_ms = (time.perf_counter() - t0) * 1000.0

                raw_findings.extend(tool_findings)
                analyzers_run.append(tool_name)
                execution_infos.append(
                    AnalyzerExecutionInfo(
                        analyzer_name=tool_name,
                        status="SUCCESS",
                        duration_ms=duration_ms,
                        findings_count=len(tool_findings),
                    )
                )
                logger.info("Analyzer %s finished in %.2fms (findings: %d)", tool_name, duration_ms, len(tool_findings))

            except Exception as err:
                duration_ms = (time.perf_counter() - t0) * 1000.0
                analyzers_failed.append(tool_name)
                execution_infos.append(
                    AnalyzerExecutionInfo(
                        analyzer_name=tool_name,
                        status="FAILED",
                        duration_ms=duration_ms,
                        findings_count=0,
                        error_message=str(err),
                    )
                )
                logger.warning("Analyzer %s failed after %.2fms: %s", tool_name, duration_ms, err, exc_info=True)

        # Deduplicate and merge evidence across tools
        deduped_findings = deduplicate_and_merge_static_findings(raw_findings)
        total_duration_ms = (time.perf_counter() - start_time) * 1000.0

        # Calculate summary statistics
        summary = self._compute_summary_counts(deduped_findings)

        return StaticAnalysisResult(
            success=len(analyzers_run) > 0 or len(self.analyzers) == 0,
            findings=deduped_findings,
            analyzers_run=analyzers_run,
            analyzers_failed=analyzers_failed,
            analyzer_executions=execution_infos,
            total_duration_ms=total_duration_ms,
            summary=summary,
        )

    def _compute_summary_counts(self, findings: List[StaticFinding]) -> StaticSummaryCounts:
        """Compute severity and category distribution for static findings."""
        counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }
        by_category = {}
        by_analyzer = {}

        for f in findings:
            sev_key = f.severity.value.lower()
            if sev_key in counts:
                counts[sev_key] += 1

            cat_key = f.category.value.lower()
            by_category[cat_key] = by_category.get(cat_key, 0) + 1

            for tool in f.analyzer_name.split(","):
                by_analyzer[tool] = by_analyzer.get(tool, 0) + 1

        return StaticSummaryCounts(
            total=len(findings),
            critical=counts["critical"],
            high=counts["high"],
            medium=counts["medium"],
            low=counts["low"],
            info=counts["info"],
            by_category=by_category,
            by_analyzer=by_analyzer,
        )
