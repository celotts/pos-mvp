from core.crud_product import crud_product
from core.crud_sale import crud_sale
from langchain.tools import ToolRuntime, tool
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import logger


def _get_context(runtime: ToolRuntime) -> dict:
    """Recupera el contexto inyectado en el agente (db y store_id)."""
    context = runtime.context or {}
    db = context.get("db")
    if db is None:
        raise RuntimeError(
            "No se encontró la sesión de base de datos en el contexto del agente."
        )
    return context


def _get_db(runtime: ToolRuntime) -> AsyncSession:
    return _get_context(runtime)["db"]


def _get_store_id(runtime: ToolRuntime):
    """store_id se pasa por contexto (no por el LLM) para evitar errores de formato."""
    return _get_context(runtime).get("store_id")


@tool
async def get_inventory_health_metrics(runtime: ToolRuntime = None) -> dict:
    """
    Calcula KPIs clave de inventario: productos con stock bajo, artículos sin movimiento
    en los últimos 30 días y valor total del inventario estancado.
    """
    db = _get_db(runtime)
    store_id = _get_store_id(runtime)
    logger.info(f"Ejecutando evaluación de salud de inventario para tienda {store_id}")
    low_stock = await crud_product.get_low_stock_products(db, store_id=store_id)
    dead_stock_value = round(
        await crud_product.get_dead_stock_value(db, store_id=store_id, days=30), 2
    )

    return {
        "low_stock_count": len(low_stock),
        "dead_stock_value_usd": dead_stock_value,
        "critical_items": [p["name"] for p in low_stock[:5]],
    }


@tool
async def analyze_sales_margins(
    days: int = 30,
    runtime: ToolRuntime = None,
) -> dict:
    """
    Retorna el top 5 de productos con mayor y menor margen de ganancia real
    basado en ventas históricas recientes.
    """
    db = _get_db(runtime)
    store_id = _get_store_id(runtime)
    logger.info(f"Analizando márgenes de venta de los últimos {days} días")
    margin_data = await crud_sale.get_margin_analytics(db, days=days, store_id=store_id)
    return margin_data


@tool
async def get_sales_summary(
    days: int = 30,
    runtime: ToolRuntime = None,
) -> dict:
    """
    Resumen comercial del periodo: ingresos totales, número de tickets,
    ticket promedio, impuestos y descuentos aplicados.
    """
    db = _get_db(runtime)
    store_id = _get_store_id(runtime)
    logger.info(f"Resumen de ventas de los últimos {days} días (tienda {store_id})")
    return await crud_sale.get_sales_summary(db, days=days, store_id=store_id)


@tool
async def get_top_products(
    days: int = 30,
    limit: int = 5,
    runtime: ToolRuntime = None,
) -> dict:
    """
    Retorna los productos más vendidos del periodo por ingresos y unidades.
    Úsala cuando el usuario pregunte por lo que más se vende o mejores productos.
    """
    db = _get_db(runtime)
    store_id = _get_store_id(runtime)
    logger.info(f"Top {limit} productos de los últimos {days} días (tienda {store_id})")
    products = await crud_sale.get_top_products(
        db, days=days, limit=limit, store_id=store_id
    )
    return {"top_products": products}
