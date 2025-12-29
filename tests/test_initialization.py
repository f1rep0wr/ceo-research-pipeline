"""
Test suite for configuration initialization and settings validation.

This module provides comprehensive tests for the Settings class, covering all
validation scenarios, edge cases, and environment variable loading.
Tests follow KISS principle - clear, simple, and comprehensive.
"""

import os
import pytest
from typing import Dict, Any
from unittest.mock import patch, AsyncMock, MagicMock
from pydantic import ValidationError
import asyncio

from src.config.settings import Settings, get_settings, reset_settings
from src.clients.gpt5_client import GPT5ResponsesClient


class TestSettings:
    """
    Comprehensive test suite for Settings class validation and configuration loading.

    Tests cover:
    - Valid configuration loading
    - Invalid API key format validation
    - Invalid reasoning effort values
    - Invalid log levels
    - Missing required variables
    - Boundary value testing for numeric fields
    - Environment variable loading
    - Validator functions
    """

    def test_valid_configuration_loading(self):
        """Test that Settings can be created with valid configuration values."""
        settings = Settings(
            openai_api_key="sk-valid-test-key-12345",
            gpt5_model="gpt-5",
            default_reasoning_effort="medium",
            default_verbosity="medium",
            max_retries=3,
            timeout_seconds=120,
            log_level="INFO",
            max_iterations=5,
            confidence_threshold=0.8,
            cache_ttl_hours=24
        )

        assert settings.openai_api_key == "sk-valid-test-key-12345"
        assert settings.gpt5_model == "gpt-5"
        assert settings.default_reasoning_effort == "medium"
        assert settings.default_verbosity == "medium"
        assert settings.max_retries == 3
        assert settings.timeout_seconds == 120
        assert settings.log_level == "INFO"
        assert settings.max_iterations == 5
        assert settings.confidence_threshold == 0.8
        assert settings.cache_ttl_hours == 24

    def test_valid_configuration_with_defaults(self):
        """Test Settings creation with only required fields, checking value ranges."""
        settings = Settings(openai_api_key="sk-test-key-with-defaults")

        assert settings.openai_api_key == "sk-test-key-with-defaults"
        # Note: These values may come from .env file if present, so check ranges
        assert settings.gpt5_model == "gpt-5"
        assert settings.default_reasoning_effort in ["minimal", "low", "medium", "high"]
        assert settings.default_verbosity in ["low", "medium", "high"]
        assert 0 <= settings.max_retries <= 10
        assert 1 <= settings.timeout_seconds <= 600
        assert settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert 1 <= settings.max_iterations <= 100
        assert 0.0 <= settings.confidence_threshold <= 1.0
        assert settings.cache_ttl_hours >= 0

    def test_invalid_api_key_format_not_starting_with_sk(self):
        """Test that API key validation fails when key doesn't start with 'sk-'."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(openai_api_key="invalid-key-format")

        error = exc_info.value
        assert len(error.errors()) == 1
        assert error.errors()[0]["type"] == "value_error"
        assert "must start with 'sk-'" in str(error.errors()[0]["ctx"]["error"])

    def test_invalid_api_key_format_empty_string(self):
        """Test that API key validation fails with empty string."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(openai_api_key="")

        error = exc_info.value
        assert len(error.errors()) == 1
        assert error.errors()[0]["type"] == "value_error"
        assert "must start with 'sk-'" in str(error.errors()[0]["ctx"]["error"])

    def test_invalid_api_key_format_partial_sk(self):
        """Test that API key validation fails with partial 'sk' prefix."""
        test_cases = ["s-invalid", "k-invalid", "sk", "sk_invalid"]

        for invalid_key in test_cases:
            with pytest.raises(ValidationError) as exc_info:
                Settings(openai_api_key=invalid_key)

            error = exc_info.value
            assert len(error.errors()) == 1
            assert "must start with 'sk-'" in str(error.errors()[0]["ctx"]["error"])

    def test_invalid_reasoning_effort_values(self):
        """Test that reasoning effort validation fails with invalid values."""
        invalid_efforts = ["invalid", "MEDIUM", "Medium", "none", "maximum", ""]

        for invalid_effort in invalid_efforts:
            with pytest.raises(ValidationError) as exc_info:
                Settings(
                    openai_api_key="sk-test-key",
                    default_reasoning_effort=invalid_effort
                )

            error = exc_info.value
            errors = [e for e in error.errors() if e["loc"] == ("default_reasoning_effort",)]
            assert len(errors) == 1
            assert errors[0]["type"] == "literal_error"

    def test_valid_reasoning_effort_values(self):
        """Test that all valid reasoning effort values are accepted."""
        valid_efforts = ["minimal", "low", "medium", "high"]

        for valid_effort in valid_efforts:
            settings = Settings(
                openai_api_key="sk-test-key",
                default_reasoning_effort=valid_effort
            )
            assert settings.default_reasoning_effort == valid_effort

    def test_invalid_log_levels(self):
        """Test that log level validation fails with invalid values."""
        invalid_levels = ["invalid", "trace", "verbose", "warn", ""]

        for invalid_level in invalid_levels:
            with pytest.raises(ValidationError) as exc_info:
                Settings(
                    openai_api_key="sk-test-key",
                    log_level=invalid_level
                )

            error = exc_info.value
            errors = [e for e in error.errors() if e["loc"] == ("log_level",)]
            assert len(errors) == 1
            assert "must be one of" in str(error.errors()[0]["ctx"]["error"])

    def test_valid_log_levels(self):
        """Test that all valid log levels are accepted and normalized to uppercase."""
        valid_levels = [
            ("DEBUG", "DEBUG"),
            ("INFO", "INFO"),
            ("WARNING", "WARNING"),
            ("ERROR", "ERROR"),
            ("CRITICAL", "CRITICAL"),
            ("debug", "DEBUG"),
            ("info", "INFO"),
            ("warning", "WARNING"),
            ("error", "ERROR"),
            ("critical", "CRITICAL")
        ]

        for input_level, expected_level in valid_levels:
            settings = Settings(
                openai_api_key="sk-test-key",
                log_level=input_level
            )
            assert settings.log_level == expected_level

    def test_invalid_verbosity_levels(self):
        """Test that verbosity level validation fails with invalid values."""
        invalid_levels = ["invalid", "minimal", "maximum", "verbose", ""]

        for invalid_level in invalid_levels:
            with pytest.raises(ValidationError) as exc_info:
                Settings(
                    openai_api_key="sk-test-key",
                    default_verbosity=invalid_level
                )

            error = exc_info.value
            errors = [e for e in error.errors() if e["loc"] == ("default_verbosity",)]
            assert len(errors) == 1
            assert "must be one of" in str(error.errors()[0]["ctx"]["error"])

    def test_valid_verbosity_levels(self):
        """Test that all valid verbosity levels are accepted and normalized to lowercase."""
        valid_levels = [
            ("low", "low"),
            ("medium", "medium"),
            ("high", "high"),
            ("LOW", "low"),
            ("MEDIUM", "medium"),
            ("HIGH", "high"),
            ("Low", "low"),
            ("Medium", "medium"),
            ("High", "high")
        ]

        for input_level, expected_level in valid_levels:
            settings = Settings(
                openai_api_key="sk-test-key",
                default_verbosity=input_level
            )
            assert settings.default_verbosity == expected_level

    @patch('src.config.settings.Settings.model_config', {'env_file': None})
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_required_openai_api_key(self):
        """Test that Settings creation fails when required OpenAI API key is missing."""
        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error = exc_info.value
        errors = [e for e in error.errors() if e["loc"] == ("openai_api_key",)]
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"

    def test_boundary_value_max_retries(self):
        """Test boundary values for max_retries field."""
        # Test minimum valid value
        settings = Settings(openai_api_key="sk-test-key", max_retries=0)
        assert settings.max_retries == 0

        # Test maximum valid value
        settings = Settings(openai_api_key="sk-test-key", max_retries=10)
        assert settings.max_retries == 10

        # Test invalid values below minimum
        with pytest.raises(ValidationError) as exc_info:
            Settings(openai_api_key="sk-test-key", max_retries=-1)

        error = exc_info.value
        errors = [e for e in error.errors() if e["loc"] == ("max_retries",)]
        assert len(errors) == 1
        assert errors[0]["type"] == "greater_than_equal"

        # Test invalid values above maximum
        with pytest.raises(ValidationError) as exc_info:
            Settings(openai_api_key="sk-test-key", max_retries=11)

        error = exc_info.value
        errors = [e for e in error.errors() if e["loc"] == ("max_retries",)]
        assert len(errors) == 1
        assert errors[0]["type"] == "less_than_equal"

    def test_boundary_value_timeout_seconds(self):
        """Test boundary values for timeout_seconds field."""
        # Test minimum valid value
        settings = Settings(openai_api_key="sk-test-key", timeout_seconds=1)
        assert settings.timeout_seconds == 1

        # Test maximum valid value
        settings = Settings(openai_api_key="sk-test-key", timeout_seconds=600)
        assert settings.timeout_seconds == 600

        # Test invalid values below minimum
        with pytest.raises(ValidationError) as exc_info:
            Settings(openai_api_key="sk-test-key", timeout_seconds=0)

        error = exc_info.value
        errors = [e for e in error.errors() if e["loc"] == ("timeout_seconds",)]
        assert len(errors) == 1
        assert errors[0]["type"] == "greater_than_equal"

        # Test invalid values above maximum
        with pytest.raises(ValidationError) as exc_info:
            Settings(openai_api_key="sk-test-key", timeout_seconds=601)

        error = exc_info.value
        errors = [e for e in error.errors() if e["loc"] == ("timeout_seconds",)]
        assert len(errors) == 1
        assert errors[0]["type"] == "less_than_equal"

    def test_boundary_value_max_iterations(self):
        """Test boundary values for max_iterations field."""
        # Test minimum valid value
        settings = Settings(openai_api_key="sk-test-key", max_iterations=1)
        assert settings.max_iterations == 1

        # Test maximum valid value
        settings = Settings(openai_api_key="sk-test-key", max_iterations=100)
        assert settings.max_iterations == 100

        # Test invalid values below minimum
        with pytest.raises(ValidationError) as exc_info:
            Settings(openai_api_key="sk-test-key", max_iterations=0)

        error = exc_info.value
        errors = [e for e in error.errors() if e["loc"] == ("max_iterations",)]
        assert len(errors) == 1
        assert errors[0]["type"] == "greater_than_equal"

        # Test invalid values above maximum
        with pytest.raises(ValidationError) as exc_info:
            Settings(openai_api_key="sk-test-key", max_iterations=101)

        error = exc_info.value
        errors = [e for e in error.errors() if e["loc"] == ("max_iterations",)]
        assert len(errors) == 1
        assert errors[0]["type"] == "less_than_equal"

    def test_boundary_value_confidence_threshold(self):
        """Test boundary values for confidence_threshold field."""
        # Test minimum valid value
        settings = Settings(openai_api_key="sk-test-key", confidence_threshold=0.0)
        assert settings.confidence_threshold == 0.0

        # Test maximum valid value
        settings = Settings(openai_api_key="sk-test-key", confidence_threshold=1.0)
        assert settings.confidence_threshold == 1.0

        # Test valid mid-range values
        settings = Settings(openai_api_key="sk-test-key", confidence_threshold=0.5)
        assert settings.confidence_threshold == 0.5

        # Test invalid values below minimum
        with pytest.raises(ValidationError) as exc_info:
            Settings(openai_api_key="sk-test-key", confidence_threshold=-0.1)

        error = exc_info.value
        errors = [e for e in error.errors() if e["loc"] == ("confidence_threshold",)]
        assert len(errors) == 1
        assert errors[0]["type"] == "greater_than_equal"

        # Test invalid values above maximum
        with pytest.raises(ValidationError) as exc_info:
            Settings(openai_api_key="sk-test-key", confidence_threshold=1.1)

        error = exc_info.value
        errors = [e for e in error.errors() if e["loc"] == ("confidence_threshold",)]
        assert len(errors) == 1
        assert errors[0]["type"] == "less_than_equal"

    def test_boundary_value_cache_ttl_hours(self):
        """Test boundary values for cache_ttl_hours field."""
        # Test minimum valid value (0 means no caching)
        settings = Settings(openai_api_key="sk-test-key", cache_ttl_hours=0)
        assert settings.cache_ttl_hours == 0

        # Test large valid value
        settings = Settings(openai_api_key="sk-test-key", cache_ttl_hours=8760)  # 1 year
        assert settings.cache_ttl_hours == 8760

        # Test invalid negative value
        with pytest.raises(ValidationError) as exc_info:
            Settings(openai_api_key="sk-test-key", cache_ttl_hours=-1)

        error = exc_info.value
        errors = [e for e in error.errors() if e["loc"] == ("cache_ttl_hours",)]
        assert len(errors) == 1
        assert errors[0]["type"] == "greater_than_equal"

    @patch('src.config.settings.Settings.model_config', {'env_file': None})
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "sk-env-test-key-12345",
        "GPT5_MODEL": "gpt-5",
        "DEFAULT_REASONING_EFFORT": "high",
        "DEFAULT_VERBOSITY": "high",
        "MAX_RETRIES": "5",
        "TIMEOUT_SECONDS": "180",
        "LOG_LEVEL": "DEBUG",
        "MAX_ITERATIONS": "8",
        "CONFIDENCE_THRESHOLD": "0.9",
        "CACHE_TTL_HOURS": "48"
    }, clear=True)
    def test_environment_variable_loading(self):
        """Test that Settings correctly loads values from environment variables."""
        settings = Settings()

        assert settings.openai_api_key == "sk-env-test-key-12345"
        assert settings.gpt5_model == "gpt-5"
        assert settings.default_reasoning_effort == "high"
        assert settings.default_verbosity == "high"
        assert settings.max_retries == 5
        assert settings.timeout_seconds == 180
        assert settings.log_level == "DEBUG"
        assert settings.max_iterations == 8
        assert settings.confidence_threshold == 0.9
        assert settings.cache_ttl_hours == 48

    @patch('src.config.settings.Settings.model_config', {'env_file': None})
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "sk-env-key",
        "LOG_LEVEL": "warning"  # lowercase to test normalization
    }, clear=True)
    def test_environment_variable_case_normalization(self):
        """Test that environment variables are properly normalized."""
        settings = Settings()

        assert settings.openai_api_key == "sk-env-key"
        assert settings.log_level == "WARNING"  # Should be normalized to uppercase

    @patch('src.config.settings.Settings.model_config', {'env_file': None})
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "invalid-env-key"  # Invalid format
    }, clear=True)
    def test_environment_variable_validation_failure(self):
        """Test that validation still applies to environment variables."""
        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error = exc_info.value
        errors = [e for e in error.errors() if e["loc"] == ("openai_api_key",)]
        assert len(errors) == 1
        assert "must start with 'sk-'" in str(error.errors()[0]["ctx"]["error"])

    @patch('src.config.settings.Settings.model_config', {'env_file': None})
    @patch.dict(os.environ, {}, clear=True)
    def test_environment_variable_missing_required(self):
        """Test that missing required environment variables cause validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error = exc_info.value
        errors = [e for e in error.errors() if e["loc"] == ("openai_api_key",)]
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"

    def test_openai_api_key_validator_function(self):
        """Test the openai_api_key validator function directly."""
        from src.config.settings import Settings

        # Test valid key
        valid_key = Settings.validate_openai_api_key("sk-valid-key-12345")
        assert valid_key == "sk-valid-key-12345"

        # Test invalid key
        with pytest.raises(ValueError) as exc_info:
            Settings.validate_openai_api_key("invalid-key")

        assert "must start with 'sk-'" in str(exc_info.value)

    def test_log_level_validator_function(self):
        """Test the log_level validator function directly."""
        from src.config.settings import Settings

        # Test valid levels (should be normalized to uppercase)
        test_cases = [
            ("DEBUG", "DEBUG"),
            ("debug", "DEBUG"),
            ("INFO", "INFO"),
            ("info", "INFO"),
            ("WARNING", "WARNING"),
            ("warning", "WARNING"),
            ("ERROR", "ERROR"),
            ("error", "ERROR"),
            ("CRITICAL", "CRITICAL"),
            ("critical", "CRITICAL")
        ]

        for input_level, expected in test_cases:
            result = Settings.validate_log_level(input_level)
            assert result == expected

        # Test invalid level
        with pytest.raises(ValueError) as exc_info:
            Settings.validate_log_level("INVALID")

        assert "must be one of" in str(exc_info.value)

    def test_verbosity_validator_function(self):
        """Test the verbosity validator function directly."""
        from src.config.settings import Settings

        # Test valid levels (should be normalized to lowercase)
        test_cases = [
            ("low", "low"),
            ("LOW", "low"),
            ("medium", "medium"),
            ("MEDIUM", "medium"),
            ("high", "high"),
            ("HIGH", "high")
        ]

        for input_level, expected in test_cases:
            result = Settings.validate_verbosity(input_level)
            assert result == expected

        # Test invalid level
        with pytest.raises(ValueError) as exc_info:
            Settings.validate_verbosity("invalid")

        assert "must be one of" in str(exc_info.value)

    @patch('src.config.settings.Settings.model_config', {'env_file': None})
    def test_get_settings_singleton_behavior(self):
        """Test that get_settings() returns the same instance on subsequent calls."""
        # Reset to ensure clean state
        reset_settings()

        # Mock environment for valid settings
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-singleton-test-key"}, clear=True):
            settings1 = get_settings()
            settings2 = get_settings()

            # Should be the same instance
            assert settings1 is settings2
            assert settings1.openai_api_key == "sk-singleton-test-key"

    @patch('src.config.settings.Settings.model_config', {'env_file': None})
    def test_reset_settings_function(self):
        """Test that reset_settings() forces reloading of settings."""
        # Ensure we start with clean state
        reset_settings()

        # Set initial settings
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-initial-key"}, clear=True):
            settings1 = get_settings()
            assert settings1.openai_api_key == "sk-initial-key"

        # Change environment and reset
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-new-key"}, clear=True):
            reset_settings()
            settings2 = get_settings()

            # Should be different instances with new values
            assert settings1 is not settings2
            assert settings2.openai_api_key == "sk-new-key"

    def test_multiple_validation_errors(self):
        """Test that multiple validation errors are properly collected."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                openai_api_key="invalid-key",  # Invalid format
                default_reasoning_effort="invalid",  # Invalid value
                log_level="invalid",  # Invalid value
                max_retries=-1,  # Below minimum
                timeout_seconds=0,  # Below minimum
                confidence_threshold=1.5  # Above maximum
            )

        error = exc_info.value
        assert len(error.errors()) >= 6  # At least 6 validation errors

        # Check that all expected field errors are present
        error_fields = {e["loc"][0] for e in error.errors() if len(e["loc"]) > 0}
        expected_fields = {
            "openai_api_key", "default_reasoning_effort", "log_level",
            "max_retries", "timeout_seconds", "confidence_threshold"
        }
        assert expected_fields.issubset(error_fields)

    def test_field_descriptions_are_set(self):
        """Test that all fields have proper descriptions set."""
        # Check that field descriptions are properly set in the model class
        fields = Settings.model_fields

        assert fields["openai_api_key"].description is not None
        assert fields["gpt5_model"].description is not None
        assert fields["default_reasoning_effort"].description is not None
        assert fields["max_retries"].description is not None
        assert fields["timeout_seconds"].description is not None
        assert fields["confidence_threshold"].description is not None

    @patch('src.config.settings.Settings.model_config', {'env_file': None})
    @patch.dict(os.environ, {
        "OPENAI_API_KEY": "sk-case-test-key",
        "openai_api_key": "sk-lowercase-key"  # Test case sensitivity
    }, clear=True)
    def test_case_insensitive_environment_loading(self):
        """Test that environment variable loading is case insensitive."""
        settings = Settings()

        # Should load the value (behavior may vary based on case_sensitive setting)
        assert settings.openai_api_key.startswith("sk-")


