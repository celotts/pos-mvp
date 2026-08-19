from typing import Annotated

from dependencies import get_db, get_llm_service
from fastapi import APIRouter, Depends
from modules.inventory_service import InventoryAnalysisService
from modules.llm_service import LLMAnalysisService
from schemas.inventory import PurchaseSuggestionsResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get(
    "/purchase-suggestions",
    response_model=PurchaseSuggestionsResponse,
    summary="Obtener Sugerencias Inteligentes de Compra de Inventario",
    description="""
    Analiza el inventario para proveer sugerencias estructuradas y un resumen ejecutivo por IA.
    - **high_turnover**: Productos con riesgo de agotarse.
    - **seasonal**: Productos con patrones de venta estacionales.
    - **dead_stock**: Productos que no se están vendiendo.

    Si el servicio de IA no está disponible, `executive_summary` será `null`,
    pero el análisis estructurado (`analysis`) se devolverá igualmente.
    """,
)
async def get_purchase_suggestions(
    db: Annotated[AsyncSession, Depends(get_db)],
    inventory_service: Annotated[InventoryAnalysisService, Depends()],
    llm_service: Annotated[LLMAnalysisService, Depends(get_llm_service)],
):
    suggestions = await inventory_service.get_purchase_suggestions(db, llm_service)
    return suggestions
