from uuid import UUID

from core.crud_state_province import crud_state_province
from schemas.state_province import StateProvinceCreate, StateProvinceUpdate
from sqlalchemy.orm import Session


class StateProvinceService:
    def __init__(self):
        self.crud = crud_state_province

    async def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return await self.crud.get_multi(db, skip=skip, limit=limit)

    async def get_by_id(self, db: Session, id: UUID):
        return await self.crud.get(db, id)

    async def create(self, db: Session, *, obj_in: StateProvinceCreate):
        return await self.crud.create(db, obj_in=obj_in)

    async def update(self, db: Session, *, id: UUID, obj_in: StateProvinceUpdate):
        db_obj = await self.crud.get(db, id)
        return await self.crud.update(db, db_obj=db_obj, obj_in=obj_in)


state_province_service = StateProvinceService()
