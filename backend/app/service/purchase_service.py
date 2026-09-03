from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.i18n import tr
from models.product import Product
from models.purchase import Purchase, PurchaseItem
from models.user import User
from schemas.purchase import PurchaseCreate, PurchaseUpdate

from .base_service import CRUDService


class PurchaseService(CRUDService[Purchase, PurchaseCreate, PurchaseUpdate]):
    """
    Servicio para las operaciones CRUD de Compras con lógica de negocio extendida.
    """

    async def get(self, db: AsyncSession, id: Any) -> Purchase | None:
        query = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(Purchase.items))
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_all(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[Purchase]:
        query = (
            select(self.model)
            .offset(skip)
            .limit(limit)
            .options(selectinload(Purchase.items))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, *, obj_in: PurchaseCreate, current_user: User | None = None
    ) -> Purchase:
        """
        Crea una nueva compra, valida los items, calcula los totales y crea
        los registros asociados en la base de datos.
        """
        total_amount = Decimal("0.0")
        # La lógica de impuestos se puede expandir aquí. Por ahora es 0.
        total_tax_amount = Decimal("0.0")
        purchase_items_to_create = []

        if not obj_in.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=tr("VALIDATION.EMPTY_PURCHASE"),
            )

        # 1. Validar items y calcular totales
        for item_in in obj_in.items:
            product = await db.get(Product, item_in.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=tr(
                        "NOT_FOUND.PRODUCT_ID", product_id=str(item_in.product_id)
                    ),
                )

            item_total = Decimal(str(item_in.price_at_purchase)) * Decimal(
                item_in.quantity
            )
            total_amount += item_total

            purchase_items_to_create.append(
                PurchaseItem(
                    product_id=item_in.product_id,
                    quantity=item_in.quantity,
                    price_at_purchase=item_in.price_at_purchase,
                )
            )

        # 2. Crear el objeto Purchase con los datos calculados y los items
        purchase_data = {
            "supplier_id": obj_in.supplier_id,
            "store_id": obj_in.store_id,
            "pos_terminal_id": obj_in.pos_terminal_id,
            "total_amount": total_amount,
            "total_tax_amount": total_tax_amount,
            "created_by": current_user.id if current_user else None,
            "items": purchase_items_to_create,
        }

        # 3. Usar el constructor del modelo para crear la instancia con sus relaciones
        db_obj = self.model(**purchase_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj


# Instancia del servicio para ser usada en los controladores
purchase_service = PurchaseService(Purchase)
