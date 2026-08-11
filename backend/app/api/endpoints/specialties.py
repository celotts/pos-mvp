import uuid
from typing import Any

from api.deps import get_db
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_admin_user, get_current_user
from fastapi import APIRouter, Depends, status
from models.user import User as UserModel
from modules import specialty_service
from schemas.specialty import Specialty, SpecialtyCreate, SpecialtyUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# Define dependencias a nivel de módulo para evitar advertencias de linter (Ruff B008)
db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
current_admin_user_dependency = Depends(get_current_admin_user)


@router.post(
    "/",
    response_model=ApiResponse[Specialty],
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva especialidad",
)
async def create_specialty(
    *,
    specialty_in: SpecialtyCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """
    Crea una nueva especialidad médica.
    """
    specialty = await specialty_service.create_specialty(
        db=db, specialty_in=specialty_in, user_id=current_user.id
    )
    return create_api_response(
        data=specialty,
        status_code=status.HTTP_201_CREATED,
        message="Especialidad creada con éxito.",
    )


@router.get(
    "/",
    response_model=ApiResponse[list[Specialty]],
    summary="Obtener una lista de especialidades",
)
async def read_specialties(
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Obtiene una lista de especialidades.
    """
    specialties = await specialty_service.get_specialties(db, skip=skip, limit=limit)
    return create_api_response(data=specialties)


@router.get(
    "/{specialty_id}",
    response_model=ApiResponse[Specialty],
    summary="Obtener una especialidad por su ID",
)
async def read_specialty(
    *,
    specialty_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Obtiene una especialidad por su ID.
    """
    specialty = await specialty_service.get_specialty(db, specialty_id=specialty_id)
    return create_api_response(data=specialty)


@router.put(
    "/{specialty_id}",
    response_model=ApiResponse[Specialty],
    summary="Actualizar una especialidad",
)
async def update_specialty(
    *,
    specialty_id: uuid.UUID,
    specialty_in: SpecialtyUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """
    Actualiza una especialidad.
    """
    specialty = await specialty_service.update_specialty(
        db=db,
        specialty_id=specialty_id,
        specialty_in=specialty_in,
        user_id=current_user.id,
    )
    return create_api_response(
        data=specialty, message="Especialidad actualizada con éxito."
    )


@router.delete(
    "/{specialty_id}",
    response_model=ApiResponse[Specialty],
    summary="Eliminar una especialidad",
)
async def delete_specialty(
    *,
    specialty_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """
    Elimina una especialidad.
    """
    specialty = await specialty_service.remove_specialty(db, specialty_id=specialty_id)
    return create_api_response(
        data=specialty, message="Especialidad eliminada con éxito."
    )
