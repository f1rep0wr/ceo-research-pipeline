"""
Web Tools Module

This module provides a simple wrapper for web search and content fetching capabilities.
The WebTools class is designed to integrate with real web search and fetch tools.

CRITICAL: This module MUST return REAL search results and NEVER generate fake URLs.
All search results and fetched content must come from actual web sources.
"""

from typing import List, Dict, Any
import asyncio
from src.config.settings import Settings
from src.utils.logger import get_logger
from src.utils.web_search import web_search_tool, format_search_results
from src.utils.web_fetch import web_fetch_tool, extract_main_content


class WebTools:
    """
    Web Tools class for search and content fetching operations.

    This is a simple wrapper that will integrate with actual web search and fetch tools.
    All methods MUST use real web services and return actual results.
    """

    def __init__(self, settings: Settings):
        """
        Initialize WebTools with settings.

        Args:
            settings: Application settings configuration
        """
        self.settings = settings
        self.logger = get_logger(__name__)

    async def search_web(self, query: str) -> List[Dict[str, Any]]:
        """
        Search the web for the given query and return real results.

        IMPORTANT: This method integrates with actual web search tools
        and returns REAL search results. Never generates fake URLs or content.

        Args:
            query: The search query string

        Returns:
            List of search results with structure:
            [{'url': str, 'title': str, 'snippet': str}, ...]
        """
        self.logger.info(f"WebTools.search_web called with query: '{query}'")

        try:
            # Use the web search utility to get real search results
            results = await web_search_tool(query)

            if results:
                self.logger.info(f"Successfully retrieved {len(results)} search results")
            else:
                self.logger.warning(f"No search results found for query: '{query}'")

            return results

        except Exception as e:
            self.logger.error(f"Error in search_web for query '{query}': {str(e)}")
            return []

    async def fetch_content(self, url: str) -> str:
        """
        Fetch content from the given URL.

        IMPORTANT: This method integrates with actual web fetch tools
        and returns REAL content from the specified URL.

        Args:
            url: The URL to fetch content from

        Returns:
            The text content from the URL
        """
        self.logger.info(f"WebTools.fetch_content called with URL: '{url}'")

        try:
            # Use the web fetch utility to get real content
            raw_content = await web_fetch_tool(url)

            if raw_content:
                # Extract and clean the main content
                content = extract_main_content(raw_content)
                self.logger.info(f"Successfully fetched content from URL: {len(content)} characters")
                return content
            else:
                self.logger.warning(f"No content retrieved from URL: '{url}'")
                return ""

        except Exception as e:
            self.logger.error(f"Error in fetch_content for URL '{url}': {str(e)}")
            return ""