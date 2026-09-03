import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.crud_permission import crud_permission
from core.crud_role import crud_role
from core.i18n import tr
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
            detail=tr("DUPLICATE.ROLE_NAME", name=role_in.name),
        )
    return await crud_role.create(db=db, obj_in=role_in)


async def get_role(db: AsyncSession, *, role_id: uuid.UUID) -> Role:
    """Get a role by ID, handling the not-found case."""
    db_role = await crud_role.get(db=db, id=role_id)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=tr("NOT_FOUND.ROLE")
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
            detail=tr("ROLE.PROTECTED_MODIFY", name=db_role.name),
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
                detail=tr("DUPLICATE.ROLE_NAME", name=role_in.name),
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
            detail=tr("ROLE.PROTECTED_DELETE", name=db_role.name),
        )

    # Protección N°2: Roles en uso.
    # Protection #2: Roles in use.
    if db_role.users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=tr("ROLE.DELETE_ASSIGNED", name=db_role.name),
        )

    deleted_role = await crud_role.remove(db=db, id=role_id)
    # This check is for safety, although get_role already validates it.
    if not deleted_role:
        raise HTTPException(status_code=404, detail=tr("NOT_FOUND.ROLE"))
    return deleted_role


async def get_permissions(db: AsyncSession) -> list:
    """Lista todos los permisos del catálogo (para la UI de administración)."""
    return await crud_permission.get_all(db)


async def assign_permissions_to_role(
    db: AsyncSession, *, role_id: uuid.UUID, permission_codes: list[str]
) -> Role:
    """Reemplaza el conjunto de permisos de un rol por los códigos indicados.

    Solo aplicable a roles no protegidos (SUPER_ADMIN/ADMIN quedan intactos).
    """
    db_role = await get_role(db=db, role_id=role_id)
    if db_role.name in settings.PROTECTED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=tr("ROLE.PROTECTED_MODIFY", name=db_role.name),
        )

    # Validamos que todos los códigos existan en el catálogo; los ignorados se rechazan.
    existing = {p.code: p for p in await crud_permission.get_all(db)}
    unknown = [c for c in permission_codes if c not in existing]
    if unknown:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=tr("VALIDATION.UNKNOWN_PERMISSIONS", unknown=", ".join(unknown)),
        )

    db_role.permissions = [existing[c] for c in set(permission_codes)]
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role
