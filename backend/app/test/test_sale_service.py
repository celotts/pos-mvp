import uuid
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import BackgroundTasks, HTTPException

from models.product import Product
from models.user import User
from schemas.sale import SaleCreate, SaleItemCreate
from service.sale_service import sale_service

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

    # Product query (batch load con SELECT ... IN) → lista de productos
    products_result = MagicMock()
    products_result.scalars.return_value.all.return_value = [product1, product2]

    # get_stock_levels → comprado 10 de cada, vendido 0
    purchased_result = MagicMock()
    purchased_result.all.return_value = [
        SimpleNamespace(product_id=product1_id, qty=10),
        SimpleNamespace(product_id=product2_id, qty=10),
    ]
    sold_result = MagicMock()
    sold_result.all.return_value = []

    mock_db.execute.side_effect = [products_result, purchased_result, sold_result]

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
    assert task_args[1] == created_sale.id  # sale_id


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
    products_result = MagicMock()
    products_result.scalars.return_value.all.return_value = []
    empty_result = MagicMock()
    empty_result.all.return_value = []
    mock_db.execute.side_effect = [products_result, empty_result, empty_result]

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


async def test_create_sale_insufficient_stock(
    mock_db: AsyncMock,
    mock_background_tasks: MagicMock,
    current_user: User,
    sale_create_schema: SaleCreate,
):
    """Prueba que se lance 409 si el stock disponible es menor a lo solicitado."""
    # Arrange
    product1_id = sale_create_schema.items[0].product_id
    product1 = Product(id=product1_id, name="Producto A", price=Decimal("20.00"))
    products_result = MagicMock()
    products_result.scalars.return_value.all.return_value = [product1]
    purchased_result = MagicMock()
    purchased_result.all.return_value = [
        SimpleNamespace(product_id=product1_id, qty=1),
    ]
    sold_result = MagicMock()
    sold_result.all.return_value = []
    mock_db.execute.side_effect = [products_result, purchased_result, sold_result]

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await sale_service.create_sale(
            db=mock_db,
            sale_in=sale_create_schema,
            current_user=current_user,
            background_tasks=mock_background_tasks,
        )
    assert exc_info.value.status_code == 409
    assert "Insufficient stock" in exc_info.value.detail
    mock_db.add.assert_not_called()
