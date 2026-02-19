"""
WebTools - FREE Web Search & Information Retrieval
==================================================
Uses DuckDuckGo for web search (no paid APIs required).
"""

import os
import json
import time
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error

# Try to import optional dependencies
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    from duckduckgo_search import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False


class WebTools:
    """
    FREE web search and information retrieval tools.
    
    Features:
    - DuckDuckGo search (free)
    - Web page fetching and parsing
    - Wikipedia lookup
    - Current date/time
    - Rate limiting (respectful to free services)
    """
    
    def __init__(
        self,
        cache_dir: str = "./data/cache",
        rate_limit_delay: float = 2.0,  # seconds between requests
        timeout: int = 30,
        user_agent: str = "ClawForge/1.0"
    ):
        """
        Initialize WebTools.
        
        Args:
            cache_dir: Directory for caching results
            rate_limit_delay: Delay between web requests (seconds)
            timeout: Request timeout
            user_agent: User agent string
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.rate_limit_delay = rate_limit_delay
        self.timeout = timeout
        self.user_agent = user_agent
        
        self._last_request_time = 0
        self._request_count = 0
        self._daily_limit = 1000  # Reasonable daily limit
        
    def _rate_limit(self) -> None:
        """Enforce rate limiting."""
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        
        self._last_request_time = time.time()
        self._request_count += 1
    
    def _get_cache_path(self, query: str, operation: str) -> Path:
        """Generate cache file path."""
        query_hash = hashlib.md5(query.encode()).hexdigest()[:16]
        return self.cache_dir / f"{operation}_{query_hash}.json"
    
    def _get_cached(self, query: str, operation: str, max_age_hours: int = 24) -> Optional[Dict]:
        """Get cached result if valid."""
        cache_path = self._get_cache_path(query, operation)
        
        if cache_path.exists():
            age_hours = (datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)).total_seconds() / 3600
            if age_hours < max_age_hours:
                with open(cache_path, 'r') as f:
                    return json.load(f)
        return None
    
    def _save_cache(self, query: str, operation: str, data: Dict) -> None:
        """Save result to cache."""
        cache_path = self._get_cache_path(query, operation)
        with open(cache_path, 'w') as f:
            json.dump(data, f, default=str)
    
    # ==================== SEARCH ====================
    
    def search(
        self,
        query: str,
        max_results: int = 10,
        use_cache: bool = True,
        timeout: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Search the web using DuckDuckGo (FREE).
        
        Args:
            query: Search query
            max_results: Maximum number of results
            use_cache: Use cached results if available
            timeout: Request timeout (overrides default)
            
        Returns:
            List of search results with title, url, and snippet
        """
        # Check cache
        if use_cache:
            cached = self._get_cached(query, "search")
            if cached:
                return cached.get("results", [])[:max_results]
        
        self._rate_limit()
        
        results = []
        
        if HAS_DDGS:
            # Use official duckduckgo-search library
            try:
                with DDGS() as ddgs:
                    for r in ddgs.text(query, max_results=max_results):
                        results.append({
                            "title": r.get("title", ""),
                            "url": r.get("href", ""),
                            "snippet": r.get("body", ""),
                            "engine": "duckduckgo"
                        })
            except Exception as e:
                print(f"DuckDuckGo search error: {e}")
                # Fall back to manual search
                results = self._manual_search(query, max_results)
        else:
            # Fall back to manual search
            results = self._manual_search(query, max_results)
        
        # Cache and return
        if use_cache and results:
            self._save_cache(query, "search", {
                "results": results,
                "timestamp": datetime.now().isoformat(),
                "query": query
            })
        
        return results
    
    def _manual_search(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """Manual search using DuckDuckGo HTML (fallback)."""
        if not HAS_REQUESTS:
            return [{"error": "requests library not installed"}]
        
        search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        
        try:
            response = requests.get(
                search_url,
                headers={"User-Agent": self.user_agent},
                timeout=self.timeout or self.timeout
            )
            
            if HAS_BS4:
                soup = BeautifulSoup(response.text, "html.parser")
                
                for result in soup.select(".result")[:max_results]:
                    title_elem = result.select_one(".result__a")
                    url_elem = result.select_one(".result__url")
                    snippet_elem = result.select_one(".result__snippet")
                    
                    if title_elem:
                        results.append({
                            "title": title_elem.get_text(strip=True),
                            "url": url_elem.get_text(strip=True) if url_elem else "",
                            "snippet": snippet_elem.get_text(strip=True) if snippet_elem else "",
                            "engine": "duckduckgo-html"
                        })
            else:
                return [{"error": "beautifulsoup4 not installed"}]
                
        except Exception as e:
            return [{"error": str(e)}]
        
        return results
    
    def search_news(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """Search for news articles."""
        return self.search(f"{query} news", max_results)
    
    def search_images(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """Search for images."""
        # DuckDuckGo doesn't provide direct image search API
        # Return web results that might have images
        results = self.search(query, max_results)
        for r in results:
            r["type"] = "image_search_hint"
        return results
    
    # ==================== FETCH PAGE ====================
    
    def fetch_page(
        self,
        url: str,
        use_cache: bool = True,
        extract_text: bool = True,
        max_chars: int = 10000
    ) -> Dict[str, Any]:
        """
        Fetch and parse a web page.
        
        Args:
            url: Page URL to fetch
            use_cache: Use cached version if available
            extract_text: Extract main text content
            max_chars: Maximum characters to return
            
        Returns:
            Dict with url, title, text, links, images, etc.
        """
        if not HAS_REQUESTS:
            return {"error": "requests library not installed"}
        
        # Check cache
        if use_cache:
            cached = self._get_cached(url, "fetch")
            if cached:
                return cached
        
        self._rate_limit()
        
        result = {
            "url": url,
            "title": "",
            "text": "",
            "links": [],
            "images": [],
            "headers": {},
            "status_code": 0,
            "fetched_at": datetime.now().isoformat()
        }
        
        try:
            response = requests.get(
                url,
                headers={"User-Agent": self.user_agent},
                timeout=self.timeout or self.timeout
            )
            
            result["status_code"] = response.status_code
            result["headers"] = dict(response.headers)
            
            if HAS_BS4:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Extract title
                title_tag = soup.find("title")
                result["title"] = title_tag.get_text(strip=True) if title_tag else ""
                
                # Remove unwanted elements
                for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
                    tag.decompose()
                
                # Extract text
                if extract_text:
                    text = soup.get_text(separator="\n")
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    result["text"] = "\n".join(lines)[:max_chars]
                
                # Extract links
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if href.startswith("http"):
                        result["links"].append({
                            "url": href,
                            "text": a.get_text(strip=True)[:100]
                        })
                
                # Extract images
                for img in soup.find_all("img", src=True):
                    src = img["src"]
                    if src.startswith("http"):
                        result["images"].append({
                            "url": src,
                            "alt": img.get("alt", "")[:100]
                        })
            
            # Cache result
            if use_cache:
                self._save_cache(url, "fetch", result)
                
        except requests.exceptions.Timeout:
            result["error"] = "Request timed out"
        except requests.exceptions.RequestException as e:
            result["error"] = str(e)
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def extract_main_content(self, url: str) -> str:
        """Extract main article content from a URL."""
        page = self.fetch_page(url)
        return page.get("text", page.get("error", ""))
    
    # ==================== WIKIPEDIA ====================
    
    def wikipedia_summary(self, topic: str, use_cache: bool = True) -> str:
        """
        Get Wikipedia summary for a topic.
        
        Args:
            topic: Topic to look up
            use_cache: Use cached results
            
        Returns:
            Wikipedia article summary
        """
        if not HAS_REQUESTS:
            return "requests library not installed"
        
        # Check cache
        if use_cache:
            cached = self._get_cached(topic, "wikipedia")
            if cached:
                return cached.get("summary", "")
        
        topic_normalized = topic.replace(" ", "_")
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic_normalized}"
        
        try:
            response = requests.get(api_url, timeout=self.timeout)
            data = response.json()
            
            summary = data.get("extract", "No article found.")
            
            # Cache result
            if use_cache:
                self._save_cache(topic, "wikipedia", {
                    "summary": summary,
                    "title": data.get("title", topic),
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
                })
            
            return summary
            
        except Exception as e:
            return f"Wikipedia lookup failed: {e}"
    
    def wikipedia_search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Search Wikipedia for topics."""
        if not HAS_REQUESTS:
            return [{"error": "requests library not installed"}]
        
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": max_results
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=self.timeout)
            data = response.json()
            
            results = []
            for item in data.get("query", {}).get("search", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", "") + "...",
                    "url": f"https://en.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}",
                    "pageid": str(item.get("pageid", ""))
                })
            
            return results
            
        except Exception as e:
            return [{"error": str(e)}]
    
    # ==================== CURRENT DATETIME ====================
    
    def get_current_datetime(
        self,
        format: str = "full",
        timezone: str = "local"
    ) -> Dict[str, str]:
        """
        Get current date and time.
        
        Args:
            format: 'full', 'date', 'time', 'iso'
            timezone: 'local' or 'utc'
            
        Returns:
            Dict with various time formats
        """
        if timezone == "utc":
            now = datetime.utcnow()
        else:
            now = datetime.now()
        
        return {
            "full": now.strftime("%A, %B %d %Y at %I:%M:%S %p"),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%I:%M:%S %p"),
            "iso": now.isoformat(),
            "unix": str(int(now.timestamp())),
            "weekday": now.strftime("%A"),
            "month": now.strftime("%B"),
            "year": str(now.year),
            "timezone": timezone
        }
    
    # ==================== UTILITY TOOLS ====================
    
    def whois_lookup(self, domain: str) -> Dict[str, str]:
        """Basic WHOIS-like information (limited, no paid API)."""
        return {
            "domain": domain,
            "note": "Full WHOIS requires paid API or service",
            "suggestion": "Use whois.domaintools.com or similar free service"
        }
    
    def get_page_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from a page."""
        page = self.fetch_page(url, extract_text=False)
        
        return {
            "url": url,
            "title": page.get("title", ""),
            "links_count": len(page.get("links", [])),
            "images_count": len(page.get("images", [])),
            "status": page.get("status_code", 0),
            "content_type": page.get("headers", {}).get("Content-Type", ""),
            "fetched_at": page.get("fetched_at", "")
        }
    
    def compare_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Compare multiple URLs."""
        return [self.get_page_metadata(url) for url in urls]
    
    def extract_text_from_pdf(self, url: str) -> str:
        """
        Extract text from PDF URL.
        Requires pypdf or similar.
        """
        # Note: Full PDF extraction requires additional libraries
        return "PDF extraction requires pypdf library. Install: pip install pypdf"
    
    # ==================== BATCH OPERATIONS ====================
    
    def batch_search(
        self,
        queries: List[str],
        max_results: int = 5,
        delay_between: float = 3.0
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Search multiple queries.
        
        Args:
            queries: List of search queries
            max_results: Results per query
            delay_between: Delay between searches
            
        Returns:
            Dict mapping queries to results
        """
        results = {}
        original_delay = self.rate_limit_delay
        
        for query in queries:
            self.rate_limit_delay = delay_between
            results[query] = self.search(query, max_results)
        
        self.rate_limit_delay = original_delay
        return results
    
    def batch_fetch(
        self,
        urls: List[str],
        delay_between: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Fetch multiple URLs.
        
        Args:
            urls: List of URLs to fetch
            delay_between: Delay between fetches
            
        Returns:
            List of page results
        """
        results = []
        original_delay = self.rate_limit_delay
        
        for url in urls:
            self.rate_limit_delay = delay_between
            results.append(self.fetch_page(url))
        
        self.rate_limit_delay = original_delay
        return results
    
    # ==================== STATS & MAINTENANCE ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get WebTools statistics."""
        cache_files = list(self.cache_dir.glob("*.json"))
        cache_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "cache_dir": str(self.cache_dir),
            "cached_files": len(cache_files),
            "cache_size_mb": round(cache_size / (1024 * 1024), 2),
            "requests_made": self._request_count,
            "features": {
                "search": HAS_DDGS or HAS_REQUESTS,
                "page_fetch": HAS_REQUESTS,
                "html_parsing": HAS_BS4,
                "wikipedia": HAS_REQUESTS
            }
        }
    
    def clear_cache(self, older_than_hours: int = 24) -> int:
        """
        Clear cached results.
        
        Args:
            older_than_hours: Clear cache older than this
            
        Returns:
            Number of files deleted
        """
        deleted = 0
        cutoff = datetime.now().timestamp() - (older_than_hours * 3600)
        
        for cache_file in self.cache_dir.glob("*.json"):
            if cache_file.stat().st_mtime < cutoff:
                cache_file.unlink()
                deleted += 1
        
        return deleted


# Example usage
if __name__ == "__main__":
    # Initialize
    web = WebTools()
    
    # Search
    print("=== Search Results ===")
    results = web.search("Python web scraping", max_results=3)
    for r in results:
        print(f"- {r.get('title', 'No title')}")
        print(f"  {r.get('url', '')}")
    
    # Fetch page
    print("\n=== Fetch Page ===")
    page = web.fetch_page("https://en.wikipedia.org/wiki/Python_(programming_language)")
    print(f"Title: {page.get('title', 'No title')}")
    print(f"Text (first 200 chars): {page.get('text', '')[:200]}...")
    
    # Wikipedia
    print("\n=== Wikipedia ===")
    summary = web.wikipedia_summary("Machine learning")
    print(f"Summary: {summary[:200]}...")
    
    # DateTime
    print("\n=== DateTime ===")
    dt = web.get_current_datetime()
    print(f"Full: {dt['full']}")
    print(f"ISO: {dt['iso']}")
    
    # Stats
    print("\n=== Stats ===")
    stats = web.get_stats()
    print(f"Cached files: {stats['cached_files']}")
    print(f"Cache size: {stats['cache_size_mb']} MB")
