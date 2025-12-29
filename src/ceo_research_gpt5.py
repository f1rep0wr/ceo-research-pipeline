"""
CEO Research using GPT-5 Responses API with Web Search

This module provides the main CEO research functionality using GPT-5 Responses API
with web search capabilities. Follows KISS principles - simple, direct implementation.
"""

import json
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from src.clients.gpt5_client import GPT5ResponsesClient
from src.models.ceo_profile import CEOProfile
from src.config.settings import Settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def research_ceo_with_websearch(
    ceo_name: str,
    company_name: str,
    reasoning_effort: str = "medium"
) -> CEOProfile:
    """
    Research a CEO using GPT-5 with web search capabilities.

    Args:
        ceo_name: Full name of the CEO to research
        company_name: Name of the company
        reasoning_effort: Reasoning effort level for GPT-5 (default: "high")

    Returns:
        CEOProfile: Populated CEO profile with research data

    Raises:
        ValueError: If required parameters are missing
        Exception: If research fails
    """

    if not ceo_name or not company_name:
        raise ValueError("CEO name and company name are required")

    logger.info(f"Starting CEO research for {ceo_name} at {company_name}")

    # Initialize settings and client
    settings = Settings()
    client = GPT5ResponsesClient(settings)

    if not client.is_ready:
        raise ValueError("GPT-5 client not ready - check OpenAI API key")

    # Create research prompt
    prompt = _create_research_prompt(ceo_name, company_name)

    try:
        # Make GPT-5 API call with web search enabled
        logger.info("Making GPT-5 API call with web search enabled")
        response = await client.create_response(
            prompt=prompt,
            reasoning_effort=reasoning_effort,
            tools=[{"type": "web_search"}],  # Enable web search
            verbosity="high"  # Get detailed responses
        )

        # Extract text from response - robust approach
        text_content = _extract_text_from_response(response)

        if not text_content:
            raise ValueError("No text content found in GPT-5 response")

        logger.info("Successfully extracted response text from GPT-5")

        # Parse JSON response into CEOProfile
        profile = _parse_response_to_profile(text_content, ceo_name, company_name)

        logger.info(f"Successfully completed research for {ceo_name}")
        return profile

    except Exception as e:
        logger.error(f"CEO research failed: {e}")
        raise


def _create_research_prompt(ceo_name: str, company_name: str) -> str:
    """
    Create a comprehensive research prompt for CEO information gathering.

    Args:
        ceo_name: CEO name to research
        company_name: Company name

    Returns:
        str: Formatted research prompt
    """

    prompt = f"""
You are an expert business researcher tasked with gathering comprehensive information about a CEO.

RESEARCH TARGET:
- CEO Name: {ceo_name}
- Company: {company_name}

INSTRUCTIONS:
1. Use web search to find the most current and accurate information
2. Focus on finding reliable sources (SEC filings, company websites, major news outlets)
3. Gather information for ALL the fields listed below when possible
4. Return ONLY a valid JSON object with the specified structure
5. Use "unknown" or null for fields where reliable data cannot be found
6. Ensure all dates are in MM/DD/YYYY format
7. CRITICAL RULES for previous_company and previous_position fields:
   - For INSIDERS: previous_company should be null (they were already at the company)
                   previous_position should be their last role AT THE SAME COMPANY before becoming CEO
   - For OUTSIDERS: previous_company should be their last employer before joining as CEO
                    previous_position should be their role at that previous external company
8. For initial_join_year, find the YEAR (YYYY) when the person FIRST joined the company in ANY role (even as intern, analyst, etc.)
9. Be thorough and accurate - this is for research purposes

CRITICAL CLASSIFICATION RULES FOR insider_outsider:
- Set to "insider" if the person worked at the company BEFORE becoming CEO (promoted from within)
- Set to "outsider" if the person was hired as CEO from outside (first role at company was CEO)
- Set to "unknown" ONLY if you cannot determine their prior employment at the company
- Key indicators:
  * INSIDER: Had roles like COO, CFO, President, EVP, or any position at the company before CEO
  * OUTSIDER: Came from another company directly to CEO role
  * Check "years_before_ceo" field - if > 0, they are an INSIDER

REQUIRED JSON STRUCTURE:
Return a JSON object with these exact field names:

{{
    "ceo_name": "{ceo_name}",
    "company_name": "{company_name}",
    "ceo_title": "string or null",
    "insider_outsider": "insider/outsider/unknown (see classification rules above)",
    "ceo_type": "string or null",
    "appointment_date": "MM/DD/YYYY or null",
    "start_date": "MM/DD/YYYY or null",
    "departure_date": "MM/DD/YYYY or 'incumbent'",
    "tenure_years": "integer or null",
    "tenure_months": "integer or null",
    "previous_company": "OUTSIDER: last external company; INSIDER: null (see rule 7)",
    "previous_position": "OUTSIDER: role at previous company; INSIDER: last role at same company before CEO",
    "initial_join_year": "year (YYYY) when first joined company in ANY role or null",
    "years_at_company": "integer or null",
    "years_before_ceo": "integer or null",
    "previous_ceo_experience": "boolean or null",
    "predecessor_name": "string or null",
    "succession_type": "string or null",
    "interim_period": "boolean or null",
    "board_connection": "string or null",
    "departure_reason": "string or null",
    "departure_voluntary": "boolean or null",
    "successor_name": "string or null",
    "post_ceo_role": "string or null",
    "data_completeness": "high/medium/low",
    "primary_sources": ["array of source descriptions"],
    "last_updated": "{datetime.now().strftime('%m/%d/%Y')}",
    "confidence_score": "number between 0.0 and 1.0",
    "notes": "string with any important caveats or additional context"
}}

IMPORTANT:
- Use web search extensively to find current, accurate information
- Prioritize official sources (SEC filings, company press releases, major business publications)
- Return ONLY the JSON object, no additional text or explanation
- Ensure the JSON is valid and properly formatted
- Be thorough but accurate - mark uncertain information appropriately
"""

    return prompt


