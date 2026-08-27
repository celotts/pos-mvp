import uuid
from unittest.mock import AsyncMock

import pytest
from app.models.cash_account import CashAccount, CashAccountType
from app.models.user import User
from app.schemas.cash_account import CashAccountCreate
from app.service import cash_account_service
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_db() -> AsyncMock:
    """Fixture para una sesión de base de datos asíncrona mockeada."""
    return AsyncMock()


@pytest.fixture
def current_user() -> User:
    """Fixture para un usuario 'actual' que realiza las acciones."""
    return User(
        id=uuid.uuid4(),
        full_name="Current Test User",
        email="current@test.com",
        role_id=uuid.uuid4(),
    )


@pytest.fixture
def sample_cash_account(current_user: User) -> CashAccount:
    """Fixture para una cuenta de caja de ejemplo."""
    return CashAccount(
        id=uuid.uuid4(),
        name="Test Bank Account",
        account_type=CashAccountType.BANK,
        created_by=current_user.id,
    )


# --- Pruebas para create_cash_account ---


async def test_create_cash_account_success(
    mock_db: AsyncMock, current_user: User, monkeypatch
):
    """Prueba la creación exitosa de una cuenta de caja."""
    # Arrange
    account_in = CashAccountCreate(
        name="New Checking", account_type=CashAccountType.BANK
    )

    mock_crud_create = AsyncMock(
        return_value=CashAccount(id=uuid.uuid4(), **account_in.model_dump())
    )
    monkeypatch.setattr(
        "app.modules.cash_account_service.crud_cash_account.create",
        mock_crud_create,
    )

    # Act
    created_account = await cash_account_service.create_cash_account(
        db=mock_db, account_in=account_in, current_user=current_user
    )

    # Assert
    assert created_account is not None
    assert created_account.name == account_in.name
    mock_crud_create.assert_called_once_with(
        db=mock_db,
        obj_in=account_in,
        created_by=current_user.id,
        created_by_role_id=current_user.role_id,
    )


async def test_create_cash_account_name_conflict(
    mock_db: AsyncMock, current_user: User, monkeypatch
):
    """Prueba que crear una cuenta con un nombre duplicado lanza un error 409."""
    # Arrange
    account_in = CashAccountCreate(
        name="Existing Account", account_type=CashAccountType.CASH
    )

    # Simula IntegrityError de la base de datos
    mock_crud_create = AsyncMock(
        side_effect=IntegrityError("mock error", "mock params", "mock orig")
    )
    monkeypatch.setattr(
        "app.modules.cash_account_service.crud_cash_account.create",
        mock_crud_create,
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await cash_account_service.create_cash_account(
            db=mock_db, account_in=account_in, current_user=current_user
        )

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail


# --- Pruebas para get_cash_account ---


async def test_get_cash_account_found(
    mock_db: AsyncMock, sample_cash_account: CashAccount, monkeypatch
):
    """Prueba obtener una cuenta de caja que existe."""
    # Arrange
    mock_crud_get = AsyncMock(return_value=sample_cash_account)
    monkeypatch.setattr(
        "app.modules.cash_account_service.crud_cash_account.get", mock_crud_get
    )

    # Act
    found_account = await cash_account_service.get_cash_account(
        db=mock_db, account_id=sample_cash_account.id
    )

    # Assert
    assert found_account == sample_cash_account
    mock_crud_get.assert_called_once_with(db=mock_db, id=sample_cash_account.id)


async def test_get_cash_account_not_found(mock_db: AsyncMock, monkeypatch):
    """Prueba que intentar obtener una cuenta inexistente lanza un error 404."""
    # Arrange
    non_existent_id = uuid.uuid4()
    mock_crud_get = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "app.modules.cash_account_service.crud_cash_account.get", mock_crud_get
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await cash_account_service.get_cash_account(
            db=mock_db, account_id=non_existent_id
        )

    assert exc_info.value.status_code == 404
    assert "Account not found" in exc_info.value.detail
