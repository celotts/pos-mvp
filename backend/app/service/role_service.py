import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.crud_role import crud_role
from models.role import Role
from schemas.role import RoleCreate, RoleUpdate


async def get_roles(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Role]:
    """Get a list of roles."""
    return await crud_role.get_multi(db, skip=skip, limit=limit)


async def create_role(db: AsyncSession, *, role_in: RoleCreate) -> Role:
    """Create a new role."""
    # Asegura que el nombre del rol se guarde en mayúsculas.
    role_in.name = role_in.name.upper()

    existing_role = await crud_role.get_by_name(db, name=role_in.name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A role with the name '{role_in.name}' already exists.",
        )
    return await crud_role.create(db=db, obj_in=role_in)


async def get_role(db: AsyncSession, *, role_id: uuid.UUID) -> Role:
    """Get a role by ID, handling the not-found case."""
    db_role = await crud_role.get(db=db, id=role_id)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found."
        )
    return db_role


async def update_role(
    db: AsyncSession, *, role_id: uuid.UUID, role_in: RoleUpdate
) -> Role:
    """Update a role, first checking for its existence and if it is protected."""
    db_role = await get_role(db=db, role_id=role_id)

    # Protection logic: protected roles cannot be modified.
    if db_role.name in settings.PROTECTED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{db_role.name}' is protected and cannot be modified.",
        )

    # Si se está actualizando el nombre, convertirlo a mayúsculas y verificar duplicados.
    # If the name is being updated, convert it to uppercase and check for duplicates.
    if role_in.name is not None:
        role_in.name = role_in.name.upper()
        existing_role = await crud_role.get_by_name(db, name=role_in.name)
        # If a role with that name already exists and it's not the one we are updating.
        if existing_role and existing_role.id != role_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A role with the name '{role_in.name}' already exists.",
            )

    return await crud_role.update(db=db, db_obj=db_role, obj_in=role_in)


async def remove_role(db: AsyncSession, *, role_id: uuid.UUID) -> Role:
    """Deletes a role, with two levels of protection:
    1. Protected roles cannot be deleted.
    2. Roles cannot be deleted if they are assigned to any user.
    """
    db_role = await get_role(db=db, role_id=role_id)

    # Protection #1: System roles.
    if db_role.name in settings.PROTECTED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{db_role.name}' is protected and cannot be deleted.",
        )

    # Protección N°2: Roles en uso.
    # Protection #2: Roles in use.
    if db_role.users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Role '{db_role.name}' cannot be deleted because it is assigned to one or more users.",
        )

    deleted_role = await crud_role.remove(db=db, id=role_id)
    # This check is for safety, although get_role already validates it.
    if not deleted_role:
        raise HTTPException(status_code=404, detail="Role not found to delete.")
    return deleted_role
