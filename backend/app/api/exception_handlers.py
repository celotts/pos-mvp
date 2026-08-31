import logging

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

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
    return _error_response(
        status_code=422,
        message="Validation error. Check the request payload.",
        data=exc.errors(),
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """SQLAlchemy IntegrityError (duplicados, violación de constraints) -> 409."""
    return _error_response(
        status_code=409, message="The resource conflicts with existing data."
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """Cualquier otro error SQLAlchemy -> 500 sin filtrar detalles/internals."""
    logger.error("DB error: %s", exc)
    return _error_response(
        status_code=500, message="A database error occurred. Please try again."
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
            "message": "Too many login attempts. Please try again later.",
            "data": None,
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    """Último recurso: nunca expone stack traces ni detalles internos."""
    logger.error("Unhandled error: %s", exc)
    return _error_response(
        status_code=500, message="An unexpected internal error occurred."
    )
