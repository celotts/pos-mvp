import uuid

from pydantic import BaseModel


class PurchaseSuggestionItem(BaseModel):
    model_config = {"from_attributes": True}

    product_id: uuid.UUID
    product_name: str
    stock_quantity: int
    classification: str
    days_of_stock_left: float | None
    total_quantity_sold_last_30_days: int


class PurchaseSuggestionsAnalysis(BaseModel):
    """Contiene las listas de productos clasificados para sugerencias de compra."""

    high_turnover: list[PurchaseSuggestionItem]
    seasonal: list[PurchaseSuggestionItem]
    dead_stock: list[PurchaseSuggestionItem]


class PurchaseSuggestionsResponse(BaseModel):
    """El modelo de respuesta completo para el endpoint de sugerencias de compra."""

    analysis: PurchaseSuggestionsAnalysis
    executive_summary: str | None
