import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx
from core.config import settings

logger = logging.getLogger(__name__)


def _build_executive_summary_prompt(data: dict[str, Any]) -> str:
    """Construye el prompt para el LLM basado en los datos estructurados."""
    high_turnover_count = len(data.get("high_turnover", []))
    seasonal_count = len(data.get("seasonal", []))
    dead_stock_count = len(data.get("dead_stock", []))
    return f"""
Eres un asistente experto en gestión de inventarios para un punto de venta.
Tu tarea es analizar el siguiente resumen de datos y redactar un "Resumen Ejecutivo y Sugerencia Táctica" conciso y accionable para el administrador del negocio en español.
Análisis de Datos:
1. **Productos de Alta Rotación (Riesgo de Agotarse):** {high_turnover_count} productos.
2. **Productos Estacionales:** {seasonal_count} productos.
3. **Stock Muerto (Sin Rotación):** {dead_stock_count} productos.
**Instrucciones para tu respuesta:**
- Comienza con el título: "Resumen Ejecutivo y Sugerencia Táctica".
- Para 'Alta Rotación', sugiere una reposición urgente.
- Para 'Estacionales', recomienda planificar las compras para anticipar los picos de demanda.
- Para 'Stock Muerto', sugiere estrategias como ofertas, descuentos o liquidación.
- Sé breve y directo. El administrador necesita acciones claras.
Genera el resumen ahora.
""".strip()


class AbstractLLMService(ABC):
    """Clase base abstracta para cualquier servicio de Modelo de Lenguaje (LLM)."""

    @abstractmethod
    async def generate_executive_summary(
        self, structured_data: dict[str, Any]
    ) -> str | None:
        """Genera un resumen ejecutivo a partir de datos estructurados."""


class PurchaseSuggestionAnalysisException(Exception):
    """Excepción específica para el análisis de sugerencias de compra."""


class OllamaService(AbstractLLMService):
    """Servicio para interactuar con un modelo de lenguaje local (Ollama)."""

    def __init__(
        self,
        ollama_base_url: str | None = None,
        model_name: str | None = None,
    ):
        # Fallback a settings o a las URLs por defecto de la red de Podman/Docker
        self.base_url = (
            ollama_base_url
            or getattr(settings, "OLLAMA_BASE_URL", None)
            or "http://host.containers.internal:11434"
        )
        self.model = (
            model_name or getattr(settings, "LLM_MODEL", None) or "llama3.2:latest"
        )

    async def generate_executive_summary(
        self, structured_data: dict[str, Any]
    ) -> str | None:
        """Genera un resumen ejecutivo usando el LLM."""
        if not self.base_url:
            logger.warning(
                "OLLAMA_BASE_URL no está configurada. Omitiendo resumen de IA."
            )
            return "Servicio de IA no configurado."

        prompt = _build_executive_summary_prompt(structured_data)

        async with httpx.AsyncClient(base_url=self.base_url, timeout=120.0) as client:
            try:
                response = await client.post(
                    "/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False},
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "").strip()
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                logger.error(
                    f"Error de comunicación con Ollama en {self.base_url} (Modelo: {self.model}): {type(e).__name__} - {e}"
                )
                return "No fue posible generar el resumen ejecutivo debido a un fallo de conexión con la IA."


def llm_service_factory() -> OllamaService:
    return OllamaService()
