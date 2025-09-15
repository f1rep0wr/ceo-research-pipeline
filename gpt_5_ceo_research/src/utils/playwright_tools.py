"""
Playwright-based Web Tools

Simple, robust web scraping using Playwright as a fallback for failed HTTP requests.
Integrates seamlessly with existing WebTools interface.
"""

from typing import List, Dict, Any, Optional
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import quote
from .logger import get_logger

logger = get_logger(__name__)

# Global browser instance for reuse
_browser_instance = None
_playwright_instance = None


async def get_browser():
    """Get or create a global browser instance."""
    global _browser_instance, _playwright_instance

    if _browser_instance is None:
        try:
            logger.info("Starting Playwright browser")
            _playwright_instance = await async_playwright().start()
            _browser_instance = await _playwright_instance.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            logger.info("Playwright browser started")
        except Exception as e:
            logger.error(f"Failed to start Playwright: {e}")
            return None

    return _browser_instance


async def playwright_search(query: str) -> List[Dict[str, Any]]:
    """
    Search using Playwright when regular search fails.
    Simple Google search that extracts URLs and titles.

    Args:
        query: Search query

    Returns:
        List of search results with url, title, snippet
    """
    browser = await get_browser()
    if not browser:
        return []

    page = None
    try:
        logger.info(f"Playwright search for: {query}")

        # Create new page
        page = await browser.new_page()

        # Go to Google search
        search_url = f"https://www.google.com/search?q={quote(query)}"
        await page.goto(search_url, timeout=15000)

        # Wait a bit for results to load
        await page.wait_for_timeout(2000)

        # Get page content
        html = await page.content()

        # Parse with BeautifulSoup (more reliable than JS evaluation)
        soup = BeautifulSoup(html, 'lxml')

        results = []

        # Find search result divs
        for g in soup.find_all('div', class_='g'):
            # Find link
            link_elem = g.find('a', href=True)
            if not link_elem:
                continue

            url = link_elem['href']

            # Skip Google's own URLs
            if 'google.com' in url or url.startswith('/'):
                continue

            # Find title (usually in h3)
            title_elem = g.find('h3')
            title = title_elem.text if title_elem else 'No title'

            # Find snippet (various possible locations)
            snippet = ''
            for selector in ['span', 'div']:
                snippet_elem = g.find(selector, class_=lambda x: x and 'st' in x.lower() if x else False)
                if snippet_elem:
                    snippet = snippet_elem.text
                    break

            if not snippet:
                # Try to get any text content as snippet
                text_elems = g.find_all(text=True)
                snippet = ' '.join(text_elems[:3])[:200]

            results.append({
                'url': url,
                'title': title,
                'snippet': snippet[:500]  # Limit snippet length
            })

            if len(results) >= 10:
                break

        logger.info(f"Playwright found {len(results)} results")
        return results

    except Exception as e:
        logger.error(f"Playwright search error: {e}")
        return []
    finally:
        if page:
            try:
                await page.close()
            except:
                pass


async def playwright_fetch(url: str) -> str:
    """
    Fetch page content using Playwright when regular fetch fails.

    Args:
        url: URL to fetch

    Returns:
        Page text content
    """
    browser = await get_browser()
    if not browser:
        return ""

    page = None
    try:
        logger.info(f"Playwright fetch: {url}")

        # Create new page
        page = await browser.new_page()

        # Navigate to URL
        response = await page.goto(url, timeout=20000, wait_until='domcontentloaded')

        if not response or response.status >= 400:
            logger.warning(f"Bad response status: {response.status if response else 'None'}")
            return ""

        # Wait a bit for dynamic content
        await page.wait_for_timeout(2000)

        # Get page content
        html = await page.content()

        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')

        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'noscript']):
            tag.decompose()

        # Special handling for Wikipedia
        if 'wikipedia.org' in url:
            # Find main content area
            content_div = soup.find('div', id='mw-content-text')
            if content_div:
                # Remove infoboxes, navboxes, etc
                for unwanted in content_div.find_all(['table', 'div'], class_=['infobox', 'navbox', 'metadata']):
                    unwanted.decompose()

                # Get text from paragraphs
                paragraphs = content_div.find_all('p')
                text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs)
                return text[:50000]

        # Generic text extraction
        text = soup.get_text(separator='\n', strip=True)

        # Clean up excessive whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)

        # Limit size
        return text[:50000]

    except Exception as e:
        logger.error(f"Playwright fetch error for {url}: {e}")
        return ""
    finally:
        if page:
            try:
                await page.close()
            except:
                pass


async def cleanup_browser():
    """Clean up the global browser instance."""
    global _browser_instance, _playwright_instance

    if _browser_instance:
        try:
            await _browser_instance.close()
        except:
            pass
        _browser_instance = None

    if _playwright_instance:
        try:
            await _playwright_instance.stop()
        except:
            pass
        _playwright_instance = None