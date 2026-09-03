import logging

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from core.i18n import tr

logger = logging.getLogger("pos.api")


def _error_response(status_code: int, message: str, data=None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "status_code": status_code,
            "message": message,
            "data": data,
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejador de excepciones global para formatear errores HTTP."""
    headers = getattr(exc, "headers", None)
    response = _error_response(exc.status_code, exc.detail)
    if headers:
        for key, value in headers.items():
            response.headers[key] = value
    return response


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    """Devuelve un 422 JSON unificado en vez del payload por defecto de FastAPI."""
    try:
        errors = _serializable_validation_errors(exc.errors())
    except Exception:  # el manejo de errores jamás debe crashear
        logger.exception("Error serializando errores de validación")
        errors = None

    # Mensaje descriptivo si hay un error de UUID malformado.
    uuid_message = _first_uuid_error_message(errors)
    message = uuid_message or tr("VALIDATION.ERROR")
    return _error_response(status_code=422, message=message, data=errors)


def _first_uuid_error_message(errors):
    """Devuelve un mensaje descriptivo para el primer error de tipo UUID, o None."""
    if not errors:
        return None
    for err in errors:
        if err.get("type") in ("uuid_parsing", "uuid_type"):
            loc = err.get("loc", [])
            field = ".".join(str(x) for x in loc if x not in ("body", "query", "path"))
            value = err.get("input")
            return tr(
                "VALIDATION.UUID_INVALID",
                field=field,
                value=str(value),
            )
    return None


def _serializable_validation_errors(errors: list[dict]):
    """Limpia los errores de validación para que JSONResponse pueda serializarlos.

    FastAPI incluye valores crudos (`input`) en los errores; cuando el body no era
    JSON estos llegan como `bytes` y rompen la serialización. Los convertimos.
    """

    def _clean(value):
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        if isinstance(value, dict):
            return {k: _clean(v) for k, v in value.items()}
        if isinstance(value, list):
            return [_clean(item) for item in value]
        return value

    return _clean(errors)


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """SQLAlchemy IntegrityError (duplicados, violación de constraints) -> 409."""
    logger.error(
        "IntegrityError on %s %s: %s",
        request.method,
        request.url.path,
        exc.orig,
    )
    # Intentar extraer un detalle legible del error del driver.
    detail_msg = ""
    orig = getattr(exc, "orig", None)
    if orig is not None:
        # psycopg2 / psycopg
        diag = getattr(orig, "diag", None)
        if diag:
            detail_msg = getattr(diag, "message_primary", "") or getattr(
                diag, "message_detail", ""
            )
        # asyncpg
        if not detail_msg:
            detail_msg = getattr(orig, "detail", "") or getattr(orig, "msg", "")
        if not detail_msg:
            detail_msg = str(orig)

    # Resumir a una línea clara, sin basura técnica.
    detail_msg = detail_msg.split("\n")[0].strip()[:200] or ""

    if detail_msg:
        message = tr("DB.INTEGRITY_DETAIL", detail=detail_msg)
    else:
        message = tr("DB.INTEGRITY_GENERIC")

    return _error_response(status_code=409, message=message)


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """Cualquier otro error SQLAlchemy -> 500 sin filtrar detalles/internals."""
    logger.error("DB error: %s", exc)
    return _error_response(
        status_code=500, message=tr("DB.GENERIC")
    )


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Límite de peticiones excedido (login) -> 429 con formato unificado."""
    return JSONResponse(
        status_code=429,
        headers={
            "Retry-After": "60",
        },
        content={
            "success": False,
            "status_code": 429,
            "message": tr("RATE_LIMIT"),
            "data": None,
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    """Último recurso: nunca expone stack traces ni detalles internos."""
    logger.error("Unhandled error: %s", exc)
    return _error_response(
        status_code=500, message=tr("SERVER.UNEXPECTED")
    )
