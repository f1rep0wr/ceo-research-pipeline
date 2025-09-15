# GPT-5 CEO Research

A Python application for conducting AI-powered CEO research using OpenAI's GPT-5 API. This project provides a structured framework for making asynchronous API calls to GPT-5 with proper configuration management, error handling, and logging.

## Overview

This application is designed to:
- Interface with GPT-5 API for CEO and executive research
- Provide structured data validation and response handling
- Support different GPT-5 model variants (gpt-5, gpt-5-mini, gpt-5-nano)
- Implement robust async patterns with retry mechanisms
- Offer configurable reasoning effort levels and verbosity settings

## Prerequisites

Before setting up this project, ensure you have:

- **Python 3.11+** - Required for modern async features and type annotations
- **Git** - For version control and cloning repositories
- **OpenAI API Key** - Get one from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Internet Connection** - For API calls and package installation

## Quick Setup

Get started in under 10 minutes:

### 1. Clone and Enter Project Directory
```bash
git clone <your-repository-url>
cd gpt_5
```

### 2. Run Automated Setup
```bash
python scripts/setup_project.py
```

This script will:
- Verify Python version (3.11+)
- Create all required directories and files
- Install dependencies (openai, aiohttp, pydantic, etc.)
- Set up git repository
- Create configuration templates

### 3. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your API key
# Windows: notepad .env
# Linux/Mac: nano .env
```

### 4. Add Your API Key
Edit `.env` and update:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 5. Test Installation
```bash
cd gpt_5_ceo_research
python -c "from src.clients.gpt5_client import GPT5ResponsesClient; print('✓ Setup complete!')"
```

## Manual Setup (Alternative)

If you prefer manual setup:

### 1. Create Virtual Environment
```bash
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Configuration
```bash
cp .env.example .env
# Edit .env with your API key and preferences
```

## Configuration Guide

### Environment Variables

The `.env` file contains all configuration options:

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required | sk-... |
| `GPT5_MODEL` | GPT-5 model variant | gpt-5 | gpt-5, gpt-5-mini, gpt-5-nano |
| `DEFAULT_REASONING_EFFORT` | Reasoning depth | medium | minimal, low, medium, high |
| `DEFAULT_VERBOSITY` | Response detail level | medium | low, medium, high |
| `MAX_RETRIES` | API retry attempts | 3 | 1-10 |
| `TIMEOUT_SECONDS` | Request timeout | 120 | 30-600 |
| `LOG_LEVEL` | Logging verbosity | INFO | DEBUG, INFO, WARNING, ERROR |

### Model Selection Guide

- **gpt-5**: Most capable, slowest, highest cost - use for complex research
- **gpt-5-mini**: Balanced performance and cost - recommended for most tasks
- **gpt-5-nano**: Fastest and cheapest - use for simple queries

### Reasoning Effort Levels

- **minimal**: Quick responses, basic reasoning
- **low**: Simple analysis with some context
- **medium**: Balanced depth and speed (recommended)
- **high**: Deep analysis, slower responses

## Basic Usage Examples

### Simple Query
```python
import asyncio
from src.clients.gpt5_client import GPT5ResponsesClient

async def main():
    client = GPT5ResponsesClient()

    response = await client.get_completion(
        prompt="Research the current CEO of Microsoft",
        reasoning_effort="medium"
    )

    print(response)

asyncio.run(main())
```

### Advanced Configuration
```python
import asyncio
from src.clients.gpt5_client import GPT5ResponsesClient

async def main():
    client = GPT5ResponsesClient()

    # Detailed CEO research with high reasoning
    response = await client.get_completion(
        prompt="Provide detailed analysis of Tesla's CEO including recent strategic decisions",
        model="gpt-5",
        reasoning_effort="high",
        verbosity="high",
        max_tokens=2000
    )

    print(f"Response: {response}")

asyncio.run(main())
```

### Batch Processing
```python
import asyncio
from src.clients.gpt5_client import GPT5ResponsesClient

async def research_multiple_ceos():
    client = GPT5ResponsesClient()

    companies = ["Apple", "Google", "Amazon", "Microsoft"]

    tasks = [
        client.get_completion(f"Research the current CEO of {company}")
        for company in companies
    ]

    responses = await asyncio.gather(*tasks)

    for company, response in zip(companies, responses):
        print(f"\n{company} CEO Research:")
        print(response)

asyncio.run(research_multiple_ceos())
```

