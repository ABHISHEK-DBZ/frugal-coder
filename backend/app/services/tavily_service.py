import httpx
import logging
import ssl
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

class TavilyResearchService:
    """
    Dedicated Research Service integrating Tavily Search API.
    Provides verified web documentation, error solutions, and API references
    to enrich the Frugal Coder agent before code synthesis through Bifrost.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.base_url = (base_url or settings.TAVILY_BASE_URL).rstrip("/")
        # In case system cert store is missing local certs on Windows
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def is_configured(self) -> bool:
        """Checks if a valid Tavily API key is provided."""
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    @staticmethod
    def should_research(task_description: str) -> bool:
        """
        Determines whether external web research is needed for a task.
        Avoids unnecessary research (and token bloat) for simple or self-contained tasks.
        """
        desc = task_description.lower()
        research_keywords = [
            "deprecated", "migration", "migrate", "upgrade", "latest version",
            "documentation", "docs", "error", "exception", "traceback",
            "api reference", "how to use", "best practice", "vulnerability", "cve"
        ]
        return any(kw in desc for kw in research_keywords)

    async def search(
        self,
        query: str,
        max_results: int = 4,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Executes a real Tavily Search request.
        Returns curated sources, URLs, titles, and score metrics.
        """
        if not self.is_configured():
            logger.warning("Tavily API key is not configured. Web research skipped.")
            return {
                "query": query,
                "status": "unconfigured",
                "results": [],
                "error": "TAVILY_API_KEY not configured in backend environment."
            }

        endpoint = f"{self.base_url}/search"
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": min(max_results, 6),
            "search_depth": search_depth,
            "include_answer": True
        }
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains

        try:
            async with httpx.AsyncClient(verify=False, timeout=12.0) as client:
                res = await client.post(endpoint, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    results = []
                    for r in data.get("results", []):
                        results.append({
                            "title": r.get("title", "Untitled Source"),
                            "url": r.get("url", ""),
                            "content": r.get("content", ""),
                            "score": r.get("score", 0.0),
                            "raw_content": r.get("raw_content", None)
                        })

                    return {
                        "query": query,
                        "status": "success",
                        "answer": data.get("answer", ""),
                        "results": results,
                        "timestamp": datetime.utcnow().isoformat(),
                        "total_results": len(results)
                    }
                else:
                    logger.error(f"Tavily API returned status {res.status_code}: {res.text}")
                    return {
                        "query": query,
                        "status": "error",
                        "error": f"Tavily HTTP {res.status_code}: {res.text}",
                        "results": []
                    }
        except Exception as e:
            logger.error(f"Tavily search failed: {str(e)}")
            return {
                "query": query,
                "status": "failed",
                "error": str(e),
                "results": []
            }

