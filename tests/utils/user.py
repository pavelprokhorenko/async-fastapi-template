from typing import Any

from databases import Database
from httpx import AsyncClient

from app import crud
from app.core.config import settings
from app.schemas.user import UserIn, UserUpdate
from tests.utils.utils import random_email, random_lower_string


async def user_authentication_headers(
    *, api_client: AsyncClient, email: str, password: str
) -> dict[str, str]:
    data = dict(username=email, password=password)

    response = await api_client.post(
        f"{settings.API_V1_STR}/login/access-token", data=data
    )
    resp_data = response.json()
    auth_token = resp_data["access_token"]

    return dict(Authorization=f"Bearer {auth_token}")


async def create_random_user(db: Database) -> Any:
    email = random_email()
    password = random_lower_string()
    first_name = random_lower_string()
    last_name = random_lower_string()
    user_in = UserIn(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )

    user = await crud.user.create(db=db, obj_in=user_in)
    return user


async def authentication_token_from_email(
    *, api_client: AsyncClient, email: str, db: Database
) -> dict[str, str]:
    """
    Return a valid token for the user with given email.
    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = await crud.user.get_by_email(db, email=email)
    if not user:
        first_name = random_lower_string()
        last_name = random_lower_string()
        user_in_create = UserIn(
            email=email, password=password, first_name=first_name, last_name=last_name
        )
        await crud.user.create(db, obj_in=user_in_create)
    else:
        user_in_update = UserUpdate(password=password)
        await crud.user.update(db, db_obj=user, obj_in=user_in_update)

    return await user_authentication_headers(
        api_client=api_client, email=email, password=password
    )
