import uuid
from typing import Any

from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, Query
from models.user import User as UserModel
from schemas.analytics import (
    CrossSellItem,
    CrossSellResponse,
    ProductBundle,
    StockoutRiskItem,
    StockoutRiskResponse,
)
from service.analytics_service import analytics_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/analytics", tags=["Analytics"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)


@router.get(
    "/cross-sell",
    response_model=CrossSellResponse,
    summary="Recomendaciones de venta cruzada (Market Basket)",
    description=(
        "Para un producto dado, devuelve los artículos que más se compran junto a él, "
        "ranqueados por lift con umbral de soporte mínimo."
    ),
)
async def get_cross_sell(
    product_id: uuid.UUID = Query(..., description="Producto de origen (UUID)."),
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(5, ge=1, le=20),
    min_support: float = Query(0.01, ge=0.0, le=1.0),
    store_id: uuid.UUID | None = Query(None, description="Sucursal específica."),
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    product_name, total, recs = await analytics_service.get_cross_sell(
        db=db,
        product_id=product_id,
        days=days,
        limit=limit,
        min_support=min_support,
        store_id=store_id,
    )
    names = await analytics_service.resolve_names(db, {r[0] for r in recs})
    return CrossSellResponse(
        product_id=product_id,
        product_name=product_name,
        transactions_analyzed=total,
        recommendations=[
            CrossSellItem(
                product_id=pid,
                product_name=names.get(pid, "?"),
                confidence=round(c, 4),
                lift=round(l, 4),
                support=round(s, 4),
            )
            for pid, c, l, s in recs
        ],
    )


@router.get(
    "/bundles",
    response_model=list[ProductBundle],
    summary="Pares de productos más comprados juntos",
)
async def get_bundles(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
    min_support: float = Query(0.01, ge=0.0, le=1.0),
    store_id: uuid.UUID | None = Query(None, description="Sucursal específica."),
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    _, bundles = await analytics_service.get_bundles(
        db=db, days=days, limit=limit, min_support=min_support, store_id=store_id
    )
    ids = {p for b in bundles for p in b[:2]}
    names = await analytics_service.resolve_names(db, ids)
    return [
        ProductBundle(
            product_a=names.get(a, "?"),
            product_b=names.get(b, "?"),
            transactions=cnt,
            support=round(sup, 4),
            lift=round(lift_, 4),
        )
        for a, b, cnt, sup, lift_ in bundles
    ]


@router.get(
    "/stockout-risk",
    response_model=StockoutRiskResponse,
    summary="Predicción de quedarse sin stock y reposición sugerida",
    description=(
        "Estima la demanda diaria por producto (suavizado exponencial) y calcula "
        "cuántos días de stock quedan, el riesgo de agotarse en el horizonte y la "
        "cantidad de reposición sugerida para cubrir lead time + horizonte."
    ),
)
async def get_stockout_risk(
    horizon: int = Query(7, ge=1, le=90, description="Días a proyectar."),
    lead_time_days: int = Query(5, ge=0, le=60, description="Días de reposición."),
    lookback_days: int = Query(45, ge=7, le=365, description="Historial a analizar."),
    store_id: uuid.UUID | None = Query(None, description="Sucursal específica."),
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    items = await analytics_service.get_stockout_risk(
        db=db,
        horizon=horizon,
        lead_time_days=lead_time_days,
        lookback_days=lookback_days,
        store_id=store_id,
    )
    return StockoutRiskResponse(
        horizon_days=horizon,
        lead_time_days=lead_time_days,
        items=[StockoutRiskItem(**i) for i in items],
    )
