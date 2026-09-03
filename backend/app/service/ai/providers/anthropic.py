"""Proveedor de IA basado en Anthropic (Claude).

El proveedor de chat funciona vía HTTP sin dependencias extra. El agente,
sin embargo, requiere `langchain-anthropic` para construir un chat model
compatible con el driver; si no está instalado, el agente no estará
disponible y devolverá un mensaje claro (no se inventa soporte inexistente).
"""

import httpx

from core.config import settings
from utils.logger import logger


class AnthropicChatProvider:
    """Cubre IChatProvider usando la Messages API de Anthropic."""

    name = "anthropic"
    API_URL = "https://api.anthropic.com/v1/messages"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or getattr(settings, "ANTHROPIC_API_KEY", "") or ""
        self.model = model or getattr(settings, "ANTHROPIC_MODEL", "") or "claude-3-5-sonnet-20241022"

    async def complete(self, *, system_prompt: str, prompt: str) -> str:
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY no configurada. Omitiendo llamada de IA.")
            return "Servicio de IA no configurado."

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "system": system_prompt or "Eres un asistente experto de negocios.",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(self.API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            blocks = data.get("content", [])
            return "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()

    def get_chat_model(self):
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError as exc:  # pragma: no cover - depende del entorno
            raise RuntimeError(
                "El agente (driver) con Anthropic requiere instalar 'langchain-anthropic'."
            ) from exc
        return ChatAnthropic(model=self.model, api_key=self.api_key, temperature=0)

    async def close(self) -> None:
        return None