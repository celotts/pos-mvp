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
    title="POS-RAG API",
    description="API for inventory control with Retrieval-Augmented Generation (RAG) capabilities.",
    version="0.1.0",
)

# Registra el manejador de excepciones personalizado
app.add_exception_handler(HTTPException, http_exception_handler)


@app.on_event("startup")
async def on_startup():
    """Executes the initialization logic on startup."""
    async with async_session_maker() as session:
        await init_db(session)


# Crea un router principal para la versión v1 de la API
api_router = APIRouter(prefix="/api/v1")


@api_router.get("/", summary="Check the API status")
def read_root():
    """Status endpoint to check if the API is running."""
    return {"status": "ok"}


# Incluye los routers de los endpoints en el router principal
api_router.include_router(login_controller.router)
api_router.include_router(users_controller.router, prefix="/users")
api_router.include_router(roles_controller.router, prefix="/roles")
api_router.include_router(customers_controller.router, prefix="/customers")
api_router.include_router(countries_controller.router, prefix="/countries")
api_router.include_router(state_province_controller.router, prefix="/states-provinces")
api_router.include_router(municipality_controller.router, prefix="/municipalities")
api_router.include_router(specialties_controller.router, prefix="/specialties")
api_router.include_router(supplier_controller.router, prefix="/suppliers")
api_router.include_router(store_controller.router, prefix="/stores")
api_router.include_router(cash_account_controller.router, prefix="/cash-accounts")
api_router.include_router(pos_terminal_controller.router, prefix="/pos-terminals")
api_router.include_router(shift_controller.router, prefix="/shifts")
api_router.include_router(sale_controller.router, prefix="/sales")
api_router.include_router(product_controller.router, prefix="/products")
api_router.include_router(purchase_controller.router, prefix="/purchases")
api_router.include_router(
    accounts_payable_controller.router, prefix="/accounts-payable"
)
api_router.include_router(
    accounts_receivable_controller.router,
    prefix="/accounts-receivable",
)
api_router.include_router(assistant_controller.router)

# Incluye el router principal en la aplicación
app.include_router(api_router)
