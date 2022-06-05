from typing import Any

from databases import Database
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
)
from pydantic import EmailStr

from app import crud, schemas, utils
from app.api.deps import (
    get_db_pg,
    get_request_active_superuser,
    get_request_active_user,
)
from app.core.config import settings

router = APIRouter()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[schemas.User],
    dependencies=[Depends(get_request_active_superuser)],
)
async def read_users(
    *,
    skip: int = Query(0),
    limit: int = Query(100),
    db: Database = Depends(get_db_pg),
) -> Any:
    """
    Retrieve users.
    """
    return await crud.user.get_multi(db, skip=skip, limit=limit)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.User,
    dependencies=[Depends(get_request_active_superuser)],
)
async def create_user(
    *,
    user: schemas.UserIn = Body(...),
    background_tasks: BackgroundTasks,
    db: Database = Depends(get_db_pg),
) -> Any:
    """
    Create new user.
    """
    db_user = await crud.user.get_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists.",
        )

    background_tasks.add_task(
        utils.send_new_account_email,
        email_to=user.email,
        fullname=crud.user.get_fullname(db_user=user),
    )

    return await crud.user.create(db, obj_in=user)


@router.get("/me", status_code=status.HTTP_200_OK, response_model=schemas.User)
async def read_user_me(
    request_user: Any = Depends(get_request_active_user),
) -> Any:
    """
    Get request user.
    """
    return request_user


@router.patch("/me", status_code=status.HTTP_200_OK, response_model=schemas.User)
async def update_user_me(
    *,
    request_user: Any = Depends(get_request_active_user),
    user_in: schemas.UserUpdate = Body(...),
    db: Database = Depends(get_db_pg),
) -> Any:
    """
    Update request user.
    """
    return await crud.user.update(db, db_obj=request_user, obj_in=user_in)


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.User,
    dependencies=[Depends(get_request_active_superuser)],
)
async def read_user_by_id(
    *,
    user_id: int = Path(...),
    db: Database = Depends(get_db_pg),
) -> Any:
    """
    Get a specific user by id.
    """
    user = await crud.user.get(db, model_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this id does not exist",
        )

    return user


@router.patch(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.User,
    dependencies=[Depends(get_request_active_superuser)],
)
async def update_user(
    *,
    user_id: int = Path(...),
    user_in: schemas.UserUpdate = Body(...),
    db: Database = Depends(get_db_pg),
) -> Any:
    """
    Update a user.
    """
    user = await crud.user.get(db, model_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this id does not exist",
        )

    return await crud.user.update(db, db_obj=user, obj_in=user_in)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_request_active_superuser)],
)
async def delete_user(
    *,
    user_id: int = Path(...),
    db: Database = Depends(get_db_pg),
) -> None:
    """
    Delete a user.
    """
    user = await crud.user.get(db, model_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this id does not exist",
        )

    return await crud.user.remove(db, model_id=user_id)


@router.post(
    "/sign-up",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.User,
)
async def open_sign_up(
    *,
    email: EmailStr = Body(...),
    password: str = Body(...),
    phone_number: str | None = Body(...),
    first_name: str | None = Body(...),
    last_name: str | None = Body(...),
    background_tasks: BackgroundTasks,
    db: Database = Depends(get_db_pg),
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_SIGN_UP:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )

    db_user = await crud.user.get_by_email(db, email=email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists.",
        )

    user = await crud.user.create(
        db,
        obj_in=schemas.UserIn(
            email=email,
            password=password,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
        ),
    )

    background_tasks.add_task(
        utils.send_new_account_email,
        email_to=user.email,
        fullname=crud.user.get_fullname(db_user=user),
    )

    return user
