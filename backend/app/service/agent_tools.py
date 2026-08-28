from core.crud_product import crud_product
from core.crud_sale import crud_sale
from langchain.tools import tool
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import logger


@tool
async def get_inventory_health_metrics(db: AsyncSession, store_id: int) -> dict:
    """
    Calcula KPIs clave de inventario: productos con stock bajo, artículos sin movimiento
    en los últimos 30 días y valor total del inventario estancado.
    """
    logger.info(f"Ejecutando evaluación de salud de inventario para tienda {store_id}")
    # Invocación a capa CRUD existente
    low_stock = await crud_product.get_low_stock_products(db, store_id=store_id)
    dead_stock_value = await crud_product.get_dead_stock_value(
        db, store_id=store_id, days=30
    )

    return {
        "low_stock_count": len(low_stock),
        "dead_stock_value_usd": dead_stock_value,
        "critical_items": [p.name for p in low_stock[:5]],
    }


@tool
async def analyze_sales_margins(db: AsyncSession, days: int = 30) -> dict:
    """
    Retorna el top 5 de productos con mayor y menor margen de ganancia real
    basado en ventas históricas recientes.
    """
    logger.info(f"Analizando márgenes de venta de los últimos {days} días")
    margin_data = await crud_sale.get_margin_analytics(db, days=days)
    return margin_data
