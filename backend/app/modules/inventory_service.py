from typing import Any

from schemas.inventory import PurchaseSuggestionItem, PurchaseSuggestionsAnalysis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .llm_service import LLMAnalysisService


class InventoryAnalysisService:
    """
    Servicio de negocio para analizar el inventario y generar sugerencias de compra.
    """

    async def get_purchase_suggestions(
        self, db: AsyncSession, llm_service: LLMAnalysisService
    ) -> dict[str, Any]:
        """
        Orquesta el análisis de datos desde SQL y el enriquecimiento opcional con IA.
        """
        # Esta consulta SQL es el núcleo del análisis determinista.
        # ADAPTAR: Los nombres de tablas (products, sale_details, sales) y columnas
        # deben coincidir con tu esquema de base de datos real.
        query = text("""
            WITH product_sales AS (
                -- Agrega datos de ventas por producto en los últimos 90 días.
                SELECT
                    p.id AS product_id, p.name AS product_name, p.stock_quantity,
                    COALESCE(SUM(CASE WHEN s.created_at >= NOW() - INTERVAL '30 days' THEN sd.quantity ELSE 0 END), 0) AS total_quantity_sold_last_30_days,
                    COALESCE(SUM(CASE WHEN s.created_at >= NOW() - INTERVAL '90 days' THEN sd.quantity ELSE 0 END), 0) AS total_quantity_sold_last_90_days,
                    COALESCE(SUM(CASE WHEN EXTRACT(ISODOW FROM s.created_at) IN (6, 7) THEN sd.quantity ELSE 0 END), 0) AS weekend_sales,
                    COALESCE(SUM(CASE WHEN EXTRACT(ISODOW FROM s.created_at) NOT IN (6, 7) THEN sd.quantity ELSE 0 END), 0) AS weekday_sales
                FROM products p
                LEFT JOIN sale_items sd ON p.id = sd.product_id
                LEFT JOIN sales s ON sd.sale_id = s.id AND s.created_at >= NOW() - INTERVAL '90 days'
                GROUP BY p.id, p.name, p.stock_quantity
            ),
            calculated_metrics AS (
                -- Calcula métricas clave como el promedio de ventas diario y la estacionalidad.
                SELECT
                    *,
                    (total_quantity_sold_last_30_days / 30.0) AS avg_daily_sales_last_30,
                    (weekend_sales / 2.0 > (weekday_sales / 5.0) * 1.5 AND weekend_sales > 0) AS is_weekend_seasonal
                FROM product_sales
            ),
            classified_products AS (
                -- Clasifica cada producto según las métricas calculadas.
                SELECT
                    product_id, product_name, stock_quantity, total_quantity_sold_last_30_days,
                    CASE
                        WHEN avg_daily_sales_last_30 > 0 THEN stock_quantity / avg_daily_sales_last_30
                        ELSE NULL
                    END AS days_of_stock_left,
                    CASE
                        WHEN avg_daily_sales_last_30 > 0 AND (stock_quantity / avg_daily_sales_last_30) < 7 THEN 'high_turnover'
                        WHEN stock_quantity > 0 AND total_quantity_sold_last_90_days = 0 THEN 'dead_stock'
                        WHEN is_weekend_seasonal THEN 'seasonal'
                        ELSE NULL
                    END AS classification
                FROM calculated_metrics
            )
            -- Filtra solo los productos que caen en una de nuestras clasificaciones de interés.
            SELECT * FROM classified_products
            WHERE classification IS NOT NULL
            ORDER BY classification, days_of_stock_left ASC;
        """)

        result = await db.execute(query)
        rows = result.mappings().all()

        # Organiza los resultados en la estructura definida por los esquemas Pydantic.
        analysis = PurchaseSuggestionsAnalysis(
            high_turnover=[], seasonal=[], dead_stock=[]
        )
        for row in rows:
            item = PurchaseSuggestionItem.from_orm(row)
            if item.classification == "high_turnover":
                analysis.high_turnover.append(item)
            elif item.classification == "seasonal":
                analysis.seasonal.append(item)
            elif item.classification == "dead_stock":
                analysis.dead_stock.append(item)

        # Genera el resumen de IA de forma asíncrona.
        executive_summary = await llm_service.generate_executive_summary(
            analysis.model_dump()
        )

        return {
            "analysis": analysis,
            "executive_summary": executive_summary,
        }
