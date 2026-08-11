import uuid

from core import crud_role
from fastapi import HTTPException, status
from models.role import Role
from schemas.role import RoleCreate, RoleUpdate
from sqlalchemy.ext.asyncio import AsyncSession


async def get_roles(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Role]:
    """Obtiene una lista de roles."""
    return await crud_role.get_roles(db, skip=skip, limit=limit)


async def create_role(db: AsyncSession, *, role_in: RoleCreate) -> Role:
    """Crea un nuevo rol."""
    return await crud_role.create_role(db=db, role_in=role_in)


async def get_role(db: AsyncSession, *, role_id: uuid.UUID) -> Role:
    """Obtiene un rol por ID, manejando el caso de no encontrarlo."""
    db_role = await crud_role.get_role(db=db, role_id=role_id)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado."
        )
    return db_role


async def update_role(
    db: AsyncSession, *, role_id: uuid.UUID, role_in: RoleUpdate
) -> Role:
    """Actualiza un rol, verificando primero su existencia."""
    db_role = await get_role(db=db, role_id=role_id)
    return await crud_role.update_role(db=db, db_role=db_role, role_in=role_in)
