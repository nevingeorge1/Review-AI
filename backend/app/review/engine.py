"""ReviewEngine pipeline orchestrator for ReviewAI."""

import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from backend.app.analyzers.composite import StaticAnalysisEngine
from backend.app.analyzers.models import StaticAnalysisResult
from backend.app.core.config import Settings, get_settings
from backend.app.core.logging import logger
from backend.app.llm.models import LLMReviewResult
from backend.app.llm.service import LLMReviewService
from backend.app.models.domain import (
    AnalysisMetadata,
    AnalysisRequest,
    AnalysisResponse,
    CodeSubmission,
    QualityScore,
    ReviewFinding,
    ReviewSummary,
    SourceFile,
    StaticFinding,
)
from backend.app.models.enums import Category, DetectionSource, Language, ReviewStatus, Severity
from backend.app.preprocessing.models import PreprocessingResult
from backend.app.preprocessing.python_preprocessor import PythonPreprocessor
from backend.app.review.fusion import FindingFusion
from backend.app.review.prioritizer import FindingPrioritizer
from backend.app.review.scorer import ScoreCalculator


class ReviewEngine:
    """Master review engine coordinating preprocessing, static analysis, LLM reasoning, fusion, and scoring."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        preprocessor: Optional[PythonPreprocessor] = None,
        static_engine: Optional[StaticAnalysisEngine] = None,
        llm_service: Optional[LLMReviewService] = None,
        fusion: Optional[FindingFusion] = None,
        prioritizer: Optional[FindingPrioritizer] = None,
        scorer: Optional[ScoreCalculator] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.preprocessor = preprocessor or PythonPreprocessor(settings=self.settings)
        self.static_engine = static_engine or StaticAnalysisEngine(
            settings=self.settings,
            preprocessor=self.preprocessor,
        )
        self.llm_service = llm_service or LLMReviewService(settings=self.settings)
        self.fusion = fusion or FindingFusion()
        self.prioritizer = prioritizer or FindingPrioritizer()
        self.scorer = scorer or ScoreCalculator()

    async def review_code(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Execute full end-to-end code review pipeline on an incoming submission.

        Pipeline Stages:
        1. Preprocessing & AST Structural Intelligence
        2. Multi-Tool Static Analysis (Ruff, Bandit, AST Rules)
        3. Local LLM Contextual Reasoning (or Static-Only Fallback)
        4. Finding Fusion & Multi-Source Evidence Correlation
        5. Priority Ranking
        6. Quality Score & Category Breakdown Calculation
        7. Executive Summary & Telemetry Assembly
        """
        overall_start = time.perf_counter()
        stage_durations: Dict[str, float] = {}

        source_text = request.submission.code
        filename = request.submission.filename or "submission.py"
        language = request.submission.language

        # ------------------------------------------------------------------
        # Stage 1: Preprocessing & AST Intelligence
        # ------------------------------------------------------------------
        t0 = time.perf_counter()
        prep_result = self.preprocessor.analyze_source(code=source_text, filename=filename)
        stage_durations["preprocessing"] = round((time.perf_counter() - t0) * 1000.0, 2)

        source_file = SourceFile(
            filename=filename,
            content=source_text,
            language=language,
            line_count=prep_result.source_lines,
            byte_size=prep_result.source_size,
        )

        # Handle Syntax Errors gracefully
        if not prep_result.syntax_valid:
            logger.info("Syntax error detected during review preprocessing: %s", prep_result.syntax_error)
            err_msg = prep_result.syntax_error.message if prep_result.syntax_error else "Syntax error"
            err_line = prep_result.syntax_error.line if prep_result.syntax_error else 1

            syntax_finding = ReviewFinding(
                id=str(uuid.uuid4()),
                category=Category.BUG,
                severity=Severity.CRITICAL,
                title=f"Python Syntax Error: {err_msg[:60]}",
                description=f"Source code could not be compiled into an AST due to a syntax error on line {err_line}: {err_msg}",
                line_number=err_line,
                end_line=err_line,
                explanation="Syntax errors prevent execution, linting, and AST parsing.",
                recommendation="Fix Python syntax error at indicated line.",
                confidence=1.0,
                confidence_level="HIGH",
                detection_source=DetectionSource.STATIC_ANALYSIS,
                detected_by=["python_ast_parser"],
            )

            quality_score = QualityScore(
                overall_score=0.0,
                security_score=0.0,
                reliability_score=0.0,
                performance_score=0.0,
                maintainability_score=0.0,
                style_score=0.0,
                category_scores={"bug": 0.0, "security": 0.0, "performance": 0.0, "maintainability": 0.0, "style": 0.0},
                grade="F",
            )

            total_ms = round((time.perf_counter() - overall_start) * 1000.0, 2)
            return AnalysisResponse(
                id=request.id,
                status=ReviewStatus.FAILED,
                findings=[syntax_finding],
                summary=ReviewSummary(
                    total_findings=1,
                    critical_count=1,
                    category_breakdown={"bug": 1},
                    review_mode="STATIC_ONLY",
                    analyzers_used=["python_ast_parser"],
                    llm_status="SKIPPED",
                    executive_summary=f"Analysis halted: Syntax error detected on line {err_line} ({err_msg}).",
                ),
                quality_score=quality_score,
                metadata=AnalysisMetadata(
                    analysis_id=request.id,
                    language=language,
                    line_count=source_file.line_count,
                    byte_size=source_file.byte_size,
                    review_mode="STATIC_ONLY",
                    static_analysis_enabled=True,
                    llm_enabled=request.enable_llm,
                    static_only_mode=True,
                    analyzers_executed=["python_ast_parser"],
                    stage_durations_ms=stage_durations,
                    total_duration_ms=total_ms,
                ),
            )

        # ------------------------------------------------------------------
        # Stage 2: Multi-Tool Static Analysis
        # ------------------------------------------------------------------
        t0 = time.perf_counter()
        static_result = StaticAnalysisResult()
        if request.enable_static_analysis and self.settings.ENABLE_STATIC_ANALYSIS:
            static_result = await self.static_engine.analyze_source(
                source_file=source_file,
                preprocessing_result=prep_result,
            )
        stage_durations["static_analysis"] = round((time.perf_counter() - t0) * 1000.0, 2)

        # ------------------------------------------------------------------
        # Stage 3: Local LLM Reasoning Layer
        # ------------------------------------------------------------------
        t0 = time.perf_counter()
        llm_result = LLMReviewResult(
            provider=self.settings.LLM_PROVIDER,
            model_used=self.settings.OLLAMA_MODEL,
        )

        review_mode = "STATIC_ONLY"
        if request.enable_llm and self.settings.ENABLE_LLM:
            try:
                llm_result = await self.llm_service.review_code(
                    source_file=source_file,
                    preprocessing_result=prep_result,
                    static_analysis_result=static_result,
                    developer_notes=request.submission.context_notes,
                )
                if llm_result.status == "COMPLETED":
                    review_mode = "HYBRID"
            except Exception as llm_err:
                logger.warning("LLM reasoning stage encountered exception: %s", llm_err)
                review_mode = "STATIC_ONLY"

        stage_durations["llm_reasoning"] = round((time.perf_counter() - t0) * 1000.0, 2)

        # ------------------------------------------------------------------
        # Stage 4: Finding Fusion & Deduplication
        # ------------------------------------------------------------------
        t0 = time.perf_counter()
        fused_findings = self.fusion.fuse_findings(
            static_findings=static_result.findings,
            llm_findings=llm_result.findings,
        )

        # ------------------------------------------------------------------
        # Stage 5: Prioritization
        # ------------------------------------------------------------------
        prioritized_findings = self.prioritizer.prioritize_findings(fused_findings)

        # ------------------------------------------------------------------
        # Stage 6: Quality Scoring & Summary
        # ------------------------------------------------------------------
        quality_score = self.scorer.calculate_quality_score(prioritized_findings)
        stage_durations["fusion_and_scoring"] = round((time.perf_counter() - t0) * 1000.0, 2)

        total_duration_ms = round((time.perf_counter() - overall_start) * 1000.0, 2)

        # Calculate counts
        sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        cat_counts = {}
        analyzers_used_set = set(static_result.analyzers_run)
        if review_mode == "HYBRID":
            analyzers_used_set.add(self.llm_service.provider.provider_name)

        for f in prioritized_findings:
            sev_counts[f.severity.value.lower()] = sev_counts.get(f.severity.value.lower(), 0) + 1
            cat_counts[f.category.value.lower()] = cat_counts.get(f.category.value.lower(), 0) + 1

        # Formulate executive summary
        if llm_result.status == "COMPLETED" and llm_result.executive_summary:
            exec_summary = llm_result.executive_summary
        elif prioritized_findings:
            top_cat = max(cat_counts.items(), key=lambda x: x[1])[0] if cat_counts else "general"
            exec_summary = (
                f"Code review completed in {review_mode} mode ({total_duration_ms:.0f}ms). "
                f"Discovered {len(prioritized_findings)} finding(s) with primary concentration in {top_cat}. "
                f"Overall code health score is {quality_score.overall_score}/100 (Grade: {quality_score.grade})."
            )
        else:
            exec_summary = (
                f"Clean code submission: Zero issues discovered in {review_mode} mode across "
                f"{len(analyzers_used_set)} analyzers. Overall score: {quality_score.overall_score}/100 (Grade: A+)."
            )

        summary = ReviewSummary(
            total_findings=len(prioritized_findings),
            critical_count=sev_counts["critical"],
            high_count=sev_counts["high"],
            medium_count=sev_counts["medium"],
            low_count=sev_counts["low"],
            info_count=sev_counts["info"],
            category_breakdown=cat_counts,
            review_mode=review_mode,
            analyzers_used=sorted(list(analyzers_used_set)),
            llm_status=llm_result.status,
            executive_summary=exec_summary,
        )

        metadata = AnalysisMetadata(
            analysis_id=request.id,
            language=language,
            line_count=source_file.line_count,
            byte_size=source_file.byte_size,
            review_mode=review_mode,
            static_analysis_enabled=request.enable_static_analysis,
            llm_enabled=request.enable_llm,
            llm_model_used=self.settings.OLLAMA_MODEL if review_mode == "HYBRID" else None,
            static_only_mode=(review_mode == "STATIC_ONLY"),
            analyzers_executed=sorted(list(analyzers_used_set)),
            stage_durations_ms=stage_durations,
            total_duration_ms=total_duration_ms,
        )

        logger.info(
            "Completed review %s: mode=%s, findings=%d, score=%.1f, grade=%s, duration=%.2fms",
            request.id,
            review_mode,
            len(prioritized_findings),
            quality_score.overall_score,
            quality_score.grade,
            total_duration_ms,
        )

        return AnalysisResponse(
            id=request.id,
            status=ReviewStatus.COMPLETED,
            findings=prioritized_findings,
            summary=summary,
            quality_score=quality_score,
            metadata=metadata,
            created_at=request.created_at,
        )
