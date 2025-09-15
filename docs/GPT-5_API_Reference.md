# GPT-5 API Reference

## Models

### Available Models
| Model | Input Price | Output Price | Context Window | Use Case |
|-------|------------|--------------|----------------|----------|
| `gpt-5` | $1.25/1M tokens | $10/1M tokens | 400K total | Complex tasks, high accuracy |
| `gpt-5-mini` | $0.25/1M tokens | $2/1M tokens | 400K total | Balanced performance/cost |
| `gpt-5-nano` | $0.05/1M tokens | $0.40/1M tokens | 400K total | High-volume, cost-sensitive |

### Token Limits
- **Maximum Input Tokens**: 272,000
- **Maximum Output Tokens**: 128,000 (reasoning + output combined)
- **Total Context Length**: 400,000 tokens

## Core Parameters

### reasoning
Controls the depth of reasoning before generating a response.

```python
reasoning = {
    "effort": "medium"  # Options: minimal, low, medium, high
}
```

- **minimal**: Very few or no reasoning tokens, fastest response
- **low**: Light reasoning for simple tasks
- **medium**: (Default) Balanced reasoning depth
- **high**: Extended reasoning for complex problems

### text
Controls output characteristics.

```python
text = {
    "verbosity": "medium",  # Options: low, medium, high
    "format": {
        "type": "json_schema",
        "schema": {...}  # JSON schema definition
    }
}
```

### verbosity
- **low**: Short, concise answers
- **medium**: Balanced detail level
- **high**: Comprehensive, detailed responses

## Tools

### Built-in Tools

#### Web Search
```python
tools = [
    {"type": "web_search"}
]
```
Enables real-time web searching capabilities.

#### File Search
```python
tools = [
    {"type": "file_search"}
]
```
Search through uploaded files and documents.

#### Code Interpreter
```python
tools = [
    {"type": "code_interpreter"}
]
```
Execute Python code in a sandboxed environment.

### Custom Tools

#### JSON-based Tools (Traditional)
```python
tools = [{
    "type": "function",
    "function": {
        "name": "extract_data",
        "description": "Extract structured data from text",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "fields": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["text", "fields"]
        }
    }
}]
```

#### Plaintext Custom Tools (New)
```python
tools = [{
    "type": "custom",
    "name": "process_sql",
    "description": "Process raw SQL queries without JSON wrapping"
}]
```

## Custom Tool Definitions for CEO Research

### extract_tenure_dates
```python
{
    "type": "custom",
    "name": "extract_tenure_dates",
    "description": "Extract CEO start/end dates from text. Returns dates in MM/DD/YYYY format with precision indicator (exact, month_year, year_only). Handles various date formats and relative references."
}
```

### classify_insider_outsider
```python
{
    "type": "custom",
    "name": "classify_insider_outsider",
    "description": "Classify CEO as insider (1) or outsider (0) based on career history. Analyzes promotion path, previous positions within company, and time with organization. Returns classification with supporting evidence."
}
```

### extract_career_progression
```python
{
    "type": "custom",
    "name": "extract_career_progression",
    "description": "Extract complete career timeline including positions, companies, and dates. Maps executive progression, board positions, and subsidiary roles. Returns structured career path data."
}
```

### classify_departure_type
```python
{
    "type": "custom",
    "name": "classify_departure_type",
    "description": "Analyze CEO departure circumstances to determine if forced (1) or voluntary (0). Examines language patterns, timing, successor planning, and contextual clues. Returns classification with confidence score."
}
```

### validate_sources
```python
{
    "type": "custom",
    "name": "validate_sources",
    "description": "Score source reliability based on type (official filing, news, database), recency, and authority. Returns reliability score 0-1 and flags potential issues."
}
```

### assess_data_completeness
```python
{
    "type": "custom",
    "name": "assess_data_completeness",
    "description": "Evaluate collected data against required fields. Identifies gaps, suggests follow-up queries, and calculates overall completeness percentage. Returns assessment with specific missing fields."
}
```

### resolve_conflicts
```python
{
    "type": "custom",
    "name": "resolve_conflicts",
    "description": "Resolve conflicting information across sources using reasoning and source reliability. Returns consolidated data point with explanation of resolution logic."
}
```

## Structured Output

### JSON Schema Format
```python
response = client.responses.create(
    model="gpt-5",
    input="Extract CEO information",
    text={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "person_name": {"type": "string"},
                    "insider_outsider": {"type": "integer"},
                    "ceo_start_date": {"type": "string"},
                    "confidence_score": {"type": "number"}
                },
                "required": ["person_name", "insider_outsider"]
            }
        }
    }
)
```

