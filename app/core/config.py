import logging
from pathlib import Path
from typing import Any, List, Mapping, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    # Base
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: Optional[str]
    SERVER_HOST: Optional[AnyHttpUrl]
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://0.0.0.0:8001"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str

    # Paths
    BASE_DIR: Path = Path(__file__).absolute().parent.parent
    STATIC_DIR: Path = BASE_DIR / "statics"

    # Databases
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_TEST_DB: str = ""

    POSTGRES_URL: Optional[PostgresDsn]
    TEST_POSTGRES_URL: Optional[PostgresDsn]

    @validator("POSTGRES_URL", pre=True)
    def assemble_postgres_db_url(
        cls, v: Optional[str], values: Mapping[str, Any]
    ) -> Any:
        if v and isinstance(v, str):
            return v

        return str(
            PostgresDsn.build(
                scheme="postgresql",
                user=values["POSTGRES_USER"],
                password=values["POSTGRES_PASSWORD"],
                host=values["POSTGRES_HOST"],
                port=str(values["POSTGRES_PORT"]),
                path=f'/{values["POSTGRES_DB"]}',
            )
        )

    @validator("TEST_POSTGRES_URL", pre=True)
    def assemble_test_postgres_url(
        cls, v: Optional[str], values: Mapping[str, Any]
    ) -> Any:
        if not values.get("POSTGRES_TEST_DB"):
            return ""
        if v and isinstance(v, str):
            return v

        return str(
            PostgresDsn.build(
                scheme="postgresql",
                user=values["POSTGRES_USER"],
                password=values["POSTGRES_PASSWORD"],
                host=values["POSTGRES_HOST"],
                port=str(values["POSTGRES_PORT"]),
                path=f'/{values["POSTGRES_TEST_DB"]}',
            )
        )


settings = Settings()

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)
