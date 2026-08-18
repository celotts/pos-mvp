from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings

# Crea el motor de base de datos asíncrono utilizando la URL de tu configuración.
# pool_pre_ping=True asegura que la conexión esté viva antes de usarla.
engine = create_async_engine(str(settings.DATABASE_URL), pool_pre_ping=True)

# Crea una fábrica de sesiones asíncronas.
# expire_on_commit=False es importante para evitar que los objetos se desvinculen de la sesión.
async_session_maker = async_sessionmaker(engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get a database session."""
    async with async_session_maker() as session:
        yield session
