from decimal import Decimal

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.product import Product
from models.sale import Sale
from models.sale_item import SaleItem
from models.user import User
from schemas.sale import SaleCreate, SaleStatus, SaleUpdate

from .ai_service import ai_service
from .base_service import CRUDService


class SaleService(CRUDService[Sale, SaleCreate, SaleUpdate]):
    """
    Servicio para las operaciones CRUD de Ventas con lógica de negocio extendida,
    incluyendo la integración con el servicio de IA.
    """

    async def get(self, db: AsyncSession, id) -> Sale | None:
        query = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(Sale.items))
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_all(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[Sale]:
        query = (
            select(self.model)
            .order_by(self.model.sale_date.desc())
            .offset(skip)
            .limit(limit)
            .options(selectinload(Sale.items))
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def return_sale(
        self, db: AsyncSession, *, sale_id, current_user: User
    ) -> Sale:
        """Devuelve (cancela) una venta completa. Reintegra stock al excluirla del cómputo."""
        db_sale = await self.get(db, id=sale_id)
        if not db_sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale does not exist.",
            )
        if db_sale.status == SaleStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The sale is already cancelled.",
            )
        db_sale.status = SaleStatus.CANCELLED
        await db.commit()
        await db.refresh(db_sale)
        return db_sale

    async def create_sale(
        self,
        db: AsyncSession,
        *,
        sale_in: SaleCreate,
        current_user: User,
        background_tasks: BackgroundTasks,
    ) -> Sale:
        """
        Crea una nueva venta, valida los productos, calcula el total y
        dispara la creación del embedding en segundo plano.
        """
        total_amount = Decimal("0.0")
        sale_items_to_create = []

        if not sale_in.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A sale must have at least one product.",
            )

        # 1. Validar items y calcular totales
        for item_in in sale_in.items:
            product = await db.get(Product, item_in.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with id {item_in.product_id} not found.",
                )

            item_total = product.price * Decimal(item_in.quantity)
            total_amount += item_total

            sale_items_to_create.append(
                SaleItem(
                    product_id=item_in.product_id,
                    quantity=item_in.quantity,
                    price_at_sale=product.price,
                )
            )

        # 2. Crear el objeto Sale con sus items
        db_obj = Sale(
            **sale_in.model_dump(exclude={"items"}),
            user_id=current_user.id,
            total_amount=total_amount,
            total_tax_amount=Decimal("0.0"),
            discount_amount=Decimal("0.0"),
            items=sale_items_to_create,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # 3. Disparar la creación del embedding en segundo plano
        background_tasks.add_task(ai_service.create_and_store_sale_embedding, db_obj.id)

        return db_obj


sale_service = SaleService(Sale)
