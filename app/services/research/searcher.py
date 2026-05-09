from typing import Any

from tavily import TavilyClient

from app.core.settings import settings


def ensure_tavily_configured() -> None:
    if not settings.TAVILY_API_KEY:
        raise RuntimeError("TAVILY_API_KEY is not configured")


def search_company_web(queries: list[str]) -> list[dict[str, Any]]:
    ensure_tavily_configured()
    tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)
    results: list[dict[str, Any]] = []
    for query in queries:
        response = tavily.search(
            query=query, search_depth="advanced", max_results=5, include_answer=False
        )
        results.append({"query": query, "results": response.get("results", [])})
    return results