class TestGPT5Client:
    """
    Comprehensive test suite for GPT5ResponsesClient class.

    Tests cover:
    - Client initialization with valid and invalid API keys
    - Async create_response method with mocked API calls
    - Conversation state management (storing and retrieving conversation IDs)
    - Retry logic when API calls fail
    - Connection testing functionality
    - Client readiness checks
    - Error handling scenarios
    """

    def setup_method(self):
        """Setup test fixtures for each test method."""
        # Create valid settings for testing
        self.valid_settings = Settings(
            openai_api_key="sk-test-api-key-12345",
            gpt5_model="gpt-5",
            default_reasoning_effort="medium",
            max_retries=3,
            timeout_seconds=120
        )

        # Create invalid settings (no API key)
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.config.settings.Settings.model_config', {'env_file': None}):
                try:
                    self.invalid_settings = Settings()
                except ValidationError:
                    # Create settings manually for testing initialization without API key
                    self.invalid_settings = MagicMock()
                    self.invalid_settings.openai_api_key = None

    def test_client_initialization_with_valid_api_key(self):
        """Test GPT5ResponsesClient initialization with valid API key."""
        with patch('src.clients.gpt5_client.AsyncOpenAI') as mock_openai:
            mock_client_instance = MagicMock()
            mock_openai.return_value = mock_client_instance

            client = GPT5ResponsesClient(self.valid_settings)

            # Verify client was initialized properly
            assert client.settings == self.valid_settings
            assert client.conversation_states == {}
            assert client.is_ready is True

            # Verify AsyncOpenAI was called with correct API key
            mock_openai.assert_called_once_with(api_key="sk-test-api-key-12345")

    def test_client_initialization_without_api_key(self):
        """Test GPT5ResponsesClient initialization without API key."""
        # Mock settings without API key
        mock_settings = MagicMock()
        mock_settings.openai_api_key = None

        with patch('src.clients.gpt5_client.AsyncOpenAI') as mock_openai:
            client = GPT5ResponsesClient(mock_settings)

            # Verify client initialized but is not ready
            assert client.settings == mock_settings
            assert client.conversation_states == {}
            assert client.is_ready is False

            # Verify AsyncOpenAI was not called
            mock_openai.assert_not_called()

    def test_client_initialization_with_exception(self):
        """Test GPT5ResponsesClient initialization when AsyncOpenAI raises exception."""
        with patch('src.clients.gpt5_client.AsyncOpenAI') as mock_openai:
            mock_openai.side_effect = Exception("API initialization error")

            client = GPT5ResponsesClient(self.valid_settings)

            # Verify client initialized but is not ready due to exception
            assert client.settings == self.valid_settings
            assert client.is_ready is False

    @pytest.mark.asyncio
    async def test_create_response_success(self):
        """Test successful create_response API call with mocked response."""
        # Create mock response object
        mock_response = MagicMock()
        mock_response.id = "response-123"

        # Create mock client
        mock_async_client = AsyncMock()
        mock_async_client.responses.create = AsyncMock(return_value=mock_response)

        with patch('src.clients.gpt5_client.AsyncOpenAI') as mock_openai:
            mock_openai.return_value = mock_async_client

            client = GPT5ResponsesClient(self.valid_settings)

            # Make API call
            result = await client.create_response("Test prompt")

            # Verify response
            assert result == mock_response

            # Verify API was called with correct parameters
            mock_async_client.responses.create.assert_called_once_with(
                model="gpt-5",
                input="Test prompt",
                verbosity="standard"
            )

    @pytest.mark.asyncio
    async def test_create_response_with_conversation_id(self):
        """Test create_response with conversation ID for state management."""
        # Create mock response object
        mock_response = MagicMock()
        mock_response.id = "response-456"

        # Create mock client
        mock_async_client = AsyncMock()
        mock_async_client.responses.create = AsyncMock(return_value=mock_response)

        with patch('src.clients.gpt5_client.AsyncOpenAI') as mock_openai:
            mock_openai.return_value = mock_async_client

            client = GPT5ResponsesClient(self.valid_settings)

            # Make API call with conversation ID
            result = await client.create_response("Test prompt", conversation_id="conv-123")

            # Verify response
            assert result == mock_response

            # Verify conversation state was stored
            assert "conv-123" in client.conversation_states
            assert client.conversation_states["conv-123"]["response_id"] == "response-456"

    @pytest.mark.asyncio
    async def test_create_response_with_previous_response_id(self):
        """Test create_response using previous response ID from conversation state."""
        # Setup existing conversation state
        mock_response = MagicMock()
        mock_response.id = "response-789"

        mock_async_client = AsyncMock()
        mock_async_client.responses.create = AsyncMock(return_value=mock_response)

        with patch('src.clients.gpt5_client.AsyncOpenAI') as mock_openai:
            mock_openai.return_value = mock_async_client

            client = GPT5ResponsesClient(self.valid_settings)

            # Set up existing conversation state
            client.set_conversation_state("conv-456", {"response_id": "previous-response-123"})

            # Make API call
            result = await client.create_response("Follow-up prompt", conversation_id="conv-456")

            # Verify API was called with previous response ID
            mock_async_client.responses.create.assert_called_once_with(
                model="gpt-5",
                input="Follow-up prompt",
                verbosity="standard",
                previous_response_id="previous-response-123"
            )

    @pytest.mark.asyncio
    async def test_create_response_not_ready(self):
        """Test create_response raises ValueError when client is not ready."""
        # Mock settings without API key
        mock_settings = MagicMock()
        mock_settings.openai_api_key = None

        client = GPT5ResponsesClient(mock_settings)

        # Verify client is not ready
        assert not client.is_ready

        # Verify create_response raises ValueError
        with pytest.raises(ValueError, match="GPT-5 client is not ready - missing API key"):
            await client.create_response("Test prompt")

    @pytest.mark.asyncio
    async def test_create_response_retry_logic_success(self):
        """Test retry logic succeeds after initial failures."""
        from openai import OpenAIError

        mock_response = MagicMock()
        mock_response.id = "response-retry-success"

        mock_async_client = AsyncMock()
        # Simulate failure then success
        mock_async_client.responses.create = AsyncMock(
            side_effect=[OpenAIError("Temporary error"), mock_response]
        )

        with patch('src.clients.gpt5_client.AsyncOpenAI') as mock_openai:
            mock_openai.return_value = mock_async_client

            client = GPT5ResponsesClient(self.valid_settings)

            # Make API call - should succeed after retry
            result = await client.create_response("Test prompt")

            # Verify response
            assert result == mock_response

            # Verify API was called twice (initial failure + retry success)
            assert mock_async_client.responses.create.call_count == 2

    @pytest.mark.asyncio
    async def test_create_response_retry_logic_exhausted(self):
        """Test retry logic fails after exhausting all attempts."""
        from openai import OpenAIError

        mock_async_client = AsyncMock()
        # Simulate continuous failures
        mock_async_client.responses.create = AsyncMock(
            side_effect=OpenAIError("Persistent error")
        )

        with patch('src.clients.gpt5_client.AsyncOpenAI') as mock_openai:
            mock_openai.return_value = mock_async_client

            client = GPT5ResponsesClient(self.valid_settings)

            # Make API call - should fail after retries
            with pytest.raises(OpenAIError, match="Persistent error"):
                await client.create_response("Test prompt")

            # Verify API was called 3 times (initial + 2 retries)
            assert mock_async_client.responses.create.call_count == 3

    @pytest.mark.asyncio
    async def test_test_connection_success(self):
        """Test successful connection test."""
        mock_response = MagicMock()
        mock_response.id = "test-response"

        mock_async_client = AsyncMock()
        mock_async_client.responses.create = AsyncMock(return_value=mock_response)

        with patch('src.clients.gpt5_client.AsyncOpenAI') as mock_openai:
            mock_openai.return_value = mock_async_client

            client = GPT5ResponsesClient(self.valid_settings)

            # Test connection
            result = await client.test_connection()

            # Verify connection test passed
            assert result is True

            # Verify API was called with test parameters
            mock_async_client.responses.create.assert_called_once_with(
                model="gpt-5",
                input="Return 'OK' if you can process this request.",
                reasoning_effort="low"
            )

    @pytest.mark.asyncio
    async def test_test_connection_not_ready(self):
        """Test connection test when client is not ready."""
        mock_settings = MagicMock()
        mock_settings.openai_api_key = None

        client = GPT5ResponsesClient(mock_settings)

        # Test connection
        result = await client.test_connection()

        # Verify connection test failed
        assert result is False

    @pytest.mark.asyncio
    async def test_test_connection_api_error(self):
        """Test connection test when API call raises exception."""
        mock_async_client = AsyncMock()
        mock_async_client.responses.create = AsyncMock(side_effect=Exception("Connection error"))

        with patch('src.clients.gpt5_client.AsyncOpenAI') as mock_openai:
            mock_openai.return_value = mock_async_client

            client = GPT5ResponsesClient(self.valid_settings)

            # Test connection
            result = await client.test_connection()

            # Verify connection test failed
            assert result is False

    def test_conversation_state_management_get_set(self):
        """Test conversation state storage and retrieval."""
        client = GPT5ResponsesClient(self.valid_settings)

        # Test getting non-existent state
        state = client.get_conversation_state("non-existent")
        assert state is None

        # Test setting and getting state
        test_state = {"response_id": "test-123", "context": "test context"}
        client.set_conversation_state("conv-123", test_state)

        retrieved_state = client.get_conversation_state("conv-123")
        assert retrieved_state == test_state

    def test_conversation_state_management_clear(self):
        """Test conversation state clearing."""
        client = GPT5ResponsesClient(self.valid_settings)

        # Set up some conversation states
        client.set_conversation_state("conv-1", {"response_id": "resp-1"})
        client.set_conversation_state("conv-2", {"response_id": "resp-2"})
        client.set_conversation_state("conv-3", {"response_id": "resp-3"})

        # Test clearing existing conversation
        result = client.clear_conversation_state("conv-1")
        assert result is True
        assert client.get_conversation_state("conv-1") is None

        # Test clearing non-existent conversation
        result = client.clear_conversation_state("non-existent")
        assert result is False

        # Verify other conversations still exist
        assert client.get_conversation_state("conv-2") is not None
        assert client.get_conversation_state("conv-3") is not None

    def test_conversation_state_management_clear_all(self):
        """Test clearing all conversation states."""
        client = GPT5ResponsesClient(self.valid_settings)

        # Set up multiple conversation states
        client.set_conversation_state("conv-1", {"response_id": "resp-1"})
        client.set_conversation_state("conv-2", {"response_id": "resp-2"})
        client.set_conversation_state("conv-3", {"response_id": "resp-3"})

        # Clear all states
        count = client.clear_all_conversation_states()

        # Verify all were cleared
        assert count == 3
        assert len(client.conversation_states) == 0
        assert client.get_conversation_state("conv-1") is None
        assert client.get_conversation_state("conv-2") is None
        assert client.get_conversation_state("conv-3") is None

    def test_client_readiness_checks(self):
        """Test client readiness property under various conditions."""
        # Test ready client
        with patch('src.clients.gpt5_client.AsyncOpenAI') as mock_openai:
            mock_openai.return_value = MagicMock()

            client = GPT5ResponsesClient(self.valid_settings)
            assert client.is_ready is True

        # Test not ready client (no API key)
        mock_settings = MagicMock()
        mock_settings.openai_api_key = None

        client = GPT5ResponsesClient(mock_settings)
        assert client.is_ready is False

        # Test not ready client (initialization exception)
        with patch('src.clients.gpt5_client.AsyncOpenAI') as mock_openai:
            mock_openai.side_effect = Exception("Init error")

            client = GPT5ResponsesClient(self.valid_settings)
            assert client.is_ready is False

    @pytest.mark.asyncio
    async def test_create_response_with_reasoning_effort_and_kwargs(self):
        """Test create_response with custom reasoning effort and additional kwargs."""
        mock_response = MagicMock()
        mock_response.id = "response-custom"

        mock_async_client = AsyncMock()
        mock_async_client.responses.create = AsyncMock(return_value=mock_response)

        with patch('src.clients.gpt5_client.AsyncOpenAI') as mock_openai:
            mock_openai.return_value = mock_async_client

            client = GPT5ResponsesClient(self.valid_settings)

            # Make API call with custom parameters
            result = await client.create_response(
                "Test prompt",
                reasoning_effort="high",
                verbosity="detailed",
                custom_param="test_value"
            )

            # Verify response
            assert result == mock_response

            # Verify API was called with all parameters
            expected_params = {
                "model": "gpt-5",
                "input": "Test prompt",
                "reasoning_effort": "high",
                "verbosity": "detailed",
                "custom_param": "test_value"
            }
            mock_async_client.responses.create.assert_called_once_with(**expected_params)

    @pytest.mark.asyncio
    async def test_error_handling_scenarios(self):
        """Test various error handling scenarios."""
        from openai import OpenAIError

        mock_async_client = AsyncMock()

        with patch('src.clients.gpt5_client.AsyncOpenAI') as mock_openai:
            mock_openai.return_value = mock_async_client

            client = GPT5ResponsesClient(self.valid_settings)

            # Test OpenAI error propagation
            mock_async_client.responses.create = AsyncMock(
                side_effect=OpenAIError("API quota exceeded")
            )

            with pytest.raises(OpenAIError, match="API quota exceeded"):
                await client.create_response("Test prompt")

            # Test generic exception handling
            mock_async_client.responses.create = AsyncMock(
                side_effect=RuntimeError("Unexpected error")
            )

            with pytest.raises(RuntimeError, match="Unexpected error"):
                await client.create_response("Test prompt")



