from uuid import UUID

from core.crud_supplier import crud_supplier
from schemas.supplier import SupplierCreate, SupplierUpdate
from sqlalchemy.ext.asyncio import AsyncSession


class SupplierService:
    def __init__(self):
        self.crud = crud_supplier

    async def get_all(self, db: AsyncSession, *, skip: int = 0, limit: int = 100):
        return await self.crud.get_multi(db, skip=skip, limit=limit)

    async def get_by_id(self, db: AsyncSession, *, id: UUID):
        return await self.crud.get(db, id)

    async def create(self, db: AsyncSession, *, obj_in: SupplierCreate):
        return await self.crud.create(db, obj_in=obj_in)

    async def update(self, db: AsyncSession, *, id: UUID, obj_in: SupplierUpdate):
        db_obj = await self.crud.get(db, id)
        return await self.crud.update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, id: UUID):
        """Elimina un proveedor."""
        return await self.crud.remove(db=db, id=id)


supplier_service = SupplierService()
