from typing import Generator, Optional

from databases import Database
from fastapi.security import OAuth2PasswordBearer

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
