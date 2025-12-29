"""
System constants for GPT-5 CEO Research application.

This module contains all system-wide constants including model names,
reasoning levels, verbosity levels, and API limits.
"""

from typing import Final

# GPT-5 Model Names
GPT_5_MODEL: Final[str] = "gpt-5"
GPT_5_MINI_MODEL: Final[str] = "gpt-5-mini"
GPT_5_NANO_MODEL: Final[str] = "gpt-5-nano"

# Model list for validation
GPT_5_MODELS: Final[tuple[str, ...]] = (
    GPT_5_MODEL,
    GPT_5_MINI_MODEL,
    GPT_5_NANO_MODEL,
)

# Reasoning Effort Levels
REASONING_MINIMAL: Final[str] = "minimal"
REASONING_LOW: Final[str] = "low"
REASONING_MEDIUM: Final[str] = "medium"
REASONING_HIGH: Final[str] = "high"

# Reasoning levels list for validation
REASONING_LEVELS: Final[tuple[str, ...]] = (
    REASONING_MINIMAL,
    REASONING_LOW,
    REASONING_MEDIUM,
    REASONING_HIGH,
)

# Verbosity Levels
VERBOSITY_LOW: Final[str] = "low"
VERBOSITY_MEDIUM: Final[str] = "medium"
VERBOSITY_HIGH: Final[str] = "high"

# Verbosity levels list for validation
VERBOSITY_LEVELS: Final[tuple[str, ...]] = (
    VERBOSITY_LOW,
    VERBOSITY_MEDIUM,
    VERBOSITY_HIGH,
)

# API Limits and Configuration
MAX_TOKENS: Final[int] = 4096
MAX_CONTEXT_LENGTH: Final[int] = 128000
MAX_RETRIES: Final[int] = 3
REQUEST_TIMEOUT: Final[int] = 60
RATE_LIMIT_DELAY: Final[float] = 1.0

# Response limits
MAX_RESPONSE_TOKENS: Final[int] = 4096
MIN_RESPONSE_TOKENS: Final[int] = 1

# Temperature and sampling constants
DEFAULT_TEMPERATURE: Final[float] = 0.7
MIN_TEMPERATURE: Final[float] = 0.0
MAX_TEMPERATURE: Final[float] = 2.0

DEFAULT_TOP_P: Final[float] = 0.9
MIN_TOP_P: Final[float] = 0.1
MAX_TOP_P: Final[float] = 1.0

# System operation constants
DEFAULT_VERBOSITY: Final[str] = VERBOSITY_MEDIUM
DEFAULT_REASONING: Final[str] = REASONING_MEDIUM
DEFAULT_MODEL: Final[str] = GPT_5_MODEL

# Cache and storage limits
MAX_CACHE_SIZE: Final[int] = 1000
CACHE_TTL_SECONDS: Final[int] = 3600

# File and data processing limits
MAX_FILE_SIZE_MB: Final[int] = 100
MAX_BATCH_SIZE: Final[int] = 50
MAX_CONCURRENT_REQUESTS: Final[int] = 10

# Logging levels
LOG_LEVEL_DEBUG: Final[str] = "DEBUG"
LOG_LEVEL_INFO: Final[str] = "INFO"
LOG_LEVEL_WARNING: Final[str] = "WARNING"
LOG_LEVEL_ERROR: Final[str] = "ERROR"

DEFAULT_LOG_LEVEL: Final[str] = LOG_LEVEL_INFO

# HTTP status codes for API responses
HTTP_OK: Final[int] = 200
HTTP_BAD_REQUEST: Final[int] = 400
HTTP_UNAUTHORIZED: Final[int] = 401
HTTP_FORBIDDEN: Final[int] = 403
HTTP_NOT_FOUND: Final[int] = 404
HTTP_RATE_LIMITED: Final[int] = 429
HTTP_INTERNAL_ERROR: Final[int] = 500
HTTP_SERVICE_UNAVAILABLE: Final[int] = 503