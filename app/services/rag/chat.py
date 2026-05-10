import json
from collections.abc import Iterator

from sqlmodel import Session, select

from app.core.llm import client, ensure_openrouter_configured
from app.core.settings import settings
from app.models.company import Company
from app.models.message import ChatMessage
from app.services.embedder import search
from app.services.rag.guardrails import check_relevance
from app.services.rag.prompts import OFF_TOPIC_REPLY, SYSTEM_PROMPT


def _format_context(company_id: str, query: str) -> str:
    results = search(query=query, company_id=company_id, top_k=5)
    if not results:
        return "No relevant research chunks were found."
    return "\n\n".join(f"[Source {i + 1}]\n{r.content}" for i, r in enumerate(results))


def _format_history(db: Session, session_id: str) -> list[dict]:
    messages = db.exec(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    ).all()
    return [{"role": m.role, "content": m.content} for m in messages]


def _persist(db: Session, session_id: str, role: str, content: str) -> None:
    db.add(ChatMessage(session_id=session_id, role=role, content=content))
    db.commit()


def _sse(payload: dict) -> dict[str, str]:
    return {"data": json.dumps(payload)}


def stream_rag_response(
    *,
    db: Session,
    company_id: str,
    session_id: str,
    user_content: str,
) -> Iterator[dict[str, str]]:
    ensure_openrouter_configured()

    company = db.get(Company, company_id)
    company_name = company.name if company else "this company"

    _persist(db, session_id, "user", user_content)

    relevance = check_relevance(user_content, company_name)
    if not relevance.is_relevant:
        for ch in OFF_TOPIC_REPLY:
            yield _sse({"type": "text_delta", "content": ch})
        _persist(db, session_id, "assistant", OFF_TOPIC_REPLY)
        yield _sse({"type": "done"})
        return

    context = _format_context(company_id, user_content)
    history = _format_history(db, session_id)
    assistant_parts: list[str] = []

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(company_name=company_name, context=context),
        },
        *history,
    ]

    try:
        stream = client.chat.completions.create(
            model=settings.LLM_MODEL_FAST, messages=messages, temperature=0.2, stream=True
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if not delta:
                continue
            assistant_parts.append(delta)
            yield _sse({"type": "text_delta", "content": delta})

        assistant_content = "".join(assistant_parts)
        _persist(db, session_id, "assistant", assistant_content)
        yield _sse({"type": "done"})
    except Exception as exc:
        db.rollback()
        yield _sse({"type": "error", "message": str(exc)})
