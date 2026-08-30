import uuid
from typing import Literal

from pydantic import BaseModel, Field


# --- Market Basket / Cross-Sell ---
class CrossSellItem(BaseModel):
    """Producto recomendado junto al consultado, con métricas de asociación."""

    product_id: uuid.UUID
    product_name: str
    confidence: float = Field(
        ..., description="P(B|A): prob. de venta conjunta con el consultado."
    )
    lift: float = Field(..., description="Elevación: >1 indica asociación real.")
    support: float = Field(
        ..., description="Frecuencia de la co-ocurrencia (proporción de tickets)."
    )


class CrossSellResponse(BaseModel):
    product_id: uuid.UUID
    product_name: str
    transactions_analyzed: int
    recommendations: list[CrossSellItem]


class ProductBundle(BaseModel):
    """Par de productos que se compran juntos con frecuencia."""

    product_a: str
    product_b: str
    transactions: int
    support: float
    lift: float


# --- Predicción de Stockout ---
class StockoutRiskItem(BaseModel):
    product_id: uuid.UUID
    product_name: str
    stock_quantity: int
    avg_daily_demand: float = Field(
        ..., description="Demanda diaria estimada (suavizado exponencial)."
    )
    forecast_next_days: float = Field(
        ..., description="Demanda proyectada para el horizonte."
    )
    days_of_stock_left: float | None = Field(
        None, description="Días que dura el stock al ritmo actual."
    )
    risk: Literal["OUT_OF_STOCK", "CRITICAL", "WARNING", "OK", "NO_SALES"] = Field(
        ..., description="Nivel de riesgo de quedarse sin stock."
    )
    recommended_quantity: int = Field(
        0, description="Reposición sugerida: cubre lead time + horizonte."
    )


class StockoutRiskResponse(BaseModel):
    horizon_days: int
    lead_time_days: int
    items: list[StockoutRiskItem]
