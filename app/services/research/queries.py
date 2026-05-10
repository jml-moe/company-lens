from app.core.llm import client, ensure_openrouter_configured
from app.core.settings import settings
from app.services.research.prompts import QUERY_GENERATION_PROMPT
from app.services.research.schemas import QueriesSchema

SEARCH_CATEGORIES: dict[str, list[str]] = {
    "financial": ["{name} annual revenue profit"],
    "leadership": ["{name} CEO executive leadership team"],
    "operations": ["{name} business model operations"],
    "market_position": ["{name} market share competitive landscape"],
    "products_services": ["{name} product portfolio service offerings"],
    "corporate_history": ["{name} founding history company timeline"],
    "recent_developments": ["{name} latest news 2025 2026"],
    "strategic": ["{name} acquisitions partnerships expansion"],
    "esg": ["{name} ESG sustainability environmental"],
    "competitors": ["{name} top competitors versus comparison"],
}


def build_static_queries(company_name: str) -> list[str]:
    return [
        template.format(name=company_name)
        for templates in SEARCH_CATEGORIES.values()
        for template in templates
    ]


def generate_dynamic_queries(company_name: str) -> list[str]:
    ensure_openrouter_configured()
    response = client.beta.chat.completions.parse(
        model=settings.LLM_MODEL_FAST,
        messages=[
            {"role": "system", "content": "You generate targeted web search queries."},
            {"role": "user", "content": QUERY_GENERATION_PROMPT.format(company_name=company_name)},
        ],
        response_format=QueriesSchema,
        temperature=0.4,
    )
    parsed = response.choices[0].message.parsed
    if parsed is None:
        return []
    return [q.strip() for q in parsed.queries if q.strip()]


def build_search_queries(company_name: str) -> list[str]:
    static = build_static_queries(company_name)
    try:
        dynamic = generate_dynamic_queries(company_name)
    except Exception:
        dynamic = []

    seen: set[str] = set()
    combined: list[str] = []
    for q in [*static, *dynamic]:
        key = q.lower().strip()
        if key and key not in seen:
            seen.add(key)
            combined.append(q)
    return combined
