from datetime import datetime

from pydantic import BaseModel


class SessionRead(BaseModel):
    id: str
    company_id: str
    created_at: datetime
