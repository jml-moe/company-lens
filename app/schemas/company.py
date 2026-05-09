from datetime import datetime

from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    company_name: str = Field(min_length=1)


class CompanyRead(BaseModel):
    id: str
    name: str
    industry: str
    overview: str
    products: str
    competitors: str
    recent_news: str
    researched_at: datetime
    created_at: datetime
    updated_at: datetime


class CompanyListItem(BaseModel):
    id: str
    name: str
    industry: str
