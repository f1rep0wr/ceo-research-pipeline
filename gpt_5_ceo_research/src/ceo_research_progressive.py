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
import os
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, unquote
from datetime import datetime

from src.clients.gpt5_client import GPT5ResponsesClient
from src.models.ceo_profile import CEOProfile
from src.prompts.ceo_research_prompts import CEOResearchPrompts
from src.config.settings import Settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

LLM_GAP_HINTS = (
    "not enough information",
    "insufficient",
    "unable to",
    "no data",
    "not available",
    "unknown",
)



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
                self._merge_profile_data(profile_data, basic_info)
                logger.info(f"Basic research completed. Classification: {basic_info.get('insider_outsider', 'unknown')}")
            
            # Stage 2: Career Details (based on classification - insider, outsider, or unknown)
            if 'career_details' in stages and basic_info:
                career_stage = self.prompts.should_use_insider_or_outsider_career(basic_info)
                logger.info(f"Stage 2: Gathering {career_stage} details")
                career_info = await self._run_career_research(
                    ceo_name, company_name, basic_info, career_stage, reasoning_effort
                )
                if career_info:
                    self._merge_profile_data(profile_data, career_info)
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
                    self._merge_profile_data(profile_data, succession_info)
                    logger.info("Succession research completed")
            
            # Stage 4: Post-CEO Details
            if 'post_ceo' in stages and basic_info:
                departure_value = profile_data.get("departure_date") or basic_info.get("departure_date")
                successor_name = profile_data.get("successor_name") or basic_info.get("successor_name")

                has_departed = False
                if departure_value:
                    normalized_departure = str(departure_value).strip().lower()
                    if normalized_departure not in {"", "incumbent", "current", "present", "ongoing", "now"}:
                        has_departed = True

                if not has_departed and successor_name and str(successor_name).strip():
                    has_departed = True

                if not has_departed:
                    logger.info("Skipping post-CEO research: CEO appears to remain in role")
                else:
                    logger.info("Stage 4: Gathering post-CEO career and verification")
                    post_ceo_info = await self._run_post_ceo_research(
                        ceo_name, company_name, basic_info, reasoning_effort
                    )
                    if post_ceo_info:
                        self._merge_profile_data(profile_data, post_ceo_info)
                        logger.info("Post-CEO research completed")
                    
            # Final assessment
            self._clean_source_lists(profile_data, ceo_name, company_name)

            # Re-rank merged sources for optimal value ordering
            if profile_data.get('source_urls'):
                profile_data['source_urls'] = await self._rerank_merged_sources(
                    profile_data['source_urls'],
                    ceo_name,
                    company_name
                )

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
            self._log_llm_feedback("comprehensive", profile_data)
            
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
            
        result = self._parse_json_response(text_content, ceo_name, company_name)
        self._log_llm_feedback("basic", result)
        return result

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
                
            result = self._parse_json_response(text_content, ceo_name, company_name)
            self._log_llm_feedback(career_stage, result)
            return result
            
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
                
            result = self._parse_json_response(text_content, ceo_name, company_name)
            self._log_llm_feedback("succession", result)
            return result
            
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
                
            result = self._parse_json_response(text_content, ceo_name, company_name)
            self._log_llm_feedback("post_ceo", result)
            return result
            
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
            self._clean_source_lists(data, ceo_name, company_name)
            
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


    def _log_llm_feedback(self, stage: str, data: Dict[str, Any]) -> None:
        """Log the LLM notes and highlight fields that look incomplete."""
        if not isinstance(data, dict):
            return

        note_fields = ("notes", "conflicting_data_notes", "data_quality_notes")
        stage_notes: List[str] = []
        difficulty_entries: List[str] = []

        for field in note_fields:
            value = data.get(field)
            if isinstance(value, str):
                cleaned = value.strip()
                if cleaned:
                    logger.info("LLM %s (%s stage): %s", field, stage, cleaned)
                    if field != "notes":
                        stage_notes.append(f"{field}: {cleaned}")
                        difficulty_entries.append(f"{field}: {cleaned}")

        flagged_messages: List[str] = []
        for field, value in data.items():
            if isinstance(value, str):
                cleaned_value = value.strip()
                if not cleaned_value:
                    continue
                lowered = cleaned_value.lower()
                if any(hint in lowered for hint in LLM_GAP_HINTS):
                    flagged_messages.append(f"{field}: {cleaned_value}")

        if flagged_messages:
            limited_text = " | ".join(flagged_messages)
            logger.info("LLM indicated limited information (%s stage): %s", stage, limited_text)
            stage_notes.append(f"limited info -> {limited_text}")
            difficulty_entries.append(f"limited info -> {limited_text}")

        if stage_notes:
            combined_note = f"{stage} stage: " + " | ".join(stage_notes)
            data["notes"] = self._merge_notes(data.get("notes"), combined_note)

        if difficulty_entries:
            combined_difficulty = f"{stage} stage: " + " | ".join(difficulty_entries)
            data["why_incorrect"] = self._merge_notes(data.get("why_incorrect"), combined_difficulty)

    def _merge_profile_data(self, base: Dict[str, Any], new_data: Optional[Dict[str, Any]]) -> None:
        """Merge stage data into the profile without losing previously validated values."""
        if not new_data:
            return

        list_fields = {'source_urls', 'primary_sources', 'alternative_verification_paths'}
        for key, value in new_data.items():
            if key in list_fields:
                base[key] = self._merge_list_field(base.get(key), value)
            elif key in {'notes', 'why_incorrect'}:
                base[key] = self._merge_notes(base.get(key), value)
            elif value not in (None, '', [], {}):
                base[key] = value

    def _merge_list_field(self, current_values, new_values) -> List[str]:
        combined = self._normalize_to_list(current_values) + self._normalize_to_list(new_values)
        if not combined:
            return []

        merged: List[str] = []
        seen = set()
        for item in combined:
            if item is None:
                continue
            if isinstance(item, str):
                cleaned = item.strip()
                if not cleaned:
                    continue
                dedupe_key = cleaned.lower()
            else:
                cleaned = item
                dedupe_key = str(item)

            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            merged.append(cleaned)

        return merged

    def _normalize_to_list(self, value) -> List:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [value]

        try:
            return list(value)
        except TypeError:
            return [value]

    def _merge_notes(self, existing, new_value):
        notes = []
        for note in (existing, new_value):
            if isinstance(note, str):
                cleaned = note.strip()
                if cleaned:
                    notes.append(cleaned)

        if not notes:
            return existing if existing is not None else new_value

        deduped = []
        seen = set()
        for note in notes:
            key = note.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(note)

        return ' | '.join(deduped)

    def _clean_source_lists(self, data: Dict[str, Any], ceo_name: str, company_name: str) -> None:
        """Remove low-value or duplicate sources while preserving verifiable links."""
        if 'source_urls' in data:
            data['source_urls'] = self._filter_source_urls(
                data.get('source_urls'),
                ceo_name,
                company_name
            )
        if 'primary_sources' in data:
            data['primary_sources'] = self._deduplicate_strings(data.get('primary_sources'))
        if 'alternative_verification_paths' in data:
            data['alternative_verification_paths'] = self._deduplicate_strings(
                data.get('alternative_verification_paths')
            )

    def _filter_source_urls(self, urls, ceo_name: str, company_name: str) -> List[str]:
        url_list = self._normalize_to_list(urls)
        if not url_list:
            return []

        ceo_tokens = [token.lower() for token in ceo_name.split() if token]
        company_tokens = [token.lower() for token in company_name.split() if token]
        allow_without_tokens = ('sec.gov', 'occ.treas.gov', 'fdic.gov', 'treasury.gov', 'frbservices.org')

        cleaned_urls: List[str] = []
        seen = set()

        for raw_url in url_list:
            if not isinstance(raw_url, str):
                continue

            url = raw_url.strip()
            if not url:
                continue

            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                continue
            if not parsed.netloc:
                continue

            domain = parsed.netloc.lower()

            if any(bad in domain for bad in ('google.', 'bing.com', 'duckduckgo.', 'yahoo.com', 'search.aol.com')):
                continue

            path_lower = (parsed.path or '').lower()
            query_lower = (parsed.query or '').lower()
            if 'search' in path_lower or 'search=' in query_lower:
                continue

            normalized_path = parsed.path.strip('/')
            if not normalized_path and not parsed.query:
                if not any(domain.endswith(allowed) for allowed in allow_without_tokens):
                    continue

            descriptor = unquote(f"{parsed.path} {parsed.query}").lower()
            has_name = any(token in descriptor for token in ceo_tokens)
            has_company = any(token in descriptor for token in company_tokens)
            keywords = ('press', 'article', 'news', 'leadership', 'management', 'ceo', 'executive',
                        'investor', 'filing', 'proxy', 'succession', 'board', 'release', 'appointment')
            has_keyword = any(keyword in descriptor for keyword in keywords)
            extension = os.path.splitext(parsed.path)[1].lower()

            if not (has_name or has_company or has_keyword or extension in ('.pdf', '.htm', '.html', '.txt')):
                if not any(domain.endswith(allowed) for allowed in allow_without_tokens):
                    continue

            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if parsed.query:
                normalized += f"?{parsed.query}"

            normalized = normalized.split('#', 1)[0]

            dedupe_key = normalized.lower()
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            cleaned_urls.append(normalized)

        return cleaned_urls

    def _deduplicate_strings(self, values) -> List[str]:
        items = self._normalize_to_list(values)
        if not items:
            return []

        deduped: List[str] = []
        seen = set()
        for item in items:
            if not isinstance(item, str):
                continue
            cleaned = item.strip()
            if len(cleaned) < 3:
                continue
            key = cleaned.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(cleaned)

        return deduped


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

    async def _rerank_merged_sources(self, all_sources: List[str], ceo_name: str, company_name: str) -> List[str]:
        """
        Re-rank all merged sources from multiple research stages by value and authority.

        Uses GPT-5 to intelligently rank sources based on authority, information depth,
        and relevance to CEO research.

        Args:
            all_sources: Combined list of sources from all research stages
            ceo_name: CEO name for context
            company_name: Company name for context

        Returns:
            Re-ranked list with most valuable sources first
        """

        if not all_sources or len(all_sources) <= 1:
            return all_sources

        logger.info(f"Re-ranking {len(all_sources)} merged sources for {ceo_name}")

        # Build numbered source list for prompt
        source_list = "\n".join(f"{i+1}. {url}" for i, url in enumerate(all_sources))

        prompt = f"""You just completed multi-stage research on {ceo_name} (CEO of {company_name}) and collected these sources across different research stages:

{source_list}

**Task:** Re-rank these sources from MOST to LEAST valuable for CEO succession research.

**Ranking Criteria (in priority order):**

1. **Authority & Reliability**
   - Government/Regulatory (SEC.gov, FDIC, OCC) = Highest authority
   - Official company sources (investor relations, press releases from company domain) = Very high
   - Premium financial news (WSJ, FT, Bloomberg, Reuters) = High
   - Trade publications (American Banker, Bank Director) = Medium-high
   - Press distribution (BusinessWire, PRNewswire) = Medium
   - General news/Wikipedia = Lower

2. **Information Depth**
   - Detailed filings (proxy statements, 10-K, 8-K) = Most informative
   - Long-form articles/profiles = Very informative
   - Press releases with details = Informative
   - Brief mentions/listings = Less informative

3. **Relevance**
   - Sources specifically about this CEO's career/succession = Most relevant
   - Sources about the company's leadership = Relevant
   - General industry sources = Less relevant

4. **Specificity**
   - Direct evidence (appointment dates, titles, quotes) = Most specific
   - Biographical details = Specific
   - General context = Less specific

**Output Format:**
Return ONLY valid JSON (no markdown, no explanation):
{{
  "ranked_sources": ["url1", "url2", "url3", ...],
  "reasoning": "Brief explanation of top 3 source rankings"
}}

The ranked_sources array MUST contain ALL {len(all_sources)} URLs in your preferred order."""

        try:
            response = await self.client.create_response(
                prompt=prompt,
                reasoning_effort="low",  # Fast but still thoughtful
                tools=[],  # No web search needed
                verbosity="low"  # Valid values: low, medium, high
            )

            text_content = self._extract_text_from_response(response)
            if not text_content:
                logger.warning("No response from source re-ranking, keeping original order")
                return all_sources

            # Parse JSON response
            try:
                # Clean response
                cleaned = text_content.strip()
                if cleaned.startswith('```'):
                    lines = cleaned.split('\n')
                    cleaned = '\n'.join(line for line in lines if not line.strip().startswith('```'))

                result = json.loads(cleaned)
                ranked = result.get('ranked_sources', [])
                reasoning = result.get('reasoning', 'No reasoning provided')

                if not ranked:
                    logger.warning("Empty ranked_sources in response, keeping original order")
                    return all_sources

                # Normalize ranked list to match original sources exactly (KISS):
                # 1) If model returned indices, map them to URLs
                # 2) Drop unknowns and duplicates while preserving order
                # 3) Append any missing originals at the end in original order

                def _normalize_ranked(ranked_list):
                    # Map integers to URLs (1-based or 0-based tolerant)
                    mapped: list[str] = []
                    for item in ranked_list:
                        if isinstance(item, int):
                            # Prefer 1-based, fallback to 0-based if out of range
                            url = None
                            if 1 <= item <= len(all_sources):
                                url = all_sources[item - 1]
                            elif 0 <= item < len(all_sources):
                                url = all_sources[item]
                            if url is not None:
                                mapped.append(url)
                        elif isinstance(item, str):
                            mapped.append(item.strip())
                    # Deduplicate and filter to known sources
                    seen = set()
                    known = set(all_sources)
                    deduped: list[str] = []
                    for url in mapped:
                        if url in known and url not in seen:
                            deduped.append(url)
                            seen.add(url)
                    # Append any missing originals in original order
                    for url in all_sources:
                        if url not in seen:
                            deduped.append(url)
                            seen.add(url)
                    return deduped

                normalized_ranked = _normalize_ranked(ranked)

                if len(normalized_ranked) != len(all_sources):
                    # As a safety net; should not happen after normalization
                    logger.warning(
                        f"Ranked sources count mismatch after normalization ({len(normalized_ranked)} vs {len(all_sources)}), using original order"
                    )
                    return all_sources

                if len(ranked) != len(all_sources):
                    logger.warning(
                        f"Ranked sources count mismatch ({len(ranked)} vs {len(all_sources)}), normalized order will be used"
                    )

                logger.info(f"Successfully re-ranked sources. Reasoning: {reasoning}")
                return normalized_ranked

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse re-ranking JSON: {e}")
                logger.error(f"Response text: {text_content[:200]}")
                return all_sources

        except Exception as e:
            logger.error(f"Source re-ranking failed: {e}")
            return all_sources  # Fallback to original order


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
