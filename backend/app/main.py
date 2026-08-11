from api.endpoints import (
    cash_account,
    countries,
    customers,
    login,
    municipality,
    pos_terminal,
    roles,
    specialties,
    state_province,
    store,
    supplier,
    users,
)
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
api_router.include_router(customers, prefix="/customers", tags=["Customers"])
api_router.include_router(countries, prefix="/countries", tags=["Locations"])
api_router.include_router(
    state_province, prefix="/states-provinces", tags=["Locations"]
)
api_router.include_router(municipality, prefix="/municipalities", tags=["Locations"])
api_router.include_router(specialties, prefix="/specialties", tags=["Specialties"])
api_router.include_router(supplier, prefix="/suppliers", tags=["Suppliers"])
api_router.include_router(store, prefix="/stores", tags=["Locations"])
api_router.include_router(cash_account, prefix="/cash-accounts", tags=["Accounting"])
api_router.include_router(pos_terminal, prefix="/pos-terminals", tags=["POS"])

# Incluye el router principal en la aplicación
app.include_router(api_router)