def _extract_text_from_response(response) -> Optional[str]:
    """
    Extract text content from GPT-5 API response object.

    Uses KISS principle - checks the correct locations based on web search usage.
    When web search is enabled, text is at response.output[1].content[0].text
    When web search is disabled, text is at response.output[0].content[0].text

    Args:
        response: The response object from GPT-5 API

    Returns:
        str: The extracted text content or None if not found
    """
    try:
        # Check if response has output structure (primary method for GPT-5)
        if hasattr(response, 'output') and response.output:

            # KISS: Check the LAST item first - it's usually the final response
            # When web search is used, there are many reasoning/search pairs,
            # with the actual response at the end
            if len(response.output) > 0:
                last_item = response.output[-1]

                # Check if it's a ResponseOutputMessage with content
                if hasattr(last_item, 'content') and last_item.content:
                    if len(last_item.content) > 0:
                        content_item = last_item.content[0]
                        if hasattr(content_item, 'text'):
                            text_content = content_item.text
                            if text_content is not None:
                                logger.debug(f"Extracting text via response.output[-1].content[0].text (last item)")
                                return text_content

            # Fallback: Try indices 1 and 0 for simpler responses
            for output_index in [1, 0]:
                if len(response.output) > output_index:
                    output_item = response.output[output_index]
                    if hasattr(output_item, 'content') and output_item.content:
                        if len(output_item.content) > 0:
                            content_item = output_item.content[0]
                            if hasattr(content_item, 'text'):
                                text_content = content_item.text
                                if text_content is not None:
                                    logger.debug(f"Extracting text via response.output[{output_index}].content[0].text")
                                    return text_content

        # Fallback: try direct output_text attribute
        if hasattr(response, 'output_text') and response.output_text:
            logger.debug("Extracting text via response.output_text")
            return response.output_text

        # Final fallback: log detailed structure for debugging
        logger.error("Unable to extract text from response - no valid text content found")
        logger.debug(f"Response type: {type(response)}")
        if hasattr(response, 'output') and response.output:
            logger.debug(f"Output length: {len(response.output)}")
            for i, item in enumerate(response.output):
                logger.debug(f"Output[{i}] type: {type(item)}, has content: {hasattr(item, 'content')}")
                if hasattr(item, 'content') and item.content:
                    logger.debug(f"Output[{i}].content length: {len(item.content)}")
        return None

    except Exception as e:
        logger.error(f"Failed to extract text from response: {e}")
        return None


def _parse_response_to_profile(response_text: str, ceo_name: str, company_name: str) -> CEOProfile:
    """
    Parse GPT-5 response text into CEOProfile object.

    Args:
        response_text: JSON response text from GPT-5
        ceo_name: CEO name for fallback
        company_name: Company name for fallback

    Returns:
        CEOProfile: Parsed profile object

    Raises:
        ValueError: If response cannot be parsed
    """

    try:
        # Clean and parse JSON response
        cleaned_text = response_text.strip()

        # Remove any markdown code blocks if present
        if cleaned_text.startswith('```'):
            lines = cleaned_text.split('\n')
            # Find first line that starts with { and last line that ends with }
            start_idx = 0
            end_idx = len(lines) - 1

            for i, line in enumerate(lines):
                if line.strip().startswith('{'):
                    start_idx = i
                    break

            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip().endswith('}'):
                    end_idx = i
                    break

            cleaned_text = '\n'.join(lines[start_idx:end_idx + 1])

        # Parse JSON
        data = json.loads(cleaned_text)
        logger.info("Successfully parsed JSON response")

        # Create CEOProfile object
        profile = CEOProfile(**data)
        logger.info(f"Successfully created CEOProfile for {profile.ceo_name}")

        return profile

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.error(f"Response text: {response_text[:500]}...")

        # Create minimal profile as fallback
        return CEOProfile(
            ceo_name=ceo_name,
            company_name=company_name,
            data_completeness="low",
            confidence_score=0.1,
            notes=f"Failed to parse GPT-5 response: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Failed to create CEOProfile: {e}")

        # Create minimal profile as fallback
        return CEOProfile(
            ceo_name=ceo_name,
            company_name=company_name,
            data_completeness="low",
            confidence_score=0.1,
            notes=f"Failed to process response: {str(e)}"
        )


