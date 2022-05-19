from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def project_dir() -> Path:
    return Path(__file__).parent.parent.parent
