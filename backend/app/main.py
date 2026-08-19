from contextlib import asynccontextmanager

# Temporalmente, importamos solo el router de inventario para depurar
from api.endpoints import inventory
from core.db import async_session_maker
from fastapi import APIRouter, FastAPI
from initial_data import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona los eventos de inicio y apagado de la aplicación.
    Aquí se ejecuta la inicialización de la base de datos.
    """
    async with async_session_maker() as session:
        await init_db(session)
    yield
    # Aquí se puede añadir lógica de limpieza al apagar la aplicación


app = FastAPI(
    title="POS-RAG API",
    version="0.1.0",
    description="API for inventory control with Retrieval-Augmented Generation (RAG) capabilities.",
    lifespan=lifespan,
)

# Router principal con prefijo para versionado de la API
api_router = APIRouter(prefix="/api/v1")

# Incluimos únicamente el router de inventario para la prueba
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])

app.include_router(api_router)
