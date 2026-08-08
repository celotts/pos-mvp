from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from core.config import settings

# Crea el motor de base de datos asíncrono utilizando la URL de tu configuración.
# pool_pre_ping=True asegura que la conexión esté viva antes de usarla.
engine = create_async_engine(str(settings.DATABASE_URL), pool_pre_ping=True)

# Crea una fábrica de sesiones asíncronas.
# expire_on_commit=False es importante para evitar que los objetos se desvinculen de la sesión.
async_session_maker = async_sessionmaker(engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass
