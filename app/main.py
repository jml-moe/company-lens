from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.core.settings import settings
from app.routers import companies, messages, sessions

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)
app.include_router(companies.router)
app.include_router(sessions.router)
app.include_router(messages.router)


@app.get("/scalar")
def scalar_docs():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title=app.title)
