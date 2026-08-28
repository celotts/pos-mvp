from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        ..., description="Consulta del usuario o directivo sobre el negocio."
    )
    context_store_id: int | None = Field(
        None, description="ID de la tienda para filtrar analíticas."
    )


class InsightRecommendation(BaseModel):
    category: str = Field(..., description="Categoría: INVENTORY, SALES, MARGIN, RISK")
    action_item: str = Field(..., description="Acción concreta sugerida")
    impact_level: str = Field(..., description="HIGH, MEDIUM, LOW")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="Análisis ejecutivo o respuesta a la consulta")
    insights: list[InsightRecommendation] = Field(default_factory=list)
    raw_metrics: dict[str, Any] | None = Field(default=None)
