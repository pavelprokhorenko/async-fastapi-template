from databases import Database

from app import crud, schemas
from app.core.config import settings


async def init_db(db: Database) -> None:
    """Creating superuser for using and testing API"""
    user = await crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER_USERNAME)
    if not user:
        user_in = schemas.UserIn(
            email=settings.FIRST_SUPERUSER_USERNAME,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            first_name=settings.FIRST_SUPERUSER_FIRST_NAME,
            last_name=settings.FIRST_SUPERUSER_LAST_NAME,
            is_superuser=True,
        )
        await crud.user.create(db, obj_in=user_in)
