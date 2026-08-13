import uuid
from typing import Any

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, status
from models.user import User as UserModel
from modules import state_province_service
from schemas.state_province import (
    StateProvince,
    StateProvinceCreate,
    StateProvinceUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
current_admin_user_dependency = Depends(get_current_admin_user)


@router.post(
    "/",
    response_model=ApiResponse[StateProvince],
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo Estado/Provincia",
)
async def create_state_province(
    *,
    state_in: StateProvinceCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Crea un nuevo estado o provincia, asociado a un país."""
    state = await state_province_service.create_state_province(
        db=db, state_in=state_in, current_user=current_user
    )
    return create_api_response(
        data=state,
        status_code=status.HTTP_201_CREATED,
        message="Estado/Provincia creado con éxito.",
    )


@router.get(
    "/",
    response_model=ApiResponse[list[StateProvince]],
    summary="Obtener una lista de Estados/Provincias",
)
async def read_states_provinces(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Obtiene una lista paginada de estados y provincias."""
    states = await state_province_service.get_states_provinces(
        db, skip=skip, limit=limit
    )
    return create_api_response(data=states)


@router.get(
    "/{state_id}",
    response_model=ApiResponse[StateProvince],
    summary="Obtener un Estado/Provincia por ID",
)
async def read_state_province(
    *,
    state_id: uuid.UUID,
    db: AsyncSession = db_dependency,
) -> Any:
    """Obtiene un estado o provincia específico por su ID."""
    state = await state_province_service.get_state_province(db, state_id=state_id)
    return create_api_response(data=state)


@router.put(
    "/{state_id}",
    response_model=ApiResponse[StateProvince],
    summary="Actualizar un Estado/Provincia",
)
async def update_state_province(
    *,
    state_id: uuid.UUID,
    state_in: StateProvinceUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Actualiza un estado o provincia por su ID."""
    updated_state = await state_province_service.update_state_province(
        db=db,
        state_id=state_id,
        state_in=state_in,
        current_user=current_user,
    )
    return create_api_response(
        data=updated_state, message="Estado/Provincia actualizado con éxito."
    )


@router.delete(
    "/{state_id}",
    response_model=ApiResponse[StateProvince],
    summary="Eliminar un Estado/Provincia",
)
async def delete_state_province(
    *,
    state_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Elimina un estado o provincia por su ID."""
    deleted_state = await state_province_service.remove_state_province(
        db, state_id=state_id
    )
    return create_api_response(
        data=deleted_state, message="Estado/Provincia eliminado con éxito."
    )
