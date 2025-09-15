"""
Web Fetch Utility

This module provides web content fetching using actual HTTP requests.
Since MCP tools are not available in Python, we use the aiohttp library.
"""

from typing import Optional
import asyncio
import aiohttp
from .logger import get_logger
from .playwright_tools import playwright_fetch

logger = get_logger(__name__)


async def web_fetch_tool(url: str) -> str:
    """
    Fetch content from a URL using HTTP requests.

    Since we don't have access to MCP tools from Python, this implementation
    uses aiohttp to fetch web content directly.

    Args:
        url: The URL to fetch content from

    Returns:
        The text content from the URL, or empty string on failure
    """
    try:
        logger.info(f"Fetching content from URL: '{url}'")

        # Validate URL format
        if not url or not isinstance(url, str):
            logger.error(f"Invalid URL provided: {url}")
            return ""

        if not url.startswith(('http://', 'https://')):
            logger.error(f"URL must start with http:// or https://: {url}")
            return ""

        # First try regular HTTP fetch with aiohttp
        content = ""

        async with aiohttp.ClientSession() as session:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        if content:
                            content = extract_main_content(content)
                            logger.info(f"HTTP fetch got {len(content)} characters from {url}")
                            return content
                    elif response.status in [401, 403, 429]:
                        logger.warning(f"HTTP fetch blocked with {response.status}, trying Playwright")
                    else:
                        logger.warning(f"HTTP fetch failed with {response.status}")

            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                logger.warning(f"HTTP fetch failed: {e}, trying Playwright")
            except Exception as e:
                logger.error(f"HTTP fetch error: {e}")

        # If regular fetch failed, try Playwright
        if not content:
            logger.info(f"Falling back to Playwright for {url}")
            try:
                content = await playwright_fetch(url)
                if content:
                    logger.info(f"Playwright fetch got {len(content)} characters")
                    return content
            except Exception as e:
                logger.error(f"Playwright fetch also failed: {e}")

        return ""

    except Exception as e:
        logger.error(f"Error fetching content from URL '{url}': {str(e)}")
        return ""


def clean_and_format_content(raw_content: str) -> str:
    """
    Clean and format raw HTML content.

    Args:
        raw_content: Raw HTML content from web page

    Returns:
        Cleaned and formatted text content
    """
    try:
        if not raw_content or not isinstance(raw_content, str):
            return ""

        # Remove HTML tags (simple implementation)
        import re

        # Remove script and style elements
        content = re.sub(r'<script[^>]*>.*?</script>', '', raw_content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML tags
        content = re.sub(r'<[^>]+>', ' ', content)

        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)

        # Decode HTML entities
        import html
        content = html.unescape(content)

        # Trim and limit content
        content = content.strip()

        # Limit content length to prevent excessive memory usage
        max_content_length = 50000  # 50KB limit
        if len(content) > max_content_length:
            content = content[:max_content_length] + "...\n[Content truncated]"
            logger.warning(f"Content truncated to {max_content_length} characters")

        logger.info(f"Cleaned content: {len(content)} characters")
        return content

    except Exception as e:
        logger.error(f"Error cleaning content: {str(e)}")
        return ""


def extract_main_content(html_content: str) -> str:
    """
    Extract main content from HTML.

    Args:
        html_content: Full HTML content from web page

    Returns:
        Extracted main text content
    """
    try:
        if not html_content:
            return ""

        # For CEO research, look for biographical and professional information
        import re

        # Extract title if present
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
        title = title_match.group(1) if title_match else ""

        # Extract meta description
        desc_match = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', html_content, re.IGNORECASE)
        description = desc_match.group(1) if desc_match else ""

        # Extract main content areas (article, main, body text)
        content_patterns = [
            r'<article[^>]*>(.*?)</article>',
            r'<main[^>]*>(.*?)</main>',
            r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*id="[^"]*content[^"]*"[^>]*>(.*?)</div>',
        ]

        main_content = ""
        for pattern in content_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            if matches:
                main_content += " ".join(matches)
                break

        # If no specific content areas found, use cleaned body content
        if not main_content:
            body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
            if body_match:
                main_content = body_match.group(1)

        # Combine title, description, and main content
        combined_content = f"{title}\n\n{description}\n\n{main_content}" if main_content else html_content

        # Clean and format the combined content
        return clean_and_format_content(combined_content)

    except Exception as e:
        logger.error(f"Error extracting main content: {str(e)}")
        return clean_and_format_content(html_content)  # Fall back to basic cleaning