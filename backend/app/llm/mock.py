"""Deterministic Mock LLM Provider for testing, offline execution, and fallback verification."""

import asyncio
import json
from typing import Any, Dict, List, Optional

from backend.app.core.errors import (
    LLMProviderError,
    LLMTimeoutError,
    LLMUnavailableError,
)
from backend.app.llm.base import LLMProvider, ModelMetadata


class MockLLMProvider(LLMProvider):
    """Configurable mock LLM provider returning predetermined JSON responses without external dependencies."""

    def __init__(
        self,
        model_name: str = "mock-qwen2.5-coder:7b",
        simulate_timeout: bool = False,
        simulate_unavailable: bool = False,
        simulate_malformed: bool = False,
        custom_response: Optional[str] = None,
        latency_ms: float = 5.0,
    ) -> None:
        self._model_name = model_name
        self.simulate_timeout = simulate_timeout
        self.simulate_unavailable = simulate_unavailable
        self.simulate_malformed = simulate_malformed
        self.custom_response = custom_response
        self.latency_ms = latency_ms

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return self._model_name

    async def check_health(self) -> bool:
        """Return False if simulated as unavailable, else True."""
        return not self.simulate_unavailable

    async def get_model_metadata(self) -> ModelMetadata:
        return ModelMetadata(
            provider_name=self.provider_name,
            model_name=self.model_name,
            context_window=8192,
            is_local=True,
            is_available=not self.simulate_unavailable,
            parameters={"mock": True, "latency_ms": self.latency_ms},
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Simulate LLM generation according to configuration."""
        if self.latency_ms > 0:
            await asyncio.sleep(self.latency_ms / 1000.0)

        if self.simulate_unavailable:
            raise LLMUnavailableError(provider="mock", url="mock://localhost")

        if self.simulate_timeout:
            raise LLMTimeoutError(provider="mock", timeout_seconds=1)

        if self.simulate_malformed:
            return "This is a conversational text response without valid JSON {malformed"

        if self.custom_response is not None:
            return self.custom_response

        # Default realistic mock code review response
        default_payload = {
            "executive_summary": "The code submission demonstrates basic functionality but contains critical security and correctness issues including dynamic code execution and mutable default parameters.",
            "findings": [
                {
                    "category": "security",
                    "severity": "high",
                    "title": "Unsanitized dynamic code execution via eval()",
                    "description": "Direct invocation of eval() executes arbitrary Python expressions supplied in user input.",
                    "line_number": 5,
                    "end_line": 5,
                    "code_evidence": "eval(user_input)",
                    "explanation": "eval() allows attackers to execute arbitrary system commands, bypass security boundaries, and leak secrets.",
                    "recommendation": "Use ast.literal_eval() for data literals or a dedicated mathematical expression parser.",
                    "suggested_fix": {
                        "original_snippet": "return eval(user_input)",
                        "replacement_snippet": "import ast\n    return ast.literal_eval(user_input)",
                        "explanation": "Safely parse literal data types without arbitrary execution."
                    },
                    "reasoning": "Dynamic code evaluation is one of the most critical security vulnerabilities in Python.",
                    "confidence": 0.95
                },
                {
                    "category": "bug",
                    "severity": "high",
                    "title": "Mutable default list argument causes state leakage",
                    "description": "Default list argument is evaluated once at function definition time and shared across invocations.",
                    "line_number": 8,
                    "end_line": 8,
                    "code_evidence": "def process(items=[]):",
                    "explanation": "Subsequent calls without passing items will accumulate items across calls rather than using a fresh list.",
                    "recommendation": "Use None as the default value and initialize with items = items or [] in the function body.",
                    "suggested_fix": {
                        "original_snippet": "def process(items=[]):",
                        "replacement_snippet": "def process(items: Optional[List[str]] = None):\n    items = list(items) if items is not None else []",
                        "explanation": "Initialize a fresh list on each call."
                    },
                    "reasoning": "Common Python pitfall where mutable objects retain state across function invocations.",
                    "confidence": 0.98
                }
            ]
        }
        return json.dumps(default_payload)
