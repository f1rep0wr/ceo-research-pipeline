# GPT-5 Implementation Guide for CEO Research Automation

## Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key with GPT-5 access
- Required libraries: `openai`, `aiohttp`, `pydantic`, `pandas`, `playwright`

### Installation
```bash
pip install openai aiohttp pydantic pandas playwright
playwright install  # For browser automation
```

### Environment Setup
```bash
# .env file
OPENAI_API_KEY=your-api-key-here
GPT5_MODEL=gpt-5  # or gpt-5-mini, gpt-5-nano
REASONING_EFFORT=medium
VERBOSITY=medium
```

## Core Implementation

### 1. API Client Setup
```python
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class GPT5Client:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("GPT5_MODEL", "gpt-5")
        self.default_reasoning = os.getenv("REASONING_EFFORT", "medium")
        self.default_verbosity = os.getenv("VERBOSITY", "medium")

    def create_response(self, prompt, reasoning_effort=None, **kwargs):
        return self.client.responses.create(
            model=self.model,
            input=prompt,
            reasoning={"effort": reasoning_effort or self.default_reasoning},
            text={"verbosity": self.default_verbosity},
            **kwargs
        )
```

### 2. Iterative Collection with GPT-5
```python
class CEODataCollector:
    def __init__(self, gpt5_client):
        self.client = gpt5_client
        self.confidence_threshold = 0.8
        self.max_iterations = 5

    async def collect_ceo_data(self, ceo_name, company):
        """Iteratively collect CEO data until confidence threshold met"""
        collected_data = []
        iteration = 0
        previous_response_id = None

        while iteration < self.max_iterations:
            # Build query based on what we're missing
            if iteration == 0:
                query = f"Search for comprehensive information about {ceo_name}, CEO of {company}"
            else:
                query = self._generate_followup_query(collected_data)

            # Make API call with web search
            response = self.client.create_response(
                prompt=query,
                reasoning_effort="high" if iteration > 0 else "medium",
                tools=[{"type": "web_search"}],
                previous_response_id=previous_response_id
            )

            previous_response_id = response.id
            collected_data.append(response.choices[0].message.content)

            # Assess completeness
            assessment = self._assess_completeness(collected_data)

            if assessment['confidence'] >= self.confidence_threshold:
                break

            iteration += 1

        return collected_data, assessment

    def _assess_completeness(self, data):
        """Use GPT-5 to assess data completeness"""
        assessment_prompt = f"""
        Assess the completeness of this CEO data:
        {' '.join(data)}

        Required fields: name, company, insider/outsider status, start date,
        end date or incumbent, previous positions, career path

        Return confidence score 0-1 and list missing fields.
        """

        response = self.client.create_response(
            prompt=assessment_prompt,
            reasoning_effort="medium",
            tools=[{
                "type": "custom",
                "name": "assess_data_completeness",
                "description": "Evaluate data completeness"
            }]
        )

        # Parse assessment
        return self._parse_assessment(response)
```

### 3. CEO Classification with Structured Output
```python
class CEOClassifier:
    def __init__(self, gpt5_client):
        self.client = gpt5_client
        self.classification_schema = {
            "type": "object",
            "properties": {
                "insider_outsider": {
                    "type": "integer",
                    "description": "1 for insider, 0 for outsider"
                },
                "confidence": {"type": "number"},
                "reasoning": {"type": "string"},
                "supporting_evidence": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["insider_outsider", "confidence", "reasoning"]
        }

    def classify_ceo(self, ceo_data):
        """Classify CEO as insider or outsider"""
        classification_prompt = f"""
        Analyze this CEO's career path and classify as:
        - Insider (1): Promoted from within the company
        - Outsider (0): Hired from external company

        Data: {ceo_data}

        Apply these rules:
        - If worked at company before becoming CEO = Insider
        - If first role at company was CEO = Outsider
        - Consider board membership at the company
        """

        response = self.client.create_response(
            prompt=classification_prompt,
            reasoning_effort="high",
            text={
                "format": {
                    "type": "json_schema",
                    "schema": self.classification_schema
                }
            },
            tools=[{
                "type": "custom",
                "name": "classify_insider_outsider",
                "description": "Classify CEO promotion path"
            }]
        )

        return json.loads(response.choices[0].message.content)
```

