from decimal import Decimal

from core.crud_product import crud_product
from core.crud_sale import crud_sale
from models.sale import SaleItem
from models.user import User
from schemas.sale import SaleCreate
from sqlalchemy.orm import Session


class SaleService:
    def __init__(self):
        self.crud = crud_sale

    async def create_sale(
        self, db: Session, *, sale_in: SaleCreate, current_user: User
    ):
        total_amount = Decimal("0.0")
        sale_items_to_create = []

        # Calcular el total y preparar los items
        for item_in in sale_in.items:
            product = await crud_product.get(db, item_in.product_id)
            if not product:
                raise ValueError(f"Product with id {item_in.product_id} not found")

            item_total = product.price * item_in.quantity
            total_amount += item_total

            sale_items_to_create.append(
                SaleItem(
                    product_id=item_in.product_id,
                    quantity=item_in.quantity,
                    price_at_sale=product.price,
                )
            )

        # Crear la venta
        sale_obj = await self.crud.create(
            db,
            obj_in=sale_in,
            user_id=current_user.id,
            total_amount=total_amount,
            items=sale_items_to_create,
        )
        return sale_obj


sale_service = SaleService()
