import json

from app.services.research.queries import build_search_queries
from app.services.research.schemas import ResearchResult
from app.services.research.searcher import search_company_web
from app.services.research.summarizer import summarize_all
from app.services.research.synthesizer import extract_structured_fields, generate_profile


def research_company(company_name: str) -> ResearchResult:
    queries = build_search_queries(company_name)
    raw = search_company_web(queries)
    summaries = summarize_all(raw)
    profile = generate_profile(company_name, queries, summaries)
    fields = extract_structured_fields(profile)

    return ResearchResult(
        industry=fields.industry,
        overview=profile,
        products=fields.products,
        competitors=fields.competitors,
        recent_news=fields.recent_news,
        raw_search_data=json.dumps(raw, ensure_ascii=False),
    )
