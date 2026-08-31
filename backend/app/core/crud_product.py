import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select

from core.crud_base import CRUDBase
from core.tenancy import get_current_tenant
from models.product import Product
from models.purchase import Purchase, PurchaseItem
from models.sale import Sale
from models.sale_item import SaleItem
from schemas.product import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def __init__(self, model: type[Product]):
        super().__init__(model)

    async def get_stock_levels(
        self, db, store_id: uuid.UUID | None = None
    ) -> dict[uuid.UUID, int]:
        """
        Stock por producto = total comprado - total vendido.
        Si se pasa store_id, el stock se calcula solo dentro de esa tienda.
        """
        purchased_stmt = select(
            PurchaseItem.product_id,
            func.coalesce(func.sum(PurchaseItem.quantity), 0).label("qty"),
        ).join(Purchase, Purchase.id == PurchaseItem.purchase_id)
        sold_stmt = select(
            SaleItem.product_id,
            func.coalesce(func.sum(SaleItem.quantity), 0).label("qty"),
        ).join(Sale, Sale.id == SaleItem.sale_id)

        tenant_id = get_current_tenant()
        if tenant_id:
            purchased_stmt = purchased_stmt.where(
                Purchase.tenant_id == tenant_id
            )
            sold_stmt = sold_stmt.where(Sale.tenant_id == tenant_id)

        if store_id:
            purchased_stmt = purchased_stmt.where(Purchase.store_id == store_id)
            sold_stmt = sold_stmt.where(Sale.store_id == store_id)

        purchased_stmt = purchased_stmt.group_by(PurchaseItem.product_id)
        sold_stmt = sold_stmt.group_by(SaleItem.product_id)

        purchased = {r.product_id: int(r.qty) for r in (await db.execute(purchased_stmt)).all()}
        sold = {r.product_id: int(r.qty) for r in (await db.execute(sold_stmt)).all()}

        return {
            pid: purchased.get(pid, 0) - sold.get(pid, 0)
            for pid in set(purchased) | set(sold)
        }

    async def get_low_stock_products(
        self,
        db,
        store_id: uuid.UUID | None = None,
        threshold: int = 5,
        limit: int = 20,
    ) -> list[dict]:
        """Productos cuyo stock restante es menor o igual al umbral."""
        levels = await self.get_stock_levels(db, store_id=store_id)
        low_ids = [pid for pid, qty in levels.items() if qty <= threshold]
        if not low_ids:
            return []

        stmt = select(Product).where(Product.id.in_(low_ids))
        products = (await db.execute(stmt)).scalars().all()
        items = [
            {"product_id": str(p.id), "name": p.name, "stock": levels[p.id]}
            for p in products
        ]
        items.sort(key=lambda x: x["stock"])
        return items[:limit]

    async def get_dead_stock_value(
        self,
        db,
        store_id: uuid.UUID | None = None,
        days: int = 30,
    ) -> float:
        """
        Valor en costo del stock sin rotación en los últimos `days` días.
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)

        sold_stmt = (
            select(SaleItem.product_id)
            .join(Sale, Sale.id == SaleItem.sale_id)
            .where(Sale.sale_date >= since)
            .distinct()
        )
        if store_id:
            sold_stmt = sold_stmt.where(Sale.store_id == store_id)
        moved_ids = {r.product_id for r in (await db.execute(sold_stmt)).all()}

        levels = await self.get_stock_levels(db, store_id=store_id)
        dead_ids = [pid for pid, qty in levels.items() if qty > 0 and pid not in moved_ids]
        if not dead_ids:
            return 0.0

        cost_stmt = (
            select(
                PurchaseItem.product_id,
                func.coalesce(func.avg(PurchaseItem.price_at_purchase), 0).label("cost"),
            )
            .where(PurchaseItem.product_id.in_(dead_ids))
            .group_by(PurchaseItem.product_id)
        )
        avg_cost = {
            r.product_id: Decimal(str(r.cost))
            for r in (await db.execute(cost_stmt)).all()
        }

        total = Decimal(0)
        for pid in dead_ids:
            total += avg_cost.get(pid, Decimal(0)) * levels[pid]
        return float(total)


crud_product = CRUDProduct(Product)
