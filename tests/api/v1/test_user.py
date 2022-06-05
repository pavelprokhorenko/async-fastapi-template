from typing import Dict

import pytest
from databases import Database
from httpx import AsyncClient

from app import crud
from app.core.config import settings
from app.schemas import UserIn
from tests.utils.utils import random_email, random_lower_string

pytestmark = pytest.mark.usefixtures("use_postgres")


async def test_get_users_superuser_me(
    api_client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    response = await api_client.get(
        f"{settings.API_V1_STR}/user/me", headers=superuser_token_headers
    )
    current_user = response.json()

    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is True
    assert current_user["email"] == settings.FIRST_SUPERUSER_USERNAME
    assert current_user["first_name"] == settings.FIRST_SUPERUSER_FIRST_NAME
    assert current_user["last_name"] == settings.FIRST_SUPERUSER_LAST_NAME


async def test_get_users_normal_user_me(
    api_client: AsyncClient, normal_user_token_headers: Dict[str, str]
) -> None:
    response = await api_client.get(
        f"{settings.API_V1_STR}/user/me", headers=normal_user_token_headers
    )
    current_user = response.json()

    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False
    assert current_user["email"]


async def test_create_user_new_email(
    api_client: AsyncClient, superuser_token_headers: dict, pg_db: Database
) -> None:
    username = random_email()
    password = random_lower_string()
    first_name = random_lower_string()
    last_name = random_lower_string()
    data = {
        "email": username,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
    }
    response = await api_client.post(
        f"{settings.API_V1_STR}/user/",
        headers=superuser_token_headers,
        json=data,
    )

    assert 200 <= response.status_code < 300
    created_user = response.json()
    user = await crud.user.get_by_email(pg_db, email=username)
    assert user
    assert user.email == created_user["email"]


async def test_get_existing_user(
    api_client: AsyncClient, superuser_token_headers: dict, pg_db: Database
) -> None:
    username = random_email()
    password = random_lower_string()
    first_name = random_lower_string()
    last_name = random_lower_string()
    user_in = UserIn(
        email=username, password=password, first_name=first_name, last_name=last_name
    )
    user = await crud.user.create(pg_db, obj_in=user_in)

    user_id = user.id
    response = await api_client.get(
        f"{settings.API_V1_STR}/user/{user_id}",
        headers=superuser_token_headers,
    )

    assert 200 <= response.status_code < 300
    api_user = response.json()
    existing_user = await crud.user.get_by_email(pg_db, email=username)
    assert existing_user
    assert existing_user.email == api_user["email"]


async def test_create_user_existing_username(
    api_client: AsyncClient, superuser_token_headers: dict, pg_db: Database
) -> None:
    username = random_email()
    password = random_lower_string()
    first_name = random_lower_string()
    last_name = random_lower_string()
    user_in = UserIn(
        email=username, password=password, first_name=first_name, last_name=last_name
    )
    await crud.user.create(pg_db, obj_in=user_in)

    data = {
        "email": username,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
    }
    response = await api_client.post(
        f"{settings.API_V1_STR}/user/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 400


async def test_create_user_by_normal_user(
    api_client: AsyncClient, normal_user_token_headers: Dict[str, str]
) -> None:
    username = random_email()
    password = random_lower_string()
    first_name = random_lower_string()
    last_name = random_lower_string()
    data = {
        "email": username,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
    }
    response = await api_client.post(
        f"{settings.API_V1_STR}/user/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 400


async def test_retrieve_users(
    api_client: AsyncClient, superuser_token_headers: dict, pg_db: Database
) -> None:
    username = random_email()
    password = random_lower_string()
    first_name = random_lower_string()
    last_name = random_lower_string()
    user_in = UserIn(
        email=username, password=password, first_name=first_name, last_name=last_name
    )
    await crud.user.create(pg_db, obj_in=user_in)

    username2 = random_email()
    password2 = random_lower_string()
    first_name2 = random_lower_string()
    last_name2 = random_lower_string()
    user_in2 = UserIn(
        email=username2,
        password=password2,
        first_name=first_name2,
        last_name=last_name2,
    )
    await crud.user.create(pg_db, obj_in=user_in2)

    response = await api_client.get(
        f"{settings.API_V1_STR}/user/", headers=superuser_token_headers
    )
    all_users = response.json()

    assert len(all_users) > 1
    for item in all_users:
        assert "email" in item


async def test_open_sign_up(api_client: AsyncClient, pg_db: Database):
    if settings.USERS_OPEN_SIGN_UP:
        username = random_email()
        password = random_lower_string()
        data = {"email": username, "password": password}

        response = await api_client.post(
            f"{settings.API_V1_STR}/user/sign-up/", json=data
        )

        assert 200 <= response.status_code < 300
        created_user = response.json()
        user = await crud.user.get_by_email(pg_db, email=username)
        assert user
        assert user.email == created_user["email"]
        assert user.is_active is True
        assert user.is_superuser is False
