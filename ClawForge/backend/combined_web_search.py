"""
Combined Web Search Module for ClawForge
Uses both Brave API (when available) and DuckDuckGo HTML (free fallback)
Returns combined, deduplicated results for better coverage.
"""

import requests
import os
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import re

# Brave API configuration
BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "")
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

# DuckDuckGo configuration  
DUCK_DUCK_GO_URL = "https://html.duckduckgo.com/html/"


def extract_domain(url: str) -> str:
    """Extract domain from URL for deduplication."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower().replace("www.", "")
    except:
        return ""


def clean_text(text: str) -> str:
    """Clean HTML tags and whitespace from text."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Strip whitespace
    return text.strip()


def search_brave(query: str, count: int = 10, 
                 country: str = "US", 
                 search_lang: str = "en",
                 freshness: str = None) -> List[Dict[str, Any]]:
    """
    Search using Brave API.
    Returns empty list if API key not available.
    """
    if not BRAVE_API_KEY:
        return []
    
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    
    params = {
        "q": query,
        "count": min(count, 20),
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
                "published_at": item.get("published_at", ""),
                "source": "brave",
                "domain": extract_domain(item.get("url", ""))
            })
        
        return results
    except Exception as e:
        print(f"[WebSearch] Brave API error: {e}")
        return []


def search_duckduckgo(query: str, count: int = 10) -> List[Dict[str, Any]]:
    """
    Search using DuckDuckGo HTML (free, no API key).
    Uses curl-like requests with proper headers to avoid blocking.
    """
    import subprocess
    
    try:
        # Use curl via subprocess for better HTML handling
        result = subprocess.run([
            "curl", "-s", "--max-time", "15",
            "-X", "POST",
            "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "-H", "Accept: text/html",
            "-H", "Accept-Language: en-US,en;q=0.9",
            "-d", f"q={query}",
            DUCK_DUCK_GO_URL
        ], capture_output=True, text=True, timeout=20)
        
        html = result.stdout
        results = []
        
        # Parse DuckDuckGo HTML results
        # Pattern 1: Links with titles
        link_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
        # Pattern 2: Snippets
        snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>([^<]*)</a>'
        
        # Find all links and titles
        links = re.findall(link_pattern, html, re.IGNORECASE)
        snippets = re.findall(snippet_pattern, html, re.IGNORECASE)
        
        for i, (url, title) in enumerate(links):
            # Clean up URL (DuckDuckGo redirects through their own URL)
            if "uddg=" in url:
                try:
                    parsed = urlparse(url)
                    real_url = parsed.query.get("uddg", "")
                    if real_url:
                        url = real_url
                except:
                    pass
            
            # Skip if not a valid URL
            if not url.startswith("http"):
                continue
            
            # Get snippet if available
            description = snippets[i] if i < len(snippets) else ""
            description = clean_text(description)
            title = clean_text(title)
            
            if title and url:
                results.append({
                    "title": title,
                    "url": url,
                    "description": description,
                    "snippet": description,
                    "published_at": "",
                    "source": "duckduckgo",
                    "domain": extract_domain(url)
                })
        
        return results[:count]
        
    except Exception as e:
        print(f"[WebSearch] DuckDuckGo error: {e}")
        return []


def deduplicate_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate results based on domain and URL similarity."""
    seen_domains = set()
    seen_urls = set()
    unique_results = []
    
    for result in results:
        domain = result.get("domain", "").lower()
        url = result.get("url", "").lower()
        
        # Skip if exact URL seen
        if url in seen_urls:
            continue
        
        # Skip if multiple results from same domain (keep first only)
        if domain in seen_domains:
            continue
        
        seen_domains.add(domain)
        seen_urls.add(url)
        unique_results.append(result)
    
    return unique_results


def rank_results(results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Rank results by relevance to query."""
    query_words = set(query.lower().split())
    
    def score_result(result: Dict) -> int:
        score = 0
        title = result.get("title", "").lower()
        description = result.get("description", "").lower()
        
        # Check title for query words
        for word in query_words:
            if word in title:
                score += 10
        
        # Check description for query words
        for word in query_words:
            if word in description:
                score += 5
        
        # Prefer Brave results (usually higher quality)
        if result.get("source") == "brave":
            score += 2
        
        return score
    
    # Sort by score (descending)
    scored = [(score_result(r), r) for r in results]
    scored.sort(key=lambda x: -x[0])
    
    return [r for _, r in scored]


def combined_web_search(query: str, count: int = 10,
                       country: str = "US",
                       search_lang: str = "en",
                       freshness: str = None) -> Dict[str, Any]:
    """
    Combined web search using Brave API + DuckDuckGo.
    
    Strategy:
    1. If Brave API key available: Get Brave results
    2. Always get DuckDuckGo results (free fallback)
    3. Combine and deduplicate
    4. Rank by relevance
    5. Return best results
    
    Args:
        query: Search query
        count: Number of results to return (default 10)
        country: Country code for Brave
        search_lang: Language code for Brave
        freshness: Freshness filter for Brave (pd, pw, pm, py)
    
    Returns:
        Dictionary with status, results, and metadata
    """
    all_results = []
    sources_used = []
    
    # Step 1: Try Brave API (if key available)
    if BRAVE_API_KEY:
        brave_results = search_brave(query, count=count, country=country, 
                                    search_lang=search_lang, freshness=freshness)
        if brave_results:
            all_results.extend(brave_results)
            sources_used.append("brave")
            print(f"[WebSearch] Brave: Got {len(brave_results)} results")
    else:
        print("[WebSearch] No Brave API key - using DuckDuckGo only")
    
    # Step 2: Always get DuckDuckGo results (free fallback)
    ddg_results = search_duckduckgo(query, count=count)
    if ddg_results:
        all_results.extend(ddg_results)
        sources_used.append("duckduckgo")
        print(f"[WebSearch] DuckDuckGo: Got {len(ddg_results)} results")
    
    # Step 3: Deduplicate
    unique_results = deduplicate_results(all_results)
    print(f"[WebSearch] After deduplication: {len(unique_results)} results")
    
    # Step 4: Rank by relevance
    ranked_results = rank_results(unique_results, query)
    
    # Step 5: Return top N results
    final_results = ranked_results[:count]
    
    return {
        "status": "success",
        "query": query,
        "count": len(final_results),
        "sources": list(set(sources_used)),
        "results": final_results,
        "total_found": len(unique_results),
        "took_ms": 0  # Could add timing if needed
    }


def web_search_enhanced(query: str, count: int = 10) -> Dict[str, Any]:
    """
    Enhanced web search - main entry point.
    Uses combined Brave + DuckDuckGo search.
    """
    return combined_web_search(query=query, count=count)


def search_and_summarize(query: str, num_results: int = 5) -> Dict[str, Any]:
    """
    Search the web and get a summary.
    Returns combined results with brief summary.
    """
    results = combined_web_search(query, count=num_results * 2)  # Get more for combining
    
    # Create summary
    summary = f"Found {len(results.get('results', []))} results for '{query}'.\n\n"
    for i, result in enumerate(results.get("results", [])[:num_results], 1):
        summary += f"{i}. {result.get('title', 'No title')}\n"
        summary += f"   URL: {result.get('url', 'No URL')}\n"
        if result.get("snippet"):
            snippet = result["snippet"][:150]
            summary += f"   {snippet}...\n"
        summary += "\n"
    
    return {
        "query": query,
        "results": results.get("results", [])[:num_results],
        "summary": summary,
        "sources": results.get("sources", [])
    }
