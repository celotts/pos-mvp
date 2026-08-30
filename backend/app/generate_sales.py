import asyncio
import random
import uuid
from datetime import datetime, timedelta

from core.config import settings
from core.crud_user import crud_user
from core.db import async_session_maker
from models.product import Product
from models.sale import Sale, SaleItem
from models.sales_vector import SalesVector
from models.store import Store
from sqlalchemy import select


async def generate_mock_data():
    async with async_session_maker() as db:
        print("Buscando superusuario...")
        user = await crud_user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
        if not user:
            print(
                "Superusuario no encontrado. Asegúrate de correr initial_data.py primero."
            )
            return

        print("Buscando o creando tienda de prueba...")
        store_result = await db.execute(select(Store).limit(1))
        store = store_result.scalars().first()
        if not store:
            store = Store(name="Tienda Principal", address="Centro")
            db.add(store)
            await db.commit()
            await db.refresh(store)

        print("Buscando o creando producto de prueba...")
        product_result = await db.execute(select(Product).limit(1))
        product = product_result.scalars().first()
        if not product:
            product = Product(
                name="Producto de Prueba",
                sku=f"TEST-{uuid.uuid4().hex[:6]}",
                description="Producto para pruebas AI",
                price=50.00,
            )
            db.add(product)
            await db.commit()
            await db.refresh(product)

        print("Generando ventas falsas para los últimos 12 meses...")
        now = datetime.now()

        # Generar unas 50 ventas distribuidas en los últimos meses
        for i in range(50):
            days_ago = random.randint(1, 360)
            sale_date = now - timedelta(days=days_ago)
            quantity = random.randint(1, 5)
            price = float(product.price)
            total = quantity * price

            sale = Sale(
                sale_date=sale_date,
                total_amount=total,
                total_tax_amount=total * 0.16,
                discount_amount=0,
                status="COMPLETED",
                payment_status="PAID",
                store_id=store.id,
                user_id=user.id,
                created_at=sale_date,
            )
            db.add(sale)

            # Flush para obtener el ID de la venta
            await db.flush()

            item = SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                quantity=quantity,
                price_at_sale=price,
            )
            db.add(item)

            # Create dummy vector entry for the RAG part just in case
            content = f"Sale on {sale_date.strftime('%Y-%m-%d')} at {store.name}. Total: ${total}"
            # mock embedding array of 768 zeros
            dummy_embedding = [0.0] * 768
            vector = SalesVector(
                sale_id=sale.id, content=content, embedding=dummy_embedding
            )
            db.add(vector)

        await db.commit()
        print("¡50 ventas de prueba generadas exitosamente!")


if __name__ == "__main__":
    asyncio.run(generate_mock_data())
