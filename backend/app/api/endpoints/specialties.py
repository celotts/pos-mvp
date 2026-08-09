import uuid

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from core import crud_specialty
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User as UserModel
from schemas.specialty import Specialty, SpecialtyCreate, SpecialtyUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# Define dependencias a nivel de módulo para evitar advertencias de linter (Ruff B008)
db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
current_admin_user_dependency = Depends(get_current_admin_user)


@router.post(
    "/", response_model=ApiResponse[Specialty], status_code=status.HTTP_201_CREATED
)
async def create_specialty(
    *,
    specialty_in: SpecialtyCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> ApiResponse[Specialty]:
    """
    Crea una nueva especialidad médica.
    """
    specialty = await crud_specialty.create_specialty(
        db=db, specialty_in=specialty_in, user_id=current_user.id
    )
    return create_api_response(
        data=specialty,
        status_code=status.HTTP_201_CREATED,
        message="Especialidad creada con éxito.",
    )


@router.get("/", response_model=ApiResponse[list[Specialty]])
async def read_specialties(
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
    skip: int = 0,
    limit: int = 100,
) -> ApiResponse[list[Specialty]]:
    """
    Obtiene una lista de especialidades.
    """
    specialties = await crud_specialty.get_specialties(db, skip=skip, limit=limit)
    return create_api_response(data=specialties)


@router.get("/{specialty_id}", response_model=ApiResponse[Specialty])
async def read_specialty(
    *,
    specialty_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> ApiResponse[Specialty]:
    """
    Obtiene una especialidad por su ID.
    """
    specialty = await crud_specialty.get_specialty(db, specialty_id=specialty_id)
    if not specialty:
        raise HTTPException(status_code=404, detail="Especialidad no encontrada.")
    return create_api_response(data=specialty)


@router.put("/{specialty_id}", response_model=ApiResponse[Specialty])
async def update_specialty(
    *,
    specialty_id: uuid.UUID,
    specialty_in: SpecialtyUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> ApiResponse[Specialty]:
    """
    Actualiza una especialidad.
    """
    db_specialty = await crud_specialty.get_specialty(db, specialty_id=specialty_id)
    if not db_specialty:
        raise HTTPException(status_code=404, detail="Especialidad no encontrada.")
    specialty = await crud_specialty.update_specialty(
        db=db,
        db_specialty=db_specialty,
        specialty_in=specialty_in,
        user_id=current_user.id,
    )
    return create_api_response(
        data=specialty, message="Especialidad actualizada con éxito."
    )


@router.delete("/{specialty_id}", response_model=ApiResponse[Specialty])
async def delete_specialty(
    *,
    specialty_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> ApiResponse[Specialty]:
    """
    Elimina una especialidad.
    """
    specialty = await crud_specialty.remove_specialty(db, specialty_id=specialty_id)
    if not specialty:
        raise HTTPException(status_code=404, detail="Especialidad no encontrada.")
    return create_api_response(
        data=specialty, message="Especialidad eliminada con éxito."
    )
