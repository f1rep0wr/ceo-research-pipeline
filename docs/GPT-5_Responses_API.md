# GPT-5 Responses API Documentation

## Overview

The Responses API is a new stateful API from OpenAI that brings together the best capabilities from the chat completions and assistants API in one unified experience. It's specifically designed to enhance GPT-5's capabilities for agentic and tool-calling workflows.

## Key Features

### 1. Stateful Design
- **No conversation history management**: Pass an ID representing conversation state instead of entire history
- **Automatic state management**: OpenAI maintains conversation context server-side
- **Reasoning persistence**: Reasoning traces are preserved between tool calls

### 2. Performance Benefits
- **Improved accuracy**: Tau-Bench Retail scores increase from 73.9% to 78.2% when switching from Chat Completions API
- **Token efficiency**: Eliminates need to reconstruct plans after each tool call
- **Lower latency**: Faster responses due to persistent context

### 3. Built-in Tools
- Web search
- File search
- Code interpreter
- Image generation
- Custom tools support

## API Configuration

### Basic Request Structure
```python
from openai import OpenAI

client = OpenAI()

# Initial request
response = client.responses.create(
    model="gpt-5",
    input="Your prompt here",
    reasoning={"effort": "medium"},  # Options: minimal, low, medium, high
    text={"verbosity": "medium"},    # Options: low, medium, high
    tools=[
        {"type": "web_search"},
        {"type": "custom", "name": "your_tool"}
    ]
)

# Follow-up request using state
follow_up = client.responses.create(
    model="gpt-5",
    input="Follow-up question",
    previous_response_id=response.id  # Maintains conversation state
)
```

## Reasoning Control

### Reasoning Effort Levels

#### 1. Minimal
- Very few or no reasoning tokens
- Fastest time-to-first-token
- Best for simple queries

#### 2. Low
- Light reasoning
- Quick responses
- Suitable for straightforward tasks

#### 3. Medium (Default)
- Balanced reasoning depth
- Good for most use cases
- Optimal cost/performance ratio

#### 4. High
- Extended reasoning
- Maximum quality
- Best for complex problems

### Implementation Example
```python
# High-complexity research request
response = client.responses.create(
    model="gpt-5",
    input=research_prompt,
    reasoning={"effort": "high"},      # Complex CEO research
    text={"verbosity": "medium"},
    tools=[
        {"type": "web_search"},         # Built-in web search
        {
            "type": "custom",           # Custom extraction tool
            "name": "extract_ceo_data",
            "description": "Extract structured CEO information"
        }
    ],
    text={
        "format": {                     # Structured output
            "type": "json_schema",
            "schema": CEO_PROFILE_SCHEMA
        }
    }
)

# Simple lookup request (optimized for speed/cost)
quick_response = client.responses.create(
    model="gpt-5",
    input=simple_query,
    reasoning={"effort": "minimal"},   # Simple lookups
    text={"verbosity": "low"}
)
```

## Verbosity Control

### Verbosity Levels
- **Low**: Short, concise answers
- **Medium**: Balanced detail
- **High**: Comprehensive, detailed responses

### Natural Language Overrides
GPT-5 is trained to respond to natural-language verbosity overrides in prompts for specific contexts.

## Custom Tools

### Traditional JSON Tools
```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            }
        }
    }
}]
```

### New Custom Tools (Plaintext)
```python
tools = [{
    "type": "custom",
    "name": "process_code",
    "description": "Process raw Python code",
    # Accepts plaintext instead of JSON
    # Supports context-free grammar constraints
}]
```

## Structured Output

### JSON Schema Support
```python
response = client.responses.create(
    model="gpt-5",
    input=prompt,
    text={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "classification": {"type": "integer"},
                    "confidence": {"type": "number"}
                },
                "required": ["name", "classification"]
            }
        }
    }
)
```

## Multi-turn Interactions

### Sequential Tool Calling
```python
# Initial request with tool call
response1 = client.responses.create(
    model="gpt-5",
    input="Research CEO information",
    tools=[{"type": "web_search"}]
)

# Follow-up preserving reasoning
response2 = client.responses.create(
    model="gpt-5",
    input="Extract tenure information from the research",
    previous_response_id=response1.id,
    tools=[{"type": "custom", "name": "extract_tenure"}]
)
```

## Tool Calling Improvements

### Enhanced Capabilities
1. **Better instruction following**: More accurate tool usage
2. **Error handling**: Improved handling of tool errors
3. **Sequential/parallel execution**: Smarter orchestration of multiple tools
4. **Progress updates**: Preamble messages during long tasks

### Example with Progress Updates
```python
response = client.responses.create(
    model="gpt-5",
    input="Analyze multiple data sources",
    tools=multiple_tools,
    # GPT-5 can output progress messages between tool calls
    allow_preamble=True
)
```

## Best Practices

### 1. Choose Appropriate Reasoning Effort
- Use `minimal` for simple lookups
- Use `low` for standard queries
- Use `medium` for most applications
- Reserve `high` for complex analysis

### 2. Leverage Stateful Nature
- Always pass `previous_response_id` for follow-ups
- Avoid reconstructing conversation history
- Let the API manage reasoning traces

### 3. Optimize Token Usage
- Use appropriate verbosity levels
- Leverage structured outputs
- Utilize custom tools for plaintext data

### 4. Tool Strategy
- Prefer Responses API for agentic workflows
- Use custom tools for non-JSON data
- Implement proper error handling

## Migration from Chat Completions API

### Key Differences
1. **Stateful vs Stateless**: No need to manage conversation history
2. **Reasoning persistence**: Maintains chain-of-thought between calls
3. **Tool improvements**: Better handling and orchestration
4. **Performance gains**: Significant accuracy improvements

### Migration Example
```python
# Old (Chat Completions)
messages = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Previous question"},
    {"role": "assistant", "content": "Previous answer"},
    {"role": "user", "content": "New question"}
]
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages
)

# New (Responses API)
response = client.responses.create(
    model="gpt-5",
    input="New question",
    previous_response_id=previous_response.id  # Automatic context
)
```

## Supported Models

### GPT-5 Series
- `gpt-5` (Version: 2025-08-07)
- `gpt-5-mini` (Version: 2025-08-07)
- `gpt-5-nano` (Version: 2025-08-07)
- `gpt-5-chat` (Version: 2025-08-07)

### Legacy Support
- `gpt-4o` (Multiple versions)
- `gpt-4o-mini` (Version: 2024-07-18)

## Error Handling

### Rate Limiting
```python
import time
from openai import RateLimitError

def call_with_retry(client, **kwargs):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return client.responses.create(**kwargs)
        except RateLimitError as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

## Recommendations

1. **Always use Responses API for GPT-5** when building agentic applications
2. **Leverage stateful design** for multi-turn interactions
3. **Use appropriate reasoning levels** to optimize cost/performance
4. **Implement proper error handling** for production systems
5. **Monitor token usage** and adjust verbosity/reasoning as needed