import uuid
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.audit import record_audit
from core.db import Base
from core.tenancy import get_current_tenant

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

# Techo máximo para la paginación (evita dumps masivos con skip/limit arbitrarios)
MAX_PAGE_SIZE = 100


def sanitize_pagination(skip: int, limit: int) -> tuple[int, int]:
    skip = max(0, skip or 0)
    limit = min(max(limit, 1), MAX_PAGE_SIZE)
    return skip, limit


def _is_soft_deletable(model: type) -> bool:
    """¿El modelo soporta soft-delete (tiene el mixin)?"""
    return hasattr(model, "is_deleted")


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        """
        Clase CRUD base con métodos por defecto para Crear, Leer, Actualizar, Eliminar.

        **Parámetros**

        * `model`: Una clase de modelo SQLAlchemy
        """
        self.model = model
        self.default_loads = []

    def _scope_by_tenant(self, statement):
        """Aplica el filtro de tenant y de soft-delete del request cuando el modelo los soporta."""
        tenant_id = get_current_tenant()
        if tenant_id is not None and hasattr(self.model, "tenant_id"):
            statement = statement.where(self.model.tenant_id == tenant_id)
        if _is_soft_deletable(self.model):
            statement = statement.where(self.model.is_deleted.is_(False))
        return statement

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        query = select(self.model)
        if self.default_loads:
            query = query.options(*self.default_loads)
        query = query.filter(self.model.id == id)
        query = self._scope_by_tenant(query)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        skip, limit = sanitize_pagination(skip, limit)
        query = select(self.model).offset(skip).limit(limit)
        if self.default_loads:
            query = query.options(*self.default_loads)
        query = self._scope_by_tenant(query)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, *, obj_in: CreateSchemaType, **kwargs
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        # Write-path: asigna el tenant del request si el modelo lo requiere.
        if hasattr(self.model, "tenant_id") and "tenant_id" not in kwargs:
            tenant_id = get_current_tenant()
            if tenant_id:
                kwargs = {**kwargs, "tenant_id": tenant_id}
        # Combina los datos del schema con cualquier kwarg adicional (como created_by)
        db_obj = self.model(**obj_in_data, **kwargs)
        db.add(db_obj)
        try:
            await db.flush()
        except IntegrityError:
            await db.rollback()
            raise
        except SQLAlchemyError:
            await db.rollback()
            raise
        await record_audit(
            db,
            actor_id=kwargs.get("created_by"),
            actor_email=None,
            entity=self.model.__name__,
            entity_id=getattr(db_obj, "id", None),
            action="create",
            details=obj_in_data,
        )
        try:
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise
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
        try:
            await db.flush()
        except IntegrityError:
            await db.rollback()
            raise
        except SQLAlchemyError:
            await db.rollback()
            raise
        await record_audit(
            db,
            actor_id=update_data.get("updated_by"),
            actor_email=None,
            entity=self.model.__name__,
            entity_id=getattr(db_obj, "id", None),
            action="update",
            details=update_data,
        )
        try:
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: uuid.UUID) -> ModelType | None:
        obj = await self.get(db, id=id)
        if obj:
            if _is_soft_deletable(self.model):
                # Soft-delete: marca la fila en vez de borrarla.
                await self._soft_delete(db, db_obj=obj)
            else:
                await db.delete(obj)
                try:
                    await db.commit()
                except IntegrityError:
                    await db.rollback()
                    raise
                except SQLAlchemyError:
                    await db.rollback()
                    raise
        return obj

    async def _soft_delete(
        self, db: AsyncSession, *, db_obj: ModelType
    ) -> ModelType:
        """Marca la fila como borrada (soft-delete) sin eliminarla de la BD."""
        db_obj.is_deleted = True
        db_obj.deleted_at = datetime.now(timezone.utc)
        # deleted_by se setea desde el contexto del usuario en el flujo de auditoría.
        db.add(db_obj)
        try:
            await db.flush()
        except IntegrityError:
            await db.rollback()
            raise
        except SQLAlchemyError:
            await db.rollback()
            raise
        await record_audit(
            db,
            actor_id=getattr(db_obj, "deleted_by", None),
            actor_email=None,
            entity=self.model.__name__,
            entity_id=getattr(db_obj, "id", None),
            action="delete",
            details={"is_deleted": True},
        )
        try:
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise
        await db.refresh(db_obj)
        return db_obj
