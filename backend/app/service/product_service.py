import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.crud_product import crud_product
from core.i18n import tr
from models import User
from schemas.product import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self):
        self.crud = crud_product

    async def get_all(self, db: AsyncSession, *, skip: int = 0, limit: int = 100):
        return await self.crud.get_multi(db, skip=skip, limit=limit)

    async def search(
        self,
        db: AsyncSession,
        *,
        search: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list, int]:
        """Búsqueda server-side por nombre/SKU con paginación. Retorna (items, total)."""
        return await self.crud.search(db, search=search, skip=skip, limit=limit)


    async def get_all_with_total(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> tuple[list, int]:
        """get_all con total, sin filtro de búsqueda (para el listado paginado)."""
        items, total = await self.crud.search(db, search=None, skip=skip, limit=limit)
        return items, total

    async def get_by_id(self, db: AsyncSession, *, id: uuid.UUID):
        return await self.crud.get(db, id)

    async def create(
        self, db: AsyncSession, *, obj_in: ProductCreate, current_user: User
    ):
        try:
            return await self.crud.create(db, obj_in=obj_in)
        except IntegrityError as e:
            await db.rollback()
            error_msg = str(e.orig).lower()

            # Discriminamos qué restricción de integridad falló realmente
            if "sku" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=tr("DUPLICATE.SKU"),
                )
            elif "supplier_id" in error_msg or "foreign key" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=tr(
                        "NOT_FOUND.SUPPLIER_ID",
                        supplier_id=str(obj_in.supplier_id),
                    ),
                )

            # Si fue otro error de integridad no contemplado
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=tr("DB.CONSTRAINT_VIOLATION"),
            )

    async def update(
        self,
        db: AsyncSession,
        *,
        id: uuid.UUID,
        obj_in: ProductUpdate,
        current_user: User,
    ):
        db_obj = await self.crud.get(db, id=id)
        if not db_obj:
            return None
        return await self.crud.update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, id: uuid.UUID):
        return await self.crud.remove(db=db, id=id)


product_service = ProductService()
