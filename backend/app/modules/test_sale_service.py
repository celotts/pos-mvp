import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import BackgroundTasks, HTTPException

from backend.app.models.product import Product
from backend.app.models.user import User
from backend.app.modules.sale_service import sale_service
from backend.app.schemas.sale import SaleCreate, SaleItemCreate

# Marca todos los tests en este archivo para que se ejecuten con asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_db() -> AsyncMock:
    """Fixture para una sesión de base de datos asíncrona mockeada."""
    return AsyncMock()


@pytest.fixture
def mock_background_tasks() -> MagicMock:
    """Fixture para un objeto BackgroundTasks mockeado."""
    return MagicMock(spec=BackgroundTasks)


@pytest.fixture
def current_user() -> User:
    """Fixture para un usuario de prueba."""
    return User(id=uuid.uuid4(), full_name="Test User")


@pytest.fixture
def sale_create_schema() -> SaleCreate:
    """Fixture para un esquema SaleCreate válido."""
    return SaleCreate(
        store_id=uuid.uuid4(),
        pos_terminal_id=uuid.uuid4(),
        items=[
            SaleItemCreate(product_id=uuid.uuid4(), quantity=2),
            SaleItemCreate(product_id=uuid.uuid4(), quantity=1),
        ],
    )


async def test_create_sale_success(
    mock_db: AsyncMock,
    mock_background_tasks: MagicMock,
    current_user: User,
    sale_create_schema: SaleCreate,
):
    """
    Prueba el caso de éxito para crear una venta.
    Verifica que se calcule el total correcto, se creen los objetos y se
    agregue la tarea en segundo plano.
    """
    # Arrange: Configurar el mock de la BD para que devuelva productos
    product1_id = sale_create_schema.items[0].product_id
    product2_id = sale_create_schema.items[1].product_id
    product1 = Product(id=product1_id, name="Producto A", price=Decimal("20.00"))
    product2 = Product(id=product2_id, name="Producto B", price=Decimal("5.50"))

    # Cuando se llame a db.get, devolver el producto correspondiente
    mock_db.get.side_effect = lambda model, pid: {
        product1_id: product1,
        product2_id: product2,
    }.get(pid)

    # Act: Llamar al método del servicio
    created_sale = await sale_service.create_sale(
        db=mock_db,
        sale_in=sale_create_schema,
        current_user=current_user,
        background_tasks=mock_background_tasks,
    )

    # Assert: Verificar los resultados
    expected_total = (Decimal("20.00") * 2) + (Decimal("5.50") * 1)
    assert created_sale.total_amount == expected_total
    assert created_sale.user_id == current_user.id
    assert len(created_sale.items) == 2
    assert created_sale.items[0].price_at_sale == product1.price

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    mock_background_tasks.add_task.assert_called_once()
    # Verificar que la tarea en segundo plano para la IA fue llamada con los argumentos correctos
    task_args = mock_background_tasks.add_task.call_args[0]
    assert task_args[0].__name__ == "create_and_store_sale_embedding"
    assert task_args[2] == created_sale.id  # sale_id


async def test_create_sale_no_items(
    mock_db: AsyncMock, mock_background_tasks: MagicMock, current_user: User
):
    """Prueba que se lance una excepción si la venta no tiene items."""
    # Arrange
    sale_in_empty = SaleCreate(
        store_id=uuid.uuid4(), pos_terminal_id=uuid.uuid4(), items=[]
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await sale_service.create_sale(
            db=mock_db,
            sale_in=sale_in_empty,
            current_user=current_user,
            background_tasks=mock_background_tasks,
        )
    assert exc_info.value.status_code == 400
    assert "must have at least one product" in exc_info.value.detail


async def test_create_sale_product_not_found(
    mock_db: AsyncMock,
    mock_background_tasks: MagicMock,
    current_user: User,
    sale_create_schema: SaleCreate,
):
    """Prueba que se lance una excepción si un producto no se encuentra."""
    # Arrange: Configurar el mock para que no encuentre el producto
    mock_db.get.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await sale_service.create_sale(
            db=mock_db,
            sale_in=sale_create_schema,
            current_user=current_user,
            background_tasks=mock_background_tasks,
        )
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail
