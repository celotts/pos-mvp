from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.crud_country import crud_country
from core.crud_state_province import crud_state_province
from core.i18n import tr
from schemas.state_province import StateProvinceCreate, StateProvinceUpdate


class StateProvinceService:
    def __init__(self):
        self.crud = crud_state_province

    async def _get_or_404(self, db: AsyncSession, id: UUID):
        db_obj = await self.crud.get(db, id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=tr("NOT_FOUND.STATE_PROVINCE_ID", state_id=str(id)),
            )
        return db_obj

    async def _get_country_or_404(self, db: AsyncSession, country_id: UUID):
        country = await crud_country.get(db, country_id)
        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=tr("NOT_FOUND.COUNTRY_ID", country_id=str(country_id)),
            )
        return country

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        return await self.crud.get_multi(db, skip=skip, limit=limit)

    async def get_by_id(self, db: AsyncSession, id: UUID):
        return await self._get_or_404(db, id)

    async def create(self, db: AsyncSession, *, obj_in: StateProvinceCreate):
        # Valida la existencia del país ANTES de insertar (evita depender del
        # reconocimiento frágil del mensaje del driver en el IntegrityError).
        await self._get_country_or_404(db, obj_in.country_id)
        try:
            return await self.crud.create(db, obj_in=obj_in)
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=tr("DB.INTEGRITY_GENERIC"),
            ) from e

    async def update(self, db: AsyncSession, *, id: UUID, obj_in: StateProvinceUpdate):
        db_obj = await self._get_or_404(db, id)
        if obj_in.country_id is not None:
            await self._get_country_or_404(db, obj_in.country_id)
        try:
            return await self.crud.update(db, db_obj=db_obj, obj_in=obj_in)
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=tr("DB.INTEGRITY_GENERIC"),
            ) from e

    async def delete(self, db: AsyncSession, *, id: UUID):
        # Valida que el estado exista ANTES de borrar (404 si no existe).
        await self._get_or_404(db, id)
        try:
            return await self.crud.remove(db, id=id)
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=tr("DB.INTEGRITY_GENERIC"),
            ) from e


state_province_service = StateProvinceService()