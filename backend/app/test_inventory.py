import pytest
from httpx import AsyncClient

from app.dependencies import get_llm_service
from app.main import app
from app.modules.llm_service import LLMAnalysisService
from app.schemas.inventory import PurchaseSuggestionsAnalysis

# Datos de análisis simulados que devolvería el servicio de inventario
MOCK_ANALYSIS_DATA = {
    "analysis": PurchaseSuggestionsAnalysis(
        high_turnover=[
            {
                "product_id": 1,
                "product_name": "Test Product High",
                "stock_quantity": 5,
                "classification": "high_turnover",
                "days_of_stock_left": 3.0,
                "total_quantity_sold_last_30_days": 50,
            }
        ],
        seasonal=[],
        dead_stock=[],
    ),
    "executive_summary": "Mocked AI Summary.",
}


@pytest.mark.asyncio
async def test_get_purchase_suggestions_success_with_ai_summary(
    async_client: AsyncClient,
):
    """
    Prueba el caso de éxito donde tanto el análisis de datos como el resumen de IA se generan.
    """

    # Creamos un mock del servicio de LLM que devuelve un resumen exitoso
    class MockLLMService(LLMAnalysisService):
        async def generate_executive_summary(self, structured_data):
            return "Resumen ejecutivo generado por el mock."

    # Sobrescribimos la dependencia en la app para que use nuestro mock
    app.dependency_overrides[get_llm_service] = MockLLMService

    # Realizamos la llamada al endpoint
    response = await async_client.get("/api/v1/inventory/purchase-suggestions")

    # Verificamos la respuesta
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    assert data["executive_summary"] == "Resumen ejecutivo generado por el mock."
    assert "high_turnover" in data["analysis"]

    # Limpiamos la sobrescritura de la dependencia después de la prueba
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_purchase_suggestions_graceful_degradation_no_ai(
    async_client: AsyncClient,
):
    """
    Prueba la degradación controlada: el endpoint funciona incluso si el LLM falla.
    """

    # Mock del servicio de LLM que simula una falla devolviendo None
    class MockLLMServiceFails(LLMAnalysisService):
        async def generate_executive_summary(self, structured_data):
            return None

    app.dependency_overrides[get_llm_service] = MockLLMServiceFails

    response = await async_client.get("/api/v1/inventory/purchase-suggestions")

    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    # La clave es verificar que el resumen es nulo, pero la respuesta es exitosa
    assert data["executive_summary"] is None

    app.dependency_overrides.clear()
