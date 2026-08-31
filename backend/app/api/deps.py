from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from core.db import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a SQLAlchemy async session.
    """
    async with async_session_maker() as session:
        yield session
