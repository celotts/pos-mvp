import uuid

import pytest
from app.models.role import Role
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio

API_PREFIX = "/api/v1"


@pytest.fixture
async def test_role(db: AsyncSession) -> Role:
    """Crea un rol en la BD de prueba para poder asignarlo a usuarios."""
    role = Role(id=uuid.uuid4(), name="Test Role", description="A role for testing")
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def test_create_user_success(
    client: AsyncClient, db: AsyncSession, test_role: Role
):
    """Prueba la creación exitosa de un usuario a través del endpoint POST."""
    # Arrange
    user_data = {
        "email": "test@example.com",
        "password": "a-very-secure-password",
        "full_name": "Test User",
        "role_id": str(test_role.id),
    }

    # Act
    response = await client.post(f"{API_PREFIX}/users/", json=user_data)

    # Assert
    assert response.status_code == 201  # O 200, dependiendo de tu implementación
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "password" not in data  # ¡Importante! Nunca devolver la contraseña.


async def test_create_user_email_conflict(
    client: AsyncClient, db: AsyncSession, test_role: Role
):
    """Prueba que la API devuelve un error 409 si el email ya existe."""
    # Arrange: Crea un usuario primero para que haya un conflicto.
    user_data = {
        "email": "conflict@example.com",
        "password": "password123",
        "full_name": "First User",
        "role_id": str(test_role.id),
    }
    await client.post(f"{API_PREFIX}/users/", json=user_data)

    # Act: Intenta crear otro usuario con el mismo email.
    response = await client.post(f"{API_PREFIX}/users/", json=user_data)

    # Assert
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]
