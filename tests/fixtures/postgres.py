from typing import Generator

import pytest
import pytest_asyncio
from databases import Database
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy_utils import create_database, database_exists, drop_database

from alembic import command
from alembic.config import Config
from app.api.deps import get_db_pg
from app.core.config import settings
from app.db.init_db import init_db
from app.db.metadata import postgres_metadata
from app.fastapi_app import app
from tests.common import PGSession


@pytest.fixture(scope="session")
def pg_connection() -> Connection:
    if database_exists(settings.TEST_POSTGRES_URL):
        drop_database(settings.TEST_POSTGRES_URL)
    create_database(settings.TEST_POSTGRES_URL)
    engine = create_engine(settings.TEST_POSTGRES_URL)
    connection = engine.connect()
    return connection


@pytest.fixture(scope="session")
def setup_pg_database(pg_connection: Connection, alembic_cfg: Config) -> Generator:
    postgres_metadata.bind = pg_connection

    alembic_cfg.config_ini_section = "postgres"
    alembic_cfg.attributes["connection"] = pg_connection

    command.upgrade(alembic_cfg, "head")

    PGSession.configure(bind=pg_connection)

    try:
        yield
    finally:
        command.downgrade(alembic_cfg, "base")


@pytest_asyncio.fixture
async def pg_db(setup_pg_database: Generator) -> Generator:
    db = Database(settings.TEST_POSTGRES_URL)
    try:
        await db.connect()
        await init_db(db=db)
        yield db
    finally:
        await db.disconnect()
        PGSession.remove()


@pytest.fixture
def pg_db_override(pg_db: Generator) -> None:
    def get_test_db_pg() -> Generator[Generator, None, None]:
        yield pg_db

    app.dependency_overrides[get_db_pg] = get_test_db_pg


@pytest.fixture
def use_postgres(pg_db_override: Generator) -> None:
    pass
