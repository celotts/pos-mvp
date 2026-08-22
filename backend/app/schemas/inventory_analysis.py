from pydantic import BaseModel


class PurchaseSuggestionItem(BaseModel):
    product_id: int
    product_name: str
    stock_quantity: int
    total_quantity_sold_last_30_days: int
    avg_daily_sales_last_30: float | None = None
    days_of_stock_left: float | None = None
    classification: str | None = None


class PurchaseSuggestionsAnalysis(BaseModel):
    high_turnover: list[PurchaseSuggestionItem] = []
    seasonal: list[PurchaseSuggestionItem] = []
    dead_stock: list[PurchaseSuggestionItem] = []


class PurchaseSuggestionAnalysisException(Exception):
    pass
