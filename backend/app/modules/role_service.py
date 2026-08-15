import uuid

from core.crud_role import crud_role
from fastapi import HTTPException, status
from models.role import Role
from schemas.role import RoleCreate, RoleUpdate
from sqlalchemy.ext.asyncio import AsyncSession

# Roles del sistema que no pueden ser modificados o eliminados.
PROTECTED_ROLES = {"SUPER_ADMIN", "ADMIN"}


async def get_roles(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Role]:
    """Obtiene una lista de roles."""
    return await crud_role.get_multi(db, skip=skip, limit=limit)


async def create_role(db: AsyncSession, *, role_in: RoleCreate) -> Role:
    """Crea un nuevo rol."""
    existing_role = await crud_role.get_by_name(db, name=role_in.name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A role with the name '{role_in.name}' already exists.",
        )
    return await crud_role.create(db=db, obj_in=role_in)


async def get_role(db: AsyncSession, *, role_id: uuid.UUID) -> Role:
    """Obtiene un rol por ID, manejando el caso de no encontrarlo."""
    db_role = await crud_role.get(db=db, id=role_id)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found."
        )
    return db_role


async def update_role(
    db: AsyncSession, *, role_id: uuid.UUID, role_in: RoleUpdate
) -> Role:
    """Actualiza un rol, verificando primero su existencia y si está protegido."""
    db_role = await get_role(db=db, role_id=role_id)

    # Lógica de protección: si el nombre del rol está en la lista, no se puede modificar.
    if db_role.name in PROTECTED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{db_role.name}' is protected and cannot be modified.",
        )

    return await crud_role.update(db=db, db_obj=db_role, obj_in=role_in)


async def remove_role(db: AsyncSession, *, role_id: uuid.UUID) -> Role:
    """
    Elimina un rol, con dos niveles de protección:
    1. No se pueden eliminar roles protegidos.
    2. No se pueden eliminar roles si están asignados a algún usuario.
    """
    db_role = await get_role(db=db, role_id=role_id)

    # Protección N°1: Roles del sistema.
    if db_role.name in PROTECTED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{db_role.name}' is protected and cannot be deleted.",
        )

    # Protección N°2: Roles en uso.
    if db_role.users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Role '{db_role.name}' cannot be deleted because it is assigned to one or more users.",
        )

    deleted_role = await crud_role.remove(db=db, id=role_id)
    # Esta comprobación es por seguridad, aunque get_role ya lo valida.
    if not deleted_role:
        raise HTTPException(status_code=404, detail="Role not found to delete.")
    return deleted_role
