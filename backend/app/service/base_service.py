import uuid
from typing import Any, Generic, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import Base
from core.tenancy import get_current_tenant

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        """
        Servicio CRUD con métodos por defecto: Create, Read, Update, Delete.

        **Parámetros**

        * `model`: Un modelo de SQLAlchemy
        """
        self.model = model

    def _scope_by_tenant(self, statement):
        """Aplica el filtro de tenant del request cuando el modelo lo soporta."""
        tenant_id = get_current_tenant()
        if tenant_id is not None and hasattr(self.model, "tenant_id"):
            return statement.where(self.model.tenant_id == tenant_id)
        return statement

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """Obtiene un registro por su ID."""
        query = self._scope_by_tenant(
            select(self.model).where(self.model.id == id)
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_all(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Obtiene una lista de registros."""
        query = self._scope_by_tenant(select(self.model))
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Crea un nuevo registro."""
        obj_in_data = jsonable_encoder(obj_in)
        # Write-path: asigna el tenant del request si el modelo lo requiere.
        tenant_id = get_current_tenant() if hasattr(self.model, "tenant_id") else None
        db_obj = self.model(**obj_in_data)
        if tenant_id:
            db_obj.tenant_id = tenant_id
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, *, id: uuid.UUID, obj_in: UpdateSchemaType
    ) -> ModelType:
        """Actualiza un registro."""
        db_obj = await self.get(db, id=id)
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: uuid.UUID) -> ModelType | None:
        """Elimina un registro."""
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
