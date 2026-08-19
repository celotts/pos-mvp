import json
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class LLMAnalysisService:
    """
    Servicio para interactuar con un modelo de lenguaje local (Ollama)
    y generar resúmenes ejecutivos.
    """

    def __init__(self, ollama_base_url: str | None, model_name: str = "llama3"):
        self.base_url = ollama_base_url
        self.model = model_name
        if self.base_url:
            self.client = httpx.AsyncClient(base_url=self.base_url, timeout=20.0)
        else:
            self.client = None

    async def generate_executive_summary(
        self, structured_data: dict[str, Any]
    ) -> str | None:
        """
        Genera un resumen ejecutivo usando el LLM.
        Devuelve None si el servicio no está configurado o falla la conexión.
        """
        if not self.client or not self.base_url:
            logger.warning(
                "OLLAMA_BASE_URL no está configurada. Omitiendo resumen de IA."
            )
            return None

        prompt = self._build_prompt(structured_data)

        try:
            response = await self.client.post(
                "/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error(f"Error de comunicación con Ollama en {self.base_url}: {e}")
            return None  # Degradación controlada
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar la respuesta JSON de Ollama: {e}")
            return None

    def _build_prompt(self, data: dict[str, Any]) -> str:
        """Construye el prompt para el LLM basado en los datos estructurados."""
        high_turnover_count = len(data.get("high_turnover", []))
        seasonal_count = len(data.get("seasonal", []))
        dead_stock_count = len(data.get("dead_stock", []))

        return f"""
Eres un asistente experto en gestión de inventarios para un punto de venta.
Tu tarea es analizar el siguiente resumen de datos y redactar un "Resumen Ejecutivo y Sugerencia Táctica" conciso y accionable para el administrador del negocio en español.

Análisis de Datos:
1.  **Productos de Alta Rotación (Riesgo de Agotarse):** {high_turnover_count} productos.
2.  **Productos Estacionales:** {seasonal_count} productos.
3.  **Stock Muerto (Sin Rotación):** {dead_stock_count} productos.

**Instrucciones para tu respuesta:**
- Comienza con el título: "Resumen Ejecutivo y Sugerencia Táctica".
- Para 'Alta Rotación', sugiere una reposición urgente.
- Para 'Estacionales', recomienda planificar las compras para anticipar los picos de demanda.
- Para 'Stock Muerto', sugiere estrategias como ofertas, descuentos o liquidación.
- Sé breve y directo. El administrador necesita acciones claras.

Genera el resumen ahora.
""".strip()
