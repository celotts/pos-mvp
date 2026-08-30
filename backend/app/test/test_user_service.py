import uuid
from unittest.mock import AsyncMock

import pytest
from models.role import Role
from models.user import User
from schemas.user import UserCreate, UserUpdate
from service import user_service
from fastapi import HTTPException

# Marca todas las pruebas en este archivo para que se ejecuten con asyncio
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
def other_user() -> User:
    """Fixture para otro usuario, sobre el cual se actúa."""
    return User(
        id=uuid.uuid4(),
        full_name="Other Test User",
        email="other@test.com",
        role_id=uuid.uuid4(),
    )


# --- Pruebas para get_user ---


async def test_get_user_found(mock_db: AsyncMock, other_user: User, monkeypatch):
    """Prueba que se encuentre un usuario por su ID."""
    # Arrange
    mock_crud_get = AsyncMock(return_value=other_user)
    monkeypatch.setattr("service.user_service.crud_user.get", mock_crud_get)

    # Act
    found_user = await user_service.get_user(db=mock_db, user_id=other_user.id)

    # Assert
    assert found_user == other_user
    mock_crud_get.assert_called_once_with(mock_db, id=other_user.id)


async def test_get_user_not_found(mock_db: AsyncMock, monkeypatch):
    """Prueba que se lance HTTPException si el usuario no se encuentra."""
    # Arrange
    user_id = uuid.uuid4()
    mock_crud_get = AsyncMock(return_value=None)
    monkeypatch.setattr("service.user_service.crud_user.get", mock_crud_get)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await user_service.get_user(db=mock_db, user_id=user_id)
    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail


# --- Pruebas para create_user_with_logic ---


async def test_create_user_with_logic_success(mock_db: AsyncMock, monkeypatch):
    """Prueba la creación exitosa de un usuario."""
    # Arrange
    role_id = uuid.uuid4()
    user_in = UserCreate(
        email="new@example.com",
        password="password",
        full_name="New User",
        role_id=role_id,
    )

    # Mock de dependencias CRUD
    monkeypatch.setattr(
        "service.user_service.crud_user.get_by_email", AsyncMock(return_value=None)
    )
    monkeypatch.setattr(
        "service.user_service.crud_role.get",
        AsyncMock(return_value=Role(id=role_id, name="Test Role")),
    )
    created_user_obj = User(
        id=uuid.uuid4(), email=user_in.email, full_name=user_in.full_name
    )
    mock_create = AsyncMock(return_value=created_user_obj)
    monkeypatch.setattr("service.user_service.crud_user.create", mock_create)

    # Act
    result = await user_service.create_user_with_logic(db=mock_db, user_in=user_in)

    # Assert
    assert result.email == user_in.email
    user_service.crud_role.get.assert_called_once_with(mock_db, id=role_id)
    mock_create.assert_called_once_with(db=mock_db, obj_in=user_in)


