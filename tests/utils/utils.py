import datetime
import random
import string
from typing import dict

from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient

from app.core.config import settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=random.randint(16, 32)))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def random_positive_int() -> int:
    return random.randint(1, 100_000_000)


def random_positive_float() -> float:
    return random.random() * random.randint(1, 100_000_000)


def random_bool() -> bool:
    return random.choice([True, False])


def random_date() -> str:
    return jsonable_encoder(
        datetime.date.today() - datetime.timedelta(days=random.randint(0, 10_000))
    )


def random_datetime() -> str:
    return jsonable_encoder(
        datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 10_000))
    )


async def get_superuser_token_headers(api_client: AsyncClient) -> dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER_USERNAME,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    resp = await api_client.post(
        f"{settings.API_V1_STR}/login/access-token", data=login_data
    )
    tokens = resp.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers
