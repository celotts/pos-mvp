import uuid
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from backend.app.dependencies import get_current_user, get_db
from backend.app.main import app
from backend.app.models.role import Role
from backend.app.models.user import User

# --- Dependency Overrides ---


def override_get_db():
    """A mock database session that does nothing."""
    return AsyncMock()


def override_get_current_user():
    """Returns a mock user for testing authenticated endpoints."""
    # This is needed for controllers that have auth dependencies.
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        role=Role(id=uuid.uuid4(), name="ADMIN"),
    )


# Apply overrides to the app for all tests
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
async def client() -> AsyncGenerator[AsyncClient, None]:
    """A test client for the app."""
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
