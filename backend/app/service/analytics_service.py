"""Motor de Inteligencia Comercial: Market Basket (cross-sell) y predicción de stockout.

La lógica de cálculo es pura (sin dependencias de terceros) para poder
testearla de forma determinística; las consultas a BD están aisladas.
"""
import math
import uuid
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Iterable

from models.product import Product
from models.sale import Sale
from models.sale_item import SaleItem
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.crud_product import crud_product


# ---------------------------------------------------------------------------
# Funciones puras de Market Basket
# ---------------------------------------------------------------------------
def _pair_key(a: uuid.UUID, b: uuid.UUID) -> tuple[uuid.UUID, uuid.UUID]:
    return (a, b) if a < b else (b, a)


def compute_cross_sell(
    transactions: Iterable[Iterable[uuid.UUID]],
    target_product_id: uuid.UUID,
    min_support: float = 0.01,
    limit: int = 5,
) -> tuple[int, list[tuple[uuid.UUID, float, float, float]]]:
    """Recomendaciones para `target_product_id`.

    Devuelve `(total_transacciones, [(producto, confidence, lift, support), ...])`
    ordenadas por lift descendente y con un soporte mínimo para evitar ruido.
    """
    txs = [frozenset(t) for t in transactions]
    total = len(txs)
    if not total:
        return 0, []

    if not any(target_product_id in t for t in txs):
        return total, []

    single = Counter()
    pair: Counter = Counter()
    for t in txs:
        for p in t:
            single[p] += 1
        items = list(t)
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                pair[_pair_key(items[i], items[j])] += 1

    support_target = single[target_product_id] / total
    candidates: list[tuple[uuid.UUID, float, float, float]] = []

    for (a, b), cnt in pair.items():
        if target_product_id not in (a, b):
            continue
        other = b if a == target_product_id else a
        support_ab = cnt / total
        if support_ab < min_support:
            continue
        support_other = single[other] / total
        confidence = cnt / single[target_product_id]
        lift = 0.0
        if support_target and support_other:
            lift = support_ab / (support_target * support_other)
        candidates.append((other, confidence, lift, support_ab))

    candidates.sort(key=lambda c: c[2], reverse=True)
    return total, candidates[:limit]


def compute_bundles(
    transactions: Iterable[Iterable[uuid.UUID]],
    min_support: float = 0.01,
    limit: int = 10,
) -> list[tuple[uuid.UUID, uuid.UUID, int, float, float]]:
    """Pares de productos que más se compran juntos (top por lift)."""
    txs = [frozenset(t) for t in transactions]
    total = len(txs)
    if not total:
        return []

    single = Counter()
    pair: Counter = Counter()
    for t in txs:
        for p in t:
            single[p] += 1
        items = list(t)
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                pair[_pair_key(items[i], items[j])] += 1

    bundles: list[tuple[uuid.UUID, uuid.UUID, int, float, float]] = []
    for (a, b), cnt in pair.items():
        support_ab = cnt / total
        if support_ab < min_support:
            continue
        lift = support_ab / ((single[a] / total) * (single[b] / total))
        bundles.append((a, b, cnt, support_ab, lift))

    bundles.sort(key=lambda b: b[4], reverse=True)
    return bundles[:limit]


# ---------------------------------------------------------------------------
# Funciones puras de predicción (suavizado exponencial)
# ---------------------------------------------------------------------------
def smooth_daily_demand(daily: dict[date, int], alpha: float = 0.3) -> float:
    """Demanda diaria estimada con suavizado exponencial simple.

    Si hay poca serie (>=1 observación) usa la media simple como atajo robusto.
    """
    if not daily:
        return 0.0
    values = [float(daily[k]) for k in sorted(daily)]
    if len(values) == 1:
        return values[0]
    forecast = values[0]
    for v in values[1:]:
        forecast = alpha * v + (1 - alpha) * forecast
    return max(forecast, 0.0)


def evaluate_stockout(
    stock: int,
    avg_daily: float,
    horizon: int,
    lead_time_days: int,
) -> tuple[float | None, str, int]:
    """Evalúa el riesgo de quedarse sin stock y la reposición sugerida."""
    forecast = avg_daily * horizon

    if avg_daily <= 0:
        return None, "NO_SALES", 0

    days_left = stock / avg_daily if avg_daily > 0 else None

    if stock <= 0:
        risk = "OUT_OF_STOCK"
    elif stock - forecast <= 0:
        risk = "CRITICAL"
    elif days_left <= horizon:
        risk = "WARNING"
    else:
        risk = "OK"

    recommended = max(0, math.ceil(avg_daily * (lead_time_days + horizon) - stock))
    return days_left, risk, int(recommended)


