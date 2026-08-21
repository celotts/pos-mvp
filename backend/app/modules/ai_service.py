import uuid

import httpx
from core.config import settings
from core.db import async_session_maker
from models.sale import Sale, SaleItem
from models.sales_vector import SalesVector
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class AIService:
    def __init__(self):
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.embedding_model = settings.EMBEDDING_MODEL
        self.llm_model = settings.LLM_MODEL
        self.client = httpx.AsyncClient(base_url=self.ollama_base_url, timeout=60.0)

    async def get_embedding(self, text: str) -> list[float]:
        """Generates an embedding for the given text using the Ollama service."""
        try:
            response = await self.client.post(
                "/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except httpx.RequestError as e:
            print(f"Error connecting to Ollama: {e}")
            raise
        except httpx.HTTPStatusError as e:
            print(
                f"Ollama returned an error: {e.response.status_code} - {e.response.text}"
            )
            raise

    async def create_and_store_sale_embedding(self, sale_id: uuid.UUID) -> None:
        """
        Generates and stores an embedding for a given sale.
        This is designed to be called as a background task after a sale is created.
        """
        # Crea una sesión de BD independiente para esta tarea en segundo plano
        async with async_session_maker() as db:
            # Cargar la venta con todas sus relaciones para construir el texto
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
                print(f"Error: Sale with id {sale_id} not found for embedding.")
                return

            # Construir un texto descriptivo para la venta
            items_desc = ", ".join(
                [f"{item.quantity}x '{item.product.name}'" for item in sale.items]
            )
            content = f"Sale made on {sale.created_at.strftime('%Y-%m-%d %H:%M')} at store '{sale.store.name}'. User '{sale.user.full_name}' sold: {items_desc}. Total amount: {sale.total_amount}."

            embedding = await self.get_embedding(content)
            sale_vector = SalesVector(
                sale_id=sale.id, content=content, embedding=embedding
            )
            db.add(sale_vector)
            await db.commit()

    async def get_rag_response(self, db: AsyncSession, query: str) -> str:
        """
        Performs the RAG pipeline:
        1. Embeds the query.
        2. Finds relevant context from the database.
        3. Sends the query and context to an LLM to generate a response.
        """
        # 1. Embed the user's query
        query_embedding = await self.get_embedding(query)

        # 2. Find relevant context from the database using pgvector
        # We search for the 5 most similar sales descriptions
        context_query = (
            select(SalesVector.content)
            .order_by(SalesVector.embedding.l2_distance(query_embedding))
            .limit(5)
        )
        result = await db.execute(context_query)
        context_items = result.scalars().all()

        if not context_items:
            return "Sorry, I could not find relevant information in the database to answer your question."

        context_str = "\n\n".join(context_items)

        # 3. Build the prompt for the LLM
        prompt = f"""
        You are a business intelligence assistant for a Point of Sale (POS) system.
        Your task is to answer the user's question based solely on the following context extracted from the sales database.
        Be concise and direct in your answer.

        Contexto:
        ---
        {context_str}
        ---

        User question: {query}

        Respuesta:
        """

        # 4. Send to the LLM to generate a response
        try:
            response = await self.client.post(
                "/api/generate",
                json={"model": self.llm_model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            return response.json()["response"].strip()
        except httpx.RequestError:
            return "Error: Could not connect to the AI service."
        except httpx.HTTPStatusError:
            return "Error: The AI service returned an error."


ai_service = AIService()
