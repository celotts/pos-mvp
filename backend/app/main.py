from contextlib import asynccontextmanager

from api.endpoints import (
    accounts_payable_controller,
    accounts_receivable_controller,
    assistant_controller,
    cash_account_controller,
    countries_controller,
    customers_controller,
    inventory,
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
from fastapi import APIRouter, FastAPI
from initial_data import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona los eventos de inicio y apagado de la aplicación.
    Aquí se ejecuta la inicialización de la base de datos para crear las tablas.
    """
    await init_db()
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
# --- Inclusión de todos los routers ---
# Autenticación y Usuarios
api_router.include_router(login_controller.router, tags=["Bootstrap & Auth"])
api_router.include_router(users_controller.router, prefix="/users", tags=["Users"])
api_router.include_router(roles_controller.router, prefix="/roles", tags=["Roles"])
# Entidades Principales (Productos, Clientes, etc.)
api_router.include_router(
    product_controller.router, prefix="/products", tags=["Products"]
)
api_router.include_router(
    customers_controller.router, prefix="/customers", tags=["Customers"]
)
api_router.include_router(
    supplier_controller.router, prefix="/suppliers", tags=["Suppliers"]
)
api_router.include_router(store_controller.router, prefix="/stores", tags=["Stores"])
# Operaciones del Punto de Venta (POS)
api_router.include_router(
    pos_terminal_controller.router, prefix="/terminals", tags=["POS"]
)
api_router.include_router(shift_controller.router, prefix="/shifts", tags=["POS"])
api_router.include_router(sale_controller.router, prefix="/sales", tags=["POS"])
# Compras e Inventario
api_router.include_router(
    purchase_controller.router, prefix="/purchases", tags=["Purchases"]
)
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
# Asistente de IA
api_router.include_router(assistant_controller.router)  # Ya tiene prefijo y tag
# Localización Geográfica
api_router.include_router(
    countries_controller.router, prefix="/countries", tags=["Locations"]
)
api_router.include_router(
    state_province_controller.router, prefix="/states", tags=["Locations"]
)
api_router.include_router(
    municipality_controller.router, prefix="/municipalities", tags=["Locations"]
)
# Contabilidad
api_router.include_router(
    cash_account_controller.router, prefix="/cash-accounts", tags=["Accounting"]
)
api_router.include_router(
    accounts_payable_controller.router, prefix="/accounts-payable", tags=["Accounting"]
)
api_router.include_router(
    accounts_receivable_controller.router,
    prefix="/accounts-receivable",
    tags=["Accounting"],
)
# Otros
api_router.include_router(
    specialties_controller.router, prefix="/specialties", tags=["Specialties"]
)
app.include_router(api_router)
