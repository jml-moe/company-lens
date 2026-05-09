from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from app.models.company import Company
from app.models.database import SessionDep
from app.schemas.company import CompanyCreate, CompanyListItem, CompanyRead

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
async def create_company(payload: CompanyCreate, db: SessionDep) -> Company:
    company = Company(name=payload.company_name.strip(), industry="")
    db.add(company)
    db.commit()
    db.refresh(company)
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
    db.delete(company)
    db.commit()
