from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import delete, select

from app.models.chunks import ResearchChunk
from app.models.company import Company
from app.models.database import SessionDep
from app.models.message import ChatMessage
from app.models.session import ChatSession
from app.schemas.company import CompanyCreate, CompanyListItem, CompanyRead
from app.services.embedder import build_research_document, delete_company_chunks, store_chunks
from app.services.research import research_company

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(payload: CompanyCreate, db: SessionDep) -> Company:
    name = payload.company_name.strip()
    result = research_company(name)
    company = Company(name=name, **result.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)

    document = build_research_document(
        name=company.name,
        industry=company.industry,
        overview=company.overview,
        products=company.products,
        competitors=company.competitors,
        recent_news=company.recent_news,
    )
    stored = store_chunks(company.id, document)
    for chunk in stored:
        db.add(
            ResearchChunk(
                company_id=company.id,
                content=chunk.content,
                chromadb_id=chunk.chromadb_id,
                chunk_index=chunk.chunk_index,
            )
        )
    db.commit()
    return company


@router.get("", response_model=list[CompanyListItem])
async def list_companies(
    db: SessionDep,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[Company]:
    return db.exec(select(Company).offset(offset).limit(limit)).all()


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(company_id: str, db: SessionDep) -> Company:
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: str, db: SessionDep) -> None:
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    delete_company_chunks(company_id)
    db.exec(delete(ResearchChunk).where(ResearchChunk.company_id == company_id))

    session_ids = db.exec(select(ChatSession.id).where(ChatSession.company_id == company_id)).all()
    if session_ids:
        db.exec(delete(ChatMessage).where(ChatMessage.session_id.in_(session_ids)))
    db.exec(delete(ChatSession).where(ChatSession.company_id == company_id))

    db.delete(company)
    db.commit()
