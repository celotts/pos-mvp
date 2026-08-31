"""
Colección de prueba de endpoints del POS API.

Ejecuta llamadas HTTP reales al contenedor pos-api (podman):
    make test-api

Cubre endpoints existentes (auth, productos, inventario, tiendas),
los nuevos de Analítica Comercial (bundles, cross-sell, stockout-risk),
CRUD de alta (producto/tienda/supplier), GET por id de todas las entidades,
y los endpoints de agente de IA, inventario y POS faltantes.
Requiere que el stack esté arriba (make up).
"""

import asyncio
import os
import uuid

import httpx
import pytest
from sqlalchemy import select

from core.config import settings
from core.db import async_session_maker
from core.security import get_password_hash
from models.company import Company
from models.role import Role
from models.user import User

# Dentro del contenedor pos-api la API responde en el 8000.
# En el host se publica en el 8003 (sobreescribir con TEST_API_BASE_URL).
BASE_URL = os.environ.get("TEST_API_BASE_URL") or "http://localhost:8000"

# Si se define TEST_API_TOKEN se usa directamente; si no, se hace login.
TEST_API_TOKEN = os.environ.get("TEST_API_TOKEN")


def _ollama_available() -> bool:
    """True si Ollama responde en settings.OLLAMA_BASE_URL."""
    try:
        resp = httpx.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=3)
        return resp.status_code == 200
    except (httpx.HTTPError, ValueError):
        return False


@pytest.fixture()
def client():
    with httpx.Client(base_url=BASE_URL, timeout=60) as c:
        yield c


