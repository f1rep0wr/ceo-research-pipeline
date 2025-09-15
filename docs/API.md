# GPT5ResponsesClient API Documentation

This document provides comprehensive API reference for the `GPT5ResponsesClient` class, which provides a simple, async interface for interacting with the OpenAI GPT-5 Responses API.

## Table of Contents

- [Quick Start](#quick-start)
- [Class Overview](#class-overview)
- [Initialization](#initialization)
- [Methods](#methods)
- [Conversation State Management](#conversation-state-management)
- [Error Handling](#error-handling)
- [Complete Usage Examples](#complete-usage-examples)

## Quick Start

```python
import asyncio
from gpt_5_ceo_research.src.config.settings import Settings
from gpt_5_ceo_research.src.clients.gpt5_client import GPT5ResponsesClient

# Initialize client with settings
settings = Settings(openai_api_key="sk-your-api-key-here")
client = GPT5ResponsesClient(settings)

async def main():
    # Test connection
    if await client.test_connection():
        print("Connected to GPT-5 API successfully")

    # Create a response
    response = await client.create_response(
        prompt="Explain quantum computing in simple terms",
        reasoning_effort="medium"
    )
    print(response.output)

asyncio.run(main())
```

## Class Overview

```python
class GPT5ResponsesClient:
    """
    Async client for GPT-5 API interactions with conversation state management.

    This client provides a simple interface for GPT-5 API calls while managing
    conversation states and handling configuration gracefully.
    """
```

The `GPT5ResponsesClient` is designed with the KISS principle in mind - providing straightforward async access to GPT-5's Responses API with built-in:

- Automatic retry logic with exponential backoff
- Conversation state management for multi-turn conversations
- Graceful error handling and logging
- Connection testing capabilities
- Type safety and comprehensive error messages

## Initialization

### `__init__(settings: Settings) -> None`

Initialize the GPT-5 client with application settings.

**Parameters:**
- `settings` (`Settings`): Application settings containing API configuration

**Behavior:**
- Gracefully handles missing or invalid API keys
- Initializes conversation state storage
- Sets up async OpenAI client if API key is valid
- Logs initialization status

**Example:**
```python
from gpt_5_ceo_research.src.config.settings import Settings
from gpt_5_ceo_research.src.clients.gpt5_client import GPT5ResponsesClient

# With valid API key
settings = Settings(openai_api_key="sk-your-api-key-here")
client = GPT5ResponsesClient(settings)

# Client handles missing API key gracefully
settings_no_key = Settings(openai_api_key="sk-placeholder") # Will fail validation
# Use environment variables instead or handle ValidationError
```

### Properties

#### `is_ready: bool` (property)

Check if the client is ready to make API calls.

**Returns:**
- `bool`: True if client has valid API key and is initialized, False otherwise

**Example:**
```python
client = GPT5ResponsesClient(settings)
if client.is_ready:
    response = await client.create_response("Hello, GPT-5!")
else:
    print("Client not ready - check API key configuration")
```

## Methods

### `test_connection() -> bool` (async)

Test API connectivity with a minimal request to verify API key and service availability.

**Returns:**
- `bool`: True if connection successful, False for any failure

**Example:**
```python
async def check_api_status():
    client = GPT5ResponsesClient(settings)

    if await client.test_connection():
        print("✓ GPT-5 API is accessible")
        return True
    else:
        print("✗ GPT-5 API connection failed")
        return False
```

### `create_response(prompt, conversation_id=None, reasoning_effort=None, **kwargs) -> Any` (async)

Create a response using GPT-5 Responses API with automatic retry logic and conversation state management.

**Parameters:**
- `prompt` (`str`): The input prompt for the API
- `conversation_id` (`Optional[str]`): Optional conversation ID for state management
- `reasoning_effort` (`Optional[str]`): Reasoning effort level ("minimal", "low", "medium", "high")
- `**kwargs`: Additional parameters passed to the API

**Returns:**
- API response object with `id`, `output`, and other response fields

**Raises:**
- `ValueError`: If client is not ready (missing API key)
- `OpenAIError`: If API call fails after retries
- Various `OpenAI` specific exceptions for different error types

**Examples:**

#### Basic Usage
```python
async def basic_example():
    client = GPT5ResponsesClient(settings)

    response = await client.create_response(
        prompt="What are the key principles of software architecture?"
    )

    print(f"Response ID: {response.id}")
    print(f"Content: {response.output}")
```

#### With Reasoning Effort
```python
async def reasoning_example():
    client = GPT5ResponsesClient(settings)

    # For complex analysis, use higher reasoning effort
    response = await client.create_response(
        prompt="Analyze the economic implications of renewable energy adoption",
        reasoning_effort="high"
    )

    print(response.output)
```

#### With Conversation Context
```python
async def conversation_example():
    client = GPT5ResponsesClient(settings)
    conversation_id = "financial-analysis-session"

    # First message in conversation
    response1 = await client.create_response(
        prompt="What are the current trends in cryptocurrency markets?",
        conversation_id=conversation_id,
        reasoning_effort="medium"
    )

    # Follow-up message - automatically uses previous response context
    response2 = await client.create_response(
        prompt="How might these trends affect traditional banking?",
        conversation_id=conversation_id,
        reasoning_effort="medium"
    )

    print("First response:", response1.output)
    print("Follow-up response:", response2.output)
```

#### With Additional Parameters
```python
async def advanced_example():
    client = GPT5ResponsesClient(settings)

    response = await client.create_response(
        prompt="Explain machine learning concepts",
        conversation_id="ml-tutorial",
        reasoning_effort="medium",
        verbosity="high",  # Custom verbosity level
        # Add any other API parameters as needed
    )

    print(response.output)
```

## Conversation State Management

The client automatically manages conversation state to enable multi-turn conversations with GPT-5.

### `get_conversation_state(conversation_id: str) -> Optional[Dict[str, Any]]`

Retrieve conversation state for a given conversation ID.

**Parameters:**
- `conversation_id` (`str`): Unique identifier for the conversation

**Returns:**
- `Optional[Dict[str, Any]]`: Conversation state dictionary or None if not found

### `set_conversation_state(conversation_id: str, state: Dict[str, Any]) -> None`

Set conversation state for a given conversation ID.

**Parameters:**
- `conversation_id` (`str`): Unique identifier for the conversation
- `state` (`Dict[str, Any]`): State dictionary to store

### `clear_conversation_state(conversation_id: str) -> bool`

Clear conversation state for a specific conversation.

**Parameters:**
- `conversation_id` (`str`): Unique identifier for the conversation

**Returns:**
- `bool`: True if state was found and cleared, False otherwise

### `clear_all_conversation_states() -> int`

Clear all conversation states.

**Returns:**
- `int`: Number of conversation states that were cleared

**Examples:**

```python
async def conversation_management_example():
    client = GPT5ResponsesClient(settings)

    # Start a conversation
    conversation_id = "project-planning"

    await client.create_response(
        "Let's plan a software project",
        conversation_id=conversation_id
    )

    # Check if conversation exists
    state = client.get_conversation_state(conversation_id)
    if state:
        print(f"Conversation active with response ID: {state['response_id']}")

    # Continue conversation
    await client.create_response(
        "What technologies should we consider?",
        conversation_id=conversation_id
    )

    # Clear specific conversation
    if client.clear_conversation_state(conversation_id):
        print("Conversation cleared")

    # Or clear all conversations
    cleared_count = client.clear_all_conversation_states()
    print(f"Cleared {cleared_count} conversations")
```

## Error Handling

The client implements comprehensive error handling with specific exception types and automatic retry logic.

### Exception Types

- **`ValueError`**: Raised when client is not ready (missing API key)
- **`OpenAIError`**: Base class for OpenAI API errors
- **`APIError`**: API request failed
- **`Timeout`**: Request timed out
- **`RateLimitError`**: Rate limit exceeded
- **`AuthenticationError`**: Invalid API key
- **`PermissionError`**: Insufficient permissions
- **`NotFoundError`**: Resource not found

### Retry Logic

The client automatically retries failed requests with exponential backoff:
- **Retry attempts**: Up to 3 attempts
- **Retry conditions**: OpenAIError, ConnectionError, TimeoutError
- **Backoff**: Exponential (1s, 2s, 4s, etc.) with jitter
- **Max delay**: 10 seconds between attempts

### Error Handling Examples

```python
async def error_handling_example():
    client = GPT5ResponsesClient(settings)

    try:
        response = await client.create_response(
            "Analyze complex financial data",
            reasoning_effort="high"
        )
        print(response.output)

    except ValueError as e:
        print(f"Client configuration error: {e}")
        # Handle missing API key or invalid configuration

    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
        # Handle invalid API key

    except RateLimitError as e:
        print(f"Rate limit exceeded: {e}")
        # Handle rate limiting - client will retry automatically

    except TimeoutError as e:
        print(f"Request timed out: {e}")
        # Handle timeout - client will retry automatically

    except OpenAIError as e:
        print(f"OpenAI API error: {e}")
        # Handle other API errors

    except Exception as e:
        print(f"Unexpected error: {e}")
        # Handle unexpected errors

async def graceful_degradation_example():
    """Example of graceful degradation when API is unavailable"""
    client = GPT5ResponsesClient(settings)

    # Test connection first
    if not await client.test_connection():
        print("GPT-5 API unavailable, using fallback logic")
        # Implement fallback behavior
        return "API unavailable - please try again later"

    try:
        response = await client.create_response("Your prompt here")
        return response.output
    except OpenAIError:
        print("API call failed, implementing fallback")
        # Implement fallback behavior
        return "Service temporarily unavailable"
```

## Complete Usage Examples

### Basic Research Assistant

```python
import asyncio
from gpt_5_ceo_research.src.config.settings import Settings
from gpt_5_ceo_research.src.clients.gpt5_client import GPT5ResponsesClient

async def research_assistant():
    """Basic research assistant using GPT-5"""
    settings = Settings(openai_api_key="sk-your-api-key-here")
    client = GPT5ResponsesClient(settings)

    # Verify connection
    if not await client.test_connection():
        print("Failed to connect to GPT-5 API")
        return

    conversation_id = "research-session-001"

    try:
        # Initial research query
        response1 = await client.create_response(
            prompt="What are the latest developments in quantum computing hardware?",
            conversation_id=conversation_id,
            reasoning_effort="high"
        )

        print("Initial Research:")
        print(response1.output)
        print("\n" + "="*50 + "\n")

        # Follow-up analysis
        response2 = await client.create_response(
            prompt="Which companies are leading these developments and what are their key innovations?",
            conversation_id=conversation_id,
            reasoning_effort="high"
        )

        print("Follow-up Analysis:")
        print(response2.output)

    except Exception as e:
        print(f"Research session failed: {e}")

    finally:
        # Clean up conversation
        client.clear_conversation_state(conversation_id)

if __name__ == "__main__":
    asyncio.run(research_assistant())
```

### Multi-Topic Analysis System

```python
import asyncio
from typing import List, Dict
from gpt_5_ceo_research.src.config.settings import Settings
from gpt_5_ceo_research.src.clients.gpt5_client import GPT5ResponsesClient

class AnalysisSystem:
    """Multi-topic analysis system using GPT-5"""

    def __init__(self, api_key: str):
        self.settings = Settings(openai_api_key=api_key)
        self.client = GPT5ResponsesClient(self.settings)

    async def analyze_topics(self, topics: List[str]) -> Dict[str, str]:
        """Analyze multiple topics in parallel"""

        # Test connection first
        if not await self.client.test_connection():
            raise ConnectionError("Unable to connect to GPT-5 API")

        results = {}

        # Process topics concurrently
        tasks = []
        for topic in topics:
            task = self._analyze_single_topic(topic)
            tasks.append(task)

        # Wait for all analyses to complete
        analyses = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for topic, analysis in zip(topics, analyses):
            if isinstance(analysis, Exception):
                results[topic] = f"Analysis failed: {analysis}"
            else:
                results[topic] = analysis

        return results

    async def _analyze_single_topic(self, topic: str) -> str:
        """Analyze a single topic"""
        try:
            response = await self.client.create_response(
                prompt=f"Provide a comprehensive analysis of: {topic}",
                conversation_id=f"topic-{hash(topic)}",
                reasoning_effort="high"
            )
            return response.output

        except Exception as e:
            raise Exception(f"Failed to analyze '{topic}': {e}")

    async def comparative_analysis(self, topics: List[str]) -> str:
        """Perform comparative analysis across topics"""

        # First, get individual analyses
        individual_results = await self.analyze_topics(topics)

        # Then, perform comparative analysis
        comparison_prompt = f"""
        Based on the following analyses, provide a comparative summary:

        {chr(10).join(f"Topic: {topic}{chr(10)}Analysis: {analysis}{chr(10)}"
                     for topic, analysis in individual_results.items())}

        Please identify key similarities, differences, and relationships between these topics.
        """

        try:
            comparison_response = await self.client.create_response(
                prompt=comparison_prompt,
                conversation_id="comparative-analysis",
                reasoning_effort="high"
            )
            return comparison_response.output

        except Exception as e:
            return f"Comparative analysis failed: {e}"

async def main():
    system = AnalysisSystem("sk-your-api-key-here")

    topics = [
        "Artificial Intelligence in Healthcare",
        "Blockchain Technology Applications",
        "Renewable Energy Market Trends"
    ]

    print("Starting multi-topic analysis...")

    # Individual topic analyses
    results = await system.analyze_topics(topics)

    print("\n=== INDIVIDUAL ANALYSES ===")
    for topic, analysis in results.items():
        print(f"\n{topic}:")
        print("-" * 50)
        print(analysis)

    # Comparative analysis
    print("\n=== COMPARATIVE ANALYSIS ===")
    comparison = await system.comparative_analysis(topics)
    print(comparison)

if __name__ == "__main__":
    asyncio.run(main())
```

### Production-Ready Service Integration

```python
import asyncio
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from gpt_5_ceo_research.src.config.settings import Settings
from gpt_5_ceo_research.src.clients.gpt5_client import GPT5ResponsesClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPT5Service:
    """Production-ready GPT-5 service with connection management"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._client: Optional[GPT5ResponsesClient] = None
        self._healthy = False

    async def initialize(self) -> bool:
        """Initialize the service and verify connectivity"""
        try:
            self._client = GPT5ResponsesClient(self.settings)

            if self._client.is_ready:
                self._healthy = await self._client.test_connection()
                if self._healthy:
                    logger.info("GPT-5 service initialized successfully")
                else:
                    logger.error("GPT-5 service initialization failed - connection test failed")
            else:
                logger.error("GPT-5 service initialization failed - client not ready")

            return self._healthy

        except Exception as e:
            logger.error(f"GPT-5 service initialization error: {e}")
            self._healthy = False
            return False

    async def health_check(self) -> bool:
        """Perform health check"""
        if not self._healthy or not self._client:
            return False

        try:
            return await self._client.test_connection()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def generate_response(
        self,
        prompt: str,
        conversation_id: Optional[str] = None,
        reasoning_effort: str = "medium",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response with comprehensive error handling"""

        if not self._healthy or not self._client:
            return {
                "success": False,
                "error": "Service not available",
                "response": None
            }

        try:
            response = await self._client.create_response(
                prompt=prompt,
                conversation_id=conversation_id,
                reasoning_effort=reasoning_effort,
                **kwargs
            )

            return {
                "success": True,
                "error": None,
                "response": {
                    "id": response.id,
                    "content": response.output,
                    "conversation_id": conversation_id
                }
            }

        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            return {"success": False, "error": "Configuration error", "response": None}

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return {"success": False, "error": str(e), "response": None}

    async def shutdown(self):
        """Graceful shutdown"""
        if self._client:
            # Clear all conversation states
            cleared = self._client.clear_all_conversation_states()
            logger.info(f"Cleared {cleared} conversation states during shutdown")

        self._healthy = False
        logger.info("GPT-5 service shut down")

@asynccontextmanager
async def gpt5_service_context(settings: Settings):
    """Async context manager for GPT-5 service"""
    service = GPT5Service(settings)

    try:
        if await service.initialize():
            yield service
        else:
            raise RuntimeError("Failed to initialize GPT-5 service")
    finally:
        await service.shutdown()

# Usage example
async def production_example():
    settings = Settings(openai_api_key="sk-your-api-key-here")

    async with gpt5_service_context(settings) as service:
        # Service is now ready to use

        # Health check
        if await service.health_check():
            logger.info("Service is healthy")

        # Generate responses
        result = await service.generate_response(
            prompt="Analyze current market conditions",
            conversation_id="market-analysis-001",
            reasoning_effort="high"
        )

        if result["success"]:
            print(f"Response: {result['response']['content']}")
        else:
            print(f"Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(production_example())
```

---

## Configuration Reference

The client uses `Settings` class for configuration. Key settings include:

```python
# Required
openai_api_key: str  # Must start with 'sk-'

# Optional (with defaults)
gpt5_model: str = "gpt-5"
default_reasoning_effort: Literal["minimal", "low", "medium", "high"] = "medium"
default_verbosity: str = "medium"
max_retries: int = 3  # 0-10
timeout_seconds: int = 120  # 1-600
```

For complete configuration options, see the Settings class documentation.

## Best Practices

1. **Always test connection** before making API calls in production
2. **Use conversation IDs** for multi-turn conversations
3. **Handle errors gracefully** with try-except blocks
4. **Choose appropriate reasoning effort** based on task complexity
5. **Clean up conversation states** when no longer needed
6. **Use async context managers** for service lifecycle management
7. **Monitor API usage** and implement rate limiting as needed
8. **Log important events** for debugging and monitoring

This API is designed following KISS principles - simple, reliable, and easy to use while providing the power and flexibility needed for production applications.