from schemas.assistant import ChatRequest, ChatResponse, InsightRecommendation
from service.ai_service import ai_service
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import logger


class AIAgentService:
    def __init__(self):
        self.system_prompt = (
            "Eres el Asistente Ejecutivo de Toma de Decisiones de pos-API. "
            "Tu objetivo es ayudar al dueño o gerente del negocio a maximizar ganancias, "
            "optimizar inventario y prevenir pérdidas. Responde siempre con datos concretos, "
            "justifica tus recomendaciones y prioriza acciones de alto impacto."
        )

    async def process_decision_request(
        self, db: AsyncSession, request: ChatRequest
    ) -> ChatResponse:
        logger.info(f"Procesando solicitud de decisión: {request.message}")

        try:
            # 1. Ejecutar análisis del LLM (RAG)
            response_text = await ai_service.get_rag_response(
                db=db, query=request.message
            )
        except (SQLAlchemyError, RuntimeError, ValueError) as err:
            logger.error(f"Error procesando la solicitud de IA: {err}", exc_info=True)
            response_text = f"Error al generar la consulta: {err}"

        # 3. Estructurar la respuesta para el cliente
        return ChatResponse(
            answer=response_text,
            insights=[
                InsightRecommendation(
                    category="INVENTORY",
                    action_item="Revisar inventario según el análisis provisto.",
                    impact_level="MEDIUM",
                )
            ],
            raw_metrics=None,
        )


ai_agent_service = AIAgentService()
