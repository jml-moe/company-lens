import uuid
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class ResearchChunk(SQLModel, table=True):
    __tablename__ = "research_chunks"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    company_id: str = Field(foreign_key="companies.id", index=True)
    content: str = ""
    chromadb_id: str = Field(index=True)
    chunk_index: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
