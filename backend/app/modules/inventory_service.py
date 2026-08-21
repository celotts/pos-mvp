# inventory_service.py
from typing import Any

from logger import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class InventoryService:
    """Servicio para gestionar el inventario."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_inventory_item(self, item: dict[str, Any]) -> None:
        """Crea un nuevo ítem en el inventario."""
        try:
            await self.db.add_inventory_item(item)
        except SQLAlchemyError as e:
            logger.error(f"Error al crear ítem de inventario: {e}")

    async def read_inventory_item(self, item_id: int) -> dict[str, Any]:
        """Lee un ítem del inventario."""
        try:
            return await self.db.get_inventory_item(item_id)
        except SQLAlchemyError as e:
            logger.error(f"Error al leer ítem de inventario: {e}")
            return {}

    async def update_inventory_item(self, item_id: int, item: dict[str, Any]) -> None:
        """Actualiza un ítem del inventario."""
        try:
            await self.db.update_inventory_item(item_id, item)
        except SQLAlchemyError as e:
            logger.error(f"Error al actualizar ítem de inventario: {e}")

    async def delete_inventory_item(self, item_id: int) -> None:
        """Elimina un ítem del inventario."""
        try:
            await self.db.delete_inventory_item(item_id)
        except SQLAlchemyError as e:
            logger.error(f"Error al eliminar ítem de inventario: {e}")
