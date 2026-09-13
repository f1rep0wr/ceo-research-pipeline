# Configuration Guide

This guide covers all configuration options for the GPT-5 CEO Research application. All configuration is handled through environment variables that can be set directly or via a `.env` file.

## Quick Start

1. Copy the example configuration:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual values:
   ```bash
   # Required: Set your OpenAI API key
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. Validate your configuration:
   ```bash
   python -c "from src.config.settings import get_settings; print('Configuration valid!')"
   ```

## Environment Variables Reference

### OpenAI API Configuration

#### OPENAI_API_KEY
- **Purpose**: Authentication key for OpenAI API access
- **Required**: Yes
- **Format**: Must start with `sk-`
- **Example**: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx`
- **Where to get**: [OpenAI Platform API Keys](https://platform.openai.com/api-keys)
- **Impact**: Required for all GPT-5 model interactions

### Model Configuration

#### GPT5_MODEL
- **Purpose**: Specifies which GPT-5 model variant to use
- **Required**: No
- **Default**: `gpt-5`
- **Valid values**:
  - `gpt-5`: Most capable but slowest and most expensive
  - `gpt-5-mini`: Balanced performance and cost
  - `gpt-5-nano`: Fastest and cheapest but less capable
- **Example**: `GPT5_MODEL=gpt-5-mini`
- **Impact**: Affects response quality, speed, and API costs

### Reasoning Configuration

#### DEFAULT_REASONING_EFFORT
- **Purpose**: Controls the depth of reasoning the model uses
- **Required**: No
- **Default**: `medium`
- **Valid values**: `minimal`, `low`, `medium`, `high`
- **Example**: `DEFAULT_REASONING_EFFORT=high`
- **Impact**:
  - Higher values: Better results but slower responses
  - Lower values: Faster responses but potentially less thorough

### Response Configuration

#### DEFAULT_VERBOSITY
- **Purpose**: Controls how detailed model responses are
- **Required**: No
- **Default**: `medium`
- **Valid values**: `low`, `medium`, `high`
- **Example**: `DEFAULT_VERBOSITY=high`
- **Impact**:
  - `low`: Concise, direct responses
  - `medium`: Balanced detail level
  - `high`: Detailed explanations and context

### API Request Configuration

#### MAX_RETRIES
- **Purpose**: Maximum number of retry attempts for failed API requests
- **Required**: No
- **Default**: `3`
- **Valid range**: 0-10
- **Example**: `MAX_RETRIES=5`
- **Recommended**: 3-5 for production environments
- **Impact**: Higher values increase resilience but may slow down error handling

#### TIMEOUT_SECONDS
- **Purpose**: Request timeout in seconds
- **Required**: No
- **Default**: `120`
- **Valid range**: 1-600 seconds
- **Example**: `TIMEOUT_SECONDS=300`
- **Impact**:
  - Too low: Requests may timeout prematurely
  - Too high: Long waits for failed requests
  - Adjust based on typical query complexity

### Logging Configuration

#### LOG_LEVEL
- **Purpose**: Controls application logging verbosity
- **Required**: No
- **Default**: `INFO`
- **Valid values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Example**: `LOG_LEVEL=DEBUG`
- **Impact**:
  - `DEBUG`: Detailed debugging information (verbose)
  - `INFO`: General operational messages
  - `WARNING`: Warning messages only
  - `ERROR`: Error messages only
  - `CRITICAL`: Critical errors only

### Processing Configuration

#### MAX_ITERATIONS
- **Purpose**: Maximum number of iterations for iterative processes
- **Required**: No
- **Default**: `5`
- **Valid range**: 1-100
- **Example**: `MAX_ITERATIONS=10`
- **Impact**: Prevents infinite loops in recursive reasoning processes

#### CONFIDENCE_THRESHOLD
- **Purpose**: Confidence threshold for accepting results
- **Required**: No
- **Default**: `0.8`
- **Valid range**: 0.0-1.0 (float)
- **Example**: `CONFIDENCE_THRESHOLD=0.7`
- **Impact**: Higher values require more confident results before acceptance

### Caching Configuration

#### CACHE_TTL_HOURS
- **Purpose**: Time-to-live for cached responses
- **Required**: No
- **Default**: `24`
- **Valid range**: 0+ hours (0 disables caching)
- **Example**: `CACHE_TTL_HOURS=48`
- **Impact**:
  - 0: Disables caching (always fresh requests)
  - Higher values: Better performance but potentially stale data

## Environment Examples

### Development Environment
```env
# Development configuration - verbose logging and lower thresholds
OPENAI_API_KEY=sk-your-api-key-here
GPT5_MODEL=gpt-5-nano
DEFAULT_REASONING_EFFORT=low
DEFAULT_VERBOSITY=high
MAX_RETRIES=2
TIMEOUT_SECONDS=60
LOG_LEVEL=DEBUG
MAX_ITERATIONS=3
CONFIDENCE_THRESHOLD=0.6
CACHE_TTL_HOURS=1
```

### Production Environment
```env
# Production configuration - optimized for reliability and performance
OPENAI_API_KEY=sk-your-production-api-key-here
GPT5_MODEL=gpt-5
DEFAULT_REASONING_EFFORT=medium
DEFAULT_VERBOSITY=medium
MAX_RETRIES=5
TIMEOUT_SECONDS=300
LOG_LEVEL=INFO
MAX_ITERATIONS=5
CONFIDENCE_THRESHOLD=0.8
CACHE_TTL_HOURS=24
```

### Testing Environment
```env
# Testing configuration - fast responses and minimal caching
OPENAI_API_KEY=sk-your-test-api-key-here
GPT5_MODEL=gpt-5-nano
DEFAULT_REASONING_EFFORT=minimal
DEFAULT_VERBOSITY=low
MAX_RETRIES=1
TIMEOUT_SECONDS=30
LOG_LEVEL=WARNING
MAX_ITERATIONS=2
CONFIDENCE_THRESHOLD=0.5
CACHE_TTL_HOURS=0
```

### High-Performance Environment
```env
# High-performance configuration - best quality, longer timeouts
OPENAI_API_KEY=sk-your-api-key-here
GPT5_MODEL=gpt-5
DEFAULT_REASONING_EFFORT=high
DEFAULT_VERBOSITY=high
MAX_RETRIES=3
TIMEOUT_SECONDS=600
LOG_LEVEL=INFO
MAX_ITERATIONS=10
CONFIDENCE_THRESHOLD=0.9
CACHE_TTL_HOURS=48
```

## Configuration Validation

The application uses Pydantic for automatic validation of all configuration values. Validation occurs at startup and will raise clear error messages for invalid configurations.

### Validation Rules

1. **OPENAI_API_KEY**: Must start with `sk-`
2. **MAX_RETRIES**: Must be between 0 and 10
3. **TIMEOUT_SECONDS**: Must be between 1 and 600
4. **LOG_LEVEL**: Must be one of the standard Python logging levels
5. **MAX_ITERATIONS**: Must be between 1 and 100
6. **CONFIDENCE_THRESHOLD**: Must be between 0.0 and 1.0
7. **CACHE_TTL_HOURS**: Must be 0 or positive

### Testing Your Configuration

1. **Basic validation**:
   ```bash
   python -c "from src.config.settings import get_settings; settings = get_settings(); print('All settings valid!')"
   ```

2. **Check specific values**:
   ```bash
   python -c "from src.config.settings import get_settings; settings = get_settings(); print(f'Model: {settings.gpt5_model}'); print(f'Log Level: {settings.log_level}')"
   ```

3. **Validate API key format**:
   ```bash
   python -c "from src.config.settings import get_settings; settings = get_settings(); print('API key format valid!' if settings.openai_api_key.startswith('sk-') else 'Invalid API key format')"
   ```

## Common Configuration Issues

### Issue: Invalid API Key Format
**Error**: `ValueError: OpenAI API key must start with 'sk-'`
**Solution**: Ensure your API key starts with `sk-`. Check for extra spaces or incorrect copying.

### Issue: Configuration File Not Found
**Error**: Settings load with default values instead of your custom values
**Solutions**:
1. Ensure `.env` file is in the project root directory
2. Check file permissions (must be readable)
3. Verify environment variable names match exactly (case-insensitive)

### Issue: Invalid Numeric Values
**Error**: `ValidationError` for numeric fields
**Solutions**:
1. Ensure numeric values are within valid ranges
2. Use integers for whole numbers, floats for decimals
3. Don't include units in the values (e.g., use `300`, not `300s`)

### Issue: Invalid Log Level
**Error**: `ValueError: Log level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL`
**Solution**: Use one of the exact values listed (case-insensitive)

### Issue: Timeout Too Short
**Symptoms**: Frequent timeout errors during API calls
**Solutions**:
1. Increase `TIMEOUT_SECONDS` for complex queries
2. Consider using `gpt-5-nano` for faster responses
3. Reduce `DEFAULT_REASONING_EFFORT` for quicker processing

### Issue: High API Costs
**Symptoms**: Unexpectedly high OpenAI API usage
**Solutions**:
1. Use `gpt-5-nano` or `gpt-5-mini` instead of `gpt-5`
2. Set lower `DEFAULT_REASONING_EFFORT`
3. Increase `CACHE_TTL_HOURS` to cache responses longer
4. Set `DEFAULT_VERBOSITY=low` for shorter responses

## Performance Tuning

### For Speed
```env
GPT5_MODEL=gpt-5-nano
DEFAULT_REASONING_EFFORT=minimal
DEFAULT_VERBOSITY=low
TIMEOUT_SECONDS=30
CACHE_TTL_HOURS=48
```

### For Quality
```env
GPT5_MODEL=gpt-5
DEFAULT_REASONING_EFFORT=high
DEFAULT_VERBOSITY=high
TIMEOUT_SECONDS=600
CONFIDENCE_THRESHOLD=0.9
```

### For Cost Optimization
```env
GPT5_MODEL=gpt-5-mini
DEFAULT_REASONING_EFFORT=medium
DEFAULT_VERBOSITY=medium
CACHE_TTL_HOURS=72
MAX_ITERATIONS=3
```

### For Reliability
```env
MAX_RETRIES=5
TIMEOUT_SECONDS=300
LOG_LEVEL=INFO
CONFIDENCE_THRESHOLD=0.7
```

## Security Considerations

1. **API Key Protection**:
   - Never commit `.env` files to version control
   - Use environment variables in production instead of files
   - Rotate API keys regularly
   - Use separate keys for development/testing/production

2. **File Permissions**:
   ```bash
   chmod 600 .env  # Read/write for owner only (Unix/Linux/macOS)
   ```

3. **Environment Isolation**:
   - Use different API keys for different environments
   - Set appropriate `LOG_LEVEL` to avoid logging sensitive data
   - Consider using secret management systems in production

## Environment Variable Priority

Configuration values are loaded in the following order (later values override earlier ones):

1. Default values in the code
2. `.env` file values
3. System environment variables
4. Explicitly set environment variables in the current session

## Troubleshooting Commands

```bash
# Check if .env file exists and is readable
ls -la .env

# View current environment variables (Unix/Linux/macOS)
env | grep -E "(OPENAI|GPT5|DEFAULT|MAX|TIMEOUT|LOG|CONFIDENCE|CACHE)"

# View current environment variables (Windows)
set | findstr /I "OPENAI GPT5 DEFAULT MAX TIMEOUT LOG CONFIDENCE CACHE"

# Test configuration loading
python -c "from src.config.settings import get_settings; import json; s = get_settings(); print(json.dumps(s.dict(), indent=2, default=str))"

# Validate specific setting
python -c "from src.config.settings import get_settings; print(f'Using model: {get_settings().gpt5_model}')"
```

## Getting Help

If you encounter configuration issues:

1. Check this guide for common problems
2. Validate your configuration using the test commands above
3. Review the error messages carefully - they often indicate exactly what's wrong
4. Ensure all required environment variables are set
5. Check that your `.env` file is in the correct location and format