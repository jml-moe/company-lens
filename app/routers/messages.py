from fastapi import APIRouter, HTTPException
from sqlmodel import select
from sse_starlette.sse import EventSourceResponse

from app.models.company import Company
from app.models.database import SessionDep
from app.models.message import ChatMessage
from app.models.session import ChatSession
from app.schemas.message import MessageCreate, MessageRead
from app.services.rag import stream_rag_response

router = APIRouter(
    prefix="/companies/{company_id}/sessions/{session_id}/messages",
    tags=["messages"],
)


def _validate_company_session(db: SessionDep, company_id: str, session_id: str) -> None:
    """Pastikan company exists, session exists, DAN session milik company tersebut."""
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    session = db.get(ChatSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.company_id != company_id:
        raise HTTPException(status_code=404, detail="Session does not belong to this company")


@router.post("")
async def post_message(
    company_id: str,
    session_id: str,
    payload: MessageCreate,
    db: SessionDep,
):
    _validate_company_session(db, company_id, session_id)
    return EventSourceResponse(
        stream_rag_response(
            db=db,
            company_id=company_id,
            session_id=session_id,
            user_content=payload.content,
        )
    )


@router.get("", response_model=list[MessageRead])
async def list_messages(company_id: str, session_id: str, db: SessionDep) -> list[ChatMessage]:
    _validate_company_session(db, company_id, session_id)
    return db.exec(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    ).all()
