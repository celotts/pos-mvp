# modules/agent_tools.py
from langchain_core.tools import tool


@tool
def get_sales_summary(
    start_date: str = "2026-01-01", end_date: str = "2026-12-31"
) -> str:
    """Obtiene el resumen de salidas (ventas) en un rango de fechas (YYYY-MM-DD)."""
    return f"Salidas del {start_date} al {end_date}: Total $45,000 MXN en 120 ventas."


@tool
def get_purchases_summary(
    start_date: str = "2026-01-01", end_date: str = "2026-12-31"
) -> str:
    """Obtiene el resumen de entradas (compras) en un rango de fechas (YYYY-MM-DD)."""
    return f"Entradas del {start_date} al {end_date}: Total invertido $30,000 MXN en 5 recepciones."


@tool
def get_product_kardex(product_id: str = "default") -> str:
    """Obtiene el historial de movimientos de inventario (Kardex) para un producto."""
    return f"Kardex producto {product_id}: Entradas = 100, Salidas = 85, Stock actual = 15."