# ---------------------------------------------------------------------------
# Consultas a base de datos
# ---------------------------------------------------------------------------
def _date_range(days: int) -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    return now - timedelta(days=days), now


class AnalyticsService:
    async def _transactions(
        self,
        db: AsyncSession,
        days: int,
        store_id: uuid.UUID | None,
    ) -> list[frozenset[uuid.UUID]]:
        since, _ = _date_range(days)
        stmt = (
            select(Sale.id, SaleItem.product_id)
            .join(SaleItem, SaleItem.sale_id == Sale.id)
            .where(Sale.sale_date >= since)
        )
        if store_id:
            stmt = stmt.where(Sale.store_id == store_id)

        by_sale: dict[uuid.UUID, set[uuid.UUID]] = defaultdict(set)
        for sale_id, product_id in (await db.execute(stmt)).all():
            by_sale[sale_id].add(product_id)
        return [frozenset(v) for v in by_sale.values()]

    async def resolve_names(
        self, db: AsyncSession, ids: Iterable[uuid.UUID]
    ) -> dict[uuid.UUID, str]:
        ids = list(ids)
        if not ids:
            return {}
        stmt = select(Product.id, Product.name).where(Product.id.in_(ids))
        return {pid: name for pid, name in (await db.execute(stmt)).all()}

    async def get_cross_sell(
        self,
        db: AsyncSession,
        product_id: uuid.UUID,
        days: int = 30,
        limit: int = 5,
        min_support: float = 0.01,
        store_id: uuid.UUID | None = None,
    ) -> tuple[str, int, list[tuple[uuid.UUID, float, float, float]]]:
        """Recomendaciones de venta cruzada para un producto."""
        txs = await self._transactions(db, days, store_id)
        total, recs = compute_cross_sell(txs, product_id, min_support, limit)

        names = await self.resolve_names(db, [product_id] + [r[0] for r in recs])
        return names.get(product_id, "?"), total, recs

    async def get_bundles(
        self,
        db: AsyncSession,
        days: int = 30,
        limit: int = 10,
        min_support: float = 0.01,
        store_id: uuid.UUID | None = None,
    ) -> tuple[int, list[tuple[uuid.UUID, uuid.UUID, int, float, float]]]:
        """Pares de productos que más se venden juntos."""
        txs = await self._transactions(db, days, store_id)
        bundles = compute_bundles(txs, min_support, limit)
        return len(txs), bundles

    async def get_stockout_risk(
        self,
        db: AsyncSession,
        horizon: int = 7,
        lead_time_days: int = 5,
        lookback_days: int = 45,
        store_id: uuid.UUID | None = None,
    ) -> list[dict]:
        """Riesgo de quedarse sin stock por producto (solo productos en venta)."""
        since, _ = _date_range(lookback_days)
        stmt = (
            select(
                SaleItem.product_id,
                func.date(Sale.sale_date).label("day"),
                func.sum(SaleItem.quantity).label("qty"),
            )
            .join(Sale, Sale.id == SaleItem.sale_id)
            .where(Sale.sale_date >= since)
            .group_by(SaleItem.product_id, func.date(Sale.sale_date))
        )
        if store_id:
            stmt = stmt.where(Sale.store_id == store_id)

        daily_by_product: dict[uuid.UUID, dict[date, int]] = defaultdict(dict)
        for product_id, day, qty in (await db.execute(stmt)).all():
            daily_by_product[product_id][day] = int(qty or 0)

        stock_levels = await crud_product.get_stock_levels(db, store_id=store_id)
        names = await self.resolve_names(db, set(stock_levels) | set(daily_by_product))

        results = []
        for product_id, daily in daily_by_product.items():
            avg_daily = smooth_daily_demand(daily)
            stock = stock_levels.get(product_id, 0)
            days_left, risk, recommended = evaluate_stockout(
                stock, avg_daily, horizon, lead_time_days
            )
            results.append(
                {
                    "product_id": product_id,
                    "product_name": names.get(product_id, "?"),
                    "stock_quantity": stock,
                    "avg_daily_demand": round(avg_daily, 2),
                    "forecast_next_days": round(avg_daily * horizon, 2),
                    "days_of_stock_left": (
                        round(days_left, 1) if days_left is not None else None
                    ),
                    "risk": risk,
                    "recommended_quantity": recommended,
                }
            )

        order = {
            "OUT_OF_STOCK": 0,
            "CRITICAL": 1,
            "WARNING": 2,
            "OK": 3,
            "NO_SALES": 4,
        }
        results.sort(key=lambda r: order[r["risk"]])
        return results


analytics_service = AnalyticsService()
