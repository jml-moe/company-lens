import uuid
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    company_id: str = Field(foreign_key="companies.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
