"""
Modular CEO Research Prompts

This module provides a KISS-compliant approach to CEO research prompts by breaking
down the comprehensive research framework into focused, manageable components.

Each prompt focuses on a specific aspect of CEO research to avoid overwhelming GPT-5
while ensuring comprehensive data collection through a progressive approach.
"""

from typing import Dict, List, Optional
from datetime import datetime


class CEOResearchPrompts:
    """
    Modular CEO research prompt system following KISS principles.
    
    Breaks comprehensive research into focused stages:
    1. Basic Information & Classification
    2. Career History & Insider Analysis  
    3. Succession & Transition Details
    4. Post-CEO & Verification
    """

    @staticmethod
    def get_basic_info_prompt(ceo_name: str, company_name: str) -> str:
        """
        Stage 1: Basic CEO information and insider/outsider classification.
        
        This is the core prompt that establishes fundamental facts and classification.
        Designed to be comprehensive yet focused on essential data.
        """
        
        return f"""You are a financial researcher gathering basic executive information for {ceo_name} at {company_name}.

CRITICAL CLASSIFICATION RULES:
- INSIDER: Worked at the company BEFORE becoming CEO (promoted from within)
- OUTSIDER: Hired as CEO from outside (first role at company was CEO)  
- UNKNOWN: Cannot determine from available information

Use web search to find reliable sources. Focus on SEC filings, official press releases, and major business publications.

Return ONLY valid JSON with this structure:

{{
    "ceo_name": "{ceo_name}",
    "company_name": "{company_name}",
    "ceo_title": "official title or null",
    "insider_outsider": "insider/outsider/unknown",
    "insider_outsider_confidence": "HIGH/MEDIUM/LOW/CONFLICTING",
    "appointment_date": "MM/DD/YYYY or null", 
    "start_date": "MM/DD/YYYY or null",
    "departure_date": "MM/DD/YYYY or 'incumbent'",
    "tenure_years": "number (can be decimal like 2.5) or null",
    "tenure_months": "number (can be decimal) or null",
    "initial_join_year": "YYYY when first joined company in ANY role or null",
    "years_at_company": "number (can be decimal like 21.2) or null",
    "years_before_ceo": "number (can be decimal like 1.5) or null",
    "predecessor_name": "previous CEO name or null",
    "successor_name": "next CEO name or null",
    "data_completeness": "high/medium/low",
    "confidence_score": "0.0 to 1.0",
    "primary_sources": ["source1", "source2"],
    "source_urls": ["url1", "url2"],
    "last_updated": "{datetime.now().strftime('%m/%d/%Y')}",
    "notes": "key findings or caveats"
}}

CRITICAL REQUIREMENTS:
- Use web search extensively for current, verifiable information
- Prioritize official sources (SEC filings, company press releases, official websites)
- EVERY fact must include a direct URL in source_urls field
- Include ALL URLs you accessed during research
- Mark uncertain data with appropriate confidence levels
- Return ONLY the JSON object, no additional text

SOURCE CITATION REQUIREMENTS:
- source_urls MUST contain direct URLs to all sources used
- Each URL should directly support the data you found
- Include SEC filings, press releases, news articles, company websites
- Format: ["https://www.sec.gov/...", "https://company.com/press-release/...", "https://news.site/article/..."]
- MINIMUM 3 sources required for high-quality research"""

    @staticmethod
    def get_insider_career_details_prompt(ceo_name: str, company_name: str, basic_info: Dict) -> str:
        """
        Stage 2A: Detailed career analysis for INSIDER CEOs.
        
        Used when Stage 1 identifies the CEO as an insider.
        """
        
        return f"""You are researching detailed career progression for INSIDER CEO {ceo_name} at {company_name}.

CONTEXT: This person was promoted from within the company (worked there before becoming CEO).

RESEARCH FOCUS: Find their exact career path within the company leading to CEO role.

CRITICAL LOGIC for last_position_before_ceo:
- If was Board Member before CEO -> "Board Member"
- If was President before CEO -> "President"
- If was Chairman before CEO -> "Chairman"
- If was Other Executive before CEO -> "Other Executive"

Use web search to find detailed career history. Look for:
- Internal promotions and role changes
- Years in each position
- Reporting relationships
- Board service history

Return ONLY valid JSON:

{{
    "year_insider_joined_firm": "YYYY when first joined in executive capacity",
    "last_position_before_ceo": "actual job title before CEO (see logic above)",
    "was_president": "true/false/null",
    "was_board_member": "true/false/null", 
    "was_chairman": "true/false/null",
    "was_ceo_of_subsidiary": "true/false/null",
    "was_other_executive": "true/false/null",
    "was_board_member_only": "true/false/null",
    "was_former_ceo": "true/false/null",
    "was_former_other_executive": "true/false/null",
    "joined_as_executive": "true/false/null",
    "joined_from_early_career": "true/false/null",
    "previous_position": "last internal role before CEO",
    "previous_company": "null (insider was already at company)",
    "career_timeline_verified": "true/false",
    "timeline_conflicts": "any conflicts found or null",
    "source_urls": ["url1", "url2"],
    "notes": "detailed career progression notes"
}}

CRITICAL SOURCE REQUIREMENTS:
- Include direct URLs for ALL sources accessed
- EVERY career fact must be verifiable through source_urls
- Minimum 2-3 sources for career progression details
- Include SEC filings, company announcements, business publications
- Format source_urls as: ["https://url1.com", "https://url2.com"]

Focus on accuracy and cite all sources with direct URLs."""

    @staticmethod
    def get_outsider_career_details_prompt(ceo_name: str, company_name: str, basic_info: Dict) -> str:
        """
        Stage 2B: Detailed career analysis for OUTSIDER CEOs.
        
        Used when Stage 1 identifies the CEO as an outsider.
        """
        
        return f"""You are researching detailed career background for OUTSIDER CEO {ceo_name} at {company_name}.

CONTEXT: This person was hired as CEO from outside the company (first role at company was CEO).

RESEARCH FOCUS: Find their career background before joining as CEO.

Use web search to find their previous employer and role details:
- Last company worked for before becoming CEO
- Exact job title and responsibilities  
- CEO experience at other companies
- Geographic location of previous firm
- Career trajectory leading to this CEO role

Return ONLY valid JSON:

{{
    "outsider_job_title": "exact title before joining as CEO",
    "outsider_firm": "company name with city/state if possible", 
    "was_ceo_of_other_firms": "true/false/null",
    "was_other_executive_of_other_firms": "true/false/null",
    "was_unattached_to_any": "true/false/null",
    "previous_company": "last external company before CEO role",
    "previous_position": "role at previous external company", 
    "previous_ceo_experience": "true/false/null",
    "geographic_relocation": "moved for CEO role or null",
    "career_advancement_decline": "advancement/lateral/decline assessment",
    "source_urls": ["url1", "url2"],
    "notes": "detailed background and career path notes"
}}

CRITICAL SOURCE REQUIREMENTS:
- Include direct URLs for ALL sources accessed  
- EVERY previous company/role fact must have supporting source_urls
- Minimum 2-3 sources for outsider career verification
- Include LinkedIn, company websites, press releases, business publications
- Format source_urls as: ["https://url1.com", "https://url2.com"]

Focus on verification through multiple sources and include all relevant URLs."""

    @staticmethod
    def get_succession_details_prompt(ceo_name: str, company_name: str, basic_info: Dict) -> str:
        """
        Stage 3: Succession and transition details.
        
        Focuses on circumstances around CEO appointment and departure.
        """
        
        return f"""You are researching succession details for {ceo_name} at {company_name}.

FOCUS: Circumstances around CEO appointment and any departure details.

Use web search to find information about:
- How/why this person became CEO
- Was succession planned or sudden?  
- Board connections or relationships
- Interim periods or transitions
- Departure circumstances (if applicable)
- Reason for leaving (if applicable)

Return ONLY valid JSON:

{{
    "succession_type": "planned/unplanned/emergency/interim or null",
    "succession_planned_unplanned": "planned/unplanned or null", 
    "succession_documentation": "true/false/null",
    "reason_for_succession": "why they became CEO or null",
    "interim_period": "true/false/null",
    "board_connection": "relationship to board or null",
    "departure_reason": "reason for leaving or null",
    "departure_voluntary": "true/false/null", 
    "was_forced_out": "true/false/null",
    "retirement_status": "true/false/null",
    "source_urls": ["url1", "url2"],
    "conflicting_data_notes": "any conflicting information found",
    "notes": "succession circumstances and context"
}}

Look for official announcements, board minutes, and press coverage of transitions."""

    @staticmethod
    def get_post_ceo_details_prompt(ceo_name: str, company_name: str, basic_info: Dict) -> str:
        """
        Stage 4: Post-CEO career and verification.
        
        Final stage focusing on post-CEO activities and data verification.
        """
        
        return f"""You are researching post-CEO career details for {ceo_name} at {company_name}.

FOCUS: What happened after CEO role and final data verification.

Use web search to find:
- Next role or position after CEO
- Board directorships or other positions
- Age at departure (if available)
- Whether had job lined up
- Geographic moves for next role

Also verify and assess data quality:
- Source accessibility issues
- Data precision levels  
- Alternative verification sources

Return ONLY valid JSON:

{{
    "post_ceo_role": "next role after CEO or null",
    "next_company": "company of next role or null", 
    "director_of_some_company": "director positions or null",
    "no_real_job": "true/false/null",
    "age_at_departure": "age when left CEO role or null",
    "geographic_relocation": "moved for next role or null",
    "career_advancement_decline": "trajectory assessment or null",
    "source_accessibility_issues": "problems accessing sources or null",
    "alternative_verification_paths": ["alternative sources"],
    "data_precision_level": "exact/month-year/year-only",
    "timeline_conflicts": "timeline inconsistencies or null", 
    "source_urls": ["url1", "url2"],
    "notes": "post-CEO activities and data quality assessment"
}}

Priority: Accuracy over completeness. Mark uncertain information clearly."""

    @staticmethod
    def get_comprehensive_single_prompt(ceo_name: str, company_name: str) -> str:
        """
        Alternative: Single comprehensive prompt (simplified version of your original).
        
        Use this when you want all data in one pass, but with reduced complexity
        compared to your original comprehensive prompt.
        """
        
        return f"""You are a financial researcher gathering executive information for {ceo_name} at {company_name}.

SCOPE: U.S. banks and bank holding companies, CEO transitions from 1980 to present.

CRITICAL CLASSIFICATION:
- INSIDER: Promoted from within (worked at company before CEO)
- OUTSIDER: Hired from outside (first role at company was CEO)  

Use web search extensively. Prioritize:
1. SEC filings, regulatory filings, proxy statements
2. Official press releases  
3. Trade journals (American Banker, Bank Director)
4. Official bank websites
5. Other credible sources (must cite URLs)

Return ONLY valid JSON with ALL available fields:

{{
    "ceo_name": "{ceo_name}",
    "company_name": "{company_name}", 
    "ceo_title": "string or null",
    "insider_outsider": "insider/outsider/unknown",
    "insider_outsider_confidence": "HIGH/MEDIUM/LOW/CONFLICTING",
    "appointment_date": "MM/DD/YYYY or null",
    "start_date": "MM/DD/YYYY or null", 
    "departure_date": "MM/DD/YYYY or 'incumbent'",
    "tenure_years": "number (decimal allowed) or null",
    "initial_join_year": "YYYY or null",
    "years_before_ceo": "number (decimal allowed) or null",
    
    "previous_company": "OUTSIDERS: external company; INSIDERS: null",
    "previous_position": "OUTSIDERS: external role; INSIDERS: last internal role",
    "last_position_before_ceo": "for insiders: Board Member/President/Chairman/Other Executive",
    
    "predecessor_name": "string or null",
    "successor_name": "string or null",
    "succession_type": "string or null",
    "departure_reason": "string or null", 
    "departure_voluntary": "true/false/null",
    "post_ceo_role": "string or null",
    
    "data_completeness": "high/medium/low",
    "confidence_score": "0.0 to 1.0", 
    "primary_sources": ["source descriptions"],
    "source_urls": ["direct URLs - REQUIRED for verification"],
    "last_updated": "{datetime.now().strftime('%m/%d/%Y')}",
    "notes": "key findings, conflicts, or caveats"
}}

CRITICAL VERIFICATION REQUIREMENTS:
- Every fact must be verifiable from cited sources
- source_urls field MUST contain direct URLs for ALL sources accessed
- MINIMUM 5 sources required for comprehensive research
- Include SEC filings, press releases, company websites, business publications
- Mark conflicting information clearly in conflicting_data_notes
- Distinguish between announcement vs. effective dates
- Note data precision level (exact/month-year/year-only)

SOURCE URL FORMAT:
- ["https://www.sec.gov/filing123", "https://company.com/press-release", "https://news.com/article"]
- Each URL must directly support the facts you found
- Include the exact pages you accessed during web search

Return ONLY the JSON object with comprehensive source_urls."""

    @staticmethod
    def get_prompt_by_stage(stage: str, ceo_name: str, company_name: str, basic_info: Optional[Dict] = None) -> str:
        """
        Get prompt for specific research stage.
        
        Args:
            stage: Research stage ('basic', 'insider_career', 'outsider_career', 
                   'succession', 'post_ceo', 'comprehensive')
            ceo_name: CEO name
            company_name: Company name  
            basic_info: Results from basic info stage (for subsequent stages)
            
        Returns:
            Formatted prompt string
        """
        
        prompts = {
            'basic': CEOResearchPrompts.get_basic_info_prompt,
            'insider_career': CEOResearchPrompts.get_insider_career_details_prompt, 
            'outsider_career': CEOResearchPrompts.get_outsider_career_details_prompt,
            'succession': CEOResearchPrompts.get_succession_details_prompt,
            'post_ceo': CEOResearchPrompts.get_post_ceo_details_prompt,
            'comprehensive': CEOResearchPrompts.get_comprehensive_single_prompt
        }
        
        if stage not in prompts:
            raise ValueError(f"Unknown stage: {stage}. Available: {list(prompts.keys())}")
            
        if stage in ['basic', 'comprehensive']:
            return prompts[stage](ceo_name, company_name)
        else:
            if basic_info is None:
                raise ValueError(f"Stage '{stage}' requires basic_info from previous stage")
            return prompts[stage](ceo_name, company_name, basic_info)

    @staticmethod
    def get_recommended_sequence() -> List[str]:
        """
        Get recommended sequence of research stages.
        
        Returns:
            List of stage names in recommended order
        """
        return ['basic', 'career_details', 'succession', 'post_ceo']
        
    @staticmethod
    def should_use_insider_or_outsider_career(basic_info: Dict) -> str:
        """
        Determine whether to use insider or outsider career prompt based on classification.
        
        Args:
            basic_info: Results from basic info stage
            
        Returns:
            'insider_career' or 'outsider_career' or 'skip' if unknown
        """
        classification = basic_info.get('insider_outsider', '').lower()
        
        if classification == 'insider':
            return 'insider_career'
        elif classification == 'outsider': 
            return 'outsider_career'
        else:
            return 'skip'  # Skip detailed career analysis if classification is unknown