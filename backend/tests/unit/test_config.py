"""Unit tests for configuration loading and limits."""

import pytest
from backend.app.core.config import Settings


class TestConfiguration:
    """Test environment and settings management."""

    def test_default_settings(self):
        settings = Settings()
        assert settings.APP_NAME == "ReviewAI"
        assert settings.MAX_SOURCE_LINES == 500
        assert settings.MAX_SOURCE_SIZE == 65536
        assert settings.ENABLE_STATIC_ANALYSIS is True
        assert settings.ENABLE_LLM is True
        assert settings.ALLOW_STATIC_FALLBACK is True
        assert settings.OLLAMA_MODEL == "qwen2.5-coder:7b-instruct"

    def test_custom_overrides(self):
        settings = Settings(
            APP_ENV="production",
            MAX_SOURCE_LINES=1000,
            MAX_SOURCE_SIZE=131072,
            ENABLE_LLM=False,
        )
        assert settings.APP_ENV == "production"
        assert settings.MAX_SOURCE_LINES == 1000
        assert settings.MAX_SOURCE_SIZE == 131072
        assert settings.ENABLE_LLM is False
