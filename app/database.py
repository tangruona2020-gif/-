from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


engine = create_engine(get_settings().database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(engine, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as db:
        yield db


def create_schema() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(engine)
