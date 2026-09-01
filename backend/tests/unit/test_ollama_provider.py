"""Unit tests for OllamaProvider with mocked HTTP endpoints."""

from unittest.mock import AsyncMock, patch
import httpx
import pytest
from backend.app.core.config import Settings
from backend.app.core.errors import LLMTimeoutError, LLMUnavailableError
from backend.app.llm.ollama import OllamaProvider


@pytest.fixture
def ollama_provider() -> OllamaProvider:
    settings = Settings(OLLAMA_BASE_URL="http://localhost:11434", OLLAMA_MODEL="qwen2.5-coder:7b-instruct", LLM_TIMEOUT=5)
    return OllamaProvider(settings=settings)


@pytest.mark.asyncio
async def test_ollama_provider_health_check_success(ollama_provider: OllamaProvider):
    mock_resp = AsyncMock()
    mock_resp.status_code = 200

    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_resp)):
        assert await ollama_provider.check_health() is True


@pytest.mark.asyncio
async def test_ollama_provider_health_check_failure(ollama_provider: OllamaProvider):
    with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("Connection refused")):
        assert await ollama_provider.check_health() is False


@pytest.mark.asyncio
async def test_ollama_provider_generate_success(ollama_provider: OllamaProvider):
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = AsyncMock(return_value={"response": '{"executive_summary": "All good", "findings": []}'})

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
        res = await ollama_provider.generate(prompt="test prompt")
        assert '{"executive_summary": "All good"' in res


@pytest.mark.asyncio
async def test_ollama_provider_connection_error_raises_unavailable(ollama_provider: OllamaProvider):
    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused")):
        with pytest.raises(LLMUnavailableError):
            await ollama_provider.generate(prompt="test prompt")


@pytest.mark.asyncio
async def test_ollama_provider_timeout_raises_timeout(ollama_provider: OllamaProvider):
    with patch("httpx.AsyncClient.post", side_effect=httpx.ReadTimeout("Read timeout")):
        with pytest.raises(LLMTimeoutError):
            await ollama_provider.generate(prompt="test prompt")
