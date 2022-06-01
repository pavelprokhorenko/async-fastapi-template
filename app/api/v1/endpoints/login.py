from datetime import timedelta
from typing import Any

from databases import Database
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.background import BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from app import crud, schemas, utils
from app.api.deps import get_db_pg
from app.core import security
from app.core.config import settings

router = APIRouter()


@router.post("/access-token", response_model=schemas.Token)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Database = Depends(get_db_pg)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return dict(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        token_type="bearer",
    )


@router.post("/password-recovery", response_model=schemas.Message)
async def recover_password(
    background_tasks: BackgroundTasks,
    email: str = Body(...),
    db: Database = Depends(get_db_pg),
) -> Any:
    """
    Password Recovery.
    """
    db_user = await crud.user.get_by_email(db, email=email)

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = security.generate_password_reset_token(user_id=db_user.id)
    background_tasks.add_task(
        utils.send_reset_password_email,
        email_to=db_user.email,
        fullname=crud.user.get_fullname(db_user=db_user),
        token=password_reset_token,
    )
    return dict(message="Password recovery email sent")


@router.post("/reset-password", response_model=schemas.Message)
async def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Database = Depends(get_db_pg),
) -> Any:
    """
    Reset password.
    """
    email = security.verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    await crud.user.update(
        db,
        db_obj=user,
        obj_in=dict(hashed_password=security.get_password_hash(new_password)),
    )
    return dict(message="Password updated successfully")
