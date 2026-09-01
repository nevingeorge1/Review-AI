"""LLM intelligence layer package for ReviewAI."""

from backend.app.llm.base import LLMProvider, ModelMetadata
from backend.app.llm.context import (
    CONTEXT_SCHEMA_VERSION,
    ContextFindingSummary,
    ContextSourceInfo,
    ContextStructuralInfo,
    ReviewContext,
    ReviewContextBuilder,
    ReviewPolicy,
)
from backend.app.llm.mock import MockLLMProvider
from backend.app.llm.models import (
    LLMRawFinding,
    LLMRawResponsePayload,
    LLMReviewResult,
    LLMSuggestedFix,
)
from backend.app.llm.ollama import OllamaProvider
from backend.app.llm.parser import LLMOutputParser
from backend.app.llm.prompts import PROMPT_VERSION, ReviewPromptBuilder
from backend.app.llm.service import LLMReviewService

__all__ = [
    # Contracts & Providers
    "LLMProvider",
    "ModelMetadata",
    "OllamaProvider",
    "MockLLMProvider",
    # Service
    "LLMReviewService",
    # Context & Prompts
    "CONTEXT_SCHEMA_VERSION",
    "PROMPT_VERSION",
    "ReviewContext",
    "ReviewContextBuilder",
    "ReviewPolicy",
    "ReviewPromptBuilder",
    "ContextFindingSummary",
    "ContextSourceInfo",
    "ContextStructuralInfo",
    # Parser & Models
    "LLMOutputParser",
    "LLMReviewResult",
    "LLMRawFinding",
    "LLMRawResponsePayload",
    "LLMSuggestedFix",
]
