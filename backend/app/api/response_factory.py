from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

# Define un TypeVar para poder usar tipos genéricos en el modelo de respuesta.
# Esto permite que el campo 'response' pueda ser una lista, un objeto, etc.
T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Modelo base para respuestas de API estandarizadas."""

    success: bool = Field(True, description="Indica si la operación fue exitosa.")
    status_code: int = Field(200, description="Código de estado HTTP.")
    message: str = Field(
        "Operation successful", description="Descriptive message of the response."
    )
    data: T | None = Field(None, description="El contenido de la respuesta (payload).")


def create_api_response(
    *,
    data: T | None = None,
    status_code: int = 200,
    message: str = "Operation successful",
    success: bool = True,
) -> ApiResponse[Any]:
    """Factory para crear respuestas de API estandarizadas."""
    return ApiResponse(
        success=success, status_code=status_code, message=message, data=data
    )
