import uuid
from unittest.mock import ANY, AsyncMock

import pytest
from httpx import AsyncClient

# Asume que tienes un fixture 'client' configurado en conftest.py
# y que la app principal está disponible para los tests.

API_PREFIX = "/api/v1/products"


@pytest.fixture
def mock_product_service(monkeypatch):
    """Mock para el servicio de productos."""
    mock = AsyncMock()
    monkeypatch.setattr(
        "backend.app.api.endpoints.product_controller.product_service", mock
    )
    return mock


@pytest.fixture
def sample_product():
    """Datos de un producto de ejemplo."""
    product_id = uuid.uuid4()
    return {
        "id": str(product_id),
        "name": "Test Product",
        "description": "A product for testing",
        "price": 10.99,
        "sku": "TP-001",
        "is_active": True,
        "created_at": "2023-01-01T12:00:00",
        "updated_at": "2023-01-01T12:00:00",
        "created_by": str(uuid.uuid4()),
        "updated_by": str(uuid.uuid4()),
    }


async def test_read_products(client: AsyncClient, mock_product_service, sample_product):
    """Prueba para obtener la lista de productos (GET /)."""
    mock_product_service.get_all.return_value = [sample_product]

    response = await client.get(API_PREFIX)

    assert response.status_code == 200
    assert response.json() == [sample_product]
    mock_product_service.get_all.assert_called_once_with(db=ANY, skip=0, limit=100)


async def test_create_product(
    client: AsyncClient, mock_product_service, sample_product
):
    """Prueba para crear un nuevo producto (POST /)."""
    mock_product_service.create.return_value = sample_product
    product_to_create = {"name": "New Product", "price": 15.50, "sku": "NP-001"}

    response = await client.post(API_PREFIX, json=product_to_create)

    assert response.status_code == 201
    assert response.json() == sample_product
    assert mock_product_service.create.call_count == 1
    # Verifica que el servicio fue llamado con los datos correctos
    _, called_kwargs = mock_product_service.create.call_args
    assert "obj_in" in called_kwargs
    created_product_schema = called_kwargs["obj_in"]
    assert created_product_schema.name == product_to_create["name"]
    assert created_product_schema.price == product_to_create["price"]
    assert created_product_schema.sku == product_to_create["sku"]


async def test_read_product_by_id_found(
    client: AsyncClient, mock_product_service, sample_product
):
    """Prueba para obtener un producto por ID cuando se encuentra (GET /{id})."""
    mock_product_service.get_by_id.return_value = sample_product
    product_id = sample_product["id"]

    response = await client.get(f"{API_PREFIX}/{product_id}")

    assert response.status_code == 200
    assert response.json() == sample_product
    mock_product_service.get_by_id.assert_called_once_with(
        db=ANY, id=uuid.UUID(product_id)
    )


async def test_read_product_by_id_not_found(client: AsyncClient, mock_product_service):
    """Prueba para obtener un producto por ID cuando NO se encuentra (GET /{id})."""
    mock_product_service.get_by_id.return_value = None
    product_id = uuid.uuid4()

    response = await client.get(f"{API_PREFIX}/{product_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


async def test_update_product_found(
    client: AsyncClient, mock_product_service, sample_product
):
    """Prueba para actualizar un producto cuando se encuentra (PUT /{id})."""
    updated_product_data = {**sample_product, "name": "Updated Name"}
    mock_product_service.update.return_value = updated_product_data
    product_id = sample_product["id"]
    update_payload = {"name": "Updated Name"}

    response = await client.put(f"{API_PREFIX}/{product_id}", json=update_payload)

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    assert mock_product_service.update.call_count == 1
    # Verifica que el servicio fue llamado con los datos correctos
    _, called_kwargs = mock_product_service.update.call_args
    assert "id" in called_kwargs and called_kwargs["id"] == uuid.UUID(product_id)
    assert "obj_in" in called_kwargs
    update_in_schema = called_kwargs["obj_in"]
    assert update_in_schema.name == update_payload["name"]


async def test_update_product_not_found(client: AsyncClient, mock_product_service):
    """Prueba para actualizar un producto cuando NO se encuentra (PUT /{id})."""
    mock_product_service.update.return_value = None
    product_id = uuid.uuid4()
    update_payload = {"name": "Updated Name"}

    response = await client.put(f"{API_PREFIX}/{product_id}", json=update_payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


async def test_delete_product_found(
    client: AsyncClient, mock_product_service, sample_product
):
    """Prueba para eliminar un producto cuando se encuentra (DELETE /{id})."""
    mock_product_service.delete.return_value = sample_product
    product_id = sample_product["id"]

    response = await client.delete(f"{API_PREFIX}/{product_id}")

    assert response.status_code == 200
    assert response.json() == sample_product
    mock_product_service.delete.assert_called_once_with(
        db=ANY, id=uuid.UUID(product_id)
    )


async def test_delete_product_not_found(client: AsyncClient, mock_product_service):
    """Prueba para eliminar un producto cuando NO se encuentra (DELETE /{id})."""
    mock_product_service.delete.return_value = None
    product_id = uuid.uuid4()

    response = await client.delete(f"{API_PREFIX}/{product_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}


async def test_read_products_with_pagination(client: AsyncClient, mock_product_service):
    """Prueba que los parámetros de paginación se pasen correctamente."""
    mock_product_service.get_all.return_value = []

    response = await client.get(f"{API_PREFIX}?skip=10&limit=50")

    assert response.status_code == 200
    mock_product_service.get_all.assert_called_once_with(db=ANY, skip=10, limit=50)
