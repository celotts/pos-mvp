import uuid

from core import crud_user
from models.user import User as UserModel
from schemas.user import UserCreate, UserUpdate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def create_user_with_logic(db: AsyncSession, *, user_in: UserCreate) -> UserModel:
    """
    Crea un usuario y aplica la lógica de negocio adicional.
    Este es el lugar para orquestar múltiples acciones.
    """
    # 1. La lógica de negocio podría empezar aquí.
    # Por ejemplo, verificar si el dominio del email es válido.
    if user_in.email.endswith("@example.com"):
        raise IntegrityError(
            None, None, "Los emails de example.com no están permitidos."
        )

    # 2. Llama a la capa CRUD para persistir en la base de datos.
    user = await crud_user.create_user(db=db, user_in=user_in)

    # 3. Lógica de negocio después de la creación.
    print(f"Enviando email de bienvenida a {user.email}...")  # Simulación

    return user


async def get_user_by_id(db: AsyncSession, *, user_id: uuid.UUID) -> UserModel | None:
    """Obtiene un usuario por su ID, pasando por la capa de servicio."""
    return await crud_user.get_user(db=db, user_id=user_id)


async def update_user(
    db: AsyncSession, *, db_user: UserModel, user_in: UserUpdate
) -> UserModel:
    """Actualiza un usuario, pasando por la capa de servicio."""
    # Aquí podrías añadir lógica, como registrar la actualización en un log de auditoría.
    updated_user = await crud_user.update_user(db=db, db_user=db_user, user_in=user_in)
    print(f"El usuario {updated_user.email} ha sido actualizado.")  # Simulación
    return updated_user


async def delete_user(db: AsyncSession, *, user_id: uuid.UUID) -> UserModel | None:
    """Elimina un usuario, pasando por la capa de servicio."""
    return await crud_user.remove_user(db=db, user_id=user_id)
