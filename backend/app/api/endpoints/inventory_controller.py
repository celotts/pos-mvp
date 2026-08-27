from dependencies import InventoryAnalysisServiceDep
from fastapi import APIRouter, status
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


@router.get("/inventory/purchase-suggestion")
async def get_purchase_suggestion(
    inventory_service: InventoryAnalysisServiceDep,
    query: str = "Analiza las ventas y compras para sugerir reabastecimiento",
):
    response = await inventory_service.get_agent_suggestion(query)
    return {"suggestion": response}


@router.post(
    "/vectorize-analysis",
    summary="Vectorizar y almacenar análisis de inventario",
    description="Ejecuta el análisis de inventario, genera el embedding local con Ollama y lo persiste en pgvector.",
    status_code=status.HTTP_201_CREATED,
)
async def vectorize_inventory_analysis(
    inventory_service: InventoryAnalysisServiceDep,
) -> dict:
    suggestions_response = await inventory_service.get_purchase_suggestions()
    analysis_dict = suggestions_response.analysis.model_dump()
    await inventory_service.generate_and_store_vector_analysis(analysis_dict)

    return {"message": "Análisis de inventario vectorizado y guardado exitosamente."}
