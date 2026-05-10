from pydantic import BaseModel


class RelevanceCheck(BaseModel):
    is_relevant: bool
    reason: str
