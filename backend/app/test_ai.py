from dependencies import get_current_user
from fastapi.testclient import TestClient
from main import app
from models.user import User

client = TestClient(app)


def override_get_current_user():
    user = User()
    user.id = "00000000-0000-0000-0000-000000000000"
    user.email = "test@example.com"
    return user


app.dependency_overrides[get_current_user] = override_get_current_user

response = client.post(
    "/assistant/chat", json={"message": "¿Qué me recomiidas para mejorar las ventas?"}
)
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
