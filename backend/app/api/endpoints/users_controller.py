import uuid

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, status
from models.user import User as UserModel
from modules import user_service
from schemas.user import User, UserCreate, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Users"])

get_db_dependency = Depends(get_db)
get_current_user_dependency = Depends(get_current_user)
get_current_admin_user_dependency = Depends(get_current_admin_user)


@router.get(
    "/",
    response_model=ApiResponse[list[User]],
    summary="Obtener una lista de usuarios",
)
async def read_users(
    db: AsyncSession = get_db_dependency,
    current_user: UserModel = get_current_user_dependency,
    skip: int = 0,
    limit: int = 100,
) -> ApiResponse[list[User]]:
    """Obtiene una lista de usuarios."""
    users = await user_service.get_users(db, skip=skip, limit=limit)
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
    current_user: UserModel = get_current_admin_user_dependency,
    db: AsyncSession = get_db_dependency,
) -> ApiResponse[User]:
    user = await user_service.create_user_with_logic(db=db, user_in=user_in)
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
    db: AsyncSession = get_db_dependency,
    current_user: UserModel = get_current_user_dependency,
) -> ApiResponse[User]:
    """Obtiene un usuario por su ID."""
    user = await user_service.get_user(db=db, user_id=user_id)
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
    current_user: UserModel = get_current_user_dependency,
    db: AsyncSession = get_db_dependency,
) -> ApiResponse[User]:
    """Actualiza un usuario."""
    user = await user_service.update_user(
        db=db, user_id=user_id, user_in=user_in, current_user=current_user
    )
    return create_api_response(data=user, message="Usuario actualizado con éxito.")


@router.delete(
    "/{user_id}",
    response_model=ApiResponse[User],
    summary="Eliminar un usuario",
)
async def delete_user(
    *,
    user_id: uuid.UUID,
    current_user: UserModel = get_current_admin_user_dependency,
    db: AsyncSession = get_db_dependency,
) -> ApiResponse[User]:
    """Elimina un usuario."""
    user = await user_service.remove_user(db=db, user_id=user_id)
    return create_api_response(data=user, message="Usuario eliminado con éxito.")
