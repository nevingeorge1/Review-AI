"""LLM Review Service orchestrating context preparation, prompt generation, inference, and validation."""

import time
from typing import Optional

from backend.app.analyzers.models import StaticAnalysisResult
from backend.app.core.config import Settings, get_settings
from backend.app.core.errors import (
    LLMProviderError,
    LLMTimeoutError,
    LLMUnavailableError,
)
from backend.app.core.logging import logger
from backend.app.llm.base import LLMProvider
from backend.app.llm.context import ReviewContextBuilder, ReviewPolicy
from backend.app.llm.mock import MockLLMProvider
from backend.app.llm.models import LLMReviewResult
from backend.app.llm.ollama import OllamaProvider
from backend.app.llm.parser import LLMOutputParser
from backend.app.llm.prompts import PROMPT_VERSION, ReviewPromptBuilder
from backend.app.models.domain import SourceFile
from backend.app.preprocessing.models import PreprocessingResult


class LLMReviewService:
    """Orchestrates structured LLM code review inference, context synthesis, and response validation."""

    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        settings: Optional[Settings] = None,
        context_builder: Optional[ReviewContextBuilder] = None,
        prompt_builder: Optional[ReviewPromptBuilder] = None,
        parser: Optional[LLMOutputParser] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.context_builder = context_builder or ReviewContextBuilder()
        self.prompt_builder = prompt_builder or ReviewPromptBuilder()
        self.parser = parser or LLMOutputParser()

        if provider is not None:
            self.provider = provider
        else:
            if self.settings.LLM_PROVIDER.lower() == "mock":
                self.provider = MockLLMProvider(model_name=self.settings.OLLAMA_MODEL)
            else:
                self.provider = OllamaProvider(settings=self.settings)

    async def review_code(
        self,
        source_file: SourceFile,
        preprocessing_result: Optional[PreprocessingResult] = None,
        static_analysis_result: Optional[StaticAnalysisResult] = None,
        developer_notes: Optional[str] = None,
        policy: Optional[ReviewPolicy] = None,
    ) -> LLMReviewResult:
        """
        Execute full LLM code review pipeline with defensive error and fallback handling.

        Args:
            source_file: Validated source code entity.
            preprocessing_result: Optional AST preprocessing metadata.
            static_analysis_result: Optional static analyzer evidence.
            developer_notes: Optional developer instructions.
            policy: Review priority and guidance policy.

        Returns:
            LLMReviewResult containing validated findings or structured fallback metadata.
        """
        start_time = time.perf_counter()

        # Check if LLM is explicitly disabled
        if not self.settings.ENABLE_LLM:
            logger.info("LLM reasoning is disabled in configuration (ENABLE_LLM=False). Using static-only fallback.")
            return LLMReviewResult(
                success=True,
                executive_summary="LLM reasoning disabled in configuration.",
                findings=[],
                provider=self.provider.provider_name,
                model_used=self.provider.model_name,
                prompt_version=PROMPT_VERSION,
                duration_ms=0.0,
                status="FALLBACK",
                error_message="ENABLE_LLM=False",
            )

        # 1. Build ReviewContext
        context = self.context_builder.build_context(
            source_file=source_file,
            preprocessing_result=preprocessing_result,
            static_analysis_result=static_analysis_result,
            developer_notes=developer_notes,
            policy=policy,
        )

        # 2. Build Prompts
        system_prompt, user_prompt = self.prompt_builder.build_prompt_pair(context)

        # 3. Execute LLM Inference with Fallback Safety
        raw_response = ""
        try:
            logger.info("Initiating LLM review with provider '%s' (model: %s)", self.provider.provider_name, self.provider.model_name)
            raw_response = await self.provider.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
            )
        except (LLMUnavailableError, LLMTimeoutError, LLMProviderError) as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.warning("LLM reasoning failed (%s): %s", type(exc).__name__, exc)

            if self.settings.ALLOW_STATIC_FALLBACK:
                logger.info("Falling back gracefully to static-only mode.")
                return LLMReviewResult(
                    success=False,
                    executive_summary="LLM inference unavailable; degraded to static analysis evidence.",
                    findings=[],
                    raw_response=None,
                    provider=self.provider.provider_name,
                    model_used=self.provider.model_name,
                    prompt_version=PROMPT_VERSION,
                    duration_ms=duration_ms,
                    status="FALLBACK",
                    error_message=str(exc),
                )
            raise exc

        # 4. Parse & Validate Output
        try:
            summary, findings = self.parser.parse_and_validate(
                raw_text=raw_response,
                total_source_lines=source_file.line_count or 500,
            )
            duration_ms = (time.perf_counter() - start_time) * 1000.0

            return LLMReviewResult(
                success=True,
                executive_summary=summary,
                findings=findings,
                raw_response=raw_response,
                provider=self.provider.provider_name,
                model_used=self.provider.model_name,
                prompt_version=PROMPT_VERSION,
                duration_ms=duration_ms,
                status="COMPLETED",
            )
        except Exception as parse_exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.warning("Failed to parse LLM structured output: %s", parse_exc)

            if self.settings.ALLOW_STATIC_FALLBACK:
                return LLMReviewResult(
                    success=False,
                    executive_summary="LLM output could not be parsed into valid schema; falling back to static findings.",
                    findings=[],
                    raw_response=raw_response,
                    provider=self.provider.provider_name,
                    model_used=self.provider.model_name,
                    prompt_version=PROMPT_VERSION,
                    duration_ms=duration_ms,
                    status="FALLBACK",
                    error_message=f"Output parsing error: {parse_exc}",
                )
            raise parse_exc
