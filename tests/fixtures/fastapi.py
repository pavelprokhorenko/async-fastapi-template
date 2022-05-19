from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.fastapi_app import app


@pytest.fixture
def api_client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_dependency_overrides() -> Generator:
    yield
    app.dependency_overrides = {}
