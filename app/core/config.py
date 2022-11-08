import logging
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, PostgresDsn, validator


class Settings(BaseSettings):
    # Base
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str | None
    SERVER_HOST: AnyHttpUrl
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://0.0.0.0:8001"]'
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
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

    POSTGRES_URL: PostgresDsn | None
    TEST_POSTGRES_URL: PostgresDsn | None

    @validator("POSTGRES_URL", pre=True)
    def assemble_postgres_db_url(cls, v: str | None, values: Mapping[str, Any]) -> Any:
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
        cls, v: str | None, values: Mapping[str, Any]
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

    # Email
    SEND_EMAILS_TO_USERS: bool = True
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_USER: str | None
    SMTP_PASSWORD: str | None
    EMAILS_FROM_NAME: str | None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: str | None, values: dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_MINUTES: int = 60 * 3  # 3 hours
    EMAILS_ENABLED: bool = False

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    FIRST_SUPERUSER_USERNAME: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_FIRST_NAME: str | None
    FIRST_SUPERUSER_LAST_NAME: str | None
    USERS_OPEN_SIGN_UP: bool = False


settings = Settings()

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)
