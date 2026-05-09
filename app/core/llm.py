from openai import OpenAI

from app.core.settings import settings

client = OpenAI(
    base_url=settings.OPENROUTER_BASE_URL,
    api_key=settings.OPENROUTER_API_KEY or "missing-api-key",
)


def ensure_openrouter_configured() -> None:
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not set")
