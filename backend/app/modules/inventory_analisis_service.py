import json
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from core.config import settings
from models.product import Product
from models.purchase import PurchaseItem
from models.sale import Sale
from models.sale_item import SaleItem
from models.sales_vector import SalesVector
from modules.llm_service import AbstractLLMService
from schemas.inventory import PurchaseSuggestionsAnalysis, PurchaseSuggestionsResponse
from schemas.inventory_analysis import (
    PurchaseSuggestionAnalysisException,
    PurchaseSuggestionItem,
)
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logger import logger


class InventoryAnalysisService:
    """Servicio para realizar análisis de inventario."""

    def __init__(self, llm_service: AbstractLLMService, db: AsyncSession):
        self.llm_service = llm_service
        self.db = db

    async def get_purchase_suggestions(self) -> PurchaseSuggestionsResponse:
        """Devuelve el análisis estructurado y un resumen ejecutivo opcional."""
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

        try:
            # 1. Subconsulta para compras totales históricas por producto
            purchased_sub = (
                select(
                    PurchaseItem.product_id,
                    func.coalesce(func.sum(PurchaseItem.quantity), 0).label(
                        "total_purchased"
                    ),
                )
                .group_by(PurchaseItem.product_id)
                .subquery()
            )

            # 2. Subconsulta para ventas totales históricas por producto
            sold_sub = (
                select(
                    SaleItem.product_id,
                    func.coalesce(func.sum(SaleItem.quantity), 0).label("total_sold"),
                )
                .group_by(SaleItem.product_id)
                .subquery()
            )

            # 3. Subconsulta para ventas de los últimos 30 días
            recent_sold_sub = (
                select(
                    SaleItem.product_id,
                    func.coalesce(func.sum(SaleItem.quantity), 0).label("recent_sold"),
                )
                .join(Sale, Sale.id == SaleItem.sale_id)
                .where(Sale.created_at >= thirty_days_ago)
                .group_by(SaleItem.product_id)
                .subquery()
            )

            # 4. Consulta principal uniendo las subconsultas
            stmt = (
                select(
                    Product.id.label("product_id"),
                    Product.name.label("product_name"),
                    (
                        func.coalesce(purchased_sub.c.total_purchased, 0)
                        - func.coalesce(sold_sub.c.total_sold, 0)
                    ).label("stock_quantity"),
                    func.coalesce(recent_sold_sub.c.recent_sold, 0).label(
                        "total_quantity_sold"
                    ),
                )
                .outerjoin(purchased_sub, Product.id == purchased_sub.c.product_id)
                .outerjoin(sold_sub, Product.id == sold_sub.c.product_id)
                .outerjoin(recent_sold_sub, Product.id == recent_sold_sub.c.product_id)
            )

            result = await self.db.execute(stmt)
            rows = result.all()

            # ----------------------------------------------------------------
            # 👇 AQUÍ ESTÁ EL CAMBIO REFACTORIZADO EN EL BUCLE
            # ----------------------------------------------------------------
            items = []
            for row in rows:
                total_sold = row.total_quantity_sold or 0
                stock_qty = row.stock_quantity or 0

                # 1. Evaluar dead_stock primero (sin ventas en 30 días)
                if total_sold == 0:
                    classification = "dead_stock"
                    avg_daily = 0.0
                    days_left = 999.0
                else:
                    avg_daily = total_sold / 30.0
                    days_left = stock_qty / avg_daily if avg_daily > 0 else 999.0

                    # 2. Si tiene ventas y le quedan menos de 10 días de stock
                    if days_left < 10:
                        classification = "high_turnover_risk"
                    else:
                        classification = "normal"

                items.append(
                    PurchaseSuggestionItem(
                        product_id=row.product_id,
                        product_name=row.product_name,
                        stock_quantity=stock_qty,
                        total_quantity_sold_last_30_days=total_sold,
                        avg_daily_sales_last_30=round(avg_daily, 2),
                        days_of_stock_left=round(days_left, 1),
                        classification=classification,
                    )
                )

            analysis = PurchaseSuggestionsAnalysis(
                high_turnover=[
                    i for i in items if i.classification == "high_turnover_risk"
                ],
                seasonal=[],
                dead_stock=[i for i in items if i.classification == "dead_stock"],
            )
            # ----------------------------------------------------------------

            executive_summary = await self.llm_service.generate_executive_summary(
                analysis.model_dump()
            )

            return PurchaseSuggestionsResponse(
                analysis=analysis,
                executive_summary=executive_summary,
            )

        except SQLAlchemyError as e:
            logger.error(f"Error al realizar análisis de inventario: {e}")
            raise PurchaseSuggestionAnalysisException(
                "Error al consultar la base de datos para sugerencias."
            )

    async def analyze_inventory(self) -> str:
        """Orquesta el análisis de datos desde SQL y el enriquecimiento opcional con IA."""
        try:
            query = await self._get_sql_query()
            result = await self.db.execute(query)
            rows = result.scalars().all()
            analysis = await self._process_data(rows)
            executive_summary = await self.llm_service.generate_executive_summary(
                analysis.model_dump()
            )
            return executive_summary
        except SQLAlchemyError as e:
            logger.error(f"Error al realizar análisis de inventario: {e}")
            return "No se pudo realizar el análisis de inventario."

    async def fetch_purchase_suggestions(
        self, text: str
    ) -> list[PurchaseSuggestionItem]:
        """Realiza sugerencias de compra utilizando el servicio de LLM."""
        try:
            analysis = await self.llm_service.analyze_purchase_suggestions(text)
            return analysis.suggestions
        except PurchaseSuggestionAnalysisException as e:
            logger.error(f"Error al obtener sugerencias de compra: {e}")
            return []

    async def update_inventory(
        self,
        structured_data: dict[str, Any],
    ) -> None:
        """Actualiza el inventario en la base de datos."""
        try:
            await self.db.update_inventory(structured_data)
        except SQLAlchemyError as e:
            logger.error(f"Error al actualizar inventario: {e}")
            return

    async def generate_and_store_vector_analysis(self, analysis_data: dict) -> None:
        """Genera un resumen textual, obtiene su embedding de Ollama y lo guarda en sales_vectors."""
        summary_text = f"Análisis de inventario y ventas: {json.dumps(analysis_data, ensure_ascii=False)}"

        try:
            base_url = settings.OLLAMA_BASE_URL or "http://ollama:11434"
            embed_model = settings.EMBEDDING_MODEL or "nomic-embed-text"

            ollama_url = f"{base_url}/api/embeddings"
            payload = {"model": embed_model, "prompt": summary_text}

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(ollama_url, json=payload)
                response.raise_for_status()
                embedding_vector = response.json().get("embedding")

            if not embedding_vector:
                logger.error("Ollama no devolvió un vector de embeddings válido.")
                return

            db_vector = SalesVector(content=summary_text, embedding=embedding_vector)
            self.db.add(db_vector)
            await self.db.commit()
            logger.info("Vector de inventario guardado exitosamente en pgvector.")

        except (httpx.HTTPError, SQLAlchemyError, json.JSONDecodeError) as e:
            logger.error(f"Error al generar o guardar el vector de inventario: {e}")
            await self.db.rollback()
