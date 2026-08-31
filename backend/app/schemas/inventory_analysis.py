import uuid

from pydantic import BaseModel, Field


class PurchaseSuggestionItem(BaseModel):
    product_id: uuid.UUID  # 👈 Cambiado a UUID para coincidir con el modelo Product
    product_name: str
    stock_quantity: int
    total_quantity_sold_last_30_days: int
    avg_daily_sales_last_30: float | None = None
    days_of_stock_left: float | None = None
    classification: str | None = None

    model_config = {"from_attributes": True}


class PurchaseSuggestionsAnalysis(BaseModel):
    high_turnover: list[PurchaseSuggestionItem] = Field(default_factory=list)
    seasonal: list[PurchaseSuggestionItem] = Field(default_factory=list)
    dead_stock: list[PurchaseSuggestionItem] = Field(default_factory=list)


class PurchaseSuggestionAnalysisException(Exception):
    """Excepción personalizada para fallos en el análisis de sugerencias de compra."""
