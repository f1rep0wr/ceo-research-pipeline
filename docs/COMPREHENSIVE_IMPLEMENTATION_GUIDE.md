# Comprehensive Implementation Guide - CEO Research Automation System

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Requirements](#system-requirements)
3. [Architecture Overview](#architecture-overview)
4. [Development Principles](#development-principles)
5. [Project Structure](#project-structure)
6. [GPT-5 Integration](#gpt-5-integration)
7. [Core Components](#core-components)
8. [Data Models](#data-models)
9. [Implementation Details](#implementation-details)
10. [Testing Strategy](#testing-strategy)
11. [Deployment & Operations](#deployment-operations)
12. [Success Criteria](#success-criteria)

---

## Executive Summary

### Purpose
Automate the collection, verification, and extraction of comprehensive CEO information from multiple web sources using GPT-5 and the OpenAI Responses API. This system replaces manual research processes currently tracked in spreadsheets, extracting 29 data points per CEO with intelligent data gathering, source attribution, and classification logic.

### Key Outcomes
- Reduce research time from hours to <2 minutes per CEO
- Achieve >80% data completeness per profile
- Process batches of 100 CEOs with 30+ CEOs/hour throughput
- Maintain research-quality accuracy with full source documentation

---

## System Requirements

### Technical Requirements

#### Python Environment
- **Python Version**: 3.11+ (required for latest async features)
- **Package Manager**: Poetry (preferred) or pip with virtual environment
- **Operating System**: Linux/macOS/Windows with WSL2

#### Required Libraries
```toml
[tool.poetry.dependencies]
python = "^3.11"
openai = "^1.40.0"          # GPT-5 Responses API support
aiohttp = "^3.9.0"           # Async HTTP client
pydantic = "^2.5.0"          # Data validation
pandas = "^2.1.0"            # Data manipulation
playwright = "^1.40.0"       # Browser automation
python-dotenv = "^1.0.0"     # Environment management
tenacity = "^8.2.0"          # Retry logic
structlog = "^24.1.0"        # Structured logging
redis = "^5.0.0"             # Caching layer
pytest = "^7.4.0"            # Testing framework
pytest-asyncio = "^0.21.0"   # Async test support
black = "^23.0.0"            # Code formatting
ruff = "^0.1.0"              # Linting
mypy = "^1.7.0"              # Type checking
```

#### API Requirements
- **OpenAI API Key**: With GPT-5 access enabled
- **API Tier**: Minimum Plus tier recommended for rate limits
- **Budget**: Estimate $0.10-0.50 per CEO profile depending on complexity

#### Infrastructure Requirements
- **Memory**: Minimum 8GB RAM (16GB recommended for batch processing)
- **Storage**: 10GB for caching and data storage
- **Network**: Stable internet connection with <100ms latency to OpenAI servers
- **Redis** (Optional): For distributed caching in production

### Business Requirements

#### Data Coverage
- Extract 29 specific data points per CEO
- Achieve >80% field completeness rate
- Maintain <5% error rate on classifications
- Provide confidence scores for all extracted data

#### Performance Targets - Not required but preferred
- Single CEO: <5 minutes end-to-end
- Batch processing: 10+ CEOs per hour

#### Quality Standards
- Source attribution for every data point
- Conflict resolution with reasoning documentation
- Validation flags for data quality issues
- Audit trail for all extraction decisions

---

## Architecture Overview

### System Architecture Pattern: Orchestrator + Tools

```
┌─────────────────────────────────────────────────────────────┐
│                     CEO Research System                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Research Orchestrator                   │    │
│  │                                                      │    │
│  │  • Coordinates entire pipeline                       │    │
│  │  • Manages state and context                         │    │
│  │  • Handles retries and failures                      │    │
│  │  • Tracks progress and metrics                       │    │
│  └──────────────────┬───────────────────────────────────┘    │
│                     │                                         │
│     ┌───────────────┼───────────────┬──────────────┐        │
│     ▼               ▼               ▼              ▼        │
│ ┌─────────┐ ┌─────────────┐ ┌──────────┐ ┌──────────┐     │
│ │Collector│ │ Classifier  │ │Extractor │ │Validator │     │
│ │  Tools  │ │   Tools     │ │  Tools   │ │  Tools   │     │
│ └─────────┘ └─────────────┘ └──────────┘ └──────────┘     │
│     │               │               │              │        │
│     └───────────────┴───────────────┴──────────────┘        │
│                           │                                  │
│                     ┌─────▼─────┐                           │
│                     │   GPT-5   │                           │
│                     │Responses  │                           │
│                     │    API    │                           │
│                     └───────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

#### Orchestrator (Brain)
- Pipeline coordination and state management
- Tool selection based on task requirements
- Error recovery and retry orchestration
- Progress tracking and reporting
- Cost optimization decisions

#### Tool Categories - ALL Powered by GPT-5 Reasoning

1. **Collection Tools**
   NOTE: Do NOT use "generated" websites at all. Generated websites include: Website urls that were generated by GPT-5, or any other AI tool, Website urls that are not real websites, Website urls that are not accessible, Website urls that are not relevant to the research.

   - `WebSearchTool`: Uses GPT-5 reasoning to intelligently formulate queries, evaluate source relevance, and determine information quality
   - `BrowserScrapeTool`: Uses GPT-5 to understand page structure, extract relevant sections, and handle dynamic content intelligently
   - `IterativeSearchTool`: Uses GPT-5 to assess completeness, identify specific gaps, and generate targeted follow-up queries

2. **Classification Tools**
   - `InsiderOutsiderTool`: Uses GPT-5 reasoning to analyze complex career paths, handle edge cases, and make nuanced decisions
   - `CareerPathAnalyzer`: Uses GPT-5 to understand position hierarchies, career progressions, and temporal relationships
   - `DepartureClassifier`: Uses GPT-5 to interpret departure language, context clues, and make probabilistic assessments

3. **Extraction Tools**
   - `TenureExtractor`: Uses GPT-5 to parse complex date references ("late 2020", "Q3 2019"), handle ambiguity, and infer precision levels
   - `CareerExtractor`: Uses GPT-5 to construct complete career timelines from fragmented information and resolve gaps
   - `PostCEOExtractor`: Uses GPT-5 to understand departure circumstances and interpret subsequent career moves

4. **Validation Tools**
   - `SourceValidator`: Uses GPT-5 to assess source credibility, recency, authority, and relevance intelligently
   - `ConflictResolver`: Uses GPT-5 reasoning to weigh contradictory information and make informed resolution decisions
   - `CompletenessChecker`: Uses GPT-5 to identify subtle gaps, assess data quality (not just presence), and suggest targeted searches

---

## Development Principles

### Core Principles

#### 1. KISS (Keep It Simple, Stupid)
```python
# ❌ Over-engineered
class AbstractFactoryMetaClassSingleton:
    # 100 lines of complexity

# ✅ Simple and effective
class CEOResearcher:
    def research(self, name: str, company: str) -> dict:
        # Direct, clear implementation
```

#### 2. DRY (Don't Repeat Yourself)
```python
# ✅ Reusable tool base class
class BaseTool:
    def __init__(self, gpt5_client):
        self.client = gpt5_client
        self.logger = self._setup_logger()

    def execute(self, *args, **kwargs):
        # Common execution logic
```

#### 3. YAGNI (You Aren't Gonna Need It)
- Don't build features "just in case"
- Implement only what's required now
- Add complexity only when proven necessary and when user requests it upon recommendation

#### 4. Single Responsibility Principle
```python
# Each class has ONE job
class TenureExtractor:  # ONLY extracts tenure dates
class SourceValidator:  # ONLY validates sources
class JSONFormatter:    # ONLY formats JSON output
```

#### 5. Explicit Over Implicit
```python
# ❌ Implicit
def process(data):
    return magic_transform(data)

# ✅ Explicit
def classify_ceo_as_insider_or_outsider(
    career_data: dict,
    confidence_threshold: float = 0.8
) -> InsiderClassification:
    # Clear intent and parameters
```

#### 6. Fail Fast, Fail Clearly
```python
# ✅ Immediate validation with clear errors
def research_ceo(name: str, company: str):
    if not name or not company:
        raise ValueError(f"CEO name and company required. Got: name='{name}', company='{company}'")

    if not self.api_key:
        raise ConfigurationError("OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")
```

#### 7. Composition Over Inheritance
```python
# ✅ Compose tools instead of deep inheritance
class ResearchOrchestrator:
    def __init__(self):
        self.collector = DataCollector()
        self.classifier = CEOClassifier()
        self.extractor = DataExtractor()
        # Compose, don't inherit
```

### Code Quality Standards

#### Type Hints Required
```python
from typing import Optional, List, Dict, Tuple

def extract_tenure(
    text: str,
    precision_required: bool = False
) -> Tuple[Optional[str], str]:
    """Returns (date, precision_level)"""
    pass
```

#### Docstrings for All Public Methods
```python
def classify_ceo(self, profile_data: dict) -> Classification:
    """
    Classify CEO as insider or outsider based on career history.

    Args:
        profile_data: Dictionary containing career information

    Returns:
        Classification object with insider/outsider determination

    Raises:
        InsufficientDataError: If critical data missing
    """
```

#### Error Handling Pattern
```python
async def safe_api_call(self, prompt: str) -> Optional[dict]:
    """Execute API call with comprehensive error handling."""
    try:
        return await self._make_request(prompt)
    except RateLimitError:
        self.logger.warning("Rate limit hit, queuing request")
        return await self._queue_and_retry(prompt)
    except APIError as e:
        self.logger.error(f"API error: {e}", exc_info=True)
        raise
    except Exception as e:
        self.logger.critical(f"Unexpected error: {e}", exc_info=True)
        # Don't swallow unexpected errors
        raise
```

#### Comprehensive Debugging Principles
- Use logging for all critical paths
- Implement structured logging with context
- Use exception chaining for better stack traces
- Implement comprehensive error handling
---

## Project Structure

```
gpt_5_ceo_research/
│
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore patterns
├── pyproject.toml               # Poetry configuration
├── README.md                    # Project overview
├── Makefile                     # Common commands
│
├── src/
│   ├── __init__.py
│   ├── main.py                  # Entry point
│   ├── cli.py                   # Command-line interface
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py          # Configuration management
│   │   └── constants.py         # System constants
│   │
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── research_orchestrator.py  # Main pipeline coordinator
│   │   ├── batch_orchestrator.py     # Batch processing
│   │   └── state_manager.py          # State management
│   │
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── gpt5_client.py       # GPT-5 Responses API wrapper
│   │   ├── retry_client.py      # Retry logic wrapper
│   │   └── mock_client.py       # Testing mock
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base_tool.py         # Abstract tool base
│   │   │
│   │   ├── collection/
│   │   │   ├── __init__.py
│   │   │   ├── web_search_tool.py
│   │   │   ├── browser_scrape_tool.py
│   │   │   └── iterative_search_tool.py
│   │   │
│   │   ├── classification/
│   │   │   ├── __init__.py
│   │   │   ├── insider_outsider_tool.py
│   │   │   ├── career_path_tool.py
│   │   │   └── departure_classifier_tool.py
│   │   │
│   │   ├── extraction/
│   │   │   ├── __init__.py
│   │   │   ├── tenure_extractor_tool.py
│   │   │   ├── career_extractor_tool.py
│   │   │   └── post_ceo_extractor_tool.py
│   │   │
│   │   └── validation/
│   │       ├── __init__.py
│   │       ├── source_validator_tool.py
│   │       ├── conflict_resolver_tool.py
│   │       └── completeness_checker_tool.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ceo_profile.py       # Main data model (29 fields)
│   │   ├── classification.py    # Classification results
│   │   ├── source_data.py       # Source tracking
│   │   └── validation_result.py # Validation outcomes
│   │
│   ├── cache/
│   │   ├── __init__.py
│   │   ├── cache_manager.py     # Cache orchestration
│   │   ├── redis_cache.py       # Redis implementation
│   │   └── memory_cache.py      # In-memory fallback
│   │
│   ├── output/
│   │   ├── __init__.py
│   │   ├── json_formatter.py    # JSON output
│   │   ├── csv_formatter.py     # CSV output
│   │   └── report_generator.py  # Summary reports
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py            # Structured logging
│       ├── metrics.py           # Performance tracking
│       ├── validators.py        # Input validation
│       └── exceptions.py        # Custom exceptions
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration
│   │
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_tools.py
│   │   └── test_utils.py
│   │
│   ├── integration/
│   │   ├── test_orchestrator.py
│   │   ├── test_gpt5_client.py
│   │   └── test_cache.py
│   │
│   └── e2e/
│       ├── test_single_ceo.py
│       ├── test_batch_processing.py
│       └── fixtures/
│           └── sample_ceos.json
│
├── scripts/
│   ├── setup.sh                 # Initial setup script
│   ├── test_api.py              # API connectivity test
│   └── generate_mock_data.py    # Test data generation
│
├── docs/
│   ├── API.md                   # API documentation
│   ├── DEPLOYMENT.md            # Deployment guide
│   ├── TROUBLESHOOTING.md       # Common issues
│   └── EXAMPLES.md              # Usage examples
│
└── docker/
    ├── Dockerfile               # Container definition
    └── docker-compose.yml       # Local development stack
```

---

## GPT-5 Integration

### Responses API Configuration

#### Client Initialization
```python
# src/clients/gpt5_client.py
import os
from typing import Optional, Dict, Any, List
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

logger = structlog.get_logger()

class GPT5ResponsesClient:
    """
    Wrapper for GPT-5 Responses API with stateful conversation management.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-5",
        default_reasoning: str = "medium",
        default_verbosity: str = "medium"
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.default_reasoning = default_reasoning
        self.default_verbosity = default_verbosity
        self.conversation_states: Dict[str, str] = {}  # Track response IDs

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60)
    )
    async def create_response(
        self,
        prompt: str,
        conversation_id: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
        verbosity: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        structured_output_schema: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a response using GPT-5 Responses API.

        Args:
            prompt: Input prompt
            conversation_id: Optional ID to maintain conversation state
            reasoning_effort: Override default reasoning (minimal/low/medium/high)
            verbosity: Override default verbosity (low/medium/high)
            tools: List of tools to enable
            structured_output_schema: JSON schema for structured output

        Returns:
            API response dictionary
        """

        request_params = {
            "model": self.model,
            "input": prompt,
            "reasoning": {"effort": reasoning_effort or self.default_reasoning},
            "text": {"verbosity": verbosity or self.default_verbosity}
        }

        # Add previous response ID for stateful conversation
        if conversation_id and conversation_id in self.conversation_states:
            request_params["previous_response_id"] = self.conversation_states[conversation_id]

        # Add tools if specified
        if tools:
            request_params["tools"] = tools

        # Add structured output if specified
        if structured_output_schema:
            request_params["text"]["format"] = {
                "type": "json_schema",
                "schema": structured_output_schema
            }

        # Add any additional parameters
        request_params.update(kwargs)

        logger.info(
            "Making GPT-5 API request",
            model=self.model,
            reasoning=reasoning_effort or self.default_reasoning,
            has_tools=bool(tools),
            has_schema=bool(structured_output_schema)
        )

        try:
            response = await self.client.responses.create(**request_params)

            # Store response ID for conversation continuity
            if conversation_id:
                self.conversation_states[conversation_id] = response.id

            # Log token usage for cost tracking
            if hasattr(response, 'usage'):
                logger.info(
                    "API request completed",
                    prompt_tokens=response.usage.prompt_tokens,
                    reasoning_tokens=response.usage.reasoning_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    estimated_cost=self._calculate_cost(response.usage)
                )

            return response

        except Exception as e:
            logger.error(f"GPT-5 API error: {e}", exc_info=True)
            raise

    def _calculate_cost(self, usage) -> float:
        """Calculate estimated cost based on token usage."""
        # Pricing per model
        pricing = {
            "gpt-5": {"input": 1.25, "output": 10.0},
            "gpt-5-mini": {"input": 0.25, "output": 2.0},
            "gpt-5-nano": {"input": 0.05, "output": 0.40}
        }

        model_pricing = pricing.get(self.model, pricing["gpt-5"])

        input_cost = (usage.prompt_tokens / 1_000_000) * model_pricing["input"]
        output_cost = ((usage.reasoning_tokens + usage.completion_tokens) / 1_000_000) * model_pricing["output"]

        return round(input_cost + output_cost, 4)
```

#### Tool Definitions
```python
# src/clients/tool_definitions.py

CEO_RESEARCH_TOOLS = [
    {
        "type": "web_search",
        "description": "Search the web for current information"
    },
    {
        "type": "custom",
        "name": "extract_tenure_dates",
        "description": "Extract CEO start/end dates from text. Returns dates in MM/DD/YYYY format with precision indicator (exact, month_year, year_only). Handles various date formats and relative references."
    },
    {
        "type": "custom",
        "name": "classify_insider_outsider",
        "description": "Classify CEO as insider (1) or outsider (0) based on career history. Analyzes promotion path, previous positions within company, and time with organization. Returns classification with supporting evidence."
    },
    {
        "type": "custom",
        "name": "extract_career_progression",
        "description": "Extract complete career timeline including positions, companies, and dates. Maps executive progression, board positions, and subsidiary roles. Returns structured career path data."
    },
    {
        "type": "custom",
        "name": "classify_departure_type",
        "description": "Analyze CEO departure circumstances to determine if forced (1) or voluntary (0). Examines language patterns, timing, successor planning, and contextual clues. Returns classification with confidence score."
    },
    {
        "type": "custom",
        "name": "validate_sources",
        "description": "Score source reliability based on type (official filing, news, database), recency, and authority. Returns reliability score 0-1 and flags potential issues."
    },
    {
        "type": "custom",
        "name": "assess_data_completeness",
        "description": "Evaluate collected data against required fields. Identifies gaps, suggests follow-up queries, and calculates overall completeness percentage. Returns assessment with specific missing fields."
    },
    {
        "type": "custom",
        "name": "resolve_conflicts",
        "description": "Resolve conflicting information across sources using reasoning and source reliability. Returns consolidated data point with explanation of resolution logic."
    }
]
```

### Model Selection Strategy with Reasoning Focus
```python
# src/config/model_strategy.py

class ModelSelector:
    """Select appropriate GPT-5 model AND reasoning effort based on task complexity."""

    TASK_MODEL_MAPPING = {
        # Task Type -> (Model, Reasoning Effort, Reasoning Purpose)
        "simple_lookup": ("gpt-5-nano", "minimal", "Basic field extraction"),
        "data_extraction": ("gpt-5-mini", "medium", "Parse complex formats and references"),
        "classification": ("gpt-5", "high", "Nuanced career path analysis"),
        "complex_reasoning": ("gpt-5", "high", "Deep analytical reasoning"),
        "conflict_resolution": ("gpt-5", "high", "Weigh evidence and resolve contradictions"),
        "validation": ("gpt-5-mini", "medium", "Assess data quality and reliability"),
        "iterative_search": ("gpt-5", "high", "Intelligent completeness assessment"),
        "web_search": ("gpt-5", "medium", "Smart query formulation and source evaluation"),
        "date_parsing": ("gpt-5-mini", "medium", "Handle complex temporal references"),
        "career_analysis": ("gpt-5", "high", "Understand career progressions")
    }

    @classmethod
    def select_for_task(cls, task_type: str) -> Tuple[str, str]:
        """Return (model, reasoning_effort) for task type."""
        return cls.TASK_MODEL_MAPPING.get(
            task_type,
            ("gpt-5-mini", "medium")  # Default
        )
```

---

## Core Components

### CRITICAL: GPT-5 Reasoning Integration

**IMPORTANT**: Every tool MUST leverage GPT-5's reasoning capabilities to achieve the quality targets (>80% completeness, <5% error rate). Simple pattern matching or rule-based approaches will NOT succeed. The reasoning capabilities are what differentiate this system from basic scrapers.

### Enhanced Base Tool Implementation with GPT-5 Reasoning
```python
# src/tools/base_tool.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple
import structlog

class BaseTool(ABC):
    """
    Abstract base class for all tools.
    CRITICAL: Every tool MUST use GPT-5 reasoning for intelligent decision-making.
    Simple pattern matching or rule-based approaches will NOT meet quality targets.
    """

    def __init__(self, gpt5_client: GPT5ResponsesClient):
        self.client = gpt5_client
        self.logger = structlog.get_logger(tool=self.__class__.__name__)
        # Each tool MUST define its optimal reasoning level
        self.default_reasoning_effort = self.get_optimal_reasoning_effort()

    @abstractmethod
    def get_optimal_reasoning_effort(self) -> str:
        """Return optimal reasoning effort for this tool's task complexity."""
        pass

    @abstractmethod
    async def execute_with_reasoning(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool's primary function using GPT-5 reasoning.
        This is where the intelligence happens - NOT simple pattern matching!
        """
        pass

    @abstractmethod
    def validate_input(self, *args, **kwargs) -> bool:
        """Validate input parameters."""
        pass

    async def apply_gpt5_reasoning(self,
                                  prompt: str,
                                  tools: list,
                                  reasoning_effort: Optional[str] = None,
                                  conversation_id: Optional[str] = None,
                                  structured_output: Optional[Dict] = None) -> Any:
        """
        Core method to apply GPT-5's reasoning to any problem.
        This is what makes our tools intelligent vs. simple scripts.
        """
        params = {
            "prompt": prompt,
            "reasoning_effort": reasoning_effort or self.default_reasoning_effort,
            "tools": tools,
            "conversation_id": conversation_id
        }

        if structured_output:
            params["structured_output_schema"] = structured_output

        return await self.client.create_response(**params)

    async def run(self, *args, **kwargs) -> Dict[str, Any]:
        """Run tool with validation, logging, and GPT-5 reasoning."""

        # Validate inputs
        if not self.validate_input(*args, **kwargs):
            raise ValueError(f"Invalid input for {self.__class__.__name__}")

        # Log execution start with reasoning level
        self.logger.info(
            f"Executing {self.__class__.__name__} with GPT-5 reasoning",
            reasoning_effort=self.default_reasoning_effort
        )

        try:
            # Execute tool logic WITH GPT-5 REASONING
            result = await self.execute_with_reasoning(*args, **kwargs)

            # Log success
            self.logger.info(f"{self.__class__.__name__} completed successfully")

            return result

        except Exception as e:
            self.logger.error(f"{self.__class__.__name__} failed: {e}")
            raise
```

### Research Orchestrator
```python
# src/orchestrator/research_orchestrator.py
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
import structlog

from src.clients.gpt5_client import GPT5ResponsesClient
from src.tools.collection import WebSearchTool, IterativeSearchTool
from src.tools.classification import InsiderOutsiderTool
from src.tools.extraction import TenureExtractor, CareerExtractor
from src.tools.validation import CompletenessChecker, ConflictResolver
from src.models.ceo_profile import CEOProfile

logger = structlog.get_logger()

@dataclass
class ResearchConfig:
    """Configuration for research process."""
    max_iterations: int = 5
    confidence_threshold: float = 0.8
    enable_caching: bool = True
    parallel_tools: bool = True

class ResearchOrchestrator:
    """
    Main orchestrator for CEO research pipeline.
    Coordinates all tools and manages the research workflow.
    """

    def __init__(self, config: Optional[ResearchConfig] = None):
        self.config = config or ResearchConfig()
        self.gpt5_client = GPT5ResponsesClient()

        # Initialize tools
        self._init_tools()

        # Metrics tracking
        self.metrics = {
            "total_researched": 0,
            "successful": 0,
            "failed": 0,
            "total_api_calls": 0,
            "total_cost": 0.0
        }

    def _init_tools(self):
        """Initialize all research tools."""
        # Collection tools
        self.web_search = WebSearchTool(self.gpt5_client)
        self.iterative_search = IterativeSearchTool(self.gpt5_client)

        # Classification tools
        self.insider_classifier = InsiderOutsiderTool(self.gpt5_client)

        # Extraction tools
        self.tenure_extractor = TenureExtractor(self.gpt5_client)
        self.career_extractor = CareerExtractor(self.gpt5_client)

        # Validation tools
        self.completeness_checker = CompletenessChecker(self.gpt5_client)
        self.conflict_resolver = ConflictResolver(self.gpt5_client)

    async def research_ceo(
        self,
        ceo_name: str,
        company_name: str,
        additional_context: Optional[str] = None
    ) -> CEOProfile:
        """
        Research a single CEO through the complete pipeline.

        Args:
            ceo_name: Name of the CEO
            company_name: Company name
            additional_context: Optional additional context

        Returns:
            Complete CEOProfile with all extracted data
        """

        conversation_id = f"{ceo_name}_{company_name}".replace(" ", "_")

        logger.info(
            "Starting CEO research",
            ceo=ceo_name,
            company=company_name
        )

        try:
            # Phase 1: Data Collection
            logger.info("Phase 1: Data Collection")
            collected_data = await self._collect_phase(
                ceo_name,
                company_name,
                conversation_id,
                additional_context
            )

            # Phase 2: Classification
            logger.info("Phase 2: Classification")
            classification = await self._classify_phase(
                collected_data,
                conversation_id
            )

            # Phase 3: Extraction
            logger.info("Phase 3: Extraction")
            extracted_data = await self._extract_phase(
                collected_data,
                classification,
                conversation_id
            )

            # Phase 4: Validation
            logger.info("Phase 4: Validation")
            validated_profile = await self._validate_phase(
                extracted_data,
                conversation_id
            )

            # Update metrics
            self.metrics["total_researched"] += 1
            self.metrics["successful"] += 1

            logger.info(
                "CEO research completed",
                ceo=ceo_name,
                completeness=validated_profile.completeness_score
            )

            return validated_profile

        except Exception as e:
            self.metrics["failed"] += 1
            logger.error(
                "CEO research failed",
                ceo=ceo_name,
                error=str(e)
            )
            raise

    async def _collect_phase(
        self,
        ceo_name: str,
        company_name: str,
        conversation_id: str,
        additional_context: Optional[str]
    ) -> Dict[str, Any]:
        """Phase 1: Iterative data collection until confidence threshold met."""

        # Start with web search
        initial_search = await self.web_search.run(
            query=f"{ceo_name} CEO {company_name} biography career history",
            conversation_id=conversation_id
        )

        # Iteratively collect more data if needed
        collected_data = await self.iterative_search.run(
            initial_data=initial_search,
            target_fields=CEOProfile.required_fields(),
            confidence_threshold=self.config.confidence_threshold,
            max_iterations=self.config.max_iterations,
            conversation_id=conversation_id
        )

        return collected_data

    async def _classify_phase(
        self,
        collected_data: Dict,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Phase 2: Classify CEO characteristics."""

        classification_tasks = []

        # Run classification tools in parallel if enabled
        if self.config.parallel_tools:
            classification_tasks = [
                self.insider_classifier.run(
                    data=collected_data,
                    conversation_id=conversation_id
                ),
                # Add other classification tools here
            ]

            results = await asyncio.gather(*classification_tasks)

            # Merge results
            classification = {}
            for result in results:
                classification.update(result)

        else:
            # Run sequentially
            classification = await self.insider_classifier.run(
                data=collected_data,
                conversation_id=conversation_id
            )

        return classification

    async def _extract_phase(
        self,
        collected_data: Dict,
        classification: Dict,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Phase 3: Extract all required data points."""

        extraction_tasks = []

        if self.config.parallel_tools:
            extraction_tasks = [
                self.tenure_extractor.run(
                    data=collected_data,
                    conversation_id=conversation_id
                ),
                self.career_extractor.run(
                    data=collected_data,
                    classification=classification,
                    conversation_id=conversation_id
                )
            ]

            results = await asyncio.gather(*extraction_tasks)

            # Merge all extracted data
            extracted = {}
            for result in results:
                extracted.update(result)

        else:
            # Sequential extraction
            tenure = await self.tenure_extractor.run(
                data=collected_data,
                conversation_id=conversation_id
            )

            career = await self.career_extractor.run(
                data=collected_data,
                classification=classification,
                conversation_id=conversation_id
            )

            extracted = {**tenure, **career}

        # Add classification to extracted data
        extracted.update(classification)

        return extracted

    async def _validate_phase(
        self,
        extracted_data: Dict,
        conversation_id: str
    ) -> CEOProfile:
        """Phase 4: Validate and resolve conflicts."""

        # Check completeness
        completeness = await self.completeness_checker.run(
            data=extracted_data,
            required_fields=CEOProfile.required_fields(),
            conversation_id=conversation_id
        )

        # Resolve any conflicts
        if completeness.get("has_conflicts"):
            resolved = await self.conflict_resolver.run(
                data=extracted_data,
                conflicts=completeness["conflicts"],
                conversation_id=conversation_id
            )
            extracted_data.update(resolved)

        # Create and validate final profile
        profile = CEOProfile(**extracted_data)
        profile.completeness_score = completeness["score"]
        profile.validation_flags = completeness.get("flags", [])

        return profile

    async def batch_research(
        self,
        ceo_list: List[tuple],
        batch_size: int = 5,
        progress_callback: Optional[callable] = None
    ) -> List[CEOProfile]:
        """
        Research multiple CEOs in batches.

        Args:
            ceo_list: List of (ceo_name, company_name) tuples
            batch_size: Number of concurrent researches
            progress_callback: Optional callback for progress updates

        Returns:
            List of CEOProfile objects
        """

        results = []
        total = len(ceo_list)

        for i in range(0, total, batch_size):
            batch = ceo_list[i:i+batch_size]

            # Create tasks for batch
            tasks = [
                self.research_ceo(ceo_name, company)
                for ceo_name, company in batch
            ]

            # Execute batch
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for idx, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to research {batch[idx]}: {result}")
                    # Create empty profile with error flag
                    profile = CEOProfile.create_empty(
                        person_name=batch[idx][0],
                        company_name=batch[idx][1],
                        error=str(result)
                    )
                    results.append(profile)
                else:
                    results.append(result)

            # Progress callback
            if progress_callback:
                progress_callback(
                    completed=min(i + batch_size, total),
                    total=total
                )

            # Rate limiting between batches
            if i + batch_size < total:
                await asyncio.sleep(2)

        return results
```

---

## Data Models

### CEO Profile Model (29 Fields)
```python
# src/models/ceo_profile.py
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator

class CEOProfile(BaseModel):
    """Complete CEO profile with 29 data points."""

    # === Identification ===
    person_name: str = Field(..., description="CEO name in 'Last, First' format")
    person_id: str = Field(..., description="Unique identifier")
    company_name: str = Field(..., description="Company full name")
    company_id: str = Field(..., description="Company identifier")

    # === Classification (Core) ===
    insider_outsider: int = Field(..., ge=0, le=1, description="1=insider, 0=outsider")
    interim_ceo: int = Field(0, ge=0, le=1, description="1=interim, 0=permanent")
    interim_only: int = Field(0, ge=0, le=1, description="1=never became permanent")

    # === Tenure Information ===
    ceo_start_date: str = Field(..., description="MM/DD/YYYY format")
    ceo_start_precision: str = Field(
        "exact",
        pattern="^(exact|month_year|year_only)$"
    )
    ceo_end_date: str = Field("incumbent", description="MM/DD/YYYY or 'incumbent'")
    tenure_years: Optional[float] = Field(None, description="Calculated tenure")

    # === Insider-Specific Fields ===
    year_joined_firm: Optional[int] = Field(None, description="First year as executive")
    last_position_before_ceo: Optional[str] = Field(None, description="Exact title")
    president_before_ceo: Optional[int] = Field(None, ge=0, le=1)
    chairman_before_ceo: Optional[int] = Field(None, ge=0, le=1)
    board_member_before_ceo: Optional[int] = Field(None, ge=0, le=1)
    ceo_subsidiary: Optional[int] = Field(None, ge=0, le=1)
    other_executive: Optional[int] = Field(None, ge=0, le=1)
    board_member_only: Optional[int] = Field(None, ge=0, le=1)

    # === Insider Career Path ===
    former_ceo: Optional[int] = Field(None, ge=0, le=1)
    former_other_executive: Optional[int] = Field(None, ge=0, le=1)
    joined_as_executive: Optional[int] = Field(None, ge=0, le=1)
    from_early_career: Optional[int] = Field(None, ge=0, le=1)
    previous_title: Optional[str] = Field(None)
    previous_firm: Optional[str] = Field(None)

    # === Outsider-Specific Fields ===
    outsider_job_title: Optional[str] = Field(None)
    outsider_firm: Optional[str] = Field(None)
    outsider_location: Optional[str] = Field(None)
    ceo_other_firms: Optional[int] = Field(None, ge=0, le=1)
    executive_other_firms: Optional[int] = Field(None, ge=0, le=1)
    unattached: Optional[int] = Field(None, ge=0, le=1)

    # === Post-CEO Information ===
    forced_out: Optional[int] = Field(None, ge=0, le=1)
    retirement: Optional[int] = Field(None, ge=0, le=1)
    age_at_departure: Optional[int] = Field(None, ge=0, le=150)
    no_immediate_job: Optional[int] = Field(None, ge=0, le=1)
    director_role: Optional[int] = Field(None, ge=0, le=1)
    next_job_title: Optional[str] = Field(None)
    next_company: Optional[str] = Field(None)

    # === Demographics ===
    year_born: Optional[int] = Field(None, ge=1900, le=2010)
    age_at_appointment: Optional[int] = Field(None, ge=20, le=100)
    gender: Optional[str] = Field(None, pattern="^(M|F|Other)$")

    # === Source Documentation ===
    source_urls: List[str] = Field(default_factory=list)
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)
    reasoning_summary: Optional[str] = Field(None)
    validation_flags: List[str] = Field(default_factory=list)
    completeness_score: float = Field(0.0, ge=0.0, le=1.0)

    # === Metadata ===
    api_calls_made: int = Field(0)
    total_cost: float = Field(0.0)
    processing_time_seconds: float = Field(0.0)
    error: Optional[str] = Field(None)

    @validator('person_name')
    def validate_name_format(cls, v):
        """Ensure name is in 'Last, First' format."""
        if ',' not in v:
            # Try to convert "First Last" to "Last, First"
            parts = v.strip().split()
            if len(parts) >= 2:
                return f"{parts[-1]}, {' '.join(parts[:-1])}"
        return v

    @validator('ceo_start_date')
    def validate_date_format(cls, v):
        """Validate date format."""
        if v and v != "unknown":
            try:
                datetime.strptime(v, "%m/%d/%Y")
            except ValueError:
                raise ValueError(f"Date must be in MM/DD/YYYY format: {v}")
        return v

    @classmethod
    def required_fields(cls) -> List[str]:
        """Return list of required fields for completeness checking."""
        return [
            "person_name",
            "company_name",
            "insider_outsider",
            "ceo_start_date",
            "ceo_end_date"
        ]

    @classmethod
    def create_empty(cls, person_name: str, company_name: str, error: str = None):
        """Create an empty profile with error information."""
        return cls(
            person_name=person_name,
            person_id=f"error_{person_name.replace(' ', '_')}",
            company_name=company_name,
            company_id="unknown",
            insider_outsider=0,
            ceo_start_date="01/01/1900",
            error=error,
            validation_flags=["ERROR_PROFILE"]
        )

    def to_csv_row(self) -> dict:
        """Convert to CSV-compatible dictionary."""
        data = self.dict()
        # Flatten lists for CSV
        data['source_urls'] = '; '.join(self.source_urls)
        data['validation_flags'] = '; '.join(self.validation_flags)
        data['extraction_timestamp'] = self.extraction_timestamp.isoformat()
        return data
```

---

## Implementation Details

### Iterative Collection Logic with GPT-5 Reasoning
```python
# src/tools/collection/iterative_search_tool.py
from typing import Dict, List, Any, Optional
import asyncio

class IterativeSearchTool(BaseTool):
    """
    Iteratively collect data until confidence threshold is met.
    CRITICAL: This tool's success depends entirely on GPT-5's reasoning to:
    1. Assess data completeness intelligently (not just field counting)
    2. Generate smart follow-up queries that fill specific gaps
    3. Determine when we have sufficient quality data (not just quantity)
    4. Adapt search strategy based on what's found
    """

    def get_optimal_reasoning_effort(self) -> str:
        """High reasoning needed for intelligent completeness assessment."""
        return "high"

    async def execute_with_reasoning(
        self,
        initial_data: Dict,
        target_fields: List[str],
        confidence_threshold: float = 0.8,
        max_iterations: int = 5,
        conversation_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Iteratively search for missing information.
        """

        collected_data = [initial_data]
        iteration = 0

        while iteration < max_iterations:
            # Assess current data completeness
            assessment = await self._assess_completeness(
                collected_data,
                target_fields,
                conversation_id
            )

            self.logger.info(
                f"Iteration {iteration + 1}: Completeness {assessment['confidence']:.2f}"
            )

            # Check if we've met threshold
            if assessment['confidence'] >= confidence_threshold:
                self.logger.info(f"Confidence threshold met at iteration {iteration + 1}")
                break

            # Generate targeted follow-up queries
            follow_up_queries = assessment.get('missing_info_queries', [])

            if not follow_up_queries:
                self.logger.warning("No follow-up queries generated, ending iteration")
                break

            # Execute follow-up searches
            for query in follow_up_queries[:2]:  # Limit to 2 queries per iteration
                search_result = await self._execute_search(
                    query,
                    conversation_id
                )
                collected_data.append(search_result)

            iteration += 1

        # Compile final data
        return self._compile_data(collected_data, assessment)

    async def _assess_completeness(
        self,
        data: List[Dict],
        target_fields: List[str],
        conversation_id: str
    ) -> Dict:
        """Use GPT-5 to assess data completeness."""

        assessment_prompt = f"""
        Assess the completeness of this data for CEO research.

        Data collected: {data}

        Required fields: {', '.join(target_fields)}

        Provide:
        1. Confidence score (0-1) for overall completeness
        2. List of missing critical information
        3. Specific search queries to find missing data

        Focus on actionable gaps that can be filled with web searches.
        """

        response = await self.client.create_response(
            prompt=assessment_prompt,
            conversation_id=conversation_id,
            reasoning_effort="medium",
            tools=[{
                "type": "custom",
                "name": "assess_data_completeness"
            }],
            structured_output_schema={
                "type": "object",
                "properties": {
                    "confidence": {"type": "number"},
                    "missing_fields": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "missing_info_queries": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        )

        return json.loads(response.choices[0].message.content)
```

### Classification Logic with GPT-5 Reasoning
```python
# src/tools/classification/insider_outsider_tool.py

class InsiderOutsiderTool(BaseTool):
    """
    Classify CEO as insider or outsider based on career history.
    Uses GPT-5 reasoning to handle complex edge cases:
    - Interim CEOs who became permanent
    - Board members who left and returned
    - Subsidiary CEOs promoted to parent company
    - Executives from acquired companies
    """

    def get_optimal_reasoning_effort(self) -> str:
        """High reasoning for nuanced career analysis."""
        return "high"

    CLASSIFICATION_RULES = """
    INSIDER (1) Criteria:
    - Promoted from within the company
    - Worked at company before becoming CEO
    - Rose through the ranks
    - Was on the board before CEO appointment

    OUTSIDER (0) Criteria:
    - First role at company was CEO
    - Hired from external company
    - No prior employment at the company

    Position Hierarchy (for insiders):
    1. Board Member (highest)
    2. President
    3. Chairman
    4. Other Executive

    Apply the highest applicable position.
    """

    async def execute_with_reasoning(
        self,
        data: Dict,
        conversation_id: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Classify CEO as insider or outsider using GPT-5 reasoning."""

        classification_prompt = f"""
        Analyze this CEO's career path and classify as insider or outsider.

        {self.CLASSIFICATION_RULES}

        CEO Data: {data}

        Provide:
        1. Classification (1=insider, 0=outsider)
        2. Confidence score (0-1)
        3. Supporting evidence (specific facts)
        4. Reasoning explanation
        """

        response = await self.client.create_response(
            prompt=classification_prompt,
            conversation_id=conversation_id,
            reasoning_effort="high",  # Important decision
            tools=[{
                "type": "custom",
                "name": "classify_insider_outsider"
            }],
            structured_output_schema={
                "type": "object",
                "properties": {
                    "insider_outsider": {"type": "integer"},
                    "confidence": {"type": "number"},
                    "supporting_evidence": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "reasoning": {"type": "string"}
                },
                "required": ["insider_outsider", "confidence", "reasoning"]
            }
        )

        result = json.loads(response.choices[0].message.content)

        # Add position flags if insider
        if result["insider_outsider"] == 1:
            result.update(await self._extract_position_flags(data, conversation_id))

        return result
```

### Caching Strategy
```python
# src/cache/cache_manager.py
import hashlib
import json
from typing import Optional, Any
from datetime import datetime, timedelta
import redis
import pickle

class CacheManager:
    """
    Manage caching for API responses and search results.
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        ttl_hours: int = 24,
        enable_cache: bool = True
    ):
        self.enable_cache = enable_cache
        self.ttl = timedelta(hours=ttl_hours)

        if redis_url and enable_cache:
            self.redis_client = redis.from_url(redis_url)
            self.use_redis = True
        else:
            self.memory_cache = {}
            self.use_redis = False

    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from data."""
        data_str = json.dumps(data, sort_keys=True)
        hash_val = hashlib.md5(data_str.encode()).hexdigest()
        return f"{prefix}:{hash_val}"

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve from cache."""
        if not self.enable_cache:
            return None

        try:
            if self.use_redis:
                data = self.redis_client.get(key)
                if data:
                    return pickle.loads(data)
            else:
                cached = self.memory_cache.get(key)
                if cached:
                    timestamp, data = cached
                    if datetime.now() - timestamp < self.ttl:
                        return data
                    else:
                        del self.memory_cache[key]
        except Exception as e:
            self.logger.error(f"Cache retrieval error: {e}")

        return None

    async def set(self, key: str, value: Any):
        """Store in cache."""
        if not self.enable_cache:
            return

        try:
            if self.use_redis:
                self.redis_client.setex(
                    key,
                    int(self.ttl.total_seconds()),
                    pickle.dumps(value)
                )
            else:
                self.memory_cache[key] = (datetime.now(), value)
        except Exception as e:
            self.logger.error(f"Cache storage error: {e}")

    async def get_or_compute(
        self,
        key: str,
        compute_func: callable,
        *args,
        **kwargs
    ) -> Any:
        """Get from cache or compute if missing."""

        # Try cache first
        cached = await self.get(key)
        if cached is not None:
            self.logger.info(f"Cache hit for {key}")
            return cached

        # Compute if not cached
        self.logger.info(f"Cache miss for {key}, computing...")
        result = await compute_func(*args, **kwargs)

        # Store in cache
        await self.set(key, result)

        return result
```

---

## Testing Strategy

### Unit Testing
```python
# tests/unit/test_models.py
import pytest
from src.models.ceo_profile import CEOProfile

class TestCEOProfile:

    def test_valid_profile_creation(self):
        """Test creating a valid CEO profile."""
        profile = CEOProfile(
            person_name="Smith, John",
            person_id="js_001",
            company_name="TechCorp",
            company_id="tc_001",
            insider_outsider=1,
            ceo_start_date="01/15/2020"
        )

        assert profile.person_name == "Smith, John"
        assert profile.insider_outsider == 1

    def test_name_format_conversion(self):
        """Test automatic name format conversion."""
        profile = CEOProfile(
            person_name="John Smith",  # Wrong format
            person_id="js_001",
            company_name="TechCorp",
            company_id="tc_001",
            insider_outsider=0,
            ceo_start_date="01/15/2020"
        )

        assert profile.person_name == "Smith, John"

    def test_date_validation(self):
        """Test date format validation."""
        with pytest.raises(ValueError):
            CEOProfile(
                person_name="Smith, John",
                person_id="js_001",
                company_name="TechCorp",
                company_id="tc_001",
                insider_outsider=1,
                ceo_start_date="2020-01-15"  # Wrong format
            )

    def test_required_fields(self):
        """Test required fields list."""
        required = CEOProfile.required_fields()
        assert "person_name" in required
        assert "insider_outsider" in required
```

### Integration Testing
```python
# tests/integration/test_orchestrator.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from src.orchestrator.research_orchestrator import ResearchOrchestrator

@pytest.mark.asyncio
class TestResearchOrchestrator:

    async def test_single_ceo_research(self, mock_gpt5_client):
        """Test researching a single CEO."""
        orchestrator = ResearchOrchestrator()
        orchestrator.gpt5_client = mock_gpt5_client

        # Mock responses
        mock_gpt5_client.create_response.return_value = AsyncMock(
            choices=[Mock(message=Mock(content='{"insider_outsider": 1}'))]
        )

        profile = await orchestrator.research_ceo(
            "Satya Nadella",
            "Microsoft"
        )

        assert profile.person_name == "Nadella, Satya"
        assert profile.company_name == "Microsoft"

    async def test_batch_processing(self, mock_gpt5_client):
        """Test batch CEO processing."""
        orchestrator = ResearchOrchestrator()
        orchestrator.gpt5_client = mock_gpt5_client

        ceo_list = [
            ("Tim Cook", "Apple"),
            ("Sundar Pichai", "Google"),
            ("Andy Jassy", "Amazon")
        ]

        profiles = await orchestrator.batch_research(
            ceo_list,
            batch_size=2
        )

        assert len(profiles) == 3
        assert all(isinstance(p, CEOProfile) for p in profiles)
```

### End-to-End Testing
```python
# tests/e2e/test_single_ceo.py
import pytest
import asyncio
from src.orchestrator.research_orchestrator import ResearchOrchestrator

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_complete_ceo_research():
    """Test complete CEO research pipeline with real API."""

    orchestrator = ResearchOrchestrator()

    # Use a well-known CEO for testing
    profile = await orchestrator.research_ceo(
        "Tim Cook",
        "Apple"
    )

    # Validate core fields
    assert profile.person_name == "Cook, Tim"
    assert profile.company_name == "Apple"
    assert profile.insider_outsider in [0, 1]
    assert profile.ceo_start_date is not None

    # Check data quality
    assert profile.confidence_score > 0.7
    assert profile.completeness_score > 0.8
    assert len(profile.source_urls) > 0

    # Verify no critical validation flags
    critical_flags = [f for f in profile.validation_flags if "CRITICAL" in f]
    assert len(critical_flags) == 0
```

---

## Deployment & Operations

### Docker Configuration
```dockerfile
# docker/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy application
COPY src ./src
COPY scripts ./scripts

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import openai; print('OK')" || exit 1

# Run application
CMD ["python", "src/main.py"]
```

### Environment Configuration
```bash
# .env.example
# === API Configuration ===
OPENAI_API_KEY=sk-...
GPT5_MODEL=gpt-5  # Options: gpt-5, gpt-5-mini, gpt-5-nano
DEFAULT_REASONING_EFFORT=medium  # Options: minimal, low, medium, high
DEFAULT_VERBOSITY=medium  # Options: low, medium, high

# === Performance Settings ===
MAX_ITERATIONS=5
CONFIDENCE_THRESHOLD=0.8
BATCH_SIZE=5
ENABLE_CACHING=true
CACHE_TTL_HOURS=24

# === Redis Configuration (Optional) ===
REDIS_URL=redis://localhost:6379/0

# === Logging ===
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json  # Options: json, text

# === Rate Limiting ===
MAX_REQUESTS_PER_MINUTE=100
MAX_TOKENS_PER_MINUTE=1000000

# === Output Configuration ===
OUTPUT_FORMAT=json  # Options: json, csv, both
OUTPUT_DIRECTORY=./output

# === Input Sources (TO BE FILLED) ===
# INPUT_SOURCE_TYPE=  # Options: csv, api, database
# INPUT_FILE_PATH=
# INPUT_API_ENDPOINT=
# INPUT_DATABASE_URL=

# === Output Destinations (TO BE FILLED) ===
# OUTPUT_DESTINATION_TYPE=  # Options: file, api, database
# OUTPUT_API_ENDPOINT=
# OUTPUT_DATABASE_URL=

# === Monitoring (TO BE FILLED) ===
# MONITORING_ENABLED=
# METRICS_ENDPOINT=
# ALERTING_WEBHOOK=
```

### CLI Implementation
```python
# src/cli.py
import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional
import pandas as pd

from src.orchestrator.research_orchestrator import ResearchOrchestrator
from src.utils.logger import setup_logger

def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""

    parser = argparse.ArgumentParser(
        description="CEO Research Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Research single CEO
  python -m src.cli --ceo "Tim Cook" --company "Apple"

  # Batch process from CSV
  python -m src.cli --batch input.csv --output results.json

  # Use different model
  python -m src.cli --ceo "Satya Nadella" --company "Microsoft" --model gpt-5-mini
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--ceo",
        help="CEO name for single research"
    )
    input_group.add_argument(
        "--batch",
        type=Path,
        help="CSV file for batch processing"
    )

    # Company (required with --ceo)
    parser.add_argument(
        "--company",
        help="Company name (required with --ceo)"
    )

    # Output options
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output.json"),
        help="Output file path (default: output.json)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv", "both"],
        default="json",
        help="Output format (default: json)"
    )

    # Model options
    parser.add_argument(
        "--model",
        choices=["gpt-5", "gpt-5-mini", "gpt-5-nano"],
        default="gpt-5",
        help="GPT-5 model to use (default: gpt-5)"
    )
    parser.add_argument(
        "--reasoning",
        choices=["minimal", "low", "medium", "high"],
        default="medium",
        help="Reasoning effort level (default: medium)"
    )

    # Performance options
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Batch size for concurrent processing (default: 5)"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching"
    )

    # Logging
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    return parser

async def main():
    """Main CLI entry point."""

    parser = create_parser()
    args = parser.parse_args()

    # Validate arguments
    if args.ceo and not args.company:
        parser.error("--company is required when using --ceo")

    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO" if args.verbose else "WARNING"
    logger = setup_logger(level=log_level)

    # Configure environment
    import os
    os.environ["GPT5_MODEL"] = args.model
    os.environ["DEFAULT_REASONING_EFFORT"] = args.reasoning
    os.environ["ENABLE_CACHING"] = str(not args.no_cache)

    # Initialize orchestrator
    orchestrator = ResearchOrchestrator()

    try:
        if args.ceo:
            # Single CEO research
            logger.info(f"Researching {args.ceo}, CEO of {args.company}")

            profile = await orchestrator.research_ceo(
                args.ceo,
                args.company
            )

            # Save output
            save_output([profile], args.output, args.format)

            logger.info(f"Research complete. Results saved to {args.output}")

        else:
            # Batch processing
            logger.info(f"Processing batch from {args.batch}")

            # Load CSV
            df = pd.read_csv(args.batch)

            if "ceo_name" not in df.columns or "company_name" not in df.columns:
                raise ValueError("CSV must have 'ceo_name' and 'company_name' columns")

            ceo_list = [
                (row["ceo_name"], row["company_name"])
                for _, row in df.iterrows()
            ]

            logger.info(f"Processing {len(ceo_list)} CEOs")

            # Process batch with progress
            def progress_callback(completed, total):
                print(f"Progress: {completed}/{total} ({100*completed/total:.1f}%)")

            profiles = await orchestrator.batch_research(
                ceo_list,
                batch_size=args.batch_size,
                progress_callback=progress_callback
            )

            # Save output
            save_output(profiles, args.output, args.format)

            # Print summary
            successful = len([p for p in profiles if not p.error])
            logger.info(
                f"Batch complete. {successful}/{len(profiles)} successful. "
                f"Results saved to {args.output}"
            )

    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.debug)
        sys.exit(1)

def save_output(profiles, output_path, format_type):
    """Save profiles to file."""

    if format_type in ["json", "both"]:
        json_path = output_path.with_suffix(".json")
        with open(json_path, "w") as f:
            json.dump(
                [p.dict() for p in profiles],
                f,
                indent=2,
                default=str
            )

    if format_type in ["csv", "both"]:
        csv_path = output_path.with_suffix(".csv")
        df = pd.DataFrame([p.to_csv_row() for p in profiles])
        df.to_csv(csv_path, index=False)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Success Criteria

### Technical Success Metrics

#### Performance
- ✅ Single CEO research completes in <5 minutes
- ✅ Batch processing achieves 10+ CEOs/hour throughput

#### Accuracy
- ✅ >95% accuracy on insider/outsider classification
- ✅ >90% accuracy on date extraction
- ✅ <5% false positive rate on forced departure classification
- ✅ >85% of extracted dates have exact precision
- ✅ >90% of career paths correctly mapped

#### Data Quality
- ✅ >80% field completeness per profile
- ✅ 100% source attribution for extracted data
- ✅ <10% profiles with critical validation flags
- ✅ >75% profiles achieve confidence score >0.8
- ✅ <5% unresolved conflicts after validation

#### Cost Efficiency
- ✅ Average cost per CEO profile <$0.50
- ✅ Reasoning token usage optimized (minimal for simple tasks)
- ✅ Effective model selection (nano/mini for appropriate tasks)
- ✅ Cache reduces API calls by >40%
- ✅ Batch processing reduces cost by >30% vs individual

### Business Success Metrics

#### User Satisfaction
- ✅ Researchers save >90% time vs manual process
- ✅ Output format matches existing spreadsheet structure
- ✅ Data quality meets or exceeds manual research
- ✅ System provides clear confidence indicators
- ✅ Easy to verify and audit results

#### Operational Excellence
- ✅ System uptime >99.5%
- ✅ Error recovery without data loss
- ✅ Clear error messages and troubleshooting guides
- ✅ Monitoring alerts for anomalies
- ✅ Regular performance reports generated

#### Scalability
- ✅ Handle 1000+ CEO profiles per day
- ✅ Support multiple concurrent users
- ✅ Scale horizontally with demand
- ✅ Maintain performance under load
- ✅ Cost scales linearly with usage

### Quality Assurance Checklist

#### Code Quality
- [ ] All functions have type hints
- [ ] All public methods have docstrings
- [ ] Code passes linting (ruff/black)
- [ ] No security vulnerabilities (API keys, injection)
- [ ] Error handling for all external calls

#### Testing Coverage
- [ ] >90% unit test coverage
- [ ] Integration tests for all tools
- [ ] E2E tests for complete pipeline
- [ ] Performance tests for batch processing
- [ ] Mock tests for API interactions

#### Documentation
- [ ] README with quick start guide
- [ ] API documentation for all modules
- [ ] Deployment guide with prerequisites
- [ ] Troubleshooting guide for common issues
- [ ] Example usage for all CLI commands

#### Monitoring & Observability
- [ ] Structured logging implemented
- [ ] Metrics tracked for all operations
- [ ] Cost tracking per profile
- [ ] Performance dashboards configured
- [ ] Alert rules for failures

---

## Monitoring & Observability

### Logging Strategy
```python
# src/utils/logger.py
import structlog
import logging
from typing import Optional

def setup_logger(level: str = "INFO") -> structlog.BoundLogger:
    """Configure structured logging."""

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, level.upper())
    )

    return structlog.get_logger()
```

### Metrics Collection
```python
# src/utils/metrics.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

@dataclass
class ResearchMetrics:
    """Metrics for CEO research operations."""

    # Performance metrics
    total_researched: int = 0
    successful: int = 0
    failed: int = 0
    average_time_seconds: float = 0.0

    # API metrics
    total_api_calls: int = 0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0

    # Data quality metrics
    average_completeness: float = 0.0
    average_confidence: float = 0.0
    validation_issues: int = 0

    # Timestamp
    collected_at: datetime = datetime.utcnow()

    def to_dict(self) -> Dict:
        """Convert to dictionary for reporting."""
        return {
            **self.__dict__,
            "success_rate": self.successful / max(self.total_researched, 1),
            "cache_hit_rate": self.cache_hits / max(self.cache_hits + self.cache_misses, 1),
            "cost_per_ceo": self.total_cost / max(self.successful, 1)
        }
```

---

## Security Considerations

### API Key Management
```python
# Never commit API keys
# Use environment variables or secret management service

import os
from cryptography.fernet import Fernet

class SecureConfig:
    """Secure configuration management."""

    @staticmethod
    def get_api_key() -> str:
        """Get API key from secure source."""

        # Option 1: Environment variable
        key = os.getenv("OPENAI_API_KEY")

        # Option 2: Encrypted file (for production)
        # key = SecureConfig.decrypt_from_file(".secrets/api_key.enc")

        # Option 3: AWS Secrets Manager / Azure Key Vault
        # key = SecureConfig.get_from_vault("openai-api-key")

        if not key:
            raise ValueError("API key not configured")

        return key
```

### Input Validation
```python
# src/utils/validators.py

def validate_ceo_input(name: str, company: str) -> bool:
    """Validate CEO research input."""

    # Check for injection attempts
    dangerous_patterns = ["<script>", "DROP TABLE", "'; --", "${"]

    for pattern in dangerous_patterns:
        if pattern in name or pattern in company:
            raise ValueError(f"Invalid input detected: {pattern}")

    # Validate length
    if len(name) > 100 or len(company) > 200:
        raise ValueError("Input too long")

    # Validate characters
    import re
    if not re.match(r"^[\w\s\-'.&,]+$", name):
        raise ValueError("Invalid characters in name")

    return True
```

---

## Notes for Implementation

### Phase 1: Foundation (Week 1)
1. Set up project structure and environment
2. Implement data models and basic configuration
3. Create GPT-5 client wrapper with retry logic
4. Build base tool class and first tool

### Phase 2: Core Tools (Week 2)
1. Implement all collection tools
2. Implement classification tools
3. Implement extraction tools
4. Implement validation tools

### Phase 3: Orchestration (Week 3)
1. Build research orchestrator
2. Implement batch processing
3. Add caching layer
4. Create CLI interface

### Phase 4: Testing & Refinement (Week 4)
1. Write comprehensive tests
2. Performance optimization
3. Error handling improvements
4. Documentation completion

### Phase 5: Deployment (Week 5)
1. Docker configuration
2. Monitoring setup
3. Production deployment
4. User training

---

## Appendix: Unknown/Configurable Fields

The following items need to be specified by the user:

### Input Sources
```python
# TO BE CONFIGURED
INPUT_SOURCES = {
    "csv": {
        "enabled": False,
        "file_path": None,
        "column_mapping": {}
    },
    "api": {
        "enabled": False,
        "endpoint": None,
        "authentication": None
    },
    "database": {
        "enabled": False,
        "connection_string": None,
        "query": None
    }
}
```

### Output Destinations
```python
# TO BE CONFIGURED
OUTPUT_DESTINATIONS = {
    "file": {
        "enabled": True,
        "formats": ["json", "csv"],
        "directory": "./output"
    },
    "api": {
        "enabled": False,
        "endpoint": None,
        "method": "POST"
    },
    "database": {
        "enabled": False,
        "connection_string": None,
        "table": None
    },
    "webhook": {
        "enabled": False,
        "url": None
    }
}
```

### Monitoring & Alerting
```python
# TO BE CONFIGURED
MONITORING_CONFIG = {
    "metrics_endpoint": None,  # e.g., Prometheus, Datadog
    "alerting_webhook": None,  # e.g., Slack, PagerDuty
    "error_threshold": 0.1,    # Alert if error rate > 10%
    "cost_threshold": 100.0    # Alert if daily cost > $100
}
```

### Business Rules
```python
# TO BE CONFIGURED - Specific classification rules
BUSINESS_RULES = {
    "min_confidence_threshold": 0.8,
    "require_exact_dates": False,
    "exclude_interim_ceos": False,
    "require_source_validation": True
}
```

---

This comprehensive implementation guide provides everything needed to build the CEO Research Automation System. Fields marked as "TO BE CONFIGURED" should be filled in based on specific requirements.