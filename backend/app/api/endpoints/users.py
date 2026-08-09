import uuid

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from core import crud_user
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User as UserModel
from schemas.user import User, UserCreate, UserUpdate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get(
    "/",
    response_model=ApiResponse[list[User]],
    summary="Obtener una lista de usuarios",
)
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
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
    current_user: UserModel = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[User]:
    try:
        user = await crud_user.create_user(db=db, user_in=user_in)
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
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[User]:
    """Obtiene un usuario por su ID."""
    user = await crud_user.get_user(db, user_id=user_id)
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
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[User]:
    """Actualiza un usuario."""
    db_user = await crud_user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    user = await crud_user.update_user(db=db, db_user=db_user, user_in=user_in)
    return create_api_response(data=user, message="Usuario actualizado con éxito.")


@router.delete(
    "/{user_id}",
    response_model=ApiResponse[User],
    summary="Eliminar un usuario",
)
async def delete_user(
    *,
    user_id: uuid.UUID,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[User]:
    """Elimina un usuario."""
    user = await crud_user.remove_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return create_api_response(data=user, message="Usuario eliminado con éxito.")
