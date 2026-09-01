"""Application configuration management for ReviewAI."""

from functools import lru_cache
from typing import List
from pydantic import Field
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    # Fallback definition if pydantic-settings is not yet installed in local env
    from pydantic import BaseModel as BaseSettings  # type: ignore
    SettingsConfigDict = None  # type: ignore


class Settings(BaseSettings):
    """Central application settings loaded from environment variables."""

    # Application Environment
    APP_NAME: str = "ReviewAI"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = Field(default="development", description="Environment: development, staging, production, testing")
    DEBUG: bool = Field(default=False, description="Enable debug mode")

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    JSON_LOGS: bool = Field(default=False, description="Format logs as structured JSON")

    # Backend API Server Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API server host")
    API_PORT: int = Field(default=8000, description="API server port")
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 URL prefix")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )

    # Source Code Input Limits & Constraints
    MAX_SOURCE_LINES: int = Field(default=500, description="Maximum allowed lines in submitted code")
    MAX_SOURCE_SIZE: int = Field(default=65536, description="Maximum allowed code payload size in bytes (64KB)")

    # Static Analysis Configuration
    ENABLE_STATIC_ANALYSIS: bool = Field(default=True, description="Enable deterministic static analyzers")
    ENABLE_RUFF: bool = Field(default=True, description="Enable Ruff linter static analysis")
    ENABLE_BANDIT: bool = Field(default=True, description="Enable Bandit security static analysis")
    ENABLE_AST_RULES: bool = Field(default=True, description="Enable Custom AST rules static analysis")
    STATIC_ANALYZER_TIMEOUT: int = Field(default=15, description="Timeout in seconds for external static analyzer processes")
    ENABLED_ANALYZERS: List[str] = Field(
        default=["ast", "ruff", "bandit"],
        description="Active static analyzer identifiers"
    )

    # Static Analysis Rule Thresholds
    MAX_FUNCTION_COMPLEXITY: int = Field(default=10, description="Cyclomatic complexity threshold for RULE-010")
    MAX_NESTING_DEPTH: int = Field(default=4, description="Block nesting depth threshold for RULE-011")
    MAX_FUNCTION_PARAMETERS: int = Field(default=6, description="Parameter count threshold for RULE-012")
    STATIC_CONTEXT_LINES: int = Field(default=2, description="Surrounding code lines to extract for finding snippets")

    # LLM Provider Configuration
    ENABLE_LLM: bool = Field(default=True, description="Enable LLM reasoning layer")
    LLM_PROVIDER: str = Field(default="ollama", description="LLM provider: ollama, mock, custom")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="Ollama server endpoint")
    OLLAMA_MODEL: str = Field(default="qwen2.5-coder:7b-instruct", description="Model identifier")
    LLM_TIMEOUT: int = Field(default=60, description="LLM request timeout in seconds")
    LLM_TEMPERATURE: float = Field(default=0.1, description="Sampling temperature for code review")
    LLM_MAX_RETRIES: int = Field(default=2, description="Max retry attempts for malformed LLM responses")

    # Resilience: Static-Only Fallback
    ALLOW_STATIC_FALLBACK: bool = Field(
        default=True,
        description="Gracefully degrade to static-only findings when LLM is unavailable"
    )

    # Storage Repository Configuration
    STORAGE_TYPE: str = Field(default="in_memory", description="Storage backend: in_memory, sqlite, postgresql")
    STORAGE_DATABASE_URL: str = Field(default="sqlite:///./reviewai.db", description="Database connection URL")

    # Telemetry and Observability
    ENABLE_METRICS: bool = Field(default=True, description="Enable stage timing and request metrics")
    RECORD_STAGE_TIMINGS: bool = Field(default=True, description="Record millisecond duration per review stage")

    if SettingsConfigDict is not None:
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=True,
            extra="ignore",
        )


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
