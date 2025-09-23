"""
Progressive CEO Research Implementation

This module implements a KISS-compliant progressive research approach that breaks
complex CEO research into manageable stages, allowing for better data quality
and more focused GPT-5 interactions.

The progressive approach:
1. Basic Info & Classification (essential facts)
2. Career Details (insider vs outsider specific)
3. Succession Details (transition circumstances) 
4. Post-CEO Details (what happened after)

Each stage can be run independently, and results are merged progressively.
"""

import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.clients.gpt5_client import GPT5ResponsesClient
from src.models.ceo_profile import CEOProfile
from src.prompts.ceo_research_prompts import CEOResearchPrompts
from src.config.settings import Settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProgressiveCEOResearcher:
    """
    Progressive CEO research system following KISS principles.
    
    Breaks research into focused stages to avoid overwhelming GPT-5 while 
    ensuring comprehensive data collection through progressive enhancement.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the progressive researcher."""
        self.settings = settings or Settings()
        self.client = GPT5ResponsesClient(self.settings)
        self.prompts = CEOResearchPrompts()
        
    async def research_ceo_progressive(
        self, 
        ceo_name: str, 
        company_name: str,
        reasoning_effort: str = "medium",
        stages: Optional[List[str]] = None
    ) -> CEOProfile:
        """
        Run progressive CEO research through multiple focused stages.
        
        Args:
            ceo_name: Full name of the CEO
            company_name: Name of the company  
            reasoning_effort: GPT-5 reasoning effort level
            stages: List of stages to run (default: all recommended stages)
            
        Returns:
            CEOProfile with progressively enhanced data
        """
        
        if not ceo_name or not company_name:
            raise ValueError("CEO name and company name are required")
            
        if not self.client.is_ready:
            raise ValueError("GPT-5 client not ready - check OpenAI API key")
            
        logger.info(f"Starting progressive CEO research for {ceo_name} at {company_name}")
        
        # Use recommended sequence if not specified
        if stages is None:
            stages = ['basic', 'career_details', 'succession', 'post_ceo']
            
        # Initialize with basic CEO profile
        profile_data = {
            "ceo_name": ceo_name,
            "company_name": company_name,
            "data_completeness": "low",
            "confidence_score": 0.1
        }
        
        basic_info = None
        
        try:
            # Stage 1: Basic Information & Classification 
            if 'basic' in stages:
                logger.info("Stage 1: Gathering basic information and classification")
                basic_info = await self._run_basic_research(ceo_name, company_name, reasoning_effort)
                profile_data.update(basic_info)
                logger.info(f"Basic research completed. Classification: {basic_info.get('insider_outsider', 'unknown')}")
            
            # Stage 2: Career Details (based on classification - insider, outsider, or unknown)
            if 'career_details' in stages and basic_info:
                career_stage = self.prompts.should_use_insider_or_outsider_career(basic_info)
                logger.info(f"Stage 2: Gathering {career_stage} details")
                career_info = await self._run_career_research(
                    ceo_name, company_name, basic_info, career_stage, reasoning_effort
                )
                if career_info:
                    profile_data.update(career_info)
                    logger.info("Career research completed")
                else:
                    logger.info("Career research returned no data")
            
            # Stage 3: Succession Details
            if 'succession' in stages and basic_info:
                logger.info("Stage 3: Gathering succession and transition details")
                succession_info = await self._run_succession_research(
                    ceo_name, company_name, basic_info, reasoning_effort
                )
                if succession_info:
                    profile_data.update(succession_info)
                    logger.info("Succession research completed")
            
            # Stage 4: Post-CEO Details
            if 'post_ceo' in stages and basic_info:
                logger.info("Stage 4: Gathering post-CEO career and verification")
                post_ceo_info = await self._run_post_ceo_research(
                    ceo_name, company_name, basic_info, reasoning_effort
                )
                if post_ceo_info:
                    profile_data.update(post_ceo_info)
                    logger.info("Post-CEO research completed")
                    
            # Final assessment
            self._assess_final_data_quality(profile_data)
            
            # Create final profile
            try:
                profile = CEOProfile(**profile_data)
                logger.info(f"Progressive research completed for {ceo_name}. Final confidence: {profile.confidence_score}")
                return profile
            except Exception as validation_error:
                logger.error(f"Profile validation failed: {validation_error}")
                logger.error(f"Profile data causing validation error: {profile_data}")
                
                # Try to create minimal profile for error reporting
                minimal_data = {
                    "ceo_name": ceo_name,
                    "company_name": company_name,
                    "data_completeness": "low",
                    "confidence_score": 0.1,
                    "notes": f"Profile validation failed: {str(validation_error)}"
                }
                return CEOProfile(**minimal_data)
            
        except Exception as e:
            logger.error(f"Progressive CEO research failed: {e}")
            # Return minimal profile with error notes
            minimal_data = {
                "ceo_name": ceo_name,
                "company_name": company_name,
                "data_completeness": "low",
                "confidence_score": 0.1,
                "notes": f"Research failed: {str(e)}"
            }
            return CEOProfile(**minimal_data)

    async def research_ceo_comprehensive(
        self,
        ceo_name: str,
        company_name: str, 
        reasoning_effort: str = "medium"
    ) -> CEOProfile:
        """
        Alternative: Single comprehensive research call.
        
        Uses the simplified comprehensive prompt for when you want all data
        in one pass, but with reduced complexity vs the original mega-prompt.
        """
        
        if not ceo_name or not company_name:
            raise ValueError("CEO name and company name are required")
            
        if not self.client.is_ready:
            raise ValueError("GPT-5 client not ready - check OpenAI API key")
            
        logger.info(f"Starting comprehensive CEO research for {ceo_name} at {company_name}")
        
        try:
            # Use comprehensive single prompt
            prompt = self.prompts.get_comprehensive_single_prompt(ceo_name, company_name)
            
            response = await self.client.create_response(
                prompt=prompt,
                reasoning_effort=reasoning_effort,
                tools=[{"type": "web_search"}],
                verbosity="high"
            )
            
            # Extract and parse response
            text_content = self._extract_text_from_response(response)
            if not text_content:
                raise ValueError("No text content found in GPT-5 response")
                
            profile_data = self._parse_json_response(text_content, ceo_name, company_name)
            
            # Create profile with better error handling
            try:
                profile = CEOProfile(**profile_data)
                logger.info(f"Comprehensive research completed for {ceo_name}")
                return profile
            except Exception as validation_error:
                logger.error(f"Profile validation failed in comprehensive research: {validation_error}")
                logger.error(f"Profile data causing validation error: {profile_data}")
                return CEOProfile(
                    ceo_name=ceo_name,
                    company_name=company_name,
                    data_completeness="low",
                    confidence_score=0.1,
                    notes=f"Profile validation failed: {str(validation_error)}"
                )
            
        except Exception as e:
            logger.error(f"Comprehensive CEO research failed: {e}")
            return CEOProfile(
                ceo_name=ceo_name,
                company_name=company_name,
                data_completeness="low",
                confidence_score=0.1,
                notes=f"Comprehensive research failed: {str(e)}"
            )

    async def _run_basic_research(self, ceo_name: str, company_name: str, reasoning_effort: str) -> Dict[str, Any]:
        """Run Stage 1: Basic information and classification research."""
        
        prompt = self.prompts.get_basic_info_prompt(ceo_name, company_name)
        
        response = await self.client.create_response(
            prompt=prompt,
            reasoning_effort=reasoning_effort,
            tools=[{"type": "web_search"}],
            verbosity="medium"
        )
        
        text_content = self._extract_text_from_response(response)
        if not text_content:
            raise ValueError("No response from basic research stage")
            
        return self._parse_json_response(text_content, ceo_name, company_name)

    async def _run_career_research(
        self, 
        ceo_name: str, 
        company_name: str, 
        basic_info: Dict, 
        career_stage: str,
        reasoning_effort: str
    ) -> Optional[Dict[str, Any]]:
        """Run Stage 2: Career details research (insider or outsider specific)."""
        
        try:
            prompt = self.prompts.get_prompt_by_stage(career_stage, ceo_name, company_name, basic_info)
            
            response = await self.client.create_response(
                prompt=prompt,
                reasoning_effort=reasoning_effort,
                tools=[{"type": "web_search"}],
                verbosity="medium"
            )
            
            text_content = self._extract_text_from_response(response)
            if not text_content:
                logger.warning("No response from career research stage")
                return None
                
            return self._parse_json_response(text_content, ceo_name, company_name)
            
        except Exception as e:
            logger.error(f"Career research stage failed: {e}")
            return None

    async def _run_succession_research(
        self, 
        ceo_name: str, 
        company_name: str, 
        basic_info: Dict,
        reasoning_effort: str
    ) -> Optional[Dict[str, Any]]:
        """Run Stage 3: Succession and transition details research."""
        
        try:
            prompt = self.prompts.get_succession_details_prompt(ceo_name, company_name, basic_info)
            
            response = await self.client.create_response(
                prompt=prompt,
                reasoning_effort=reasoning_effort,
                tools=[{"type": "web_search"}],
                verbosity="medium"
            )
            
            text_content = self._extract_text_from_response(response)
            if not text_content:
                logger.warning("No response from succession research stage")
                return None
                
            return self._parse_json_response(text_content, ceo_name, company_name)
            
        except Exception as e:
            logger.error(f"Succession research stage failed: {e}")
            return None

    async def _run_post_ceo_research(
        self, 
        ceo_name: str, 
        company_name: str, 
        basic_info: Dict,
        reasoning_effort: str
    ) -> Optional[Dict[str, Any]]:
        """Run Stage 4: Post-CEO career and verification research."""
        
        try:
            prompt = self.prompts.get_post_ceo_details_prompt(ceo_name, company_name, basic_info)
            
            response = await self.client.create_response(
                prompt=prompt,
                reasoning_effort=reasoning_effort,
                tools=[{"type": "web_search"}],
                verbosity="medium"
            )
            
            text_content = self._extract_text_from_response(response)
            if not text_content:
                logger.warning("No response from post-CEO research stage")
                return None
                
            return self._parse_json_response(text_content, ceo_name, company_name)
            
        except Exception as e:
            logger.error(f"Post-CEO research stage failed: {e}")
            return None

    def _extract_text_from_response(self, response) -> Optional[str]:
        """Extract text content from GPT-5 API response (reused from original)."""
        
        try:
            if hasattr(response, 'output') and response.output:
                # Check the last item first - usually the final response
                if len(response.output) > 0:
                    last_item = response.output[-1]
                    if hasattr(last_item, 'content') and last_item.content:
                        if len(last_item.content) > 0:
                            content_item = last_item.content[0]
                            if hasattr(content_item, 'text'):
                                return content_item.text

                # Fallback: try indices 1 and 0
                for output_index in [1, 0]:
                    if len(response.output) > output_index:
                        output_item = response.output[output_index]
                        if hasattr(output_item, 'content') and output_item.content:
                            if len(output_item.content) > 0:
                                content_item = output_item.content[0]
                                if hasattr(content_item, 'text'):
                                    return content_item.text

            # Fallback: direct output_text attribute
            if hasattr(response, 'output_text') and response.output_text:
                return response.output_text

            logger.error("Unable to extract text from response")
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract text from response: {e}")
            return None

    def _parse_json_response(self, response_text: str, ceo_name: str, company_name: str) -> Dict[str, Any]:
        """Parse JSON response text into dictionary."""
        
        try:
            # Clean response text
            cleaned_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned_text.startswith('```'):
                lines = cleaned_text.split('\n')
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
            logger.debug("Successfully parsed JSON response")
            
            # Preprocess data to handle common type issues
            data = self._preprocess_data_types(data)
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text (first 500 chars): {response_text[:500]}")
            return {
                "notes": f"Failed to parse stage response: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {e}")
            return {
                "notes": f"Unexpected error: {str(e)}"
            }

    def _preprocess_data_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess data to handle common type conversion issues."""
        
        # Handle string to boolean conversions
        boolean_fields = [
            'was_president', 'was_board_member', 'was_chairman', 'was_ceo_of_subsidiary',
            'was_other_executive', 'was_board_member_only', 'was_former_ceo', 
            'was_former_other_executive', 'joined_as_executive', 'joined_from_early_career',
            'was_ceo_of_other_firms', 'was_other_executive_of_other_firms', 'was_unattached_to_any',
            'previous_ceo_experience', 'interim_period', 'departure_voluntary', 
            'was_forced_out', 'retirement_status', 'no_real_job', 'succession_documentation',
            'career_timeline_verified'
        ]
        
        for field in boolean_fields:
            if field in data and data[field] is not None:
                value = data[field]
                if isinstance(value, str):
                    if value.strip() == '':
                        data[field] = None
                    elif value.lower() in ['true', '1', 'yes']:
                        data[field] = True
                    elif value.lower() in ['false', '0', 'no']:
                        data[field] = False
                    elif value.lower() in ['null', 'none', 'unknown']:
                        data[field] = None
        
        # Handle numeric string conversions for float fields
        float_fields = ['years_at_company', 'years_before_ceo', 'tenure_years', 'tenure_months', 'confidence_score']
        for field in float_fields:
            if field in data and data[field] is not None:
                value = data[field]
                if isinstance(value, str):
                    try:
                        # Handle "null" strings
                        if value.lower() in ['null', 'none', 'unknown', '']:
                            data[field] = None
                        else:
                            data[field] = float(value)
                    except ValueError:
                        logger.warning(f"Could not convert {field} value '{value}' to float, setting to None")
                        data[field] = None
        
        # Handle integer fields
        int_fields = ['initial_join_year', 'year_insider_joined_firm', 'age_at_departure']
        for field in int_fields:
            if field in data and data[field] is not None:
                value = data[field]
                if isinstance(value, str):
                    try:
                        # Handle "null" strings
                        if value.lower() in ['null', 'none', 'unknown', '']:
                            data[field] = None
                        else:
                            # Convert to int, handling floats by rounding
                            data[field] = int(round(float(value)))
                    except ValueError:
                        logger.warning(f"Could not convert {field} value '{value}' to int, setting to None")
                        data[field] = None
                elif isinstance(value, float):
                    data[field] = int(round(value))
        
        # Handle list fields (source_urls, primary_sources, alternative_verification_paths)
        list_fields = ['source_urls', 'primary_sources', 'alternative_verification_paths']
        for field in list_fields:
            if field in data and data[field] is not None:
                value = data[field]
                if isinstance(value, str):
                    # Split string by common delimiters
                    if value.strip():
                        data[field] = [item.strip() for item in value.split(';') if item.strip()]
                    else:
                        data[field] = []
                elif not isinstance(value, list):
                    data[field] = [str(value)] if value else []
        
        return data

    def _assess_final_data_quality(self, profile_data: Dict[str, Any]) -> None:
        """Assess and update final data quality metrics."""
        
        # Count non-null core fields
        core_fields = [
            'insider_outsider', 'appointment_date', 'start_date', 'departure_date',
            'tenure_years', 'previous_company', 'previous_position'
        ]
        
        filled_core = sum(1 for field in core_fields if profile_data.get(field))
        core_completeness = filled_core / len(core_fields)
        
        # Count total filled fields
        total_fields = len([v for v in profile_data.values() if v is not None and v != ''])
        
        # Update data completeness
        if core_completeness >= 0.8 and total_fields >= 15:
            profile_data['data_completeness'] = 'high'
            base_confidence = 0.8
        elif core_completeness >= 0.5 and total_fields >= 10:
            profile_data['data_completeness'] = 'medium'  
            base_confidence = 0.6
        else:
            profile_data['data_completeness'] = 'low'
            base_confidence = 0.3
            
        # Adjust confidence based on source quality
        source_urls = profile_data.get('source_urls', [])
        if isinstance(source_urls, list) and len(source_urls) >= 3:
            base_confidence += 0.1
        elif isinstance(source_urls, list) and len(source_urls) >= 1:
            base_confidence += 0.05
            
        # Adjust for classification confidence
        classification_conf = profile_data.get('insider_outsider_confidence', '').upper()
        if classification_conf == 'HIGH':
            base_confidence += 0.05
        elif classification_conf == 'CONFLICTING':
            base_confidence -= 0.1
            
        profile_data['confidence_score'] = min(1.0, max(0.1, base_confidence))


# Convenience functions for backward compatibility
async def research_ceo_progressive(
    ceo_name: str,
    company_name: str, 
    reasoning_effort: str = "medium",
    stages: Optional[List[str]] = None
) -> CEOProfile:
    """
    Convenience function for progressive CEO research.
    
    This is the RECOMMENDED approach for comprehensive research.
    """
    researcher = ProgressiveCEOResearcher()
    return await researcher.research_ceo_progressive(ceo_name, company_name, reasoning_effort, stages)


async def research_ceo_comprehensive_simple(
    ceo_name: str,
    company_name: str,
    reasoning_effort: str = "medium"  
) -> CEOProfile:
    """
    Convenience function for single-pass comprehensive research.
    
    Use this when you want faster results and don't mind potentially lower detail.
    """
    researcher = ProgressiveCEOResearcher()
    return await researcher.research_ceo_comprehensive(ceo_name, company_name, reasoning_effort)