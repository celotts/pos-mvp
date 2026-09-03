"""Proveedor de IA basado en Ollama (URL + modelo configurables)."""

import httpx
from langchain_ollama import ChatOllama

from core.config import settings
from utils.logger import logger

# nomic-embed-text falla (>500) si el prompt supera su contexto (8192 tokens).
# Con texto "real" (tildes, JSON, números) el equivalente seguro ronda 4000
# caracteres; se trunca para que ningún texto legítimo rompa el embedding.
EMBEDDING_MAX_CHARS = 4000


def _ollama_base_url() -> str:
    return getattr(settings, "OLLAMA_BASE_URL", None) or "http://host.containers.internal:11434"


class OllamaChatProvider:
    """Cubre IChatProvider usando el endpoint /api/generate de Ollama."""

    name = "ollama"

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = base_url or _ollama_base_url()
        self.model = model or getattr(settings, "LLM_MODEL", None) or "llama3.2:latest"
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)
        return self._client

    def get_chat_model(self) -> ChatOllama:
        return ChatOllama(model=self.model, base_url=self.base_url, temperature=0)

    async def complete(self, *, system_prompt: str, prompt: str) -> str:
        body = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = await self.client.post(
            "/api/generate", json={"model": self.model, "prompt": body, "stream": False}
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()


class OllamaEmbeddingProvider:
    """Cubre IEmbeddingProvider usando el endpoint /api/embeddings de Ollama."""

    name = "ollama"

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = base_url or _ollama_base_url()
        self.model = model or getattr(settings, "EMBEDDING_MODEL", None) or "nomic-embed-text"
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)
        return self._client

    async def embed(self, text: str) -> list[float]:
        if len(text) > EMBEDDING_MAX_CHARS:
            logger.warning(
                "Truncando texto para embeddings (%d -> %d caracteres)",
                len(text),
                EMBEDDING_MAX_CHARS,
            )
            text = text[:EMBEDDING_MAX_CHARS]
        response = await self.client.post(
            "/api/embeddings", json={"model": self.model, "prompt": text}
        )
        response.raise_for_status()
        return response.json()["embedding"]

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()