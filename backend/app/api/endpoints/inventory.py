from dependencies import InventoryAnalysisServiceDep
from fastapi import APIRouter
from schemas.inventory import PurchaseSuggestionsResponse

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
    inventory_service: InventoryAnalysisServiceDep,
):
    return await inventory_service.get_purchase_suggestions()
