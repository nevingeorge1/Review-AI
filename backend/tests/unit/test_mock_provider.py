"""Unit tests for MockLLMProvider (health, generation, timeout, unavailable)."""

import pytest
from backend.app.core.errors import LLMTimeoutError, LLMUnavailableError
from backend.app.llm.mock import MockLLMProvider


@pytest.mark.asyncio
async def test_mock_provider_success():
    provider = MockLLMProvider(latency_ms=1.0)
    assert await provider.check_health() is True
    metadata = await provider.get_model_metadata()
    assert metadata.provider_name == "mock"
    assert metadata.is_available is True

    response = await provider.generate("review this code")
    assert "eval()" in response
    assert "items=[]" in response


@pytest.mark.asyncio
async def test_mock_provider_timeout_simulation():
    provider = MockLLMProvider(simulate_timeout=True, latency_ms=1.0)
    with pytest.raises(LLMTimeoutError):
        await provider.generate("review this code")


@pytest.mark.asyncio
async def test_mock_provider_unavailable_simulation():
    provider = MockLLMProvider(simulate_unavailable=True, latency_ms=1.0)
    assert await provider.check_health() is False
    with pytest.raises(LLMUnavailableError):
        await provider.generate("review this code")
