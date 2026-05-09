from pydantic import BaseModel


class QueriesSchema(BaseModel):
    queries: list[str]


class ResearchFields(BaseModel):
    industry: str
    products: str
    competitors: str
    recent_news: str


class ResearchResult(BaseModel):
    industry: str
    overview: str
    products: str
    competitors: str
    recent_news: str
    raw_search_data: str