async def test_create_user_email_conflict(mock_db: AsyncMock, monkeypatch):
    """Prueba que falle la creación si el email ya existe."""
    # Arrange
    user_in = UserCreate(
        email="exists@example.com", password="pw", full_name="A", role_id=uuid.uuid4()
    )

    monkeypatch.setattr(
        "service.user_service.crud_user.get_by_email",
        AsyncMock(return_value=User(id=uuid.uuid4(), email=user_in.email)),
    )
    monkeypatch.setattr(
        "service.user_service.crud_user.get_multi",
        AsyncMock(return_value=[User(id=uuid.uuid4())]),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await user_service.create_user_with_logic(db=mock_db, user_in=user_in)
    assert exc_info.value.status_code == 409
    assert "email already exists" in exc_info.value.detail


async def test_create_user_role_not_found(mock_db: AsyncMock, monkeypatch):
    """Prueba que falle la creación si el rol no existe."""
    # Arrange
    role_id = uuid.uuid4()
    user_in = UserCreate(
        email="new@example.com", password="pw", full_name="A", role_id=role_id
    )

    monkeypatch.setattr(
        "service.user_service.crud_user.get_by_email", AsyncMock(return_value=None)
    )
    monkeypatch.setattr(
        "service.user_service.crud_user.get_multi", AsyncMock(return_value=[])
    )
    monkeypatch.setattr(
        "service.user_service.crud_role.get", AsyncMock(return_value=None)
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await user_service.create_user_with_logic(db=mock_db, user_in=user_in)
    assert exc_info.value.status_code == 404
    assert f"Role with ID '{role_id}' not found" in exc_info.value.detail


# --- Pruebas para update_user ---


async def test_update_user_success(
    mock_db: AsyncMock, current_user: User, other_user: User, monkeypatch
):
    """Prueba la actualización exitosa de otro usuario."""
    # Arrange
    user_update_in = UserUpdate(full_name="Updated Name")

    mock_get_user = AsyncMock(return_value=other_user)
    monkeypatch.setattr("service.user_service.get_user", mock_get_user)

    mock_crud_update = AsyncMock(return_value=other_user)
    monkeypatch.setattr("service.user_service.crud_user.update", mock_crud_update)

    # Act
    await user_service.update_user(
        db=mock_db,
        user_id=other_user.id,
        user_in=user_update_in,
        current_user=current_user,
    )

    # Assert
    mock_get_user.assert_called_once_with(db=mock_db, user_id=other_user.id)
    mock_crud_update.assert_called_once_with(
        db=mock_db, db_obj=other_user, obj_in=user_update_in
    )


async def test_update_user_cannot_deactivate_self(
    mock_db: AsyncMock, current_user: User, monkeypatch
):
    """Prueba que un usuario no puede desactivar su propia cuenta."""
    # Arrange
    user_update_in = UserUpdate(is_active=False)

    mock_get_user = AsyncMock(return_value=current_user)
    monkeypatch.setattr("service.user_service.get_user", mock_get_user)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await user_service.update_user(
            db=mock_db,
            user_id=current_user.id,
            user_in=user_update_in,
            current_user=current_user,
        )
    assert exc_info.value.status_code == 403
    assert "cannot deactivate your own account" in exc_info.value.detail


async def test_update_user_cannot_change_own_role(
    mock_db: AsyncMock, current_user: User, monkeypatch
):
    """Prueba que un usuario no puede cambiar su propio rol."""
    # Arrange
    user_update_in = UserUpdate(role_id=uuid.uuid4())

    mock_get_user = AsyncMock(return_value=current_user)
    monkeypatch.setattr("service.user_service.get_user", mock_get_user)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await user_service.update_user(
            db=mock_db,
            user_id=current_user.id,
            user_in=user_update_in,
            current_user=current_user,
        )
    assert exc_info.value.status_code == 403
    assert "cannot change your own role" in exc_info.value.detail


# --- Pruebas para remove_user ---


async def test_remove_user_success(mock_db: AsyncMock, other_user: User, monkeypatch):
    """Prueba la eliminación exitosa de un usuario."""
    # Arrange
    mock_get_user = AsyncMock(return_value=other_user)
    monkeypatch.setattr("service.user_service.get_user", mock_get_user)

    mock_crud_remove = AsyncMock(return_value=other_user)
    monkeypatch.setattr("service.user_service.crud_user.remove", mock_crud_remove)

    # Act
    result = await user_service.remove_user(db=mock_db, user_id=other_user.id)

    # Assert
    assert result == other_user
    mock_get_user.assert_called_once_with(db=mock_db, user_id=other_user.id)
    mock_crud_remove.assert_called_once_with(db=mock_db, id=other_user.id)


async def test_remove_user_not_found(mock_db: AsyncMock, monkeypatch):
    """Prueba que falle la eliminación si el usuario no se encuentra al final."""
    # Arrange
    user_id = uuid.uuid4()

    monkeypatch.setattr(
        "service.user_service.get_user", AsyncMock(return_value=User(id=user_id))
    )
    monkeypatch.setattr(
        "service.user_service.crud_user.remove", AsyncMock(return_value=None)
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await user_service.remove_user(db=mock_db, user_id=user_id)
    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail
