import pytest
from fastapi import Path

from alembic.config import Config


@pytest.fixture(scope="session")
def alembic_cfg(project_dir: Path) -> Config:
    return Config(project_dir / "alembic.ini")
