import uuid

from core.crud_role import crud_role
from core.crud_user import crud_user
from fastapi import HTTPException, status
from models.user import User
from schemas.user import UserCreate, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    """
    Obtiene una lista de usuarios.
    """
    return await crud_user.get_multi(db, skip=skip, limit=limit)


async def get_user(db: AsyncSession, *, user_id: uuid.UUID) -> User:
    """
    Obtiene un usuario por su ID. Lanza un error 404 si no se encuentra.
    """
    db_user = await crud_user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return db_user


async def create_user_with_logic(db: AsyncSession, *, user_in: UserCreate) -> User:
    """
    Crea un nuevo usuario con validaciones de negocio.
    """
    # 1. Verificar si el email ya existe
    existing_users = await crud_user.get_multi(db, limit=1, email=user_in.email)
    if existing_users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    # 2. Verificar si el rol asignado es válido
    role = await crud_role.get(db, id=user_in.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID '{user_in.role_id}' not found.",
        )

    # 3. Crear el usuario
    return await crud_user.create(db=db, obj_in=user_in)


async def update_user(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    user_in: UserUpdate,
    current_user: User,
) -> User:
    """
    Actualiza un usuario, con lógica de permisos.
    """
    db_user = await get_user(db=db, user_id=user_id)

    # Lógica de negocio: Un usuario no puede desactivarse a sí mismo ni cambiar su propio rol.
    is_updating_self = db_user.id == current_user.id
    if is_updating_self:
        if user_in.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot deactivate your own account.",
            )
        if user_in.role_id and user_in.role_id != db_user.role_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot change your own role.",
            )

    return await crud_user.update(db=db, db_obj=db_user, obj_in=user_in)


async def remove_user(db: AsyncSession, *, user_id: uuid.UUID) -> User:
    """
    Elimina un usuario.
    """
    db_user = await get_user(db=db, user_id=user_id)
    # Aquí se podría añadir lógica para no permitir eliminar al último superusuario, por ejemplo.
    deleted_user = await crud_user.remove(db=db, id=db_user.id)
    if not deleted_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return deleted_user
