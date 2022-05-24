from typing import Any, Generator, Optional

from databases import Database
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError

from app import crud, schemas
from app.core import security
from app.core.config import settings

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


async def get_db_pg() -> Generator:
    """
    Connect to database. After response disconnect from database.
    """
    db: Optional[Database] = None
    try:
        db = Database(settings.POSTGRES_URL)
        await db.connect()
        yield db
    finally:
        if db is not None:
            await db.disconnect()


async def get_request_user(
    db: Database = Depends(get_db_pg), token: str = Depends(reusable_oauth2)
) -> Any:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ENCODING_ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await crud.user.get(db, model_id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_request_active_user(
    request_user: Any = Depends(get_request_user),
) -> Any:
    if not request_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return request_user


async def get_request_active_superuser(
    request_user: Any = Depends(get_request_active_user),
) -> Any:
    if not request_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return request_user
