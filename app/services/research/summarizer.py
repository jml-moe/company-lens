import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from app.core.llm import client, ensure_openrouter_configured
from app.core.settings import settings
from app.services.research.prompts import RESULT_SUMMARIZATION_PROMPT

MAX_PARALLEL_SUMMARIES = 5


def summarize_query_results(query: str, results: list[dict[str, Any]]) -> str:
    if not results:
        return "No relevant information found."

    ensure_openrouter_configured()
    prompt = RESULT_SUMMARIZATION_PROMPT.format(
        query=query, results=json.dumps(results, ensure_ascii=False)
    )
    response = client.chat.completions.create(
        model=settings.LLM_MODEL_FAST,
        messages=[
            {"role": "system", "content": "You are a precise research summarizer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )
    return (response.choices[0].message.content or "").strip()


def summarize_all(search_outputs: list[dict[str, Any]]) -> list[str]:
    def _job(item: dict[str, Any]) -> str:
        return summarize_query_results(item["query"], item.get("results", []))

    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_SUMMARIES) as executor:
        return list(executor.map(_job, search_outputs))
