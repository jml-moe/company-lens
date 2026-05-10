from datetime import datetime

from pydantic import BaseModel, Field

from app.models.message import ChatRole


class MessageCreate(BaseModel):
    content: str = Field(min_length=1)


class MessageRead(BaseModel):
    id: str
    role: ChatRole
    content: str
    created_at: datetime
