from api.endpoints import (
    accounts_payable_controller,
    accounts_receivable_controller,
    assistant_controller,
    cash_account_controller,
    countries_controller,
    customers_controller,
    login_controller,
    municipality_controller,
    pos_terminal_controller,
    product_controller,
    purchase_controller,
    roles_controller,
    sale_controller,
    shift_controller,
    specialties_controller,
    state_province_controller,
    store_controller,
    supplier_controller,
    users_controller,
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
api_router.include_router(login_controller.router, tags=["Boostrap & Auth"])
api_router.include_router(users_controller.router, prefix="/users", tags=["Users"])
api_router.include_router(roles_controller.router, prefix="/roles", tags=["Roles"])
api_router.include_router(
    customers_controller.router, prefix="/customers", tags=["Customers"]
)
api_router.include_router(
    countries_controller.router, prefix="/countries", tags=["Locations"]
)
api_router.include_router(
    state_province_controller.router, prefix="/states-provinces", tags=["Locations"]
)
api_router.include_router(
    municipality_controller.router, prefix="/municipalities", tags=["Locations"]
)
api_router.include_router(
    specialties_controller.router, prefix="/specialties", tags=["Specialties"]
)
api_router.include_router(
    supplier_controller.router, prefix="/suppliers", tags=["Suppliers"]
)
api_router.include_router(store_controller.router, prefix="/stores", tags=["Locations"])
api_router.include_router(
    cash_account_controller.router, prefix="/cash-accounts", tags=["Accounting"]
)
api_router.include_router(
    pos_terminal_controller.router, prefix="/pos-terminals", tags=["POS"]
)
api_router.include_router(shift_controller.router, prefix="/shifts", tags=["POS"])
api_router.include_router(sale_controller.router, prefix="/sales", tags=["POS"])
api_router.include_router(
    product_controller.router, prefix="/products", tags=["Products"]
)
api_router.include_router(
    purchase_controller.router, prefix="/purchases", tags=["Purchases"]
)
api_router.include_router(
    accounts_payable_controller.router, prefix="/accounts-payable", tags=["Accounting"]
)
api_router.include_router(
    accounts_receivable_controller.router,
    prefix="/accounts-receivable",
    tags=["Accounting"],
)
api_router.include_router(assistant_controller.router)

# Incluye el router principal en la aplicación
app.include_router(api_router)
