import uuid

from core.crud_product import crud_product
from fastapi import HTTPException, status
from models import User
from schemas.product import ProductCreate, ProductUpdate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class ProductService:
    def __init__(self):
        self.crud = crud_product

    async def get_all(self, db: AsyncSession, *, skip: int = 0, limit: int = 100):
        """Obtiene una lista de productos."""
        return await self.crud.get_multi(db, skip=skip, limit=limit)

    async def get_by_id(self, db: AsyncSession, *, id: uuid.UUID):
        """Obtiene un producto por ID."""
        return await self.crud.get(db, id)

    async def create(
        self, db: AsyncSession, *, obj_in: ProductCreate, current_user: User
    ):
        """Crea un nuevo producto."""
        try:
            # Pasamos el ID del usuario para auditoría
            return await self.crud.create(db, obj_in=obj_in, created_by=current_user.id)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A product with this SKU already exists.",
            )

    async def update(
        self,
        db: AsyncSession,
        *,
        id: uuid.UUID,
        obj_in: ProductUpdate,
        current_user: User,
    ):
        """Actualiza un producto existente."""
        db_obj = await self.crud.get(db, id=id)
        if not db_obj:
            return None
        # Pasamos el ID del usuario para auditoría
        return await self.crud.update(
            db, db_obj=db_obj, obj_in=obj_in, updated_by=current_user.id
        )

    async def delete(self, db: AsyncSession, *, id: uuid.UUID):
        """Elimina un producto existente."""
        return await self.crud.remove(db=db, id=id)


product_service = ProductService()