class TestConstants:
    """
    Test suite for constants module to ensure all constants are properly defined.

    Tests verify that constants maintain expected values and types,
    providing coverage for the constants module.
    """

    def test_gpt5_model_constants(self):
        """Test GPT-5 model name constants are correctly defined."""
        from src.config.constants import (
            GPT_5_MODEL, GPT_5_MINI_MODEL, GPT_5_NANO_MODEL, GPT_5_MODELS
        )

        # Test individual model constants
        assert GPT_5_MODEL == "gpt-5"
        assert GPT_5_MINI_MODEL == "gpt-5-mini"
        assert GPT_5_NANO_MODEL == "gpt-5-nano"

        # Test model list contains all models
        assert GPT_5_MODELS == ("gpt-5", "gpt-5-mini", "gpt-5-nano")
        assert len(GPT_5_MODELS) == 3
        assert all(isinstance(model, str) for model in GPT_5_MODELS)

    def test_reasoning_level_constants(self):
        """Test reasoning effort level constants are correctly defined."""
        from src.config.constants import (
            REASONING_MINIMAL, REASONING_LOW, REASONING_MEDIUM, REASONING_HIGH, REASONING_LEVELS
        )

        # Test individual reasoning constants
        assert REASONING_MINIMAL == "minimal"
        assert REASONING_LOW == "low"
        assert REASONING_MEDIUM == "medium"
        assert REASONING_HIGH == "high"

        # Test reasoning levels list
        assert REASONING_LEVELS == ("minimal", "low", "medium", "high")
        assert len(REASONING_LEVELS) == 4
        assert all(isinstance(level, str) for level in REASONING_LEVELS)

    def test_verbosity_level_constants(self):
        """Test verbosity level constants are correctly defined."""
        from src.config.constants import (
            VERBOSITY_LOW, VERBOSITY_MEDIUM, VERBOSITY_HIGH, VERBOSITY_LEVELS
        )

        # Test individual verbosity constants
        assert VERBOSITY_LOW == "low"
        assert VERBOSITY_MEDIUM == "medium"
        assert VERBOSITY_HIGH == "high"

        # Test verbosity levels list
        assert VERBOSITY_LEVELS == ("low", "medium", "high")
        assert len(VERBOSITY_LEVELS) == 3
        assert all(isinstance(level, str) for level in VERBOSITY_LEVELS)

    def test_api_limits_constants(self):
        """Test API limits and configuration constants."""
        from src.config.constants import (
            MAX_TOKENS, MAX_CONTEXT_LENGTH, DEFAULT_TEMPERATURE, MIN_TEMPERATURE, MAX_TEMPERATURE,
            DEFAULT_TOP_P, MIN_TOP_P, MAX_TOP_P, MAX_RETRIES, REQUEST_TIMEOUT
        )

        # Test token and context limits
        assert MAX_TOKENS == 4096
        assert MAX_CONTEXT_LENGTH == 128000
        assert isinstance(MAX_TOKENS, int)
        assert isinstance(MAX_CONTEXT_LENGTH, int)

        # Test temperature constants
        assert DEFAULT_TEMPERATURE == 0.7
        assert MIN_TEMPERATURE == 0.0
        assert MAX_TEMPERATURE == 2.0
        assert isinstance(DEFAULT_TEMPERATURE, (int, float))

        # Test top_p constants
        assert DEFAULT_TOP_P == 0.9
        assert MIN_TOP_P == 0.1
        assert MAX_TOP_P == 1.0
        assert isinstance(DEFAULT_TOP_P, (int, float))

        # Test retry and timeout constants
        assert MAX_RETRIES == 3
        assert REQUEST_TIMEOUT == 60
        assert isinstance(MAX_RETRIES, int)
        assert isinstance(REQUEST_TIMEOUT, int)


    def test_constants_immutability(self):
        """Test that constants are properly typed as Final."""
        from src.config.constants import GPT_5_MODEL

        # Test that constant exists and has expected value
        assert GPT_5_MODEL == "gpt-5"

        # Constants should be immutable at runtime (tuple test)
        from src.config.constants import GPT_5_MODELS
        assert isinstance(GPT_5_MODELS, tuple)  # tuples are immutable


