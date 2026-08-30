from unittest.mock import AsyncMock, MagicMock

import pytest
from service.ai_service import AIService


@pytest.fixture
def ai_service():
    return AIService()


@pytest.mark.asyncio
async def test_get_embedding_success(ai_service, monkeypatch):
    """Verifica que get_embedding consuma el endpoint de Ollama y retorne el vector correctamente."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"embedding": [0.1, 0.2, 0.3]}

    mock_client = AsyncMock()
    mock_client.is_closed = False
    mock_client.post.return_value = mock_response

    monkeypatch.setattr(ai_service, "_client", mock_client)

    result = await ai_service.get_embedding("Texto de prueba")

    assert result == [0.1, 0.2, 0.3]
    mock_client.post.assert_called_once_with(
        "/api/embeddings",
        json={"model": ai_service.embedding_model, "prompt": "Texto de prueba"},
    )


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
