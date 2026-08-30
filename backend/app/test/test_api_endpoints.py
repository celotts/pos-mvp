"""
Colección de prueba de endpoints del POS API.

Ejecuta llamadas HTTP reales al contenedor pos-api (podman):
    make test-api

Cubre endpoints existentes (auth, productos, inventario, tiendas)
y los nuevos de Analítica Comercial (bundles, cross-sell, stockout-risk).
Requiere que el stack esté arriba (make up).
"""

import os

import httpx
import pytest
from core.config import settings

# Dentro del contenedor pos-api la API responde en el 8000.
# En el host se publica en el 8003 (sobreescribir con TEST_API_BASE_URL).
BASE_URL = os.environ.get("TEST_API_BASE_URL") or "http://localhost:8000"

# Si se define TEST_API_TOKEN se usa directamente; si no, se hace login.
TEST_API_TOKEN = os.environ.get("TEST_API_TOKEN")


@pytest.fixture()
def client():
    with httpx.Client(base_url=BASE_URL, timeout=60) as c:
        yield c


def _auth_headers(client: httpx.Client) -> dict:
    if TEST_API_TOKEN:
        return {"Authorization": f"Bearer {TEST_API_TOKEN}"}
    resp = client.post(
        "/api/v1/login/access-token",
        json={
            "username": settings.FIRST_SUPERUSER_EMAIL,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        },
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


# --- ENDPOINTS EXISTENTES ---


def test_login_returns_token(client: httpx.Client):
    """Login del superusuario (endpoint existente)."""
    resp = client.post(
        "/api/v1/login/access-token",
        json={
            "username": settings.FIRST_SUPERUSER_EMAIL,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["access_token"]


def test_list_products(client: httpx.Client):
    headers = _auth_headers(client)
    resp = client.get("/api/v1/products/", headers=headers)
    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json()["data"], list)


def test_list_stores(client: httpx.Client):
    headers = _auth_headers(client)
    resp = client.get("/api/v1/stores/", headers=headers)
    assert resp.status_code == 200, resp.text
    assert len(resp.json()["data"]) >= 1


def test_list_suppliers(client: httpx.Client):
    headers = _auth_headers(client)
    resp = client.get("/api/v1/suppliers/", headers=headers)
    assert resp.status_code == 200, resp.text
    assert len(resp.json()["data"]) >= 1


def test_inventory_purchase_suggestions(client: httpx.Client):
    headers = _auth_headers(client)
    resp = client.get("/api/v1/inventory/purchase-suggestions", headers=headers)
    assert resp.status_code == 200, resp.text
    assert "analysis" in resp.json()


# --- NUEVOS: ANALÍTICA COMERCIAL ---


def test_analytics_bundles(client: httpx.Client):
    """Pares de productos más comprados juntos (Market Basket)."""
    headers = _auth_headers(client)
    resp = client.get("/api/v1/analytics/bundles?limit=5", headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1, "Se esperan pares con los datos sembrados"
    first = data[0]
    assert first["product_a"] and first["product_b"]
    assert "lift" in first


def test_analytics_cross_sell(client: httpx.Client):
    """Recomendaciones de venta cruzada para un producto real."""
    headers = _auth_headers(client)
    products = client.get("/api/v1/products/", headers=headers).json()["data"]
    assert products, "No hay productos"
    product_id = products[0]["id"]
    resp = client.get(
        f"/api/v1/analytics/cross-sell?product_id={product_id}&limit=4",
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["product_id"] == product_id
    assert isinstance(data["recommendations"], list)


def test_analytics_stockout_risk(client: httpx.Client):
    """Predicción de quedarse sin stock con reposición sugerida."""
    headers = _auth_headers(client)
    resp = client.get(
        "/api/v1/analytics/stockout-risk?horizon=30&lead_time_days=2",
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    items = resp.json()["items"]
    assert isinstance(items, list)
    assert len(items) >= 1
    for item in items:
        assert "stock_quantity" in item
        assert "risk" in item
        assert "recommended_quantity" in item


def test_analytics_stockout_by_store(client: httpx.Client):
    """Stockout filtrado por la tienda real."""
    headers = _auth_headers(client)
    stores = client.get("/api/v1/stores/", headers=headers).json()["data"]
    assert stores, "No hay tiendas"
    store_id = stores[0]["id"]
    resp = client.get(
        f"/api/v1/analytics/stockout-risk?store_id={store_id}", headers=headers
    )
    assert resp.status_code == 200, resp.text
    assert "items" in resp.json()