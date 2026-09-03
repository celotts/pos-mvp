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

import uuid

from sqlalchemy import text

from core.config import settings
from core.db import async_session_maker
from core.i18n import detect_lang, set_current_lang
from core.rate_limit import api_limiter
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from initial_data import init_db
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
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
# Necesario para slowapi: el limiter debe exponerse en app.state.
app.state.limiter = api_limiter
# Middleware de rate limit GLOBAL (slowapi): aplica `api_limiter.default_limits`
# a todas las rutas como red de seguridad anti-DoS/abuso por IP. Los endpoints
# de autenticación sobrescriben con un límite más estricto vía @login_limiter.
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(
    HTTPException,
    exception_handlers.http_exception_handler,
)
app.add_exception_handler(
    RequestValidationError,
    exception_handlers.request_validation_exception_handler,
)
app.add_exception_handler(
    RateLimitExceeded,
    exception_handlers.rate_limit_exceeded_handler,
)
app.add_exception_handler(IntegrityError, exception_handlers.integrity_error_handler)
app.add_exception_handler(SQLAlchemyError, exception_handlers.sqlalchemy_error_handler)
app.add_exception_handler(Exception, exception_handlers.unhandled_exception_handler)

# Whitelist de rutas /api/v1/* que NO requieren Bearer token. Todo lo demás bajo
# /api/v1/ EXIGE autenticación por defecto (fail-closed): un endpoint nuevo que se
# olvide de declarar la dependencia queda protegido en vez de público. Las rutas
# fuera de /api/v1 (health, docs, openapi) quedan intactas.
_PUBLIC_API_ROUTES = (
    "/api/v1/login/access-token",
    "/api/v1/login/swagger",
    "/api/v1/login/refresh",
    "/api/v1/logout",
)


@app.middleware("http")
async def auth_fail_closed_middleware(request: Request, call_next):
    """Exige Authorization Bearer en /api/v1/* salvo whitelist explícita.

    Red de seguridad: no valida credenciales (eso lo hacen las dependencias por
    permiso), solo garantiza que no exista un endpoint /api/v1/ público no
    intencionado. Falla a 401 si falta el token.
    """
    path = request.url.path
    if (
        request.method == "OPTIONS"
        or not path.startswith("/api/v1/")
        or path in _PUBLIC_API_ROUTES
    ):
        return await call_next(request)

    if not request.headers.get("authorization"):
        return exception_handlers._error_response(401, "Not authenticated")

    return await call_next(request)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Añade cabeceras de seguridad, detección de idioma y no-cacheo de respuestas autenticadas."""
    set_current_lang(detect_lang(request.headers.get("accept-language")))
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    # Evitar que proxies/caches almacenen respuestas que pueden contener datos
    # o tokens: no-store si la petición trae credenciales (Authorization/Bearer)
    # o si la respuesta ya es un 401/403 (nunca cachear errores de auth).
    if request.headers.get("authorization") or response.status_code in (401, 403):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Asigna un X-Request-ID a cada request para correlación en logs.

    Reusa el header entrante si llega de un gateway upstream (para mantener la
    cadena) o genera un UUID. Se registra como la capa más externa para que TODA
    respuesta (incluidos los 401 del fail-closed) lleve el request-id. El id
    queda en request.state y se devuelve como header en la respuesta.
    """
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health", tags=["System"])
async def health_check() -> dict:
    """Healthcheck liviano para orquestadores/probes de contenedor."""
    return {
        "success": True,
        "status": "ok",
        "service": "pos-rag-api",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/ready", tags=["System"])
async def readiness_check() -> JSONResponse:
    """Readiness: verifica conectividad real con la BD.

    Devuelve 200 cuando la app puede atender tráfico (BD accesible) y 503
    con el detalle si la BD no responde, para que orquestadores no enruten
    tráfico a un nodo no preparado.
    """
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "status": "not_ready",
                "service": "pos-rag-api",
                "reason": type(exc).__name__,
            },
        )
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "status": "ready",
            "service": "pos-rag-api",
            "environment": settings.ENVIRONMENT,
        },
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
