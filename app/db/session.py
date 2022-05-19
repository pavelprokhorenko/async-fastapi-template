from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


def create_postgres_engine() -> Engine:
    return create_engine(settings.POSTGRES_URL, pool_pre_ping=True)


postgres_engine = create_postgres_engine()

engines = {"postgres": postgres_engine}

SessionLocalPG = sessionmaker(
    autocommit=False, autoflush=False, bind=engines["postgres"]
)


@contextmanager
def postgres_session() -> Generator:
    session = SessionLocalPG()
    try:
        yield session
    finally:
        session.close()
