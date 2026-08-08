from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

# Define un TypeVar para poder usar tipos genéricos en el modelo de respuesta.
# Esto permite que el campo 'response' pueda ser una lista, un objeto, etc.
T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Modelo base para respuestas de API estandarizadas."""

    codigo: int = Field(200, description="Código de estado HTTP.")
    comment: str = Field("OK", description="Mensaje descriptivo de la respuesta.")
    response: T | None = Field(
        None, description="El contenido de la respuesta (payload)."
    )


def create_api_response(
    data: Any, status_code: int = 200, message: str = "OK"
) -> ApiResponse[Any]:
    """Factory para crear respuestas de API estandarizadas."""
    return ApiResponse(codigo=status_code, comment=message, response=data)
