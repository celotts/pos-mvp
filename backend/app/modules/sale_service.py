from decimal import Decimal

from fastapi import BackgroundTasks, HTTPException, status
from models.product import Product
from models.sale import Sale, SaleItem
from models.user import User
from schemas.sale import SaleCreate, SaleUpdate
from sqlalchemy.ext.asyncio import AsyncSession

from .ai_service import ai_service
from .base_service import CRUDService


class SaleService(CRUDService[Sale, SaleCreate, SaleUpdate]):
    """
    Servicio para las operaciones CRUD de Ventas con lógica de negocio extendida,
    incluyendo la integración con el servicio de IA.
    """

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
                detail="Una venta debe tener al menos un producto.",
            )

        # 1. Validar items y calcular totales
        for item_in in sale_in.items:
            product = await db.get(Product, item_in.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto con id {item_in.product_id} no encontrado.",
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
            items=sale_items_to_create,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # 3. Disparar la creación del embedding en segundo plano
        background_tasks.add_task(
            ai_service.create_and_store_sale_embedding, db, db_obj.id
        )

        return db_obj


sale_service = SaleService(Sale)
