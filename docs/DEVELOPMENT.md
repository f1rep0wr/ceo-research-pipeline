# Development Guide

A comprehensive guide for developers contributing to the GPT-5 CEO Research project. This guide covers code standards, architecture patterns, testing practices, and development workflows with concrete examples from the existing codebase.

## Table of Contents

- [Code Style Standards](#code-style-standards)
- [Project Structure](#project-structure)
- [Adding New Features](#adding-new-features)
- [Testing Guidelines](#testing-guidelines)
- [Git Workflow](#git-workflow)
- [Debugging and Troubleshooting](#debugging-and-troubleshooting)
- [Performance Considerations](#performance-considerations)

## Code Style Standards

### PEP 8 Compliance

Follow Python PEP 8 standards with these project-specific guidelines:

**Line Length**: Maximum 100 characters (not 79) for better readability on modern screens:
```python
# Good - clear and readable
def create_response(
    self,
    prompt: str,
    conversation_id: Optional[str] = None,
    reasoning_effort: Optional[str] = None,
    **kwargs
) -> Any:
```

**Import Organization**: Use absolute imports and organize as follows:
```python
# Standard library imports
from typing import Dict, Any, Optional
import logging

# Third-party imports
from openai import AsyncOpenAI, OpenAIError
from tenacity import retry, stop_after_attempt
import structlog

# Local imports
from ..config.settings import Settings
```

### Type Annotations

**Always use comprehensive type annotations** - this is critical for LLM API integrations:

```python
# Excellent - from gpt5_client.py
async def create_response(
    self,
    prompt: str,
    conversation_id: Optional[str] = None,
    reasoning_effort: Optional[str] = None,
    **kwargs
) -> Any:
    """Create a response using GPT-5 Responses API."""
```

**Use Union types for multiple possibilities**:
```python
from typing import Union, List, Dict

# For API responses that could be different types
ResponseType = Union[str, Dict[str, Any], List[Dict[str, Any]]]
```

**Use Literal types for constrained values** (following settings.py pattern):
```python
from typing import Literal

ReasoningEffort = Literal["minimal", "low", "medium", "high"]
VerbosityLevel = Literal["low", "medium", "high"]
```

### Docstrings

Follow the project's docstring pattern with clear structure:

```python
def get_conversation_state(self, conversation_id: str) -> Optional[Dict[str, Any]]:
    """
    Get conversation state for a given conversation ID.

    Args:
        conversation_id: Unique identifier for the conversation

    Returns:
        Conversation state dictionary or None if not found
    """
```

**For complex methods**, include usage examples:
```python
async def create_response(self, prompt: str, **kwargs) -> Any:
    """
    Create a response using GPT-5 Responses API with retry logic.

    Args:
        prompt: The input prompt for the API
        conversation_id: Optional conversation ID for state management
        reasoning_effort: Optional reasoning effort level
        **kwargs: Additional parameters to pass to the API

    Returns:
        The API response object

    Raises:
        ValueError: If client is not ready (no API key)
        OpenAIError: If API call fails after retries

    Example:
        response = await client.create_response(
            "Analyze the CEO of Tesla",
            reasoning_effort="high",
            conversation_id="research-session-1"
        )
    """
```

### Error Handling

**Use specific exception types** and provide clear error messages:

```python
# Good - from gpt5_client.py
if not self.is_ready:
    raise ValueError("GPT-5 client is not ready - missing API key")

# Handle expected exceptions specifically
try:
    response = await self._client.responses.create(**request_params)
except OpenAIError as e:
    log.error("GPT-5 API call failed", error=str(e))
    raise
except Exception as e:
    log.error("Unexpected error in GPT-5 API call", error=str(e))
    raise
```

### Logging

**Use structured logging** with contextual information:

```python
import structlog

log = structlog.get_logger()

# Good - provides context and structured data
log.info(
    "Making GPT-5 API call",
    conversation_id=conversation_id,
    reasoning_effort=reasoning_effort,
    request_params=request_params
)
```

## Project Structure

### Current Architecture

```
gpt_5/
├── gpt_5_ceo_research/          # Main application package
│   ├── src/                     # Source code
│   │   ├── clients/             # API clients (GPT-5, external APIs)
│   │   ├── config/              # Configuration management
│   │   └── utils/               # Utility functions
│   ├── tests/                   # Test suite
│   └── docs/                    # Project documentation
├── scripts/                     # Setup and utility scripts
└── docs/                        # Project-wide documentation
```

### Design Patterns

**Configuration Management**: Use Pydantic BaseSettings for validation:
```python
# Following settings.py pattern
class Settings(BaseSettings):
    openai_api_key: str = Field(..., description="OpenAI API key")

    @field_validator('openai_api_key')
    @classmethod
    def validate_openai_api_key(cls, v: str) -> str:
        if not v.startswith('sk-'):
            raise ValueError("OpenAI API key must start with 'sk-'")
        return v
```

**Client Patterns**: Async clients with graceful initialization:
```python
# From gpt5_client.py - handles missing API keys gracefully
def __init__(self, settings: Settings) -> None:
    self.settings = settings
    try:
        api_key = getattr(settings, 'openai_api_key', None)
        if api_key:
            self._client = AsyncOpenAI(api_key=api_key)
        else:
            self._client = None
            logger.warning("No API key - client initialized without access")
    except Exception as e:
        self._client = None
        logger.error(f"Failed to initialize client: {e}")
```

**State Management**: Simple dictionary-based state with clear methods:
```python
# Conversation state management pattern
def get_conversation_state(self, conversation_id: str) -> Optional[Dict[str, Any]]:
    return self.conversation_states.get(conversation_id)

def set_conversation_state(self, conversation_id: str, state: Dict[str, Any]) -> None:
    self.conversation_states[conversation_id] = state
```

## Adding New Features

### 1. Feature Planning

Before coding, consider:
- **KISS Principle**: Choose the simplest solution that works
- **Integration Points**: How does this interact with existing GPT-5 client?
- **Configuration**: What new settings might be needed?
- **Testing**: How will you verify it works?

### 2. Creating a New Client

Follow the GPT-5 client pattern for consistency:

```python
# new_service_client.py
from typing import Dict, Any, Optional
import logging
from ..config.settings import Settings

logger = logging.getLogger(__name__)

class NewServiceClient:
    """Client for integrating with NewService API."""

    def __init__(self, settings: Settings) -> None:
        """Initialize client with graceful error handling."""
        self.settings = settings

        try:
            # Initialize your service client here
            self._client = SomeServiceClient(api_key=settings.new_service_key)
            logger.info("NewService client initialized successfully")
        except Exception as e:
            self._client = None
            logger.error(f"Failed to initialize NewService client: {e}")

    @property
    def is_ready(self) -> bool:
        """Check if client is ready for API calls."""
        return self._client is not None

    async def some_async_method(self, data: str) -> Dict[str, Any]:
        """Make async API call with proper error handling."""
        if not self.is_ready:
            raise ValueError("NewService client is not ready")

        try:
            response = await self._client.call_api(data)
            return response
        except Exception as e:
            logger.error(f"NewService API call failed: {e}")
            raise
```

### 3. Extending Configuration

Add new settings following the validation pattern:

```python
# In settings.py
class Settings(BaseSettings):
    # Existing settings...

    # New service configuration
    new_service_api_key: Optional[str] = Field(
        default=None,
        description="API key for NewService integration"
    )

    new_service_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Timeout for NewService API calls in seconds"
    )

    @field_validator('new_service_api_key')
    @classmethod
    def validate_new_service_key(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.startswith('ns_'):
            raise ValueError("NewService API key must start with 'ns_'")
        return v
```

### 4. Adding Utility Functions

Create focused, single-purpose utilities:

```python
# In utils/data_processing.py
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def clean_api_response(raw_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean and normalize API response data.

    Args:
        raw_response: Raw API response dictionary

    Returns:
        Cleaned response dictionary
    """
    try:
        # Remove null values
        cleaned = {k: v for k, v in raw_response.items() if v is not None}

        # Normalize string fields
        if 'message' in cleaned:
            cleaned['message'] = cleaned['message'].strip()

        return cleaned
    except Exception as e:
        logger.error(f"Failed to clean API response: {e}")
        return raw_response
```

## Testing Guidelines

### Test Structure

Follow the comprehensive testing pattern from `test_initialization.py`:

```python
class TestNewFeature:
    """
    Comprehensive test suite for NewFeature.

    Tests cover:
    - Valid configuration scenarios
    - Invalid input validation
    - Error handling
    - Boundary conditions
    """

    def setup_method(self):
        """Setup test fixtures."""
        self.valid_config = SomeConfig(param="valid-value")

    def test_valid_scenario(self):
        """Test normal operation with valid inputs."""
        # Test implementation
        assert result == expected

    def test_invalid_input_raises_error(self):
        """Test that invalid inputs raise appropriate errors."""
        with pytest.raises(ValidationError):
            SomeConfig(param="invalid-value")
```

### Async Testing

For async methods, use pytest-asyncio:

```python
@pytest.mark.asyncio
async def test_async_method_success(self):
    """Test successful async API call."""
    # Mock the external dependency
    with patch('module.ExternalClient') as mock_client:
        mock_client.return_value.call_api = AsyncMock(
            return_value={"status": "success"}
        )

        client = YourAsyncClient()
        result = await client.some_method("test")

        assert result["status"] == "success"
```

### Testing API Clients

**Mock external dependencies** but test your client logic:

```python
@pytest.mark.asyncio
async def test_client_retry_logic(self):
    """Test that client retries on failure then succeeds."""
    from your_module import SomeAPIError

    mock_response = {"data": "success"}
    mock_client = AsyncMock()

    # First call fails, second succeeds
    mock_client.call_api.side_effect = [
        SomeAPIError("Temporary failure"),
        mock_response
    ]

    with patch('your_module.ExternalAPI') as mock_api:
        mock_api.return_value = mock_client

        client = YourClient()
        result = await client.call_with_retry("test")

        assert result == mock_response
        assert mock_client.call_api.call_count == 2
```

### Test Coverage Requirements

- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test component interactions
- **Error scenarios**: Test all error paths and edge cases
- **Boundary testing**: Test limits and edge values
- **Configuration testing**: Test all settings combinations

## Git Workflow

### Commit Message Format

Use clear, descriptive commit messages following this project's pattern:

```
type(scope): brief description

Detailed explanation of the changes if needed.

- Bullet point for significant change
- Another important change

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code changes that neither fix bugs nor add features
- `test`: Add or update tests
- `chore`: Build process or auxiliary tool changes

**Examples**:
```
feat(client): add retry logic for GPT-5 API calls

Implement exponential backoff retry mechanism for handling
temporary API failures. Configurable via MAX_RETRIES setting.

- Add tenacity dependency for robust retry patterns
- Include logging for retry attempts
- Test coverage for retry scenarios
```

### Branch Naming

Use descriptive branch names:
- `feature/add-conversation-state`
- `fix/api-timeout-handling`
- `docs/update-development-guide`
- `test/improve-client-coverage`

### Pull Request Process

1. **Create feature branch** from main
2. **Implement changes** following code standards
3. **Write comprehensive tests**
4. **Update documentation** if needed
5. **Ensure tests pass**: `pytest tests/`
6. **Create PR** with clear description

**PR Template**:
```markdown
## Summary
Brief description of changes and why they're needed.

## Changes Made
- Specific change 1
- Specific change 2

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Documentation
- [ ] Code comments added
- [ ] Documentation updated if needed
```

## Debugging and Troubleshooting

### Structured Logging

Use the project's structured logging pattern for debugging:

```python
import structlog

log = structlog.get_logger()

# Add contextual information
log.debug(
    "Processing API request",
    conversation_id=conv_id,
    prompt_length=len(prompt),
    reasoning_effort=effort
)

# Log errors with full context
try:
    result = await api_call()
except Exception as e:
    log.error(
        "API call failed",
        error=str(e),
        error_type=type(e).__name__,
        conversation_id=conv_id,
        retry_count=retry_count
    )
    raise
```

### Debug Configuration

For debugging, use these environment settings:

```env
# .env for debugging
LOG_LEVEL=DEBUG
DEFAULT_REASONING_EFFORT=low
TIMEOUT_SECONDS=300
MAX_RETRIES=1
```

### Common Debugging Patterns

**API Client Issues**:
```python
# Check client readiness
if not client.is_ready:
    logger.error("Client not ready",
                api_key_present=bool(client.settings.openai_api_key))

# Log request details
logger.debug("API request details",
            model=model,
            params=request_params)
```

**Configuration Issues**:
```python
# Validate settings on startup
try:
    settings = Settings()
    logger.info("Settings loaded successfully",
               api_key_length=len(settings.openai_api_key) if settings.openai_api_key else 0)
except ValidationError as e:
    logger.error("Settings validation failed", errors=e.errors())
```

### Testing and Debugging Tools

**Run tests with verbose output**:
```bash
# Run all tests with detailed output
pytest tests/ -v --tb=short

# Run specific test file
pytest tests/test_initialization.py -v

# Run with debugging output
pytest tests/ -v --log-cli-level=DEBUG
```

**Debug specific scenarios**:
```python
# Add temporary debug prints (remove before committing)
import json
print(f"DEBUG: Response structure: {json.dumps(response, indent=2)}")

# Use pdb for interactive debugging
import pdb; pdb.set_trace()
```

## Performance Considerations

### Async Best Practices

**Use async/await properly** for I/O bound operations:

```python
# Good - concurrent API calls
async def process_batch(self, prompts: List[str]) -> List[Any]:
    """Process multiple prompts concurrently."""
    tasks = [
        self.create_response(prompt)
        for prompt in prompts
    ]
    return await asyncio.gather(*tasks, return_exceptions=True)

# Good - sequential processing when order matters
async def process_conversation(self, messages: List[str]) -> List[Any]:
    """Process conversation messages in order."""
    responses = []
    for message in messages:
        response = await self.create_response(message)
        responses.append(response)
    return responses
```

**Implement proper resource cleanup**:
```python
async def __aenter__(self):
    return self

async def __aexit__(self, exc_type, exc_val, exc_tb):
    if self._client:
        await self._client.close()
```

### Memory Management

**Clear conversation states periodically**:
```python
# From gpt5_client.py pattern
def clear_old_conversations(self, max_age_hours: int = 24) -> int:
    """Clear conversation states older than specified hours."""
    # Implementation based on timestamp tracking
    pass
```

**Use generators for large datasets**:
```python
def process_large_dataset(data_source):
    """Process large dataset efficiently with generators."""
    for batch in batch_iterator(data_source, batch_size=100):
        yield process_batch(batch)
```

### API Rate Limiting

**Implement backoff strategies**:
```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def api_call_with_backoff(self, prompt: str):
    """API call with exponential backoff retry."""
    return await self._client.create_response(prompt)
```

**Monitor API usage**:
```python
# Track API calls for monitoring
class APIMetrics:
    def __init__(self):
        self.call_count = 0
        self.total_tokens = 0

    def record_call(self, tokens_used: int):
        self.call_count += 1
        self.total_tokens += tokens_used
```

### Development Performance Tips

1. **Use `gpt-5-mini` during development** for faster responses
2. **Set `reasoning_effort="low"`** for quick testing
3. **Implement caching** for repeated API calls during development
4. **Use smaller test datasets** for faster test runs
5. **Profile code** with `cProfile` for performance bottlenecks

---

## Getting Started with Development

1. **Set up development environment**:
   ```bash
   python scripts/setup_project.py
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Install development dependencies**:
   ```bash
   pip install pytest pytest-asyncio
   ```

3. **Run tests to verify setup**:
   ```bash
   pytest tests/ -v
   ```

4. **Create your feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

5. **Follow the patterns** established in existing code
6. **Write tests first** or alongside your code
7. **Update documentation** for user-facing changes

This guide will help you maintain consistency with the existing codebase while building robust, maintainable features. Remember: **simple, clear code is always better than clever code**, especially when working with AI APIs where debugging can be challenging.