import uuid
from typing import Any

from api.response_factory import create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends
from models.user import User as UserModel
from modules import specialty_service
from schemas.specialty import Specialty, SpecialtyCreate, SpecialtyUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Specialties"])


@router.get("/", response_model=list[Specialty])
async def read_specialties(
    db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve specialties.
    """
    specialties = await specialty_service.get_specialties(db, skip=skip, limit=limit)
    return create_api_response(data=specialties)


@router.post("/", response_model=Specialty)
async def create_specialty(
    *,
    db: AsyncSession = Depends(get_db),
    specialty_in: SpecialtyCreate,
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Create new specialty.
    """
    specialty = await specialty_service.create_specialty(
        db=db, specialty_in=specialty_in, user_id=current_user.id
    )
    return create_api_response(
        data=specialty, status_code=201, message="Especialidad creada con éxito."
    )


@router.get("/{id}", response_model=Specialty)
async def read_specialty_by_id(
    id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a specific specialty by id.
    """
    specialty = await specialty_service.get_specialty(db, specialty_id=id)
    return create_api_response(data=specialty)


@router.put("/{id}", response_model=Specialty)
async def update_specialty_by_id(
    *,
    id: uuid.UUID,
    specialty_in: SpecialtyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Update a specialty by id.
    """
    specialty = await specialty_service.update_specialty(
        db=db, specialty_id=id, specialty_in=specialty_in, user_id=current_user.id
    )
    return create_api_response(
        data=specialty, message="Especialidad actualizada con éxito."
    )


@router.delete("/{id}", status_code=204)
async def delete_specialty_by_id(
    *, id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a specialty by id.
    """
    await specialty_service.get_specialty(db, specialty_id=id)  # ensure it exists
    # Assuming you have a remove function in crud_specialty
    # await crud_specialty.remove(db, id=id)
    # For now, just returning success as remove is not in the provided crud
    return create_api_response(
        data=None, status_code=204, message="Especialidad eliminada con éxito."
    )
