# Testing Guide

This document provides comprehensive testing guidance for the GPT-5 CEO Research project. Following KISS principles, we keep testing simple, clear, and reliable.

## Table of Contents
- [Testing Philosophy](#testing-philosophy)
- [Running Tests](#running-tests)
- [Writing Unit Tests](#writing-unit-tests)
- [Integration Tests](#integration-tests)
- [Mocking Strategies](#mocking-strategies)
- [Testing Fixtures](#testing-fixtures)
- [Async Testing](#async-testing)
- [Coverage Requirements](#coverage-requirements)
- [CI/CD Integration](#cicd-integration)
- [Best Practices](#best-practices)

## Testing Philosophy

Our testing approach follows these core principles:

### 1. Simple and Clear Tests
- Each test has a single, clear purpose
- Test names describe exactly what they test
- Tests are readable without extensive documentation
- Avoid complex test setups - keep fixtures simple

### 2. Comprehensive Coverage
- Test all public methods and functions
- Cover error conditions and edge cases
- Test configuration validation thoroughly
- Verify async behavior and state management

### 3. Reliable and Fast
- Tests run quickly and consistently
- No external dependencies in unit tests
- Proper isolation between tests
- Deterministic test outcomes

### 4. Maintainable Test Code
- Tests are as clean as production code
- Shared fixtures for common setup
- Clear separation between unit and integration tests
- Easy to understand failure messages

## Running Tests

### Prerequisites
```bash
# Install development dependencies
pip install -r requirements.txt

# Install additional test dependencies if needed
pip install pytest-cov pytest-mock
```

### Basic Test Commands

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest gpt_5_ceo_research/tests/test_initialization.py

# Run specific test class
pytest gpt_5_ceo_research/tests/test_initialization.py::TestSettings

# Run specific test method
pytest gpt_5_ceo_research/tests/test_initialization.py::TestSettings::test_valid_configuration_loading

# Run tests matching pattern
pytest -k "test_settings"
```

### Test Discovery
Tests are automatically discovered when they:
- Are in files named `test_*.py` or `*_test.py`
- Are in classes named `Test*`
- Are functions named `test_*`

### Parallel Testing
```bash
# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto
```

## Writing Unit Tests

### Basic Test Structure

```python
"""
Test module for feature X.

Clear description of what this module tests.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from your_module import YourClass


class TestYourClass:
    """Test suite for YourClass with clear documentation."""

    def setup_method(self):
        """Setup test fixtures for each test method."""
        self.test_instance = YourClass()

    def test_basic_functionality(self):
        """Test basic functionality with descriptive name."""
        # Arrange
        input_data = "test input"
        expected_output = "expected result"

        # Act
        result = self.test_instance.process(input_data)

        # Assert
        assert result == expected_output

    def test_error_condition(self):
        """Test error handling with specific exception."""
        with pytest.raises(ValueError, match="specific error message"):
            self.test_instance.invalid_operation()
```

### Settings Validation Tests Example

From our codebase (`test_initialization.py`), here's how to test configuration validation:

```python
def test_invalid_api_key_format_not_starting_with_sk(self):
    """Test that API key validation fails when key doesn't start with 'sk-'."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(openai_api_key="invalid-key-format")

    error = exc_info.value
    assert len(error.errors()) == 1
    assert error.errors()[0]["type"] == "value_error"
    assert "must start with 'sk-'" in str(error.errors()[0]["ctx"]["error"])

def test_boundary_value_max_retries(self):
    """Test boundary values for max_retries field."""
    # Test minimum valid value
    settings = Settings(openai_api_key="sk-test-key", max_retries=0)
    assert settings.max_retries == 0

    # Test maximum valid value
    settings = Settings(openai_api_key="sk-test-key", max_retries=10)
    assert settings.max_retries == 10

    # Test invalid values
    with pytest.raises(ValidationError) as exc_info:
        Settings(openai_api_key="sk-test-key", max_retries=-1)
```

### Environment Variable Testing

```python
@patch.dict(os.environ, {
    "OPENAI_API_KEY": "sk-env-test-key-12345",
    "GPT5_MODEL": "gpt-5",
    "LOG_LEVEL": "DEBUG"
}, clear=True)
def test_environment_variable_loading(self):
    """Test that Settings correctly loads values from environment variables."""
    settings = Settings()

    assert settings.openai_api_key == "sk-env-test-key-12345"
    assert settings.gpt5_model == "gpt-5"
    assert settings.log_level == "DEBUG"
```

## Integration Tests

Integration tests verify that components work together correctly. Keep them focused and avoid external dependencies.

```python
@pytest.mark.asyncio
async def test_client_settings_integration(mock_settings):
    """Test integration between client and settings."""
    client = GPT5ResponsesClient(mock_settings)

    assert client.settings == mock_settings
    assert client.is_ready == (mock_settings.openai_api_key is not None)

    if client.is_ready:
        # Test basic operations work together
        result = await client.test_connection()
        assert isinstance(result, bool)
```

### Database/File System Integration

```python
def test_file_operations_integration(temp_dir):
    """Test file operations with temporary directory."""
    test_file = temp_dir / "test_config.json"

    # Write configuration
    config = {"api_key": "sk-test-key", "model": "gpt-5"}
    test_file.write_text(json.dumps(config))

    # Read and validate
    loaded_config = json.loads(test_file.read_text())
    assert loaded_config == config
```

## Mocking Strategies

### GPT-5 API Mocking

Our primary mocking strategy for the GPT-5 API follows these patterns:

```python
@pytest.fixture
def mock_gpt5_response() -> Dict[str, Any]:
    """Provide a mock GPT-5 API response for testing."""
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
```

### Client Mocking

```python
@pytest.fixture
def mock_gpt5_client(mock_settings, mock_gpt5_response):
    """Provide a mocked GPT5ResponsesClient for testing."""
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

    return mock_client
```

### HTTP Request Mocking

```python
@pytest.fixture
def mock_http_response():
    """Mock HTTP response for external API calls."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    return mock_response

@patch('requests.get')
def test_external_api_call(mock_get, mock_http_response):
    """Test external API integration with mocked HTTP."""
    mock_get.return_value = mock_http_response

    result = make_external_api_call()

    mock_get.assert_called_once_with("https://api.example.com/data")
    assert result["status"] == "success"
```

### Retry Logic Mocking

```python
@pytest.mark.asyncio
async def test_create_response_retry_logic_success(mock_settings):
    """Test retry logic succeeds after initial failures."""
    from openai import OpenAIError

    mock_response = Mock()
    mock_response.id = "response-retry-success"

    mock_async_client = AsyncMock()
    # Simulate failure then success
    mock_async_client.responses.create = AsyncMock(
        side_effect=[OpenAIError("Temporary error"), mock_response]
    )

    with patch('gpt_5_ceo_research.src.clients.gpt5_client.AsyncOpenAI') as mock_openai:
        mock_openai.return_value = mock_async_client

        client = GPT5ResponsesClient(mock_settings)
        result = await client.create_response("Test prompt")

        assert result == mock_response
        assert mock_async_client.responses.create.call_count == 2
```

## Testing Fixtures

We use pytest fixtures to provide consistent test data and mock objects.

### Common Fixtures in `conftest.py`

```python
@pytest.fixture
def mock_settings() -> Settings:
    """Provide a test Settings instance with valid test values."""
    return Settings(
        openai_api_key="sk-test-key-for-testing-1234567890abcdef",
        gpt5_model="gpt-5",
        default_reasoning_effort="medium",
        max_retries=2,  # Lower for faster tests
        timeout_seconds=30,  # Lower for faster tests
        log_level="DEBUG"
    )

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for tests that need file system operations."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def sample_conversation_id() -> str:
    """Provide a sample conversation ID for testing."""
    return "test-conversation-12345"
```

### Fixture Scopes

```python
@pytest.fixture(scope="session")
def database_connection():
    """Session-scoped fixture for expensive setup."""
    # Setup once per test session
    pass

@pytest.fixture(scope="module")
def module_config():
    """Module-scoped fixture for shared module setup."""
    pass

@pytest.fixture(scope="function")  # Default
def test_data():
    """Function-scoped fixture - new instance per test."""
    pass
```

### Parameterized Fixtures

```python
@pytest.fixture(params=["minimal", "low", "medium", "high"])
def reasoning_effort(request):
    """Parameterized fixture for testing all reasoning effort levels."""
    return request.param

def test_reasoning_effort_validation(reasoning_effort):
    """Test runs once for each reasoning effort value."""
    settings = Settings(
        openai_api_key="sk-test-key",
        default_reasoning_effort=reasoning_effort
    )
    assert settings.default_reasoning_effort == reasoning_effort
```

## Async Testing

### Basic Async Test Setup

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async functions with pytest-asyncio."""
    result = await async_function()
    assert result is not None
```

### Event Loop Fixture

```python
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()
```

### Async Context Managers

```python
@pytest.mark.asyncio
async def test_async_context_manager():
    """Test async context manager behavior."""
    async with AsyncContextManager() as manager:
        result = await manager.do_something()
        assert result is not None
```

### Async Mocking

```python
@pytest.mark.asyncio
async def test_with_async_mock():
    """Test with AsyncMock for async methods."""
    mock_client = AsyncMock()
    mock_client.create_response.return_value = Mock(id="test-123")

    result = await mock_client.create_response("test prompt")

    mock_client.create_response.assert_awaited_once_with("test prompt")
    assert result.id == "test-123"
```

### Testing Async Exceptions

```python
@pytest.mark.asyncio
async def test_async_exception_handling():
    """Test async exception propagation."""
    mock_client = AsyncMock()
    mock_client.create_response.side_effect = OpenAIError("API Error")

    with pytest.raises(OpenAIError, match="API Error"):
        await mock_client.create_response("test prompt")
```

## Coverage Requirements

### Minimum Coverage Standards

- **Overall Coverage**: 85% minimum
- **Critical modules** (settings, clients): 95% minimum
- **New features**: 90% minimum coverage required
- **Bug fixes**: Must include tests covering the bug

### Running Coverage Reports

```bash
# Install coverage tools
pip install pytest-cov

# Run tests with coverage
pytest --cov=gpt_5_ceo_research --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html

# Generate coverage badge
coverage-badge -o coverage.svg
```

### Coverage Configuration

Create `.coveragerc` file:

```ini
[run]
source = gpt_5_ceo_research
omit =
    */tests/*
    */venv/*
    */__pycache__/*
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:

[html]
directory = htmlcov
```

### Coverage Exceptions

Acceptable low-coverage scenarios:
- Error handling for truly exceptional cases
- Compatibility code for different Python versions
- Debug/development-only code paths
- Code marked with `# pragma: no cover`

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest-cov

    - name: Run tests with coverage
      run: |
        pytest --cov=gpt_5_ceo_research --cov-report=xml
      env:
        OPENAI_API_KEY: sk-fake-key-for-testing

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

### Test Environment Variables

For CI/CD, set these environment variables:

```bash
# Required for tests to pass
OPENAI_API_KEY=sk-fake-key-for-testing-purposes-only
GPT5_MODEL=gpt-5
LOG_LEVEL=DEBUG

# Optional test configuration
MAX_RETRIES=2
TIMEOUT_SECONDS=30
```

## Best Practices

### 1. Test Organization

```python
class TestSettingsValidation:
    """Group related tests in classes with clear purposes."""

    def test_valid_configurations(self):
        """Test valid configuration scenarios."""
        pass

    def test_invalid_configurations(self):
        """Test invalid configuration scenarios."""
        pass

class TestSettingsEnvironmentLoading:
    """Separate class for environment variable testing."""

    def test_env_var_loading(self):
        """Test environment variable loading."""
        pass
```

### 2. Clear Test Names

```python
# Good: Describes what is tested and expected outcome
def test_api_key_validation_fails_when_not_starting_with_sk(self):
    pass

def test_retry_logic_succeeds_after_temporary_failure(self):
    pass

# Bad: Vague or unclear purpose
def test_settings(self):
    pass

def test_api_call(self):
    pass
```

### 3. Arrange-Act-Assert Pattern

```python
def test_conversation_state_storage_and_retrieval(self):
    """Test conversation state management."""
    # Arrange
    client = GPT5ResponsesClient(valid_settings)
    conversation_id = "test-conv-123"
    test_state = {"response_id": "resp-456", "context": "test"}

    # Act
    client.set_conversation_state(conversation_id, test_state)
    retrieved_state = client.get_conversation_state(conversation_id)

    # Assert
    assert retrieved_state == test_state
```

### 4. Independent Tests

```python
class TestClientState:
    def setup_method(self):
        """Create fresh instance for each test."""
        self.client = GPT5ResponsesClient(mock_settings)

    def test_set_state(self):
        """Each test starts with clean state."""
        self.client.set_conversation_state("conv1", {"data": "test1"})
        assert len(self.client.conversation_states) == 1

    def test_clear_state(self):
        """This test doesn't see state from previous test."""
        assert len(self.client.conversation_states) == 0
```

### 5. Meaningful Assertions

```python
# Good: Specific assertions
assert response.id == "expected-response-id"
assert len(client.conversation_states) == 3
assert "must start with 'sk-'" in str(error)

# Bad: Generic or unclear assertions
assert response
assert result
assert True
```

### 6. Error Testing

```python
def test_specific_error_conditions(self):
    """Test specific error scenarios with clear error messages."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(openai_api_key="invalid-key")

    # Check specific error details
    error = exc_info.value
    assert error.errors()[0]["type"] == "value_error"
    assert "must start with 'sk-'" in str(error.errors()[0]["ctx"]["error"])
```

### 7. Test Data Management

```python
# Use constants for test data
TEST_API_KEY = "sk-test-key-12345"
TEST_CONVERSATION_ID = "conv-test-789"

# Use fixtures for complex test data
@pytest.fixture
def sample_api_response():
    return {
        "id": "resp-123",
        "choices": [{"message": {"content": "Test response"}}]
    }
```

### 8. Mock Verification

```python
def test_api_call_parameters(mock_client):
    """Verify mocks are called with correct parameters."""
    mock_client.create_response("test prompt", reasoning_effort="high")

    # Verify call was made correctly
    mock_client.create_response.assert_called_once_with(
        "test prompt",
        reasoning_effort="high"
    )
```

### 9. Test Documentation

```python
def test_complex_scenario(self):
    """
    Test complex scenario with multi-step process.

    This test verifies:
    1. Initial state setup
    2. Processing with retry logic
    3. Final state validation
    4. Cleanup operations
    """
    # Implementation with clear steps
    pass
```

### 10. Performance Considerations

```python
# Fast tests - mock external dependencies
@patch('requests.get')
def test_fast_external_call(mock_get):
    mock_get.return_value.json.return_value = {"status": "ok"}
    result = external_api_call()
    assert result["status"] == "ok"

# Slow tests - mark for separate execution
@pytest.mark.slow
def test_integration_with_real_api():
    """Mark slow tests for optional execution."""
    pass

# Run fast tests only
# pytest -m "not slow"
```

---

This testing guide provides comprehensive coverage of testing strategies and practices for the GPT-5 CEO Research project. Following these guidelines will ensure reliable, maintainable, and effective test coverage that supports confident development and deployment.