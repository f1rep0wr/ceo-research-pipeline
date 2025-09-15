# Troubleshooting Guide

This guide helps you resolve common issues with the GPT-5 CEO Research application. Follow the step-by-step solutions to quickly fix problems and get back to productive research.

## Table of Contents

- [Setup and Installation Issues](#setup-and-installation-issues)
- [API Connection and Authentication Problems](#api-connection-and-authentication-problems)
- [Dependency and Environment Conflicts](#dependency-and-environment-conflicts)
- [Performance and Timeout Issues](#performance-and-timeout-issues)
- [Error Messages and Meanings](#error-messages-and-meanings)
- [Diagnostic Procedures](#diagnostic-procedures)
- [When to Seek Additional Help](#when-to-seek-additional-help)

## Setup and Installation Issues

### Python Version Error

**Error Message:**
```
RuntimeError: Python 3.11+ is required. Current version: 3.9.x
```

**Solution:**
1. Install Python 3.11 or higher:
   ```bash
   # Windows (using Python.org installer)
   # Download from https://python.org/downloads/

   # macOS (using Homebrew)
   brew install python@3.11

   # Linux (Ubuntu/Debian)
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3.11-dev
   ```

2. Verify installation:
   ```bash
   python --version  # Should show 3.11.x or higher
   ```

3. If multiple Python versions exist, use specific version:
   ```bash
   python3.11 setup_env.py
   ```

### Virtual Environment Creation Failed

**Error Message:**
```
ERROR: Virtual environment creation failed
```

**Solution:**
1. Check if `venv` module is available:
   ```bash
   python -m venv --help
   ```

2. If missing, install it:
   ```bash
   # Linux/macOS
   pip install virtualenv

   # Or use system package manager
   sudo apt install python3.11-venv  # Ubuntu/Debian
   ```

3. Create virtual environment manually:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

### Package Installation Failed

**Error Message:**
```
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**Solution:**
1. Ensure virtual environment is activated:
   ```bash
   # Look for (venv) in command prompt
   # If not present, activate:
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. If still failing, check disk space:
   ```bash
   df -h  # Linux/macOS
   dir    # Windows
   ```

3. Clear pip cache and retry:
   ```bash
   pip cache purge
   pip install -r requirements.txt
   ```

### Directory Structure Missing

**Error Message:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'gpt_5_ceo_research/src'
```

**Solution:**
1. Run the setup script to create directories:
   ```bash
   python setup_env.py
   ```

2. If setup script is missing, create directories manually:
   ```bash
   mkdir -p gpt_5_ceo_research/src/{config,api,models,utils}
   mkdir -p gpt_5_ceo_research/tests/{unit,integration}
   mkdir -p docs scripts
   ```

## API Connection and Authentication Problems

### Invalid API Key

**Error Message:**
```
openai.AuthenticationError: Incorrect API key provided
```

**Solution:**
1. Verify your API key format:
   - Should start with `sk-`
   - Should be 51 characters long
   - Contains only letters, numbers, and hyphens

2. Check your `.env` file:
   ```bash
   cat .env | grep OPENAI_API_KEY
   ```

3. Test API key manually:
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" \
        https://api.openai.com/v1/models
   ```

4. Get a new API key from [OpenAI Platform](https://platform.openai.com/api-keys)

### API Key Not Found

**Error Message:**
```
ValueError: OpenAI API key not found. Set OPENAI_API_KEY environment variable
```

**Solution:**
1. Check if `.env` file exists:
   ```bash
   ls -la .env
   ```

2. If missing, copy from example:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` file with your API key:
   ```bash
   # Open in your preferred editor
   nano .env
   # Add: OPENAI_API_KEY=sk-your-actual-key-here
   ```

4. Reload environment variables:
   ```bash
   # Restart your terminal or:
   source .env  # Linux/macOS
   ```

### Rate Limit Exceeded

**Error Message:**
```
openai.RateLimitError: Rate limit reached for requests
```

**Solution:**
1. Check your OpenAI usage limits in the [dashboard](https://platform.openai.com/usage)

2. Implement exponential backoff (already included in the application):
   ```python
   # Increase retry delays in .env
   MAX_RETRIES=5
   TIMEOUT_SECONDS=180
   ```

3. Reduce request frequency:
   - Use `gpt-5-mini` or `gpt-5-nano` models
   - Implement request queuing
   - Add delays between requests

### Network Connection Issues

**Error Message:**
```
aiohttp.ClientConnectorError: Cannot connect to host api.openai.com
```

**Solution:**
1. Check internet connectivity:
   ```bash
   ping api.openai.com
   ```

2. Check firewall settings:
   - Allow outbound HTTPS (port 443)
   - Allow access to `api.openai.com`

3. Test with proxy if behind corporate firewall:
   ```bash
   export HTTPS_PROXY=http://proxy.company.com:8080
   ```

4. Verify DNS resolution:
   ```bash
   nslookup api.openai.com
   ```

## Dependency and Environment Conflicts

### Module Not Found

**Error Message:**
```
ModuleNotFoundError: No module named 'openai'
```

**Solution:**
1. Verify virtual environment is activated:
   ```bash
   which python  # Should point to venv/bin/python
   ```

2. Install missing dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Check Python path:
   ```bash
   python -c "import sys; print(sys.path)"
   ```

### Version Conflicts

**Error Message:**
```
ERROR: pip's dependency resolver does not currently have a backtracking capability
```

**Solution:**
1. Create fresh virtual environment:
   ```bash
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   ```

2. Upgrade pip to latest version:
   ```bash
   pip install --upgrade pip
   ```

3. Install dependencies one by one:
   ```bash
   pip install openai>=1.40.0
   pip install aiohttp>=3.9.0
   pip install pydantic>=2.5.0
   # etc.
   ```

### SSL Certificate Issues

**Error Message:**
```
ssl.SSLCertVerificationError: certificate verify failed
```

**Solution:**
1. Update certificates:
   ```bash
   # macOS
   /Applications/Python\ 3.11/Install\ Certificates.command

   # Linux
   sudo apt update && sudo apt install ca-certificates
   ```

2. Temporarily disable SSL verification (not recommended for production):
   ```python
   import ssl
   ssl._create_default_https_context = ssl._create_unverified_context
   ```

### Import Path Issues

**Error Message:**
```
ImportError: attempted relative import with no known parent package
```

**Solution:**
1. Run from project root directory:
   ```bash
   cd /path/to/gpt_5
   python -m gpt_5_ceo_research.main
   ```

2. Add project to Python path:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:/path/to/gpt_5"
   ```

3. Use absolute imports in code:
   ```python
   from gpt_5_ceo_research.src.config.settings import get_settings
   ```

## Performance and Timeout Issues

### Request Timeout

**Error Message:**
```
asyncio.TimeoutError: Request timed out after 120 seconds
```

**Solution:**
1. Increase timeout in `.env`:
   ```
   TIMEOUT_SECONDS=300
   ```

2. Use faster model variants:
   ```
   GPT5_MODEL=gpt-5-mini  # or gpt-5-nano
   ```

3. Reduce reasoning effort:
   ```
   DEFAULT_REASONING_EFFORT=low
   ```

4. Break complex requests into smaller parts

### Memory Issues

**Error Message:**
```
MemoryError: Unable to allocate memory
```

**Solution:**
1. Monitor memory usage:
   ```bash
   # Linux/macOS
   top -p $(pgrep python)

   # Windows
   tasklist /fi "imagename eq python.exe"
   ```

2. Reduce batch sizes in configuration:
   ```
   MAX_ITERATIONS=3
   ```

3. Clear response caches:
   ```
   CACHE_TTL_HOURS=1
   ```

4. Process data in smaller chunks

### Slow Response Times

**Symptoms:** Requests taking longer than expected

**Solution:**
1. Check model selection:
   ```
   # Fastest to slowest:
   GPT5_MODEL=gpt-5-nano    # Fastest
   GPT5_MODEL=gpt-5-mini    # Balanced
   GPT5_MODEL=gpt-5         # Most capable but slowest
   ```

2. Optimize reasoning effort:
   ```
   DEFAULT_REASONING_EFFORT=minimal  # For simple tasks
   DEFAULT_REASONING_EFFORT=low      # For basic research
   DEFAULT_REASONING_EFFORT=medium   # For detailed analysis
   DEFAULT_REASONING_EFFORT=high     # For complex reasoning
   ```

3. Enable response caching:
   ```
   CACHE_TTL_HOURS=24
   ```

## Error Messages and Meanings

### Common OpenAI API Errors

| Error Code | Meaning | Solution |
|------------|---------|----------|
| 401 | Unauthorized | Check API key |
| 403 | Forbidden | Verify account permissions |
| 404 | Not Found | Check model name |
| 429 | Rate Limited | Reduce request frequency |
| 500 | Server Error | Retry with backoff |
| 503 | Service Unavailable | Wait and retry |

### Application-Specific Errors

#### Configuration Validation Errors

**Error:** `pydantic.ValidationError`
```
ValidationError: 1 validation error for Settings
openai_api_key
  field required (type=value_error.missing)
```

**Meaning:** Required configuration value is missing

**Solution:** Check `.env` file for missing values

#### Async Runtime Errors

**Error:** `RuntimeError: This event loop is already running`
**Meaning:** Attempting to run async code in already running loop

**Solution:**
```python
# Use this pattern:
import asyncio
if asyncio.get_event_loop().is_running():
    # Create task instead of running new loop
    task = asyncio.create_task(your_async_function())
else:
    asyncio.run(your_async_function())
```

## Diagnostic Procedures

### System Health Check

Run this comprehensive diagnostic:

```bash
# 1. Check Python version
python --version

# 2. Check virtual environment
which python
echo $VIRTUAL_ENV

# 3. Check installed packages
pip list | grep -E "(openai|aiohttp|pydantic)"

# 4. Check configuration
python -c "
from gpt_5_ceo_research.src.config.settings import get_settings
settings = get_settings()
print(f'Model: {settings.gpt5_model}')
print(f'API key set: {bool(settings.openai_api_key)}')
print(f'Timeout: {settings.timeout_seconds}s')
"

# 5. Test API connection
python -c "
import asyncio
from gpt_5_ceo_research.src.api.client import GPT5Client
async def test():
    client = GPT5Client()
    try:
        response = await client.simple_query('Hello')
        print('API connection successful')
    except Exception as e:
        print(f'API connection failed: {e}')
asyncio.run(test())
"
```

### Network Connectivity Test

```bash
# Check DNS resolution
nslookup api.openai.com

# Check HTTPS connectivity
curl -I https://api.openai.com/v1/models

# Check with authentication
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.openai.com/v1/models
```

### Logging and Debugging

Enable detailed logging to troubleshoot issues:

```bash
# Set debug level in .env
LOG_LEVEL=DEBUG

# Or temporarily:
export LOG_LEVEL=DEBUG
python your_script.py
```

Common log patterns to look for:
- `Authentication successful` - API key working
- `Rate limit encountered` - Need to slow down requests
- `Timeout occurred` - Increase timeout settings
- `Model not found` - Check model name spelling

## When to Seek Additional Help

### Before Asking for Help

Complete this checklist:

- [ ] Read through this troubleshooting guide
- [ ] Run the system health check
- [ ] Check the [GitHub Issues](https://github.com/your-repo/issues)
- [ ] Review recent changes to your configuration
- [ ] Test with minimal example code

### What Information to Include

When reporting issues, provide:

1. **System Information:**
   ```bash
   python --version
   pip --version
   uname -a  # Linux/macOS
   systeminfo  # Windows
   ```

2. **Error Details:**
   - Complete error message with stack trace
   - Steps to reproduce the issue
   - Configuration settings (redact API keys)

3. **Environment:**
   - Virtual environment status
   - Installed package versions
   - Network/proxy configuration

### Where to Get Help

1. **GitHub Issues**: Report bugs and feature requests
2. **OpenAI Community**: API-specific questions
3. **Stack Overflow**: General Python/async programming help
4. **Project Documentation**: Check other docs/ files

### Creating Minimal Reproduction

When reporting complex issues, create a minimal example:

```python
# minimal_repro.py
import asyncio
from gpt_5_ceo_research.src.api.client import GPT5Client

async def reproduce_issue():
    """Minimal code that demonstrates the problem"""
    client = GPT5Client()
    # Add minimal code that fails
    response = await client.simple_query("test")
    print(response)

if __name__ == "__main__":
    asyncio.run(reproduce_issue())
```

### Emergency Workarounds

If you need to continue working while troubleshooting:

1. **Use different model:**
   ```
   GPT5_MODEL=gpt-5-nano  # Fallback to simpler model
   ```

2. **Disable features temporarily:**
   ```
   MAX_RETRIES=1
   CACHE_TTL_HOURS=0
   DEFAULT_REASONING_EFFORT=minimal
   ```

3. **Mock API responses for development:**
   ```python
   # For testing without API calls
   class MockGPT5Client:
       async def simple_query(self, prompt):
           return "Mock response for development"
   ```

---

## Quick Reference

### Most Common Issues (90% of problems)

1. **API Key not set** → Check `.env` file
2. **Virtual environment not activated** → Run `source venv/bin/activate`
3. **Dependencies not installed** → Run `pip install -r requirements.txt`
4. **Wrong Python version** → Install Python 3.11+
5. **Rate limit exceeded** → Wait or reduce request frequency

### Emergency Commands

```bash
# Reset everything
rm -rf venv .env
cp .env.example .env
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Quick API test
python -c "import openai; print('OpenAI library works')"

# Configuration validation
python -c "from gpt_5_ceo_research.src.config.settings import get_settings; print('Config OK')"
```

### Support Contacts

- Technical Issues: Create GitHub Issue
- API Problems: Check OpenAI Status Page
- Security Concerns: Follow responsible disclosure process