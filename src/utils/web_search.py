"""Web search and website testing utilities for Maverick AI."""

import httpx
import logging
import asyncio
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from src.utils.config import settings

logger = logging.getLogger(__name__)

class WebSearchTool:
    """Utility to perform web searches and fetch website content."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.serper_api_key
        self.base_url = "https://google.serper.dev/search"
    
    async def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Perform a Google search via Serper API."""
        if not self.api_key or self.api_key == "YOUR_SERPER_API_KEY_HERE":
            logger.warning("Serper API key not configured")
            return []
            
        logger.info(f"Searching the internet for: '{query}'")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "X-API-KEY": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "q": query,
                        "num": num_results
                    },
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Serper API failed: {response.status_code}")
                    return []
                
                data = response.json()
                results = []
                for item in data.get("organic", []):
                    results.append({
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "snippet": item.get("snippet"),
                        "source": "google_search"
                    })
                return results
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []

    async def fetch_website_content(self, url: str, max_chars: int = 5000) -> Dict:
        """Fetch and clean content from a website."""
        logger.info(f"Fetching content from: {url}")
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, timeout=15.0, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                })
                
                if response.status_code != 200:
                    return {"url": url, "error": f"Failed to fetch: {response.status_code}", "status": "error"}
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Remove script and style elements
                for script in soup(["script", "style", "header", "footer", "nav"]):
                    script.extract()
                
                # Get text
                text = soup.get_text(separator=' ')
                
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                # Truncate
                if len(text) > max_chars:
                    text = text[:max_chars] + "... [Content Truncated]"
                
                return {
                    "url": url,
                    "title": soup.title.string if soup.title else "No Title",
                    "content": text,
                    "status": "success"
                }
        except Exception as e:
            logger.error(f"Error fetching website {url}: {e}")
            return {"url": url, "error": str(e), "status": "error"}

    async def test_website(self, url: str) -> Dict:
        """Test a website for basic availability and metadata."""
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                start_time = asyncio.get_event_loop().time()
                response = await client.get(url, timeout=10.0)
                end_time = asyncio.get_event_loop().time()
                
                latency = round((end_time - start_time) * 1000, 2)
                
                return {
                    "url": url,
                    "status_code": response.status_code,
                    "latency_ms": latency,
                    "is_online": response.status_code == 200,
                    "status": "success"
                }
        except Exception as e:
            return {
                "url": url,
                "is_online": False,
                "error": str(e),
                "status": "error"
            }
