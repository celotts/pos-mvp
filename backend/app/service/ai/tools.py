"""Herramientas de negocio del agente, agnósticas al framework de agentes.

Cada función tiene forma ``async (db, store_id=None, **kwargs) -> dict``.
El driver de agentes (langchain) las envuelve para exponerlas al LLM.
"""

from core.crud_product import crud_product
from core.crud_sale import crud_sale
from service.ai.ports import ToolDef
from utils.logger import logger

TOOLS = "get_sales_summary, get_top_products, analyze_sales_margins, get_inventory_health_metrics"


async def get_inventory_health_metrics(db=None, store_id=None) -> dict:
    """Calcula KPIs clave de inventario: productos con stock bajo, artículos sin movimiento
    en los últimos 30 días y valor total del inventario estancado."""
    logger.info("Ejecutando evaluación de salud de inventario para tienda %s", store_id)
    low_stock = await crud_product.get_low_stock_products(db, store_id=store_id)
    dead_stock_value = round(
        await crud_product.get_dead_stock_value(db, store_id=store_id, days=30), 2
    )
    return {
        "low_stock_count": len(low_stock),
        "dead_stock_value_usd": dead_stock_value,
        "critical_items": [p["name"] for p in low_stock[:5]],
    }


async def analyze_sales_margins(db=None, store_id=None, days: int = 30) -> dict:
    """Retorna el top 5 de productos con mayor y menor margen de ganancia real
    basado en ventas históricas recientes."""
    logger.info("Analizando márgenes de venta de los últimos %s días", days)
    return await crud_sale.get_margin_analytics(db, days=days, store_id=store_id)


async def get_sales_summary(db=None, store_id=None, days: int = 30) -> dict:
    """Resumen comercial del periodo: ingresos totales, número de tickets,
    ticket promedio, impuestos y descuentos aplicados."""
    logger.info("Resumen de ventas de los últimos %s días (tienda %s)", days, store_id)
    return await crud_sale.get_sales_summary(db, days=days, store_id=store_id)


async def get_top_products(db=None, store_id=None, days: int = 30, limit: int = 5) -> dict:
    """Retorna los productos más vendidos del periodo por ingresos y unidades.
    Úsala cuando el usuario pregunte por lo que más se vende o mejores productos."""
    logger.info("Top %s productos de los últimos %s días (tienda %s)", limit, days, store_id)
    products = await crud_sale.get_top_products(
        db, days=days, limit=limit, store_id=store_id
    )
    return {"top_products": products}


AGENT_TOOLS: list[ToolDef] = [
    ToolDef(name="get_inventory_health_metrics", description=get_inventory_health_metrics.__doc__ or "", func=get_inventory_health_metrics),
    ToolDef(name="analyze_sales_margins", description=analyze_sales_margins.__doc__ or "", func=analyze_sales_margins),
    ToolDef(name="get_sales_summary", description=get_sales_summary.__doc__ or "", func=get_sales_summary),
    ToolDef(name="get_top_products", description=get_top_products.__doc__ or "", func=get_top_products),
]