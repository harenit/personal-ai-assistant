from typing import Any
from backend.tools.base import BaseTool
from backend.permissions.models import RiskLevel
from backend.integrations.search.web_search import DuckDuckGoSearchProvider

search_provider = DuckDuckGoSearchProvider()

class SearchWebTool(BaseTool):
    name = "search_web"
    description = "Search the web for educational resources, technical tutorials, academic articles, and concept explanations."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Educational or technical search query (e.g. 'binary tree tutorials', 'gradient descent explanation')"
            },
            "max_results": {
                "type": "integer",
                "description": "Number of results to return (default 4)",
                "default": 4
            }
        },
        "required": ["query"]
    }

    def execute(self, query: str, max_results: int = 4, **kwargs) -> dict[str, Any]:
        results = search_provider.search_web(query=query, max_results=max_results)
        return {
            "success": True,
            "query": query,
            "count": len(results),
            "results": results
        }

class SearchYouTubeTool(BaseTool):
    name = "search_youtube"
    description = "Find high-quality educational video tutorials on YouTube on a specific academic or programming topic."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Topic or video to find (e.g. 'binary tree tutorial', 'A* search algorithm')"
            },
            "max_results": {
                "type": "integer",
                "description": "Number of video results (default 3)",
                "default": 3
            }
        },
        "required": ["query"]
    }

    def execute(self, query: str, max_results: int = 3, **kwargs) -> dict[str, Any]:
        videos = search_provider.search_youtube(query=query, max_results=max_results)
        return {
            "success": True,
            "query": query,
            "count": len(videos),
            "videos": videos,
            "message": f"Found {len(videos)} YouTube tutorial(s) for '{query}'."
        }
