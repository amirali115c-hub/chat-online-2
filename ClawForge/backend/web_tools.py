"""
Web Search Module for ClawForge
Provides web search and fetch capabilities using Brave Search API.
"""

import requests
from typing import List, Dict, Any
import os

# Brave Search API configuration
BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "")
BRAVE_SEARCH_URL = "https://api.search.brave.com/v1/web/search"


def web_search(query: str, count: int = 10, 
               country: str = "US", 
               search_lang: str = "en",
               freshness: str = None) -> List[Dict[str, Any]]:
    """
    Search the web using Brave Search API.
    
    Args:
        query: Search query string
        count: Number of results (1-10)
        country: 2-letter country code
        search_lang: ISO language code
        freshness: Filter by discovery time ('pd', 'pw', 'pm', 'py')
    
    Returns:
        List of search results with title, url, and snippet
    """
    if not BRAVE_API_KEY:
        # Return mock results if no API key
        return [
            {
                "title": f"Search results for: {query}",
                "url": f"https://www.google.com/search?q={query.replace(' ', '+')}",
                "description": f"Web search results for '{query}'. Configure BRAVE_API_KEY for real search.",
                "snippet": "Configure Brave Search API key for live web search."
            }
        ]
    
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    
    params = {
        "q": query,
        "count": min(count, 10),
        "country": country,
        "search_lang": search_lang,
        "text_decorations": "false",
        "summary": "true"
    }
    
    if freshness:
        params["freshness"] = freshness
    
    try:
        response = requests.get(BRAVE_SEARCH_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
                "snippet": item.get("description", ""),
                "published_at": item.get("published_at", "")
            })
        
        return results
    except Exception as e:
        return [{"error": str(e)}]


def web_fetch(url: str, extract_mode: str = "markdown", max_chars: int = 50000) -> str:
    """
    Fetch and extract readable content from a URL.
    
    Args:
        url: HTTP or HTTPS URL to fetch
        extract_mode: "markdown" or "text"
        max_chars: Maximum characters to return
    
    Returns:
        Extracted content as markdown or text
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        # Simple extraction - get text content
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Remove scripts and styles
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator="\n")
        
        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        content = "\n".join(lines)
        
        # Truncate if needed
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n... [truncated]"
        
        if extract_mode == "text":
            return content
        
        # Convert to simple markdown
        markdown = content
        
        return markdown
        
    except Exception as e:
        return f"Error fetching URL: {str(e)}"


def search_and_summarize(query: str, num_results: int = 3) -> Dict[str, Any]:
    """
    Search the web and get a summary.
    
    Args:
        query: Search query
        num_results: Number of results to fetch
    
    Returns:
        Dictionary with query, results, and summary
    """
    results = web_search(query, count=num_results)
    
    summary = f"Found {len(results)} results for '{query}'.\n\n"
    for i, result in enumerate(results, 1):
        summary += f"{i}. {result.get('title', 'No title')}\n"
        summary += f"   URL: {result.get('url', 'No URL')}\n"
        if result.get('snippet'):
            summary += f"   {result['snippet'][:200]}...\n"
        summary += "\n"
    
    return {
        "query": query,
        "results": results,
        "summary": summary
    }
