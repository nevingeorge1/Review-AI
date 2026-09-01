"""Review Context Builder assembling structured and normalized context for LLM reasoning."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.app.analyzers.models import StaticAnalysisResult
from backend.app.models.domain import SourceFile, StaticFinding
from backend.app.models.enums import Category, Language, Severity
from backend.app.preprocessing.models import PreprocessingResult

CONTEXT_SCHEMA_VERSION = "1.0"


class ContextSourceInfo(BaseModel):
    """Source code metadata and text for LLM review."""
    filename: str = Field(default="submission.py")
    language: Language = Field(default=Language.PYTHON)
    line_count: int = Field(default=0, ge=0)
    byte_size: int = Field(default=0, ge=0)
    code: str = Field(..., description="Full source code text")


class ContextStructuralInfo(BaseModel):
    """Extracted AST structural and semantic metrics."""
    function_count: int = Field(default=0)
    class_count: int = Field(default=0)
    import_count: int = Field(default=0)
    cyclomatic_complexity_total: int = Field(default=1)
    max_nesting_depth: int = Field(default=0)
    function_signatures: List[str] = Field(default_factory=list)
    class_names: List[str] = Field(default_factory=list)
    imported_modules: List[str] = Field(default_factory=list)
    security_signals: List[Dict[str, Any]] = Field(default_factory=list)


class ContextFindingSummary(BaseModel):
    """Normalized static analyzer evidence for LLM prompt."""
    analyzer: str
    rule_id: str
    category: str
    severity: str
    line_number: Optional[int] = None
    message: str
    code_evidence: Optional[str] = None


class ReviewPolicy(BaseModel):
    """Review guidance and evaluation policy."""
    category_priority: List[str] = Field(
        default=["bug", "security", "performance", "maintainability", "style"],
        description="Priority order for findings inspection",
    )
    max_findings: int = Field(default=15, description="Maximum recommended findings to return")
    evidence_first: bool = Field(default=True, description="Treat static findings as confirmed factual evidence")


class ReviewContext(BaseModel):
    """Normalized, deterministic context bundle delivered to prompt synthesizer."""
    schema_version: str = Field(default=CONTEXT_SCHEMA_VERSION)
    source: ContextSourceInfo
    structure: ContextStructuralInfo
    static_evidence: List[ContextFindingSummary] = Field(default_factory=list)
    developer_notes: Optional[str] = None
    policy: ReviewPolicy = Field(default_factory=ReviewPolicy)


class ReviewContextBuilder:
    """Constructs deterministic, compact ReviewContext from preprocessing and static analysis."""

    def build_context(
        self,
        source_file: SourceFile,
        preprocessing_result: Optional[PreprocessingResult] = None,
        static_analysis_result: Optional[StaticAnalysisResult] = None,
        developer_notes: Optional[str] = None,
        policy: Optional[ReviewPolicy] = None,
    ) -> ReviewContext:
        """
        Synthesize source, AST structure, and static evidence into a structured ReviewContext.
        """
        # 1. Source info
        source_info = ContextSourceInfo(
            filename=source_file.filename,
            language=source_file.language,
            line_count=source_file.line_count,
            byte_size=source_file.byte_size,
            code=source_file.content,
        )

        # 2. Structural AST info
        structural_info = ContextStructuralInfo()
        if preprocessing_result and preprocessing_result.context:
            ctx = preprocessing_result.context
            structural_info.function_count = len(ctx.functions)
            structural_info.class_count = len(ctx.classes)
            structural_info.import_count = len(ctx.imports)
            structural_info.cyclomatic_complexity_total = ctx.metrics.cyclomatic_complexity_total
            structural_info.max_nesting_depth = ctx.metrics.max_nesting_depth

            # Function signatures (compact representation)
            signatures = []
            for fn in ctx.functions:
                params = ", ".join(
                    f"{p.name}: {p.type_annotation}" if p.type_annotation else p.name
                    for p in fn.parameters
                )
                ret = f" -> {fn.return_annotation}" if fn.return_annotation else ""
                async_kw = "async " if fn.is_async else ""
                signatures.append(f"{async_kw}def {fn.name}({params}){ret} (line {fn.line_number}-{fn.end_line_number})")
            structural_info.function_signatures = signatures

            # Classes and imports
            structural_info.class_names = [cls.name for cls in ctx.classes]
            structural_info.imported_modules = [
                f"{imp.module}.{imp.name}" if imp.module else imp.name
                for imp in ctx.imports
            ]

            # Security signals
            signals = []
            for sig in ctx.interesting_signals:
                signals.append({
                    "name": sig.name,
                    "category": sig.category,
                    "line": sig.line_number,
                    "description": sig.description,
                })
            structural_info.security_signals = signals

        # 3. Static evidence
        evidence_list: List[ContextFindingSummary] = []
        if static_analysis_result:
            for f in static_analysis_result.findings:
                evidence_list.append(
                    ContextFindingSummary(
                        analyzer=f.analyzer_name,
                        rule_id=f.rule_id,
                        category=f.category.value,
                        severity=f.severity.value,
                        line_number=f.line_number,
                        message=f.message,
                        code_evidence=f.code_evidence,
                    )
                )

        return ReviewContext(
            schema_version=CONTEXT_SCHEMA_VERSION,
            source=source_info,
            structure=structural_info,
            static_evidence=evidence_list,
            developer_notes=developer_notes,
            policy=policy or ReviewPolicy(),
        )