### 4. Data Extraction Pipeline
```python
class CEODataExtractor:
    def __init__(self, gpt5_client):
        self.client = gpt5_client
        self.ceo_profile_schema = self._build_profile_schema()

    def _build_profile_schema(self):
        """Build comprehensive CEO profile schema"""
        return {
            "type": "object",
            "properties": {
                "person_name": {"type": "string"},
                "company_name": {"type": "string"},
                "insider_outsider": {"type": "integer"},
                "interim_ceo": {"type": "integer"},
                "ceo_start_date": {"type": "string"},
                "ceo_start_precision": {
                    "type": "string",
                    "enum": ["exact", "month_year", "year_only"]
                },
                "ceo_end_date": {"type": "string"},
                "year_joined_firm": {"type": ["integer", "null"]},
                "last_position_before_ceo": {"type": ["string", "null"]},
                "president_before_ceo": {"type": ["integer", "null"]},
                "chairman_before_ceo": {"type": ["integer", "null"]},
                "board_member_before_ceo": {"type": ["integer", "null"]},
                "forced_out": {"type": ["integer", "null"]},
                "retirement": {"type": ["integer", "null"]},
                "source_urls": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "confidence_score": {"type": "number"}
            },
            "required": ["person_name", "company_name", "insider_outsider"]
        }

    async def extract_full_profile(self, collected_data):
        """Extract complete CEO profile from collected data"""
        extraction_prompt = f"""
        Extract all CEO information from this data into a structured profile:
        {collected_data}

        Guidelines:
        - Dates in MM/DD/YYYY format
        - Use "incumbent" if still CEO
        - Set null for missing information
        - Include all source URLs
        """

        response = self.client.create_response(
            prompt=extraction_prompt,
            reasoning_effort="high",
            text={
                "verbosity": "low",  # We want structured data only
                "format": {
                    "type": "json_schema",
                    "schema": self.ceo_profile_schema
                }
            },
            tools=[
                {
                    "type": "custom",
                    "name": "extract_tenure_dates",
                    "description": "Extract CEO tenure dates"
                },
                {
                    "type": "custom",
                    "name": "extract_career_progression",
                    "description": "Extract career path"
                }
            ]
        )

        return json.loads(response.choices[0].message.content)
```

### 5. Complete Research Orchestrator
```python
import asyncio
from typing import List, Dict

class CEOResearchOrchestrator:
    def __init__(self):
        self.gpt5_client = GPT5Client()
        self.collector = CEODataCollector(self.gpt5_client)
        self.classifier = CEOClassifier(self.gpt5_client)
        self.extractor = CEODataExtractor(self.gpt5_client)

    async def research_ceo(self, ceo_name: str, company: str) -> Dict:
        """Complete CEO research pipeline"""

        # Step 1: Collect data iteratively
        print(f"Collecting data for {ceo_name}, CEO of {company}...")
        collected_data, assessment = await self.collector.collect_ceo_data(
            ceo_name, company
        )

        # Step 2: Classify CEO
        print("Classifying CEO...")
        classification = self.classifier.classify_ceo(collected_data)

        # Step 3: Extract full profile
        print("Extracting complete profile...")
        profile = await self.extractor.extract_full_profile(collected_data)

        # Step 4: Merge classification into profile
        profile.update(classification)

        # Step 5: Validate and score
        profile['data_completeness'] = assessment['confidence']

        return profile

    async def batch_research(self, ceo_list: List[tuple]) -> List[Dict]:
        """Research multiple CEOs in parallel"""
        tasks = []
        for ceo_name, company in ceo_list:
            task = self.research_ceo(ceo_name, company)
            tasks.append(task)

        # Process in batches to respect rate limits
        batch_size = 5
        results = []
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i+batch_size]
            batch_results = await asyncio.gather(*batch)
            results.extend(batch_results)

            # Add delay between batches
            if i + batch_size < len(tasks):
                await asyncio.sleep(2)

        return results
```

