from app.core.llm import client, ensure_openrouter_configured
from app.core.settings import settings
from app.services.rag.prompts import RELEVANCE_PROMPT
from app.services.rag.schemas import RelevanceCheck


def check_relevance(user_message: str, company_name: str) -> RelevanceCheck:
    ensure_openrouter_configured()
    response = client.beta.chat.completions.parse(
        model=settings.LLM_MODEL_FAST,
        messages=[
            {"role": "system", "content": "You classify message relevance precisely."},
            {
                "role": "user",
                "content": RELEVANCE_PROMPT.format(
                    company_name=company_name, user_message=user_message
                ),
            },
        ],
        response_format=RelevanceCheck,
        temperature=0.0,
    )
    parsed = response.choices[0].message.parsed
    if parsed is None:
        return RelevanceCheck(is_relevant=True, reason="Classifier empty; defaulting to allow")
    return parsed
