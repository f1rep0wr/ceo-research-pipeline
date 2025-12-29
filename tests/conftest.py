"""
Test configuration and fixtures for pytest.

This module provides common fixtures and test configuration for the GPT-5 CEO Research
application tests. All fixtures follow KISS principles - simple, clear, and useful.
"""

import asyncio
import tempfile
import shutil
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator, Dict, Any
from unittest.mock import Mock, AsyncMock, patch

import pytest
from pydantic import ValidationError

from src.config.settings import Settings
from src.clients.gpt5_client import GPT5ResponsesClient


# Configure pytest-asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create an event loop for async tests.

    Using session scope to avoid creating new event loops for each test,
    which can cause issues with async fixtures.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def mock_settings() -> Settings:
    """
    Provide a test Settings instance with valid test values.

    This fixture creates a Settings instance with safe test values that don't
    require real API keys or external dependencies.

    Returns:
        Settings: Configured settings instance for testing
    """
    return Settings(
        openai_api_key="sk-test-key-for-testing-1234567890abcdef",
        gpt5_model="gpt-5",
        default_reasoning_effort="medium",
        default_verbosity="medium",
        max_retries=2,  # Lower for faster tests
        timeout_seconds=30,  # Lower for faster tests
        log_level="DEBUG",
        max_iterations=3,  # Lower for faster tests
        confidence_threshold=0.8,
        cache_ttl_hours=1  # Lower for testing
    )


@pytest.fixture
def mock_settings_no_api_key() -> Settings:
    """
    Provide a test Settings instance without API key for testing error conditions.

    Returns:
        Settings: Settings instance with invalid/missing API key
    """
    # Create a settings instance and manually set the invalid API key
    # This bypasses validation for testing purposes
    settings = Settings(
        openai_api_key="sk-placeholder-for-testing",  # Valid format to pass validation
        gpt5_model="gpt-5",
        default_reasoning_effort="medium",
        default_verbosity="medium",
        max_retries=2,
        timeout_seconds=30,
        log_level="DEBUG",
        max_iterations=3,
        confidence_threshold=0.8,
        cache_ttl_hours=1
    )
    # Override with invalid key after creation
    settings.openai_api_key = "invalid-key"
    return settings


@pytest.fixture
def mock_gpt5_response() -> Dict[str, Any]:
    """
    Provide a mock GPT-5 API response for testing.

    Returns:
        Dict: Mock response data structure matching GPT-5 API format
    """
    return {
        "id": "response-test-12345",
        "object": "response",
        "created": 1234567890,
        "model": "gpt-5",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from GPT-5."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        },
        "reasoning": {
            "effort": "medium",
            "tokens": 50
        }
    }


@pytest.fixture
def mock_openai_client() -> Mock:
    """
    Provide a mocked AsyncOpenAI client for testing.

    Returns:
        Mock: Mocked OpenAI client with async methods
    """
    mock_client = Mock()
    mock_client.responses = Mock()
    mock_client.responses.create = AsyncMock()
    return mock_client


@pytest.fixture
def mock_gpt5_client(mock_settings: Settings, mock_gpt5_response: Dict[str, Any]) -> Mock:
    """
    Provide a mocked GPT5ResponsesClient for testing.

    This fixture creates a fully mocked client that can be used in tests without
    making real API calls. The client is configured to return test responses.

    Args:
        mock_settings: Test settings fixture
        mock_gpt5_response: Mock response data

    Returns:
        Mock: Mocked GPT5ResponsesClient instance
    """
    mock_client = Mock(spec=GPT5ResponsesClient)

    # Set up basic properties
    mock_client.settings = mock_settings
    mock_client.conversation_states = {}
    mock_client.is_ready = True

    # Mock async methods
    mock_client.test_connection = AsyncMock(return_value=True)
    mock_client.create_response = AsyncMock(return_value=Mock(**mock_gpt5_response))

    # Mock conversation state methods
    mock_client.get_conversation_state = Mock(return_value=None)
    mock_client.set_conversation_state = Mock()
    mock_client.clear_conversation_state = Mock(return_value=True)
    mock_client.clear_all_conversation_states = Mock(return_value=0)

    return mock_client