### 6. Error Handling and Retries
```python
import time
from openai import RateLimitError, APIError

class RobustGPT5Client(GPT5Client):
    def create_response(self, prompt, max_retries=3, **kwargs):
        """Create response with automatic retry logic"""
        last_error = None

        for attempt in range(max_retries):
            try:
                return super().create_response(prompt, **kwargs)

            except RateLimitError as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Rate limit hit, waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print("Max retries reached for rate limit")

            except APIError as e:
                last_error = e
                print(f"API Error: {e}")
                if "context_length_exceeded" in str(e):
                    # Try with reduced context
                    if "previous_response_id" in kwargs:
                        del kwargs["previous_response_id"]
                        print("Retrying without conversation history...")
                    else:
                        raise
                else:
                    raise

        raise last_error
```

### 7. Cost Optimization
```python
class CostOptimizedOrchestrator(CEOResearchOrchestrator):
    def select_model_for_task(self, task_type):
        """Select appropriate model based on task complexity"""
        model_selection = {
            "simple_lookup": "gpt-5-nano",
            "data_extraction": "gpt-5-mini",
            "complex_reasoning": "gpt-5",
            "classification": "gpt-5-mini",
            "validation": "gpt-5-nano"
        }
        return model_selection.get(task_type, "gpt-5-mini")

    def optimize_reasoning_effort(self, data_complexity):
        """Dynamically adjust reasoning effort"""
        if data_complexity < 0.3:
            return "minimal"
        elif data_complexity < 0.6:
            return "low"
        elif data_complexity < 0.8:
            return "medium"
        else:
            return "high"
```

## Usage Examples

### Single CEO Research
```python
async def main():
    orchestrator = CEOResearchOrchestrator()

    # Research single CEO
    result = await orchestrator.research_ceo(
        "Satya Nadella",
        "Microsoft"
    )

    print(json.dumps(result, indent=2))

# Run
asyncio.run(main())
```

### Batch Processing from CSV
```python
import pandas as pd

async def process_csv(file_path):
    # Read CSV
    df = pd.read_csv(file_path)

    # Prepare CEO list
    ceo_list = [(row['CEO_Name'], row['Company'])
                for _, row in df.iterrows()]

    # Process batch
    orchestrator = CEOResearchOrchestrator()
    results = await orchestrator.batch_research(ceo_list)

    # Save results
    output_df = pd.DataFrame(results)
    output_df.to_csv('ceo_research_results.csv', index=False)
    output_df.to_json('ceo_research_results.json', orient='records', indent=2)

# Run
asyncio.run(process_csv('ceo_input.csv'))
```

### CLI Implementation
```python
import argparse

def create_cli():
    parser = argparse.ArgumentParser(description='CEO Research Automation')
    parser.add_argument('--ceo', help='CEO name')
    parser.add_argument('--company', help='Company name')
    parser.add_argument('--batch', help='CSV file for batch processing')
    parser.add_argument('--model', default='gpt-5',
                       choices=['gpt-5', 'gpt-5-mini', 'gpt-5-nano'])
    parser.add_argument('--reasoning', default='medium',
                       choices=['minimal', 'low', 'medium', 'high'])

    return parser

async def cli_main():
    parser = create_cli()
    args = parser.parse_args()

    # Set model and reasoning
    os.environ['GPT5_MODEL'] = args.model
    os.environ['REASONING_EFFORT'] = args.reasoning

    orchestrator = CEOResearchOrchestrator()

    if args.batch:
        await process_csv(args.batch)
    elif args.ceo and args.company:
        result = await orchestrator.research_ceo(args.ceo, args.company)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(cli_main())
```

## Performance Tips

1. **Use Stateful Conversations**: Always pass `previous_response_id` for follow-ups
2. **Batch Parallel Requests**: Process multiple CEOs simultaneously with rate limit awareness
3. **Choose Right Model Size**: Use nano for simple tasks, full GPT-5 for complex reasoning
4. **Optimize Reasoning Effort**: Start with lower effort, increase only when needed
5. **Cache Results**: Implement 24-hour cache for repeated searches
6. **Monitor Token Usage**: Track costs and adjust verbosity/reasoning as needed

## Troubleshooting

### Common Issues

1. **Rate Limits**: Implement exponential backoff
2. **Context Length**: Reduce conversation history or use summarization
3. **Tool Errors**: Verify tool configuration and parameters
4. **Incomplete Data**: Increase iterations or reasoning effort
5. **Cost Overruns**: Use smaller models and lower reasoning effort where possible