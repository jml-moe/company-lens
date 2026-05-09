import uuid
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Company(SQLModel, table=True):
    __tablename__ = "companies"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(index=True)
    industry: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
