"""Abstract LLM Provider interface for ReviewAI.

Decouples core review reasoning from any specific LLM technology (Ollama, Mock).
Supports local-first execution and graceful Static-Only fallback mode.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.app.llm.models import LLMReviewResult
from backend.app.models.domain import SourceFile, StaticFinding


class ModelMetadata(BaseModel):
    """Metadata describing an LLM provider and active model."""
    provider_name: str = Field(..., description="Provider identifier (e.g. 'ollama', 'mock')")
    model_name: str = Field(..., description="Model name (e.g. 'qwen2.5-coder:7b-instruct')")
    context_window: int = Field(default=8192, description="Supported context window tokens")
    is_local: bool = Field(default=True, description="True if inference is performed entirely locally")
    is_available: bool = Field(default=True, description="Current availability status")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Optional runtime parameters")


class LLMProvider(ABC):
    """Abstract interface for LLM code review inference providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the unique provider name."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the configured model identifier."""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """
        Verify if the LLM backend is healthy and responding.
        Returns True if operational, False otherwise.
        """
        pass

    @abstractmethod
    async def get_model_metadata(self) -> ModelMetadata:
        """Return metadata about the current model and provider status."""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Execute raw text generation against the LLM model.

        Args:
            prompt: User/review payload prompt.
            system_prompt: Optional system instructions.
            temperature: Optional sampling temperature override.

        Returns:
            Raw response text from the LLM.

        Raises:
            LLMUnavailableError: If the provider is unreachable.
            LLMTimeoutError: If the request exceeds timeout limits.
            LLMProviderError: If the provider encounters an internal error.
        """
        pass