### Context-Free Grammar (CFG)
```python
tools = [{
    "type": "custom",
    "name": "parse_structured",
    "description": "Parse with grammar constraints",
    "grammar": "..."  # CFG definition
}]
```

## Response Object

### Structure
```python
{
    "id": "resp_abc123",
    "object": "response",
    "created": 1723456789,
    "model": "gpt-5",
    "usage": {
        "prompt_tokens": 150,
        "reasoning_tokens": 500,
        "completion_tokens": 200,
        "total_tokens": 850
    },
    "choices": [{
        "message": {
            "role": "assistant",
            "content": "Response content here"
        },
        "finish_reason": "stop"
    }]
}
```

### Token Usage Breakdown
- **prompt_tokens**: Input tokens
- **reasoning_tokens**: Internal reasoning (charged as output)
- **completion_tokens**: Final response tokens
- **total_tokens**: Sum of all token types

## Stateful Conversations

### Initial Request
```python
response1 = client.responses.create(
    model="gpt-5",
    input="Analyze this company's CEO",
    tools=[{"type": "web_search"}]
)
```

### Follow-up Request
```python
response2 = client.responses.create(
    model="gpt-5",
    input="Now extract tenure information",
    previous_response_id=response1.id  # Maintains context
)
```

## Error Codes

### Common Errors
| Error Code | Description | Resolution |
|------------|-------------|------------|
| `rate_limit_exceeded` | Too many requests | Implement exponential backoff |
| `context_length_exceeded` | Input too long | Reduce input size |
| `invalid_tool_call` | Tool error | Check tool configuration |
| `model_not_available` | Model access issue | Check subscription/permissions |

## Rate Limits

### Default Limits
- **Requests per minute (RPM)**: Varies by tier
- **Tokens per minute (TPM)**: Varies by tier
- **Concurrent requests**: Limited by subscription

### Tier-based Limits
| Tier | RPM | TPM | Concurrent |
|------|-----|-----|------------|
| Free | 20 | 150K | 2 |
| Plus | 100 | 1M | 10 |
| Pro | 500 | 5M | 50 |
| Enterprise | Custom | Custom | Custom |

## Best Practices

### 1. Optimize Reasoning Effort
```python
# Simple query - use minimal
simple_response = client.responses.create(
    model="gpt-5",
    input="What is 2+2?",
    reasoning={"effort": "minimal"}
)

# Complex analysis - use high
complex_response = client.responses.create(
    model="gpt-5",
    input="Analyze market trends and predict outcomes",
    reasoning={"effort": "high"}
)
```

### 2. Batch Processing
```python
# Process multiple items efficiently
async def batch_process(items):
    tasks = []
    for item in items:
        task = client.responses.create(
            model="gpt-5-nano",  # Use nano for high volume
            input=item,
            reasoning={"effort": "low"}
        )
        tasks.append(task)
    return await asyncio.gather(*tasks)
```

### 3. Error Handling
```python
import time
from openai import OpenAI, RateLimitError, APIError

def robust_api_call(client, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return client.responses.create(**kwargs)
        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
        except APIError as e:
            print(f"API Error: {e}")
            raise
```

### 4. Cost Optimization
```python
# Use appropriate model size
def select_model(task_complexity):
    if task_complexity == "simple":
        return "gpt-5-nano"
    elif task_complexity == "moderate":
        return "gpt-5-mini"
    else:
        return "gpt-5"
```

## Python SDK Example

### Complete Implementation
```python
from openai import OpenAI
import json

# Initialize client
client = OpenAI(api_key="your-api-key")

# Define schema for structured output
CEO_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "company": {"type": "string"},
        "insider_outsider": {"type": "integer"},
        "tenure_start": {"type": "string"},
        "confidence": {"type": "number"}
    },
    "required": ["name", "company"]
}

# Make API call with all features
response = client.responses.create(
    model="gpt-5",
    input="Research John Smith, CEO of TechCorp",
    reasoning={"effort": "high"},
    text={
        "verbosity": "medium",
        "format": {
            "type": "json_schema",
            "schema": CEO_SCHEMA
        }
    },
    tools=[
        {"type": "web_search"},
        {
            "type": "custom",
            "name": "classify_insider_outsider",
            "description": "Classify CEO promotion path"
        }
    ]
)

# Parse structured response
result = json.loads(response.choices[0].message.content)
print(f"CEO: {result['name']}")
print(f"Classification: {'Insider' if result.get('insider_outsider') == 1 else 'Outsider'}")
print(f"Confidence: {result.get('confidence', 'N/A')}")
```

## Additional Resources

- [OpenAI Platform Documentation](https://platform.openai.com/docs)
- [OpenAI Cookbook Examples](https://cookbook.openai.com)
- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/ai-foundry/openai)
- [Community Forums](https://community.openai.com)