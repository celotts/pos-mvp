"""Puertos (interfaces) del subsistema de IA, desacoplados de cualquier framework."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class ToolDef:
    """Definición de una herramienta agnóstica al framework de agentes.

    `func` es una función asíncrona con firma ``(db, store_id=None, **kwargs)``
    que devuelve un dict. El driver de agentes la envuelve para exponerla al LLM.
    """

    name: str
    description: str
    func: Callable[..., Awaitable[dict]]


@runtime_checkable
class IChatProvider(Protocol):
    """Abstrae el modelo de chat usado por el agente y por RAG."""

    name: str

    def get_chat_model(self) -> Any:
        """Devuelve un chat model compatible con el driver de agentes (langchain).

        Puede lanzar una excepción si el proveedor no dispone de las dependencias
        necesarias (p. ej. langchain-anthropic para Anthropic).
        """
        ...

    async def complete(self, *, system_prompt: str, prompt: str) -> str:
        """Generación simple de texto (usada por el pipeline RAG)."""
        ...

    async def close(self) -> None: ...


@runtime_checkable
class IEmbeddingProvider(Protocol):
    """Abstrae el generador de embeddings."""

    name: str

    async def embed(self, text: str) -> list[float]: ...

    async def close(self) -> None: ...