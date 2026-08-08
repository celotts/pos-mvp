import uuid

from models.role import Role as RoleModel
from schemas.role import RoleCreate as RoleCreateSchema
from schemas.role import RoleUpdate as RoleUpdateSchema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_role(db: AsyncSession, role_id: uuid.UUID) -> RoleModel | None:
    """Obtiene un rol por su ID."""
    return await db.get(RoleModel, role_id)


async def get_roles(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[RoleModel]:
    """Obtiene una lista de roles."""
    result = await db.execute(select(RoleModel).offset(skip).limit(limit))
    return result.scalars().all()


async def create_role(db: AsyncSession, *, role_in: RoleCreateSchema) -> RoleModel:
    """Crea un nuevo rol."""
    db_role = RoleModel(name=role_in.name)
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role


async def update_role(
    db: AsyncSession, *, db_role: RoleModel, role_in: RoleUpdateSchema
) -> RoleModel:
    """Actualiza un rol."""
    update_data = role_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_role, field, value)
    await db.commit()
    await db.refresh(db_role)
    return db_role
