from uuid import UUID

from core.crud_store import crud_store
from schemas.store import StoreCreate, StoreUpdate
from sqlalchemy.ext.asyncio import AsyncSession


class StoreService:
    def __init__(self):
        self.crud = crud_store

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        return await self.crud.get_multi(db, skip=skip, limit=limit)

    async def get_by_id(self, db: AsyncSession, id: UUID):
        return await self.crud.get(db, id)

    async def create(self, db: AsyncSession, *, obj_in: StoreCreate):
        return await self.crud.create(db, obj_in=obj_in)

    async def update(self, db: AsyncSession, *, id: UUID, obj_in: StoreUpdate):
        db_obj = await self.crud.get(db, id)
        return await self.crud.update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, id: UUID):
        """Elimina una tienda."""
        return await self.crud.remove(db=db, id=id)


store_service = StoreService()