## Project Structure

```
gpt_5/
├── README.md                    # This file
├── .env.example                 # Environment template
├── .env                        # Your configuration (create from template)
├── requirements.txt            # Python dependencies
├── scripts/
│   └── setup_project.py       # Automated setup script
└── gpt_5_ceo_research/        # Main application
    ├── src/
    │   ├── clients/           # API client implementations
    │   │   └── gpt5_client.py # GPT-5 API client
    │   ├── config/            # Configuration management
    │   │   ├── settings.py    # Settings loader
    │   │   └── constants.py   # Application constants
    │   └── utils/             # Utility functions
    │       └── logger.py      # Structured logging
    ├── tests/                 # Test suite
    │   ├── conftest.py       # Test configuration
    │   └── test_*.py         # Test files
    └── docs/                  # Documentation
```

## Troubleshooting

### Common Issues and Solutions

#### ❌ "OpenAI API key not found"
```
Error: OpenAI API key not found. Please check your .env file.
```

**Solution:**
1. Verify `.env` file exists in project root
2. Check `OPENAI_API_KEY=sk-your-key-here` is set correctly
3. Ensure no spaces around the `=` sign
4. Restart your terminal/IDE after editing `.env`

#### ❌ "Module not found: openai"
```
ModuleNotFoundError: No module named 'openai'
```

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### ❌ "API rate limit exceeded"
```
RateLimitError: Rate limit reached for requests
```

**Solution:**
- Reduce concurrent requests in batch operations
- Increase `TIMEOUT_SECONDS` in `.env`
- Add delays between API calls:
```python
import asyncio
await asyncio.sleep(1)  # Add 1 second delay
```

#### ❌ "Python version too old"
```
ERROR: Python 3.11+ is required. Current version is 3.9
```

**Solution:**
1. Install Python 3.11+ from [python.org](https://python.org)
2. Update your PATH to use the new Python version
3. Recreate virtual environment with new Python

#### ❌ "Import errors after setup"
```
ImportError: attempted relative import with no known parent package
```

**Solution:**
Ensure you're running from the correct directory:
```bash
cd gpt_5_ceo_research
python -m src.clients.gpt5_client  # Use module syntax
```

#### ❌ "Timeout errors"
```
TimeoutError: Request timed out after 120 seconds
```

**Solution:**
1. Increase timeout in `.env`:
```env
TIMEOUT_SECONDS=300
```
2. Or use shorter prompts and lower reasoning effort:
```python
reasoning_effort="low"  # Instead of "high"
```

### Getting Help

1. **Check Logs**: Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging
2. **Verify Configuration**: Ensure all required environment variables are set
3. **Test API Key**: Use OpenAI's API playground to verify your key works
4. **Check Python Version**: Run `python --version` to confirm 3.11+

### Performance Tips

- Use `gpt-5-mini` for faster responses during development
- Set `reasoning_effort="low"` for quicker testing
- Implement caching for repeated queries
- Use async patterns for batch processing

## Dependencies

This project uses the following key packages:

- **openai>=1.40.0** - Official OpenAI Python client
- **aiohttp>=3.9.0** - Async HTTP client for web requests
- **pydantic>=2.5.0** - Data validation and serialization
- **python-dotenv>=1.0.0** - Environment variable management
- **structlog>=24.1.0** - Structured logging
- **tenacity>=8.2.0** - Retry mechanisms with exponential backoff

Development dependencies:
- **pytest>=7.4.0** - Testing framework
- **pytest-asyncio>=0.21.0** - Async testing support

## API Key Setup

### Getting Your OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in to your account (create one if needed)
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Add it to your `.env` file

### Security Best Practices

- **Never commit** `.env` files to git (already in `.gitignore`)
- **Don't share** API keys in code, chat, or documentation
- **Rotate keys** regularly for security
- **Use environment variables** in production, not hardcoded keys
- **Monitor usage** on OpenAI platform to detect unexpected charges

---

**Quick Start Summary:**
1. Run `python scripts/setup_project.py`
2. Copy `.env.example` to `.env`
3. Add your OpenAI API key
4. Start coding with `from src.clients.gpt5_client import GPT5ResponsesClient`

For issues or questions, check the troubleshooting section above or review the configuration guide.