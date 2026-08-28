import logging
import uuid
from typing import Any

import httpx
from core.config import settings
from core.db import async_session_maker
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama
from models.sale import Sale
from models.sale_item import SaleItem
from models.sales_vector import SalesVector
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .agent_tools import (
    analyze_sales_margins,
    get_inventory_health_metrics,
)

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.embedding_model = settings.EMBEDDING_MODEL
        self.llm_model = settings.LLM_MODEL
        self._client: httpx.AsyncClient | None = None

        # Configuración del Agente de Inventario / Sugerencias
        self.agent_llm = ChatOllama(
            model=self.llm_model,
            base_url=self.ollama_base_url,
            temperature=0,
        )
        self.agent_tools: list[Any] = [
            analyze_sales_margins,
            get_inventory_health_metrics,
        ]
        self.agent_system_prompt = (
            "Eres un analista de inventarios y compras para un sistema POS. "
            "DEBES invocar tus herramientas (analyze_sales_margins, get_inventory_health_metrics) "
            "para consultar la base de datos antes de dar una respuesta o sugerencia de compra."
        )
        self.agent_executor = create_agent(
            model=self.agent_llm,
            tools=self.agent_tools,
        )

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.ollama_base_url, timeout=60.0
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # --- MÉTODO DEL AGENTE REFACTORIZADO ---
    async def get_purchase_suggestion(self, query: str) -> str:
        """Ejecuta el Agente de Inteligencia para analizar datos de inventario y dar sugerencias."""
        try:
            result = await self.agent_executor.ainvoke(
                {
                    "messages": [
                        SystemMessage(content=self.agent_system_prompt),
                        ("user", query),
                    ]
                }
            )
            messages = result.get("messages")
            if not messages:
                raise KeyError("messages")

            return str(messages[-1].content)
        except Exception:
            logger.exception("Error ejecutando el agente de sugerencias")
            return (
                "Error: No se pudo generar la sugerencia de inventario en este momento."
            )

    # --- VECTOR EMBEDDINGS & RAG ---
    async def get_embedding(self, text: str) -> list[float]:
        try:
            response = await self.client.post(
                "/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except (httpx.RequestError, httpx.HTTPStatusError, KeyError) as e:
            logger.error("Error generando embedding en Ollama: %s", e)
            raise

    async def create_and_store_sale_embedding(self, sale_id: uuid.UUID) -> None:
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
                    logger.warning("Venta ID %s no encontrada para embedding.", sale_id)
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
                logger.info("Embedding guardado correctamente para venta %s", sale_id)
        except (httpx.HTTPError, SQLAlchemyError, KeyError):
            logger.exception(
                "Error en background task de embedding para la venta %s", sale_id
            )

    async def get_rag_response(self, db: AsyncSession, query: str) -> str:
        try:
            query_embedding = await self.get_embedding(query)
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
            logger.error("Error en RAG pipeline: %s", e)
            return "Error: Ocurrió un fallo al consultar el servicio de Inteligencia Artificial."


ai_service = AIService()
