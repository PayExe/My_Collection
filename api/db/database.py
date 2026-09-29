from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from api.core.config import DATABASE_URL
from api.db.base import Base
from api.models.collection_entry import CollectionEntry as _CollectionEntry
from api.models.game import Game as _Game
from api.models.user import User as _User



engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)
session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_db_and_tables() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def close_database() -> None:
    await engine.dispose()