@pytest.fixture
async def mock_gpt5_client_async(mock_settings: Settings, mock_gpt5_response: Dict[str, Any]) -> AsyncGenerator[Mock, None]:
    """
    Provide an async-compatible mocked GPT5ResponsesClient for testing.

    This fixture is useful for tests that need to await client creation or
    perform async setup/teardown operations.

    Args:
        mock_settings: Test settings fixture
        mock_gpt5_response: Mock response data

    Yields:
        Mock: Mocked GPT5ResponsesClient instance
    """
    mock_client = Mock(spec=GPT5ResponsesClient)

    # Set up basic properties
    mock_client.settings = mock_settings
    mock_client.conversation_states = {}
    mock_client.is_ready = True

    # Mock async methods
    mock_client.test_connection = AsyncMock(return_value=True)
    mock_client.create_response = AsyncMock(return_value=Mock(**mock_gpt5_response))

    # Mock conversation state methods
    mock_client.get_conversation_state = Mock(return_value=None)
    mock_client.set_conversation_state = Mock()
    mock_client.clear_conversation_state = Mock(return_value=True)
    mock_client.clear_all_conversation_states = Mock(return_value=0)

    yield mock_client

    # Async cleanup if needed
    # In this case, no cleanup is required for the mock


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """
    Provide a temporary directory for tests that need file system operations.

    The directory is automatically cleaned up after the test.

    Yields:
        Path: Path to the temporary directory
    """
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_file(temp_dir: Path) -> Path:
    """
    Provide a temporary file path within a temporary directory.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path: Path to a temporary file (not created yet)
    """
    return temp_dir / "test_file.txt"


@pytest.fixture
def sample_conversation_id() -> str:
    """
    Provide a sample conversation ID for testing.

    Returns:
        str: Test conversation identifier
    """
    return "test-conversation-12345"


@pytest.fixture
def sample_prompt() -> str:
    """
    Provide a sample prompt for testing GPT-5 interactions.

    Returns:
        str: Test prompt text
    """
    return "This is a test prompt for GPT-5 API testing."


@pytest.fixture
def mock_env_vars(monkeypatch) -> Dict[str, str]:
    """
    Provide mocked environment variables for testing.

    This fixture sets up environment variables that can be used by Settings
    without requiring real credentials or configuration.

    Args:
        monkeypatch: pytest monkeypatch fixture

    Returns:
        Dict[str, str]: Dictionary of environment variables set
    """
    env_vars = {
        "OPENAI_API_KEY": "sk-test-key-for-testing-1234567890abcdef",
        "GPT5_MODEL": "gpt-5",
        "DEFAULT_REASONING_EFFORT": "medium",
        "DEFAULT_VERBOSITY": "medium",
        "MAX_RETRIES": "2",
        "TIMEOUT_SECONDS": "30",
        "LOG_LEVEL": "DEBUG",
        "MAX_ITERATIONS": "3",
        "CONFIDENCE_THRESHOLD": "0.8",
        "CACHE_TTL_HOURS": "1"
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars


@pytest.fixture
def settings_from_env(mock_env_vars: Dict[str, str]) -> Settings:
    """
    Provide Settings instance loaded from mocked environment variables.

    This fixture demonstrates how Settings loads from environment variables
    and can be used to test that behavior.

    Args:
        mock_env_vars: Mocked environment variables

    Returns:
        Settings: Settings instance loaded from environment
    """
    return Settings()


# Utility functions for tests (not fixtures, but commonly used)

def assert_valid_settings(settings: Settings) -> None:
    """
    Assert that a Settings instance has valid configuration for testing.

    This helper function can be used in tests to verify that settings
    are properly configured.

    Args:
        settings: Settings instance to validate

    Raises:
        AssertionError: If settings are not valid for testing
    """
    assert settings.openai_api_key.startswith("sk-")
    assert settings.gpt5_model in ["gpt-5"]
    assert settings.default_reasoning_effort in ["minimal", "low", "medium", "high"]
    assert settings.max_retries >= 0
    assert settings.timeout_seconds > 0
    assert 0.0 <= settings.confidence_threshold <= 1.0


def create_mock_response(
    content: str = "Test response",
    response_id: str = "test-response-12345",
    conversation_id: str = None
) -> Mock:
    """
    Create a mock response object for testing.

    This utility function creates mock response objects that match the expected
    structure of GPT-5 API responses.

    Args:
        content: Response content text
        response_id: Response ID
        conversation_id: Optional conversation ID

    Returns:
        Mock: Mock response object
    """
    mock_response = Mock()
    mock_response.id = response_id
    mock_response.choices = [
        Mock(message=Mock(content=content))
    ]
    if conversation_id:
        mock_response.conversation_id = conversation_id

    return mock_response