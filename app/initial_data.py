import asyncio
import logging

from databases import Database

from app.core.config import settings
from app.db.init_db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init(database: Database) -> None:
    await database.connect()
    await init_db(db=database)
    await database.disconnect()


async def main() -> None:
    postgres = Database(settings.POSTGRES_URL)

    logger.info("Creating initial data for postgres")
    await init(postgres)
    logger.info("Initial data for postgres created")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
