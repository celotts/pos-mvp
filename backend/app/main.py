# isort: skip_file
import sys
from pathlib import Path

# Inyecta la raíz del backend en sys.path antes de cargar los controladores
BASE_DIR = Path(__file__).resolve().parent
sys.path.extend([str(BASE_DIR), str(BASE_DIR.parent)])

from api import exception_handlers
from api.endpoints import (
    accounts_payable_controller,
    accounts_receivable_controller,
    analytics_controller,
    assistant_controller,
    cash_account_controller,
    countries_controller,
    customers_controller,
    inventory_controller,
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
from contextlib import asynccontextmanager

from core.config import settings
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from initial_data import init_db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona los eventos de inicio y apagado de la aplicación.
    Aquí se ejecuta la inicialización de la base de datos para crear las tablas.
    """
    logger.info("Iniciando aplicación y comprobando base de datos...")
    await init_db()
    yield
    logger.info("Apagando aplicación...")


is_production = settings.ENVIRONMENT.strip().lower() == "production"

app = FastAPI(
    title="POS-RAG API",
    version="0.1.0",
    description="API for inventory control with Retrieval-Augmented Generation (RAG) capabilities.",
    lifespan=lifespan,
    docs_url="/docs" if not is_production else None,
    redoc_url="/redoc" if not is_production else None,
    openapi_url="/openapi.json" if not is_production else None,
)

# CORS: allowlist explícita en lugar de '*'
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Handlers de error unificados (formato JSON consistente, sin fugas de detalle)
app.add_exception_handler(
    HTTPException,
    exception_handlers.http_exception_handler,
)
app.add_exception_handler(
    RequestValidationError,
    exception_handlers.request_validation_exception_handler,
)
app.add_exception_handler(IntegrityError, exception_handlers.integrity_error_handler)
app.add_exception_handler(SQLAlchemyError, exception_handlers.sqlalchemy_error_handler)
app.add_exception_handler(Exception, exception_handlers.unhandled_exception_handler)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Añade cabeceras de seguridad básicas a todas las respuestas."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


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
api_router.include_router(
    inventory_controller.router, prefix="/inventory", tags=["Inventory"]
)

# Asistente de IA
api_router.include_router(assistant_controller.router)  # Ya tiene prefijo y tag

# Analítica Comercial (Market Basket + Stockout)
api_router.include_router(analytics_controller.router)

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
