from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from .config import get_settings

settings = get_settings()
connect_args = {"check_same_thread": False}
engine = create_engine(settings.DATABASE_URL, echo=False, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


SessionDep = Annotated[Session, Depends(get_session)]
