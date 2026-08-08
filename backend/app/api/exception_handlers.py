from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from .response_factory import create_api_response


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Manejador de excepciones global para capturar HTTPException y devolver
    una respuesta estandarizada.
    """
    api_response = create_api_response(
        data=None,  # No hay payload de datos en un error
        status_code=exc.status_code,
        message=exc.detail,
    )

    return JSONResponse(status_code=exc.status_code, content=api_response.model_dump())
