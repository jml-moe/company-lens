from app.core.llm import client, ensure_openrouter_configured
from app.core.settings import settings
from app.services.research.prompts import BUSINESS_PROFILE_PROMPT, EXTRACTION_PROMPT
from app.services.research.schemas import ResearchFields


def _format_summaries(queries: list[str], summaries: list[str]) -> str:
    blocks = []
    for i, (q, s) in enumerate(zip(queries, summaries, strict=True), start=1):
        blocks.append(f"### Summary {i} — Query: {q}\n{s}")
    return "\n\n".join(blocks)


def generate_profile(company_name: str, queries: list[str], summaries: list[str]) -> str:
    ensure_openrouter_configured()
    prompt = BUSINESS_PROFILE_PROMPT.format(
        company_name=company_name, summaries=_format_summaries(queries, summaries)
    )
    response = client.chat.completions.create(
        model=settings.LLM_MODEL_STRONG,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert business analyst. Write factual, comprehensive "
                    "company research profiles based strictly on provided summaries."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or ""


def extract_structured_fields(profile: str) -> ResearchFields:
    ensure_openrouter_configured()
    response = client.beta.chat.completions.parse(
        model=settings.LLM_MODEL_FAST,
        messages=[
            {"role": "system", "content": "You extract structured data from business profiles."},
            {"role": "user", "content": EXTRACTION_PROMPT.format(profile=profile)},
        ],
        response_format=ResearchFields,
        temperature=0.1,
    )
    parsed = response.choices[0].message.parsed
    if parsed is None:
        return ResearchFields(industry="", products="", competitors="", recent_news="")
    return parsed
