from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.assistant import ChatRequest, ChatResponse, InsightRecommendation
from service.ai.agent_service import AgentService
from service.ai.factory import ai_service
from utils.logger import logger

SYSTEM_PROMPT = (
    "Eres el Asistente Ejecutivo de Toma de Decisiones de pos-API. "
    "Tu objetivo es ayudar al dueño o gerente del negocio a maximizar ganancias, "
    "optimizar inventario y prevenir pérdidas. Responde siempre con datos concretos, "
    "justifica tus recomendaciones y prioriza acciones de alto impacto."
)


class AIAgentService:
    system_prompt = SYSTEM_PROMPT

    def __init__(self, agent_service: AgentService | None = None):
        self.agent_service = agent_service or ai_service

    async def process_decision_request(
        self, db: AsyncSession, request: ChatRequest
    ) -> ChatResponse:
        logger.info("Procesando solicitud de decisión: %s", request.message)

        store_id = request.context_store_id
        try:
            # 1er intento: agente BI con cifras exactas desde las herramientas.
            response_text = await self.agent_service.get_analyst_response(
                db=db, query=request.message, store_id=store_id
            )
        except (SQLAlchemyError, RuntimeError, ValueError) as err:
            logger.error(
                "Error ejecutando agente BI: %s. Degradando a RAG.", err, exc_info=True
            )
            try:
                response_text = await self.agent_service.get_rag_response(
                    db=db, query=request.message, store_id=store_id
                )
            except (SQLAlchemyError, RuntimeError, ValueError) as rag_err:
                logger.error("Error en RAG: %s", rag_err, exc_info=True)
                return ChatResponse(
                    answer=f"Error al generar la consulta: {rag_err}",
                    insights=[],
                    raw_metrics=None,
                )

        insights = self._extract_insights(response_text)

        return ChatResponse(
            answer=response_text,
            insights=insights,
            raw_metrics=None,
        )

    @staticmethod
    def _extract_insights(response_text: str) -> list[InsightRecommendation]:
        text_lower = response_text.lower()
        insights: list[InsightRecommendation] = []

        rules = (
            ("SALES", "Sales", "in venta", "ventas", "facturación"),
            ("INVENTORY", "Inventory", "inventario", "stock", "existencia"),
            ("MARGIN", "Margin", "margen", "rentabilidad"),
            ("RISK", "Risk", "riesgo", "pérdida", "pérdidas"),
        )

        for category, label, *keywords in rules:
            if any(keyword in text_lower for keyword in keywords):
                insights.append(
                    InsightRecommendation(
                        category=category,
                        action_item=f"Aprovechar la oportunidad detectada en {label}.",
                        impact_level="MEDIUM",
                    )
                )

        return insights


ai_agent_service = AIAgentService()