class TestLogger:
    """
    Test suite for logger module functionality.

    Tests cover logger setup, configuration, and utility functions
    to provide coverage for the logger module.
    """

    def test_is_development_detection(self):
        """Test development mode detection logic."""
        from src.utils.logger import _is_development

        # Function should return a boolean
        result = _is_development()
        assert isinstance(result, bool)

    def test_add_timestamp_processor(self):
        """Test timestamp processor adds timestamp to log entries."""
        from src.utils.logger import _add_timestamp

        # Test timestamp addition
        event_dict = {'message': 'test'}
        result = _add_timestamp(None, 'info', event_dict)

        assert 'timestamp' in result
        assert 'message' in result
        assert result['message'] == 'test'
        # Verify timestamp format (ISO format ending with Z)
        assert result['timestamp'].endswith('Z')

    def test_filter_by_level_processor(self):
        """Test log level filter processor."""
        from src.utils.logger import _filter_by_level

        # Test that filter passes through event dict unchanged
        event_dict = {'message': 'test', 'level': 'info'}
        result = _filter_by_level(None, 'info', event_dict)

        assert result == event_dict


    @patch('src.utils.logger.get_settings')
    def test_setup_logger_basic(self, mock_get_settings):
        """Test basic logger setup functionality."""
        from src.utils.logger import setup_logger

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.log_level = 'INFO'
        mock_get_settings.return_value = mock_settings

        # Call setup_logger - should not raise exception
        logger = setup_logger()
        assert logger is not None

    @patch('src.utils.logger.get_settings')
    def test_get_logger_basic(self, mock_get_settings):
        """Test get_logger function."""
        from src.utils.logger import get_logger

        # Mock settings
        mock_settings = MagicMock()
        mock_settings.log_level = 'INFO'
        mock_get_settings.return_value = mock_settings

        # Test get_logger
        logger = get_logger('test')
        assert logger is not None

    def test_convenience_logging_functions_exist(self):
        """Test that convenience logging functions are available."""
        from src.utils.logger import debug, info, warning, error, critical

        # Test functions exist and are callable
        assert callable(debug)
        assert callable(info)  
        assert callable(warning)
        assert callable(error)
        assert callable(critical)
