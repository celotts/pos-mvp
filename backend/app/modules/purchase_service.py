from decimal import Decimal

from fastapi import HTTPException, status
from models.product import Product
from models.purchase import Purchase, PurchaseItem
from schemas.purchase import PurchaseCreate, PurchaseUpdate
from sqlalchemy.ext.asyncio import AsyncSession

from .base_service import CRUDService


class PurchaseService(CRUDService[Purchase, PurchaseCreate, PurchaseUpdate]):
    """
    Servicio para las operaciones CRUD de Compras con lógica de negocio extendida.
    """

    async def create(self, db: AsyncSession, *, obj_in: PurchaseCreate) -> Purchase:
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
                detail="A purchase must have at least one product.",
            )

        # 1. Validar items y calcular totales
        for item_in in obj_in.items:
            product = await db.get(Product, item_in.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with id {item_in.product_id} not found.",
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
            "total_amount": total_amount,
            "total_tax_amount": total_tax_amount,
            "items": purchase_items_to_create,
        }

        # 3. Usar el constructor del modelo para crear la instancia con sus relaciones
        db_obj = self.model(**purchase_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Aquí es donde iría la lógica de negocio extra, como actualizar el stock.
        print(f"Business logic executed! Purchase {db_obj.id} created with its items.")

        return db_obj


# Instancia del servicio para ser usada en los controladores
purchase_service = PurchaseService(Purchase)
