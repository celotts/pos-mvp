from uuid import UUID

from sqlalchemy.orm import Session

from core.crud_municipality import crud_municipality
from schemas.municipality import MunicipalityCreate, MunicipalityUpdate


class MunicipalityService:
    def __init__(self):
        self.crud = crud_municipality

    async def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return await self.crud.get_multi(db, skip=skip, limit=limit)

    async def get_by_id(self, db: Session, id: UUID):
        return await self.crud.get(db, id)

    async def create(self, db: Session, *, obj_in: MunicipalityCreate):
        return await self.crud.create(db, obj_in=obj_in)

    async def update(self, db: Session, *, id: UUID, obj_in: MunicipalityUpdate):
        return await self.crud.update(
            db, db_obj=await self.get_by_id(db, id), obj_in=obj_in
        )

    async def delete(self, db: Session, *, id: UUID):
        return await self.crud.remove(db, id=id)


municipality_service = MunicipalityService()
