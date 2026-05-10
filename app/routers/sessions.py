from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.models.company import Company
from app.models.database import SessionDep
from app.models.session import ChatSession
from app.schemas.session import SessionRead

router = APIRouter(prefix="/companies/{company_id}/sessions", tags=["sessions"])


def _get_company_or_404(db: SessionDep, company_id: str) -> Company:
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
async def create_session(company_id: str, db: SessionDep) -> ChatSession:
    _get_company_or_404(db, company_id)
    session = ChatSession(company_id=company_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("", response_model=list[SessionRead])
async def list_sessions(company_id: str, db: SessionDep) -> list[ChatSession]:
    _get_company_or_404(db, company_id)
    return db.exec(
        select(ChatSession)
        .where(ChatSession.company_id == company_id)
        .order_by(ChatSession.created_at.desc())
    ).all()
