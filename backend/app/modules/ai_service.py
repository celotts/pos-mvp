import logging
import uuid

import httpx
from core.config import settings
from core.db import async_session_maker
from models.sale import Sale
from models.sale_item import SaleItem
from models.sales_vector import SalesVector
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.embedding_model = settings.EMBEDDING_MODEL
        self.llm_model = settings.LLM_MODEL
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Inicialización perezosa (lazy) del cliente asíncrono para evitar cierres prematuros."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.ollama_base_url, timeout=60.0
            )
        return self._client

    async def close(self) -> None:
        """Cierra el cliente HTTP cuando la aplicación finaliza."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get_embedding(self, text: str) -> list[float]:
        """Genera un embedding para el texto provisto utilizando Ollama."""
        try:
            response = await self.client.post(
                "/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
            )
            response.raise_for_status()
            data = response.json()
            return data["embedding"]
        except (httpx.RequestError, httpx.HTTPStatusError, KeyError) as e:
            logger.error(f"Error generando embedding en Ollama: {e}")
            raise

    async def create_and_store_sale_embedding(self, sale_id: uuid.UUID) -> None:
        """Tarea en segundo plano para generar y guardar el embedding de una venta."""
        try:
            async with async_session_maker() as db:
                query = (
                    select(Sale)
                    .where(Sale.id == sale_id)
                    .options(
                        joinedload(Sale.items).joinedload(SaleItem.product),
                        joinedload(Sale.user),
                        joinedload(Sale.store),
                    )
                )
                result = await db.execute(query)
                sale = result.scalars().one_or_none()

                if not sale:
                    logger.warning(f"Venta ID {sale_id} no encontrada para embedding.")
                    return

                items_desc = ", ".join(
                    [f"{item.quantity}x '{item.product.name}'" for item in sale.items]
                )
                content = (
                    f"Venta realizada el {sale.created_at.strftime('%Y-%m-%d %H:%M')} "
                    f"en la tienda '{sale.store.name}'. Vendedor '{sale.user.full_name}' "
                    f"vendió: {items_desc}. Monto total: {sale.total_amount}."
                )

                embedding = await self.get_embedding(content)
                sale_vector = SalesVector(
                    sale_id=sale.id, content=content, embedding=embedding
                )
                db.add(sale_vector)
                await db.commit()
                logger.info(f"Embedding guardado correctamente para venta {sale_id}")
        except (httpx.HTTPError, SQLAlchemyError, KeyError) as e:
            logger.exception(
                f"Error en background task de embedding para la venta {sale_id}: {e}"
            )

    async def get_rag_response(self, db: AsyncSession, query: str) -> str:
        """Pipeline RAG con búsqueda vectorial y generación de respuesta."""
        try:
            query_embedding = await self.get_embedding(query)

            # Usamos cosine_distance para mejor precisión semántica
            context_query = (
                select(SalesVector.content)
                .order_by(SalesVector.embedding.cosine_distance(query_embedding))
                .limit(5)
            )
            result = await db.execute(context_query)
            context_items = result.scalars().all()

            if not context_items:
                return "No se encontró información relevante en la base de datos."

            context_str = "\n\n".join(context_items)
            prompt = f"""
Eres un asistente de inteligencia de negocios para un sistema de Punto de Venta (POS).
Responde a la pregunta del usuario basándote únicamente en el contexto provisto.
Sé conciso y directo.

Contexto:
---
{context_str}
---

Pregunta: {query}

Respuesta:
"""

            response = await self.client.post(
                "/api/generate",
                json={
                    "model": self.llm_model,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()

        except (httpx.HTTPError, SQLAlchemyError, KeyError) as e:
            logger.error(f"Error en RAG pipeline: {e}")
            return "Error: Ocurrió un fallo al consultar el servicio de Inteligencia Artificial."

    async def get_quarterly_prediction_response(
        self, db: AsyncSession, query: str
    ) -> str:
        """Agrega métricas mensuales y solicita predicciones o análisis estratégico al LLM."""
        try:
            agg_query = (
                select(
                    func.date_trunc("month", Sale.sale_date).label("month"),
                    func.count(Sale.id).label("total_sales_count"),
                    func.sum(Sale.total_amount).label("total_revenue"),
                )
                .where(Sale.status == "COMPLETED")
                .group_by(func.date_trunc("month", Sale.sale_date))
                .order_by(func.date_trunc("month", Sale.sale_date).desc())
                .limit(12)
            )

            result = await db.execute(agg_query)
            rows = result.all()

            if not rows:
                return "No hay suficientes datos de ventas completadas para generar una predicción."

            context_lines = [
                f"- Mes: {row.month.strftime('%Y-%m') if row.month else 'N/A'} | "
                f"Ventas: {row.total_sales_count} | Ingresos: ${row.total_revenue or 0}"
                for row in rows
            ]
            context_str = "\n".join(context_lines)

            prompt = f"""
Eres un Analista de Negocios y Estratega de Ventas para un sistema POS.
Analiza las siguientes métricas históricas agregadas y responde a la consulta ofreciendo recomendaciones accionables.

Datos Históricos Agregados (Últimos meses):
---
{context_str}
---

Consulta del Usuario: {query}

Análisis y Predicción:
"""

            response = await self.client.post(
                "/api/generate",
                json={
                    "model": self.llm_model,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()

        except (httpx.HTTPError, SQLAlchemyError, KeyError) as e:
            logger.error(f"Error en predicción trimestral: {e}")
            return "Error: No se pudo procesar la solicitud con el servicio de Inteligencia Artificial."


ai_service = AIService()
