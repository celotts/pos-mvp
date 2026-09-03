from unittest.mock import AsyncMock, MagicMock

import pytest

from service.ai.agent_service import AgentService


@pytest.fixture
def ai_service():
    chat_provider = MagicMock()
    chat_provider.name = "ollama"
    chat_provider.complete = AsyncMock(
        return_value="Respuesta generada por el provider."
    )

    embedding_provider = MagicMock()
    embedding_provider.name = "ollama"
    embedding_provider.embed = AsyncMock(return_value=[0.1, 0.2, 0.3])

    driver = MagicMock()
    driver.run = AsyncMock(return_value="Análisis generado por el agente.")

    return AgentService(
        chat_provider=chat_provider,
        embedding_provider=embedding_provider,
        driver=driver,
    )


@pytest.mark.asyncio
async def test_get_embedding_success(ai_service):
    """Verifica que get_embedding delegue en el embedding provider y retorne el vector."""
    result = await ai_service.get_embedding("Texto de prueba")

    assert result == [0.1, 0.2, 0.3]
    ai_service.embedding_provider.embed.assert_called_once_with("Texto de prueba")


@pytest.mark.asyncio
async def test_get_rag_response_no_context(ai_service, monkeypatch):
    """Verifica el comportamiento de RAG cuando no se encuentran vectores coincidentes."""
    mock_embedding = [0.1, 0.2, 0.3]
    monkeypatch.setattr(
        ai_service, "get_embedding", AsyncMock(return_value=mock_embedding)
    )

    # Mock de DB retornando resultado vacío
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = []
    mock_db.execute.return_value = mock_result

    response = await ai_service.get_rag_response(
        db=mock_db, query="¿Cuántas ventas hubo?"
    )

    assert response == "No se encontró información relevante en la base de datos."


@pytest.mark.asyncio
async def test_get_purchase_suggestion_delegates_to_driver(ai_service):
    """Verifica que el agente de inventario delegue en el driver."""
    mock_db = AsyncMock()
    response = await ai_service.get_purchase_suggestion(
        db=mock_db, query="qué productos reponer?"
    )

    assert response == "Análisis generado por el agente."
    ai_service.driver.run.assert_called_once()