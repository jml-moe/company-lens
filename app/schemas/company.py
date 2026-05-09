from datetime import datetime

from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    company_name: str = Field(min_length=1)


class CompanyRead(BaseModel):
    id: str
    name: str
    industry: str
    created_at: datetime
    updated_at: datetime


class CompanyListItem(BaseModel):
    id: str
    name: str
    industry: str
