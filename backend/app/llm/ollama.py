"""Local Ollama LLM provider communicating via safe HTTP endpoints."""

import time
from typing import Any, Dict, Optional
import httpx

from backend.app.core.config import Settings, get_settings
from backend.app.core.errors import (
    LLMProviderError,
    LLMTimeoutError,
    LLMUnavailableError,
)
from backend.app.core.logging import logger
from backend.app.llm.base import LLMProvider, ModelMetadata


class OllamaProvider(LLMProvider):
    """Local-first Ollama provider communicating with local open-weights code models."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.base_url = self.settings.OLLAMA_BASE_URL.rstrip("/")
        self._model_name = self.settings.OLLAMA_MODEL
        self.timeout = self.settings.LLM_TIMEOUT

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model_name

    async def check_health(self) -> bool:
        """Verify that the local Ollama server is active and reachable."""
        url = f"{self.base_url}/api/version"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(url)
                return res.status_code == 200
        except Exception:
            return False

    async def get_model_metadata(self) -> ModelMetadata:
        """Inspect model availability on the local Ollama daemon."""
        is_healthy = await self.check_health()
        return ModelMetadata(
            provider_name=self.provider_name,
            model_name=self.model_name,
            context_window=8192,
            is_local=True,
            is_available=is_healthy,
            parameters={
                "base_url": self.base_url,
                "temperature": self.settings.LLM_TEMPERATURE,
                "timeout": self.timeout,
            },
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Execute JSON-formatted text generation via local Ollama API.

        Raises:
            LLMUnavailableError: If Ollama daemon is offline or connection refused.
            LLMTimeoutError: If inference exceeds configured timeout.
            LLMProviderError: On internal server or API errors.
        """
        url = f"{self.base_url}/api/generate"
        temp = temperature if temperature is not None else self.settings.LLM_TEMPERATURE

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt or "",
            "stream": False,
            "format": "json",
            "options": {
                "temperature": temp,
            },
        }

        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                response = await client.post(url, json=payload)

                if response.status_code == 404:
                    raise LLMUnavailableError(
                        provider="ollama",
                        url=f"{self.base_url} (Model '{self.model_name}' not found on local Ollama)",
                    )
                elif response.status_code != 200:
                    raise LLMProviderError(
                        provider="ollama",
                        message=f"Ollama server returned HTTP {response.status_code}: {response.text[:200]}",
                    )

                data = response.json()
                raw_response = data.get("response", "")
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                logger.info("Ollama inference completed in %.2fms for model %s", duration_ms, self.model_name)
                return raw_response

        except (httpx.ConnectError, httpx.ConnectTimeout) as err:
            logger.warning("Ollama connection failed at %s: %s", self.base_url, err)
            raise LLMUnavailableError(provider="ollama", url=self.base_url) from err

        except (httpx.ReadTimeout, httpx.WriteTimeout) as err:
            logger.warning("Ollama inference timed out after %ds", self.timeout)
            raise LLMTimeoutError(provider="ollama", timeout_seconds=self.timeout) from err

        except LLMProviderError:
            raise

        except Exception as err:
            logger.error("Unexpected error during Ollama generation: %s", err, exc_info=True)
            raise LLMProviderError(provider="ollama", message=str(err)) from err
