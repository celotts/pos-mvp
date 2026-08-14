import httpx
from core.config import settings
from models.sales_vector import SalesVector
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


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
            return "Lo siento, no encontré información relevante en la base de datos para responder a tu pregunta."

        context_str = "\n\n".join(context_items)

        # 3. Build the prompt for the LLM
        prompt = f"""
        Eres un asistente de inteligencia de negocio para un sistema de Punto de Venta (POS).
        Tu tarea es responder a la pregunta del usuario basándote únicamente en el siguiente contexto extraído de la base de datos de ventas.
        Sé conciso y directo en tu respuesta.

        Contexto:
        ---
        {context_str}
        ---

        Pregunta del usuario: {query}

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
            return "Error: No se pudo conectar con el servicio de IA."
        except httpx.HTTPStatusError:
            return "Error: El servicio de IA devolvió un error."


ai_service = AIService()
