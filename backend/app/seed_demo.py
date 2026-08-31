"""Datos de demostración idempotentes.

Crea una tienda, un proveedor, productos, clientes y un histórico de
ventas recientes (con pares de productos para market-basket analysis).
Pensado para entornos frescos (CI, demos): ``python -m seed_demo``.
"""

import asyncio
import random
import traceback
from datetime import datetime, timedelta

from sqlalchemy import select

from core.config import settings
from core.crud_user import crud_user
from core.db import async_session_maker
from models.customer import Customer
from models.product import Product
from models.sale import Sale
from models.sale_item import SaleItem
from models.sales_vector import SalesVector
from models.store import Store
from models.supplier import Supplier

DEMO_STORE_NAME = "Tienda Principal"
DEMO_SUPPLIER_NAME = "Proveedor Central"

DEMO_PRODUCTS = [
    {
        "name": "Café Premium",
        "sku": "CAF-001",
        "description": "Café de altura, tueste medio",
        "price": 48.00,
    },
    {
        "name": "Té Verde",
        "sku": "TEA-001",
        "description": "Té verde orgánico",
        "price": 32.50,
    },
    {
        "name": "Galletas Artesanas",
        "sku": "COO-001",
        "description": "Galletas de avena y miel",
        "price": 25.00,
    },
    {
        "name": "Chocolate Amargo",
        "sku": "CHO-001",
        "description": "Chocolate 70% cacao",
        "price": 40.00,
    },
]

DEMO_CUSTOMERS = [
    {
        "full_name": "Ana Torres",
        "email": "ana.torres@example.com",
        "phone": "+52 555 0100",
    },
    {
        "full_name": "Luis Méndez",
        "email": "luis.mendez@example.com",
        "phone": "+52 555 0101",
    },
    {
        "full_name": "Marta Gutiérrez",
        "email": "marta.gutierrez@example.com",
        "phone": "+52 555 0102",
    },
]

# Combinaciones de productos que se compran juntos (market basket).
BASKETS = [
    [0, 1],  # Café + Té
    [2, 3],  # Galletas + Chocolate
    [0, 2],
    [1, 3],
    [0, 1, 2],
    [1, 2, 3],
]

SALES_COUNT = 50
LOOKBACK_DAYS = 30


async def _get_or_create_store(db) -> Store:
    result = await db.execute(
        select(Store).where(Store.name == DEMO_STORE_NAME).limit(1)
    )
    store = result.scalars().first()
    if not store:
        store = Store(name=DEMO_STORE_NAME, address="Centro")
        db.add(store)
    return store


async def _get_or_create_supplier(db) -> Supplier:
    result = await db.execute(
        select(Supplier).where(Supplier.name == DEMO_SUPPLIER_NAME).limit(1)
    )
    supplier = result.scalars().first()
    if not supplier:
        supplier = Supplier(
            name=DEMO_SUPPLIER_NAME,
            contact_name="Contacto Demo",
            phone="+52 555 0200",
            email="proveedor.demo@example.com",
            address="Zona Industrial",
        )
        db.add(supplier)
    return supplier


async def _get_or_create_products(db, supplier: Supplier) -> list[Product]:
    products_by_sku = {
        row.sku: row
        for row in (await db.execute(select(Product))).scalars().all()
        if row.sku in {p["sku"] for p in DEMO_PRODUCTS}
    }
    for data in DEMO_PRODUCTS:
        if data["sku"] not in products_by_sku:
            product = Product(
                name=data["name"],
                sku=data["sku"],
                description=data["description"],
                price=data["price"],
                supplier_id=supplier.id,
            )
            db.add(product)
            products_by_sku[data["sku"]] = product
    return [products_by_sku[data["sku"]] for data in DEMO_PRODUCTS]


async def _get_or_create_customers(db) -> list[Customer]:
    emails = {data["email"] for data in DEMO_CUSTOMERS}
    existing = {
        row.email: row
        for row in (await db.execute(select(Customer))).scalars().all()
        if row.email in emails
    }
    for data in DEMO_CUSTOMERS:
        if data["email"] not in existing:
            customer = Customer(**data)
            db.add(customer)
            existing[data["email"]] = customer
    return [existing[data["email"]] for data in DEMO_CUSTOMERS]


async def _has_recent_sales(db, store: Store, days: int) -> bool:
    since = datetime.now() - timedelta(days=days)
    result = await db.execute(
        select(Sale.id).where(Sale.store_id == store.id, Sale.sale_date >= since)
    )
    return result.first() is not None


async def _generate_sales(db, store, products: list, customers: list, user) -> None:
    now = datetime.now()
    for _ in range(SALES_COUNT):
        days_ago = random.randint(0, LOOKBACK_DAYS - 1)
        sale_date = now - timedelta(days=days_ago, hours=random.randint(0, 10))
        basket = random.choice(BASKETS)
        items = [products[i] for i in basket if products[i] is not None]
        if not items:
            continue

        total = 0
        sale_items = []
        for product in items:
            quantity = random.randint(1, 4)
            line_total = quantity * float(product.price)
            total += line_total
            sale_items.append(
                SaleItem(
                    product_id=product.id,
                    quantity=quantity,
                    price_at_sale=product.price,
                )
            )

        available_customers = [c for c in customers if c is not None]
        sale = Sale(
            sale_date=sale_date,
            total_amount=round(total, 2),
            total_tax_amount=round(total * 0.16, 2),
            discount_amount=0,
            status="COMPLETED",
            payment_status="PAID",
            store_id=store.id,
            user_id=user.id,
            created_at=sale_date,
            customer_id=(
                random.choice(available_customers).id if available_customers else None
            ),
        )
        db.add(sale)
        await db.flush()

        for item in sale_items:
            item.sale_id = sale.id
            db.add(item)

        content = (
            f"Sale on {sale_date.strftime('%Y-%m-%d')} at {store.name}. "
            f"Total: ${sale.total_amount}"
        )
        db.add(
            SalesVector(
                sale_id=sale.id,
                store_id=store.id,
                content=content,
                embedding=[0.0] * settings.EMBEDDING_DIM,
            )
        )


async def seed_demo_data() -> None:
    async with async_session_maker() as db:
        user = await crud_user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
        if not user:
            print(
                "Superusuario no encontrado. Asegúrate de correr initial_data.py "
                "primero."
            )
            return

        store = await _get_or_create_store(db)
        supplier = await _get_or_create_supplier(db)
        await db.flush()

        products = await _get_or_create_products(db, supplier)
        customers = await _get_or_create_customers(db)
        await db.flush()

        if await _has_recent_sales(db, store, LOOKBACK_DAYS):
            print(f"Ventas demo ya sembradas en '{store.name}'. Nada que hacer.")
            return

        await _generate_sales(db, store, products, customers, user)
        await db.commit()
        print(f"Se sembraron {SALES_COUNT} ventas demo en '{store.name}'.")


if __name__ == "__main__":
    try:
        asyncio.run(seed_demo_data())
    except Exception as exc:  # noqa: BLE001  (reintento ante flakes transitorios)
        print(f"Error sembrando datos ({type(exc).__name__}): {exc}")
        traceback.print_exc()
        print("Reintentando una vez (el seed es idempotente)...")
        try:
            asyncio.run(seed_demo_data())
            print("Seed completado en el segundo intento.")
        except Exception as exc2:
            print(f"Error al reintentar ({type(exc2).__name__}): {exc2}")
            raise
