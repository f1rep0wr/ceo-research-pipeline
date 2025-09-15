"""
Simple CEO Web Search Research using OpenAI

KISS principle: Minimal code, maximum simplicity.
"""

import json
from datetime import datetime
from openai import AsyncOpenAI

from src.models.ceo_profile import CEOProfile
from src.config.settings import get_settings


async def research_ceo_with_websearch(ceo_name: str, company_name: str) -> CEOProfile:
    """
    Research a CEO using OpenAI.

    Args:
        ceo_name: Full name of the CEO to research
        company_name: Name of the company

    Returns:
        CEOProfile: Structured CEO data
    """
    # Get settings and create client
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    # Comprehensive prompt asking for ALL CEO information fields
    prompt = f"""Research CEO {ceo_name} of {company_name}.

Find comprehensive information and return ONLY a JSON object with ALL these fields:

{{
    "ceo_name": "{ceo_name}",
    "company_name": "{company_name}",
    "ceo_title": "official title or null",
    "company_ticker": "stock ticker or null",
    "company_exchange": "exchange (NYSE/NASDAQ/etc) or null",

    "insider_outsider": "insider/outsider/unknown or null",
    "ceo_type": "founder/professional/interim/etc or null",

    "appointment_date": "MM/DD/YYYY or null",
    "start_date": "MM/DD/YYYY or null",
    "departure_date": "MM/DD/YYYY or 'incumbent' or null",
    "tenure_years": number_or_null,
    "tenure_months": number_or_null,

    "birth_year": number_or_null,
    "age": number_or_null,
    "age_at_appointment": number_or_null,
    "nationality": "nationality or null",
    "gender": "gender or null",
    "birthplace": "birthplace or null",

    "education_schools": ["school1", "school2"] or [],
    "education_degrees": ["degree1", "degree2"] or [],
    "education_majors": ["major1", "major2"] or [],
    "mba_school": "MBA school or null",

    "previous_companies": ["company1", "company2"] or [],
    "previous_positions": ["position1", "position2"] or [],
    "years_at_company": number_or_null,
    "years_before_ceo": number_or_null,
    "previous_ceo_experience": true_false_or_null,

    "predecessor_name": "previous CEO name or null",
    "succession_type": "planned/forced/emergency/etc or null",
    "interim_period": true_false_or_null,
    "board_connection": "board connection description or null",

    "departure_reason": "departure reason or null",
    "departure_voluntary": true_false_or_null,
    "successor_name": "successor name or null",
    "post_ceo_role": "role after CEO or null",

    "industry": "industry/sector or null",
    "company_size": "large/medium/small or null",
    "annual_revenue": number_in_billions_or_null,
    "market_cap": number_in_billions_or_null,
    "employee_count": number_or_null,
    "fortune_ranking": number_or_null,

    "stock_performance": "performance description or null",
    "revenue_growth": percentage_number_or_null,
    "major_achievements": ["achievement1", "achievement2"] or [],

    "data_completeness": "high/medium/low or null",
    "primary_sources": ["source1", "source2"] or [],
    "last_updated": "{datetime.now().strftime('%m/%d/%Y')}",
    "confidence_score": number_between_0_and_1_or_null,
    "notes": "additional notes or null"
}}

Use null for unknown data. Use empty arrays [] for unknown lists. Return ONLY valid JSON."""

    try:
        # Make API call
        response = await client.chat.completions.create(
            model="gpt-4o",  # Use reliable model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        # Extract JSON from response
        response_text = response.choices[0].message.content

        if not response_text or response_text.strip() == "":
            raise ValueError("Empty response from OpenAI API")

        # Extract JSON from markdown code blocks if present
        json_text = response_text.strip()
        if json_text.startswith("```json"):
            # Remove markdown code block formatting
            json_text = json_text[7:]  # Remove ```json
            if json_text.endswith("```"):
                json_text = json_text[:-3]  # Remove ```
        elif json_text.startswith("```"):
            # Handle generic code blocks
            json_text = json_text[3:]  # Remove ```
            if json_text.endswith("```"):
                json_text = json_text[:-3]  # Remove ```

        json_text = json_text.strip()

        # Try to parse JSON
        ceo_data = json.loads(json_text)

        # Create CEOProfile
        return CEOProfile(**ceo_data)

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Response text was: {response_text}")

        # Return minimal profile as fallback
        return CEOProfile(
            ceo_name=ceo_name,
            company_name=company_name,
            last_updated=datetime.now().strftime('%m/%d/%Y'),
            confidence_score=0.1,
            notes="Failed to parse OpenAI response"
        )
    except Exception as e:
        print(f"API call error: {e}")

        # Return minimal profile as fallback
        return CEOProfile(
            ceo_name=ceo_name,
            company_name=company_name,
            last_updated=datetime.now().strftime('%m/%d/%Y'),
            confidence_score=0.1,
            notes=f"API error: {str(e)}"
        )