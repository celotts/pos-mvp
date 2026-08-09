import uuid

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from core import crud_user
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User as UserModel
from modules import user_service
from schemas.user import User, UserCreate, UserUpdate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# Module-level dependency markers to avoid calling Depends() in arg defaults
current_user_dep = Depends(get_current_user)
current_admin_user_dep = Depends(get_current_admin_user)
db_dep = Depends(get_db)


@router.get(
    "/",
    response_model=ApiResponse[list[User]],
    summary="Obtener una lista de usuarios",
)
async def read_users(
    db: AsyncSession = db_dep,
    current_user: UserModel = current_user_dep,
    skip: int = 0,
    limit: int = 100,
) -> ApiResponse[list[User]]:
    """Obtiene una lista de usuarios."""
    users = await crud_user.get_users(db, skip=skip, limit=limit)
    return create_api_response(data=users)


@router.post(
    "/",
    response_model=ApiResponse[User],
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo usuario",
)
async def create_user(
    *,
    user_in: UserCreate,
    current_user: UserModel = current_admin_user_dep,
    db: AsyncSession = db_dep,
) -> ApiResponse[User]:
    try:
        user = await user_service.create_user_with_logic(db=db, user_in=user_in)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="El email ya está registrado.")
    return create_api_response(
        data=user,
        status_code=status.HTTP_201_CREATED,
        message="Usuario creado con éxito.",
    )


@router.get(
    "/{user_id}",
    response_model=ApiResponse[User],
    summary="Obtener un usuario por su ID",
)
async def read_user_by_id(
    user_id: uuid.UUID,
    current_user: UserModel = current_user_dep,
    db: AsyncSession = db_dep,
) -> ApiResponse[User]:
    """Obtiene un usuario por su ID."""
    user = await user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return create_api_response(data=user)


@router.put(
    "/{user_id}",
    response_model=ApiResponse[User],
    summary="Actualizar un usuario existente",
)
async def update_user(
    *,
    user_id: uuid.UUID,
    user_in: UserUpdate,
    current_user: UserModel = current_user_dep,
    db: AsyncSession = db_dep,
) -> ApiResponse[User]:
    """Actualiza un usuario."""
    # Regla de negocio: Un usuario solo puede modificarse a sí mismo,
    # a menos que sea un administrador.
    if current_user.id != user_id and (
        not current_user.role or current_user.role.name != "ADMIN"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este usuario.",
        )
    db_user = await user_service.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    user = await user_service.update_user(db=db, db_user=db_user, user_in=user_in)
    return create_api_response(data=user, message="Usuario actualizado con éxito.")


@router.delete(
    "/{user_id}",
    response_model=ApiResponse[User],
    summary="Eliminar un usuario",
)
async def delete_user(
    *,
    user_id: uuid.UUID,
    current_user: UserModel = current_admin_user_dep,
    db: AsyncSession = db_dep,
) -> ApiResponse[User]:
    """Elimina un usuario."""
    user = await user_service.delete_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return create_api_response(data=user, message="Usuario eliminado con éxito.")