def _auth_headers(
    client: httpx.Client,
    username: str | None = None,
    password: str | None = None,
) -> dict:
    if TEST_API_TOKEN:
        return {"Authorization": f"Bearer {TEST_API_TOKEN}"}
    resp = client.post(
        "/api/v1/login/access-token",
        json={
            "username": username or settings.FIRST_SUPERUSER_EMAIL,
            "password": password or settings.FIRST_SUPERUSER_PASSWORD,
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


# --- CRUD COMPLETO DEL FLUJO PRINCIPAL ---


def _get_any_id(client: httpx.Client, path: str, headers: dict) -> str | None:
    """Devuelve el id del primer registro de una lista, o None si está vacía."""
    resp = client.get(path, headers=headers)
    if resp.status_code != 200:
        return None
    data = resp.json().get("data")
    return data[0]["id"] if data else None


def test_product_crud_full(client: httpx.Client):
    headers = _auth_headers(client)
    base = "/api/v1/products"
    sku = f"TEST-CRUD-{uuid.uuid4().hex[:8]}".upper()

    created = client.post(
        base + "/",
        headers=headers,
        json={
            "name": f"Producto de prueba {sku}",
            "description": "Creado por la colección de tests",
            "price": 123.45,
            "sku": sku,
        },
    )
    assert created.status_code == 201, created.text
    product_id = created.json()["data"]["id"]

    fetched = client.get(f"{base}/{product_id}", headers=headers)
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["data"]["id"] == product_id

    updated = client.put(
        f"{base}/{product_id}",
        headers=headers,
        json={"name": f"Producto actualizado {sku}"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["data"]["name"] == f"Producto actualizado {sku}"

    deleted = client.delete(f"{base}/{product_id}", headers=headers)
    assert deleted.status_code == 200, deleted.text

    gone = client.get(f"{base}/{product_id}", headers=headers)
    assert gone.status_code == 404, gone.text


def test_store_crud_full(client: httpx.Client):
    headers = _auth_headers(client)
    base = "/api/v1/stores"
    name = f"TIENDA TEST-{uuid.uuid4().hex[:8]}".upper()

    created = client.post(base + "/", headers=headers, json={"name": name})
    assert created.status_code == 201, created.text
    store_id = created.json()["data"]["id"]

    fetched = client.get(f"{base}/{store_id}", headers=headers)
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["data"]["id"] == store_id

    updated = client.put(
        f"{base}/{store_id}", headers=headers, json={"name": f"{name}-2"}
    )
    assert updated.status_code == 200, updated.text

    deleted = client.delete(f"{base}/{store_id}", headers=headers)
    assert deleted.status_code == 200, deleted.text

    gone = client.get(f"{base}/{store_id}", headers=headers)
    assert gone.status_code == 404, gone.text


def test_supplier_crud_full(client: httpx.Client):
    headers = _auth_headers(client)
    base = "/api/v1/suppliers"
    name = f"PROVEEDOR TEST-{uuid.uuid4().hex[:8]}".upper()

    created = client.post(base + "/", headers=headers, json={"name": name})
    assert created.status_code == 201, created.text
    supplier_id = created.json()["data"]["id"]

    fetched = client.get(f"{base}/{supplier_id}", headers=headers)
    assert fetched.status_code == 200, fetched.text

    updated = client.put(
        f"{base}/{supplier_id}", headers=headers, json={"name": f"{name}-2"}
    )
    assert updated.status_code == 200, updated.text

    deleted = client.delete(f"{base}/{supplier_id}", headers=headers)
    assert deleted.status_code == 200, deleted.text

    gone = client.get(f"{base}/{supplier_id}", headers=headers)
    assert gone.status_code == 404, gone.text


def test_customer_crud_full(client: httpx.Client):
    headers = _auth_headers(client)
    base = "/api/v1/customers"
    tag = uuid.uuid4().hex[:8]

    created = client.post(
        base + "/",
        headers=headers,
        json={
            "full_name": f"Cliente TEST-{tag}",
            "email": f"test-{tag}@cliente.com",
            "phone": "555-1234",
            "address": "Calle de prueba 123",
        },
    )
    assert created.status_code == 201, created.text
    customer_id = created.json()["data"]["id"]

    fetched = client.get(f"{base}/{customer_id}", headers=headers)
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["data"]["id"] == customer_id

    updated = client.put(
        f"{base}/{customer_id}",
        headers=headers,
        json={"full_name": f"Cliente TEST-{tag}-actualizado"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["data"]["full_name"] == f"Cliente TEST-{tag}-actualizado"

    deleted = client.delete(f"{base}/{customer_id}", headers=headers)
    assert deleted.status_code == 200, deleted.text

    gone = client.get(f"{base}/{customer_id}", headers=headers)
    assert gone.status_code == 404, gone.text


# --- GET POR ID DE TODAS LAS ENTIDADES ---


@pytest.mark.parametrize(
    "entity",
    [
        "users",
        "roles",
        "products",
        "customers",
        "suppliers",
        "stores",
        "terminals",
        "purchases",
        "countries",
        "states",
        "municipalities",
        "cash-accounts",
        "accounts-payable",
        "accounts-receivable",
        "specialties",
    ],
)
def test_get_by_id_of_each_entity(client: httpx.Client, entity: str):
    headers = _auth_headers(client)
    list_resp = client.get(f"/api/v1/{entity}/", headers=headers)
    assert list_resp.status_code == 200, list_resp.text
    data = list_resp.json().get("data")
    if not data:
        pytest.skip(f"No hay registros de {entity} en la BD de demo.")

    target_id = data[0]["id"]
    resp = client.get(f"/api/v1/{entity}/{target_id}", headers=headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["id"] == target_id


# --- ENDPOINTS FALTANTES: IA, INVENTARIO, POS ---


def test_inventory_recommendation(client: httpx.Client):
    """GET /inventory/recommendation: sugerencia conversacional del agente."""
    headers = _auth_headers(client)
    resp = client.get(
        "/api/v1/inventory/recommendation",
        params={"query": "¿Qué productos recomiendas reabastecer?"},
        headers=headers,
        timeout=120,
    )
    assert resp.status_code == 200, resp.text
    assert "suggestion" in resp.json()


@pytest.mark.skipif(not _ollama_available(), reason="Ollama no disponible (embeddings)")
def test_inventory_vectorize_analysis(client: httpx.Client):
    """POST /inventory/vectorize-analysis: analiza, embebe y persiste (201)."""
    headers = _auth_headers(client)
    resp = client.post(
        "/api/v1/inventory/vectorize-analysis", headers=headers, timeout=180
    )
    assert resp.status_code == 201, resp.text
    assert "message" in resp.json()


def test_assistant_chat(client: httpx.Client):
    """Toma de decisiones asistida por el agente (RAG + herramientas)."""
    headers = _auth_headers(client)
    resp = client.post(
        "/api/v1/assistant/chat",
        headers=headers,
        json={"message": "¿Cuál fue el producto más vendido en el último mes?"},
        timeout=180,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["answer"]


def test_assistant_analyze_inventory_flow(client: httpx.Client):
    """Agente ReAct de flujo de inventario."""
    headers = _auth_headers(client)
    resp = client.post(
        "/api/v1/assistant/analyze-inventory-flow",
        headers=headers,
        json={"message": "Analiza el inventario y sugiere qué comprar."},
        timeout=180,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["answer"]


def test_shift_open_and_close(client: httpx.Client):
    """Abre y cierra un turno en un terminal real."""
    headers = _auth_headers(client)
    store_id = _get_any_id(client, "/api/v1/stores/", headers)
    terminal_id = _get_any_id(client, "/api/v1/terminals/", headers)
    if not store_id or not terminal_id:
        pytest.skip("No hay tienda o terminal en la BD de demo.")

    opened = client.post(
        "/api/v1/shifts/open",
        headers=headers,
        json={
            "pos_terminal_id": terminal_id,
            "store_id": store_id,
            "starting_cash": "500.00",
        },
    )
    assert opened.status_code == 201, opened.text
    shift_id = opened.json()["data"]["id"]

    closed = client.put(
        f"/api/v1/shifts/{shift_id}/close",
        headers=headers,
        json={"ending_cash": "750.50", "notes": "Cierre desde la colección de tests"},
    )
    assert closed.status_code == 200, closed.text


def test_sale_create_http(client: httpx.Client):
    """Registra una venta real con un producto real."""
    headers = _auth_headers(client)
    store_id = _get_any_id(client, "/api/v1/stores/", headers)
    terminal_id = _get_any_id(client, "/api/v1/terminals/", headers)
    products = client.get("/api/v1/products/", headers=headers).json()["data"]
    if not store_id or not terminal_id or not products:
        pytest.skip("No hay tienda, terminal o producto en la BD de demo.")

    product_id = products[0]["id"]
    resp = client.post(
        "/api/v1/sales/",
        headers=headers,
        json={
            "store_id": store_id,
            "pos_terminal_id": terminal_id,
            "items": [{"product_id": product_id, "quantity": 1}],
        },
        timeout=120,
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()["data"]
    assert data["total_amount"] is not None
    assert data["items"][0]["product_id"] == product_id


# --- FASE 3: RBAC — prueba de la escalada de privilegios ---

def _create_cashier(client: httpx.Client, headers: dict) -> dict:
    """Crea un usuario con rol CASHIER y devuelve sus headers autenticados."""
    resp = client.get("/api/v1/roles/", headers=headers)
    assert resp.status_code == 200, resp.text
    roles = resp.json()["data"]
    cashier_role = next(r for r in roles if r["name"] == "CASHIER")

    email = f"cashier_{uuid.uuid4().hex[:8]}@test.com"
    resp = client.post(
        "/api/v1/users/",
        headers=headers,
        json={
            "email": email,
            "password": "CashierPass123!",
            "full_name": "Cajera de Prueba",
            "role_id": str(cashier_role["id"]),
        },
    )
    assert resp.status_code == 201, resp.text

    resp = client.post(
        "/api/v1/login/access-token",
        json={"username": email, "password": "CashierPass123!"},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_rbac_cashier_escalation(client: httpx.Client):
    """Un CASHIER no puede escalar: 403 en admin-only, 200 en lo mínimo."""
    admin_headers = _auth_headers(client)
    cashier_headers = _create_cashier(client, admin_headers)

    # CASHIER NO puede crear productos (requiere product:create).
    resp = client.post(
        "/api/v1/products/",
        headers=cashier_headers,
        json={"name": "Intento CASHIER", "price": 10.0, "sku": f"ESC-{uuid.uuid4().hex[:6]}"},
    )
    assert resp.status_code == 403, resp.text

    # La operación sí funciona con SUPER_ADMIN (la autorización se aplica antes).
    resp = client.post(
        "/api/v1/products/",
        headers=admin_headers,
        json={"name": "Admin TB-OK", "price": 20.0, "sku": f"ADM-{uuid.uuid4().hex[:6]}"},
    )
    assert resp.status_code in (200, 201), resp.text

    # CASHIER NO puede leer analítica (requiere analytics:read; no lo tiene).
    resp = client.get("/api/v1/analytics/bundles", headers=cashier_headers)
    assert resp.status_code == 403, resp.text

    # CASHIER SÍ puede leer productos y crear clientes (permisos que sí tiene).
    resp = client.get("/api/v1/products/", headers=cashier_headers)
    assert resp.status_code == 200, resp.text

    resp = client.post(
        "/api/v1/customers/",
        headers=cashier_headers,
        json={"full_name": "Cliente CASHIER"},
    )
    assert resp.status_code == 201, resp.text


# --- AISLAMIENTO MULTITENANT (F3) ---


def _create_foreign_tenant_user() -> tuple[str, str]:
    """Crea una segunda compañía + admin (vía DB directa) y devuelve (company_id, email)."""

    async def _inner():
        async with async_session_maker() as db:
            role = (
                (await db.execute(select(Role).where(Role.name == "ADMIN")))
                .scalars()
                .first()
            )
            assert role, "Rol ADMIN no encontrado para el tenant foráneo"
            company = Company(name=f"Tenant aislado {uuid.uuid4().hex[:6]}")
            db.add(company)
            await db.flush()
            email = f"admin.foreign.{uuid.uuid4().hex[:8]}@example.com"
            user = User(
                email=email,
                full_name="Admin Foráneo",
                password=get_password_hash("ForeignPass1"),
                role_id=role.id,
                tenant_id=company.id,
            )
            db.add(user)
            company_id = str(company.id)
            await db.commit()
            return company_id, email

    return asyncio.run(_inner())


def test_cross_tenant_isolation(client: httpx.Client):
    """Un tenant no puede leer ni listar datos(productos) de otro tenant."""
    admin_headers = _auth_headers(client)

    sku = f"TEN-ISO-{uuid.uuid4().hex[:8]}".upper()
    created = client.post(
        "/api/v1/products/",
        headers=admin_headers,
        json={"name": f"Producto tenancy {sku}", "price": 10.5, "sku": sku},
    )
    assert created.status_code == 201, created.text
    product_id = created.json()["data"]["id"]

    # El tenant A (súperusuario) sí ve su producto.
    assert (
        client.get(f"/api/v1/products/{product_id}", headers=admin_headers).status_code
        == 200
    )

    company_b_id, email_b = _create_foreign_tenant_user()
    headers_b = _auth_headers(
        client, username=email_b, password="ForeignPass1"
    )

    # El tenant B no ve el producto de A en su listado.
    products_b = client.get("/api/v1/products/", headers=headers_b).json()["data"]
    assert all(p["id"] != product_id for p in products_b)

    # Y obtenerlo por id devuelve 404 (scoping de lectura).
    assert (
        client.get(f"/api/v1/products/{product_id}", headers=headers_b).status_code
        == 404
    )

    # Un producto creado por B no contamina el tenant A.
    sku_b = f"TEN-B-{company_b_id[:8].upper()}"
    created_b = client.post(
        "/api/v1/products/",
        headers=headers_b,
        json={"name": "Producto de tenant B", "price": 1.0, "sku": sku_b},
    )
    assert created_b.status_code == 201, created_b.text
    product_b_id = created_b.json()["data"]["id"]

    products_a = client.get("/api/v1/products/", headers=admin_headers).json()["data"]
    assert all(p["id"] != product_b_id for p in products_a)
