"""
GPT-5 CEO Research Settings Configuration

This module provides configuration management for the GPT-5 CEO Research application
using Pydantic BaseSettings for environment variable loading and validation.
"""

from typing import Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables with validation.

    All settings can be provided via environment variables or .env file.
    """

    # OpenAI API Configuration
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key - must start with 'sk-'"
    )

    # GPT-5 Model Configuration
    gpt5_model: str = Field(
        default="gpt-5",
        description="GPT-5 model variant to use"
    )

    # Default Reasoning Configuration
    default_reasoning_effort: Literal["minimal", "low", "medium", "high"] = Field(
        default="medium",
        description="Default reasoning effort level"
    )

    # Output Verbosity
    default_verbosity: str = Field(
        default="medium",
        description="Default verbosity level for responses"
    )

    # API Request Configuration
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts for failed API requests"
    )

    timeout_seconds: int = Field(
        default=120,
        ge=1,
        le=600,
        description="Request timeout in seconds"
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )

    # Processing Configuration
    max_iterations: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Maximum number of iterations for iterative processes"
    )

    confidence_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence threshold for accepting results"
    )

    # Caching Configuration
    cache_ttl_hours: int = Field(
        default=24,
        ge=0,
        description="Time-to-live for cached responses in hours"
    )

    @field_validator('openai_api_key')
    @classmethod
    def validate_openai_api_key(cls, v: str) -> str:
        """Validate that OpenAI API key starts with 'sk-'."""
        if not v.startswith('sk-'):
            raise ValueError("OpenAI API key must start with 'sk-'")
        return v

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the standard Python logging levels."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v_upper

    @field_validator('default_verbosity')
    @classmethod
    def validate_verbosity(cls, v: str) -> str:
        """Validate verbosity level."""
        valid_levels = {"low", "medium", "high"}
        v_lower = v.lower()
        if v_lower not in valid_levels:
            raise ValueError(f"Verbosity level must be one of: {', '.join(valid_levels)}")
        return v_lower

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "env_prefix": ""
    }


# Global settings instance - lazy loaded to avoid import-time issues
_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the global settings instance (lazy loaded).

    Raises:
        pydantic_core.ValidationError: If required environment variables are missing or invalid.
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance


def reset_settings() -> None:
    """Reset the global settings instance to force reloading from environment."""
    global _settings_instance
    _settings_instance = None