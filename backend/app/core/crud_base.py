import uuid
from typing import Any, Generic, TypeVar

from core.db import Base
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        """
        Clase CRUD base con métodos por defecto para Crear, Leer, Actualizar, Eliminar.

        **Parámetros**

        * `model`: Una clase de modelo SQLAlchemy
        """
        self.model = model
        self.default_loads = []

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        query = select(self.model)
        if self.default_loads:
            query = query.options(*self.default_loads)
        query = query.filter(self.model.id == id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        if self.default_loads:
            query = query.options(*self.default_loads)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, *, obj_in: CreateSchemaType, **kwargs
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        # Combina los datos del schema con cualquier kwarg adicional (como created_by)
        db_obj = self.model(**obj_in_data, **kwargs)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
        **kwargs,
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # Combina los datos de actualización con kwargs (como updated_by)
        update_data.update(kwargs)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: uuid.UUID) -> ModelType | None:
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
