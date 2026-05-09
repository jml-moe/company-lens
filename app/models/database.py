from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

from app.core.settings import settings

engine = create_engine(settings.DATABASE_URL, echo=False)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
