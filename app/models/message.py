import uuid
from datetime import UTC, datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class ChatRole(str, Enum):
    user = "user"
    assistant = "assistant"


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="chat_sessions.id", index=True)
    role: ChatRole = Field(index=True)
    content: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
