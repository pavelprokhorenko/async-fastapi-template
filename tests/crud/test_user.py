import pytest
from databases import Database
from fastapi.encoders import jsonable_encoder

from app import crud
from app.core.security import verify_password
from app.schemas.user import UserIn, UserUpdate
from tests.utils.utils import random_email, random_lower_string

pytestmark = pytest.mark.asyncio


async def test_create_user(pg_db: Database) -> None:
    email = random_email()
    password = random_lower_string()
    first_name = random_lower_string()
    last_name = random_lower_string()
    user_in = UserIn(
        email=email, password=password, first_name=first_name, last_name=last_name
    )
    user = await crud.user.create(pg_db, obj_in=user_in)

    assert user.email == email
    assert user.first_name == first_name
    assert user.last_name == last_name
    assert hasattr(user, "hashed_password")
    assert verify_password(password, user.hashed_password)


async def test_authenticate_user(pg_db: Database) -> None:
    email = random_email()
    password = random_lower_string()
    first_name = random_lower_string()
    last_name = random_lower_string()
    user_in = UserIn(
        email=email, password=password, first_name=first_name, last_name=last_name
    )
    user = await crud.user.create(pg_db, obj_in=user_in)

    authenticated_user = await crud.user.authenticate(
        pg_db, email=email, password=password
    )

    assert authenticated_user
    assert user.email == authenticated_user.email


async def test_not_authenticate_user(pg_db: Database) -> None:
    email = random_email()
    password = random_lower_string()

    user = await crud.user.authenticate(pg_db, email=email, password=password)

    assert user is None


async def test_check_if_user_is_active(pg_db: Database) -> None:
    email = random_email()
    password = random_lower_string()
    first_name = random_lower_string()
    last_name = random_lower_string()
    user_in = UserIn(
        email=email, password=password, first_name=first_name, last_name=last_name
    )

    user = await crud.user.create(pg_db, obj_in=user_in)

    assert user.is_active is True


async def test_check_if_user_is_inactive(pg_db: Database) -> None:
    email = random_email()
    password = random_lower_string()
    first_name = random_lower_string()
    last_name = random_lower_string()
    user_in = UserIn(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=False,
    )

    user = await crud.user.create(pg_db, obj_in=user_in)

    assert user.is_active is False


async def test_check_if_user_is_superuser(pg_db: Database) -> None:
    email = random_email()
    password = random_lower_string()
    first_name = random_lower_string()
    last_name = random_lower_string()
    user_in = UserIn(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_superuser=True,
    )

    user = await crud.user.create(pg_db, obj_in=user_in)

    assert user.is_superuser is True


async def test_check_if_user_is_superuser_normal_user(pg_db: Database) -> None:
    email = random_email()
    password = random_lower_string()
    first_name = random_lower_string()
    last_name = random_lower_string()
    user_in = UserIn(
        email=email, password=password, first_name=first_name, last_name=last_name
    )

    user = await crud.user.create(pg_db, obj_in=user_in)

    assert user.is_superuser is False


async def test_get_user(pg_db: Database) -> None:
    email = random_email()
    password = random_lower_string()
    first_name = random_lower_string()
    last_name = random_lower_string()
    user_in = UserIn(
        email=email, password=password, first_name=first_name, last_name=last_name
    )

    user = await crud.user.create(pg_db, obj_in=user_in)
    user_2 = await crud.user.get(pg_db, model_id=user.id)

    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


async def test_update_user(pg_db: Database) -> None:
    email = random_email()
    password = random_lower_string()
    first_name = random_lower_string()
    last_name = random_lower_string()
    user_in = UserIn(
        email=email, password=password, first_name=first_name, last_name=last_name
    )

    user = await crud.user.create(pg_db, obj_in=user_in)

    new_password = random_lower_string()
    user_in_update = UserUpdate(password=new_password)

    await crud.user.update(pg_db, db_obj=user, obj_in=user_in_update)
    user_2 = await crud.user.get(pg_db, model_id=user.id)

    assert user_2
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.hashed_password)


async def test_remove_user(pg_db: Database) -> None:
    email = random_email()
    password = random_lower_string()
    first_name = random_lower_string()
    last_name = random_lower_string()
    user_in = UserIn(
        email=email, password=password, first_name=first_name, last_name=last_name
    )

    user = await crud.user.create(pg_db, obj_in=user_in)

    await crud.user.remove(pg_db, model_id=user.id)
    non_existing_user = await crud.user.get_by_email(pg_db, email=email)

    assert non_existing_user is None
