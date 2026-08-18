from collections.abc import AsyncGenerator

import pytest

# --- AJUSTA ESTAS IMPORTACIONES SEGÚN TU ESTRUCTURA ---
# Asumo que tu app de FastAPI se encuentra en 'backend.app.main.app'
# y tu configuración de base de datos en 'backend.app.core.db'
from app.core.db import Base, get_db
from app.main import app
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# --- Configuración de la Base de Datos de Prueba ---
# Usamos una base de datos SQLite en memoria para pruebas rápidas y aisladas.
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture que crea una nueva base de datos y sesión para cada prueba.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture que crea un cliente de API para realizar peticiones.
    Sobrescribe la dependencia 'get_db' para usar la base de datos de prueba.
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
    del app.dependency_overrides[get_db]
