"""Servicio de agente de IA (fachada).

Compone un proveedor de chat, un proveedor de embeddings y un driver de
agentes. Sustituye al antiguo `AIService` manteniendo la misma API pública
para no romper a los consumidores (sale_service, ai_agent_service, etc.).
"""

import logging
import uuid

import httpx
from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.db import async_session_maker
from core.tenancy import get_current_tenant
from models.sale import Sale
from models.sale_item import SaleItem
from models.sales_vector import SalesVector
from service.ai.ports import ToolDef
from service.ai.tools import AGENT_TOOLS

logger = logging.getLogger(__name__)


class AgentService:
    """Agentes de inventario y BI, embeddings y RAG con proveedores inyectados."""

    def __init__(self, chat_provider=None, embedding_provider=None, driver=None):
        self.chat_provider = chat_provider
        self.embedding_provider = embedding_provider
        self.driver = driver
        self.inventory_tools: list[ToolDef] = AGENT_TOOLS

        self.agent_system_prompt = (
            "Eres un analista de inventarios y compras para un sistema POS. "
            "DEBES invocar tus herramientas para consultar la base de datos "
            "antes de dar una respuesta o sugerencia de compra."
        )
        self.analyst_system_prompt = (
            "Eres el Analista de Negocio (BI) de un sistema POS. "
            "Siempre que te pregunten por ventas, ingresos, productos, márgenes, "
            "inventario o rendimiento comercial, DEBES invocar tus herramientas "
            "(get_sales_summary, get_top_products, analyze_sales_margins, "
            "get_inventory_health_metrics) para responder con cifras EXACTAS "
            "de la base de datos. No inventes números ni estimaciones."
        )

    # --- AGENTES ---
    async def get_purchase_suggestion(
        self, db: AsyncSession, query: str, store_id=None
    ) -> str:
        """Ejecuta el Agente de Inventario pasando la sesión 'db' a las tools."""
        return await self.driver.run(
            system_prompt=self.agent_system_prompt,
            query=query,
            tools=self.inventory_tools,
            db=db,
            store_id=store_id,
        )

    async def get_analyst_response(
        self, db: AsyncSession, query: str, store_id=None
    ) -> str:
        """Ejecuta el agente BI con cifras exactas desde las herramientas."""
        return await self.driver.run(
            system_prompt=self.analyst_system_prompt,
            query=query,
            tools=self.inventory_tools,
            db=db,
            store_id=store_id,
        )

    # --- EMBEDDINGS & RAG ---
    async def get_embedding(self, text: str) -> list[float]:
        return await self.embedding_provider.embed(text)

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
                sale = result.scalars().unique().one_or_none()

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
                    sale_id=sale.id,
                    store_id=sale.store_id,
                    tenant_id=sale.tenant_id,
                    content=content,
                    embedding=embedding,
                )
                db.add(sale_vector)
                await db.commit()
                logger.info("Embedding guardado correctamente para venta %s", sale_id)
        except (httpx.HTTPError, SQLAlchemyError, KeyError):
            logger.exception(
                "Error en background task de embedding para la venta %s",
                sale_id,
            )

    async def get_rag_response(
        self, db: AsyncSession, query: str, store_id=None
    ) -> str:
        try:
            query_embedding = await self.get_embedding(query)
            context_query = (
                select(SalesVector.content)
                .order_by(SalesVector.embedding.cosine_distance(query_embedding))
                .limit(5)
            )
            tenant_id = get_current_tenant()
            if tenant_id:
                context_query = context_query.where(
                    SalesVector.tenant_id == tenant_id
                )
            if store_id:
                context_query = context_query.where(
                    or_(
                        SalesVector.store_id == store_id,
                        SalesVector.store_id.is_(None),
                    )
                )
            result = await db.execute(context_query)
            context_items = result.scalars().all()

            if not context_items:
                return "No se encontró información relevante en la base de datos."

            context_str = "\n\n".join(context_items)
            system_prompt = (
                "Eres un asistente de inteligencia de negocios para un sistema de Punto de Venta (POS). "
                "Responde a la pregunta del usuario basándote únicamente en el contexto provisto. "
                "Sé conciso y directo."
            )
            prompt = f"""
Contexto:
---
{context_str}
---

Pregunta: {query}

Respuesta:
"""
            return await self.chat_provider.complete(
                system_prompt=system_prompt, prompt=prompt
            )

        except (httpx.HTTPError, SQLAlchemyError, KeyError) as exc:
            logger.error("Error en RAG pipeline: %s", exc)
            return "Error: Ocurrió un fallo al consultar el servicio de Inteligencia Artificial."

    async def close(self) -> None:
        if self.chat_provider and hasattr(self.chat_provider, "close"):
            await self.chat_provider.close()
        if self.embedding_provider and hasattr(self.embedding_provider, "close"):
            await self.embedding_provider.close()