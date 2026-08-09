from api.endpoints import login, roles, users
from api.exception_handlers import http_exception_handler
from core.db import async_session_maker
from fastapi import APIRouter, FastAPI, HTTPException
from initial_data import init_db

app = FastAPI(
    title="Medical Appointments RAG API",
    description="API para la gestión de citas médicas con capacidades de Búsqueda Aumentada por Generación (RAG).",
    version="0.1.0",
)

# Registra el manejador de excepciones personalizado
app.add_exception_handler(HTTPException, http_exception_handler)


@app.on_event("startup")
async def on_startup():
    """Ejecuta la lógica de inicialización en el arranque."""
    async with async_session_maker() as session:
        await init_db(session)


# Crea un router principal para la versión v1 de la API
api_router = APIRouter(prefix="/api/v1")


@api_router.get("/", summary="Comprueba el estado de la API")
def read_root():
    """Endpoint de estado para verificar que la API está funcionando."""
    return {"status": "ok"}


# Incluye los routers de los endpoints en el router principal
api_router.include_router(login, tags=["Boostrap & Auth"])
api_router.include_router(users, prefix="/users", tags=["Users"])
api_router.include_router(roles, prefix="/roles", tags=["Roles"])

# Incluye el router principal en la aplicación
app.include_router(api_router)
