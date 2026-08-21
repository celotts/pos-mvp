from typing import Any

from logger import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.inventory_analysis import (
    PurchaseSuggestionAnalysisException,
    PurchaseSuggestionItem,
)
from app.services.llm_service import AbstractLLMService


class InventoryAnalysisService:
    """Servicio para realizar análisis de inventario."""

    def __init__(self, llm_service: AbstractLLMService, db: AsyncSession):
        self.llm_service = llm_service
        self.db = db

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
        structured_data: dict[
            str, Any
        ],  # Agregado docstring para clarificar el tipo de retorno
    ) -> None:
        """Actualiza el inventario en la base de datos."""
        try:
            await self.db.update_inventory(structured_data)
        except SQLAlchemyError as e:
            logger.error(f"Error al actualizar inventario: {e}")
            return  # Se mantiene la lógica original de retornar None en caso de error
