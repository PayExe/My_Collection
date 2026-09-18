from collections.abc import AsyncIterator

from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.database import session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session
