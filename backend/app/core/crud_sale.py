import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select

from core.crud_base import CRUDBase
from models.product import Product
from models.purchase import PurchaseItem
from models.sale import Sale
from models.sale_item import SaleItem
from schemas.sale import SaleCreate  # Usamos SaleCreate, no hay Update para Sale


class CRUDSale(CRUDBase[Sale, SaleCreate, SaleCreate]):
    def __init__(self, model: type[Sale]):
        super().__init__(model)

    def _date_filter(self, days: int = 30):
        since = datetime.now(timezone.utc) - timedelta(days=days)
        return Sale.sale_date >= since

    async def get_sales_summary(
        self, db, days: int = 30, store_id: uuid.UUID | None = None
    ) -> dict:
        """Totales de ventas del periodo (ingresos, tickets, ticket promedio, impuestos, descuentos)."""
        filters = [self._date_filter(days)]
        if store_id:
            filters.append(Sale.store_id == store_id)
        stmt = select(
            func.coalesce(func.sum(Sale.total_amount), 0).label("revenue"),
            func.count(Sale.id).label("tickets"),
            func.coalesce(func.sum(Sale.total_tax_amount), 0).label("tax"),
            func.coalesce(func.sum(Sale.discount_amount), 0).label("discounts"),
        ).where(*filters)
        row = (await db.execute(stmt)).one()
        revenue = Decimal(str(row.revenue or 0))
        tickets = int(row.tickets or 0)
        avg_ticket = (revenue / Decimal(tickets)) if tickets else Decimal("0")
        return {
            "days": days,
            "revenue": float(revenue),
            "tickets": tickets,
            "avg_ticket": float(avg_ticket),
            "tax": float(row.tax or 0),
            "discounts": float(row.discounts or 0),
        }

    async def get_top_products(
        self, db, days: int = 30, limit: int = 5, store_id: uuid.UUID | None = None
    ) -> list[dict]:
        """Top N productos por ingresos y unidades del periodo."""
        filters = [self._date_filter(days)]
        if store_id:
            filters.append(Sale.store_id == store_id)
        stmt = (
            select(
                Product.name,
                func.sum(SaleItem.quantity).label("qty"),
                func.sum(SaleItem.price_at_sale * SaleItem.quantity).label("revenue"),
            )
            .join(SaleItem, SaleItem.product_id == Product.id)
            .join(Sale, Sale.id == SaleItem.sale_id)
            .where(*filters)
            .group_by(Product.name)
            .order_by(func.sum(SaleItem.price_at_sale * SaleItem.quantity).desc())
            .limit(limit)
        )
        rows = (await db.execute(stmt)).all()
        return [
            {
                "product": r.name,
                "quantity_sold": int(r.qty or 0),
                "revenue": float(r.revenue or 0),
            }
            for r in rows
        ]

    async def get_margin_analytics(
        self, db, days: int = 30, store_id: uuid.UUID | None = None
    ) -> dict:
        """Productos con mayor y menor margen real (precio de venta vs costo de compra)."""
        filters = [self._date_filter(days)]
        if store_id:
            filters.append(Sale.store_id == store_id)

        # Ingresos y unidades por producto
        sales_stmt = (
            select(
                Product.id,
                Product.name,
                func.sum(SaleItem.quantity).label("qty"),
                func.sum(SaleItem.price_at_sale * SaleItem.quantity).label("revenue"),
            )
            .join(SaleItem, SaleItem.product_id == Product.id)
            .join(Sale, Sale.id == SaleItem.sale_id)
            .where(*filters)
            .group_by(Product.id, Product.name)
        )
        sold_rows = (await db.execute(sales_stmt)).all()

        # Costo unitario promedio por producto
        cost_stmt = select(
            PurchaseItem.product_id,
            func.coalesce(func.avg(PurchaseItem.price_at_purchase), 0).label("cost"),
        ).group_by(PurchaseItem.product_id)
        cost_rows = (await db.execute(cost_stmt)).all()
        avg_cost = {r.product_id: Decimal(str(r.cost)) for r in cost_rows}

        by_product = {}
        for r in sold_rows:
            revenue = Decimal(str(r.revenue or 0))
            qty = int(r.qty or 0)
            unit_cost = avg_cost.get(r.id, Decimal("0"))
            cost = unit_cost * qty
            margin = revenue - cost
            margin_pct = (margin / revenue * 100) if revenue else Decimal("0")
            by_product[r.id] = {
                "product": r.name,
                "revenue": float(revenue),
                "quantity_sold": qty,
                "estimated_cost": float(cost),
                "margin": float(margin),
                "margin_pct": float(margin_pct),
            }

        items = sorted(by_product.values(), key=lambda p: p["margin"])
        top = items[-5:][::-1] if items else []
        bottom = items[:5]
        return {
            "top_margin": top,
            "bottom_margin": bottom,
            "note": "Costo estimado con el precio promedio de compra (PurchaseItem.price_at_purchase).",
        }


crud_sale = CRUDSale(Sale)
