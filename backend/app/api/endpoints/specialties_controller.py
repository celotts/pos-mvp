import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from models.user import User as UserModel
from schemas.specialty import Specialty, SpecialtyCreate, SpecialtyUpdate
from service import specialty_service

router = APIRouter(tags=["Specialties"])

db_dependency = Depends(get_db)
admin_user_dependency = Depends(get_current_admin_user)
current_user_dependency = Depends(get_current_user)


@router.get("/", response_model=ApiResponse[list[Specialty]])
async def read_specialties(
    db: AsyncSession = db_dependency,
    _current_user: UserModel = current_user_dependency,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve specialties. Requires authentication.
    """
    specialties = await specialty_service.get_specialties(db, skip=skip, limit=limit)
    return create_api_response(
        data=specialties, message="Specialties retrieved successfully."
    )


@router.post(
    "/", response_model=ApiResponse[Specialty], status_code=status.HTTP_201_CREATED
)
async def create_specialty(
    *,
    db: AsyncSession = db_dependency,
    specialty_in: SpecialtyCreate,
    current_user: UserModel = admin_user_dependency,
) -> Any:
    """
    Create new specialty.
    """
    specialty = await specialty_service.create_specialty(
        db=db, specialty_in=specialty_in, user_id=current_user.id
    )
    return create_api_response(
        data=specialty, status_code=201, message="Specialty created successfully."
    )


@router.get("/{id}", response_model=ApiResponse[Specialty])
async def read_specialty_by_id(
    id: uuid.UUID,
    db: AsyncSession = db_dependency,
    _current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Get a specific specialty by id. Requires authentication.
    """
    specialty = await specialty_service.get_specialty(db, specialty_id=id)
    return create_api_response(data=specialty)


@router.put("/{id}", response_model=ApiResponse[Specialty])
async def update_specialty_by_id(
    *,
    id: uuid.UUID,
    specialty_in: SpecialtyUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = admin_user_dependency,
) -> Any:
    """
    Update a specialty by id.
    """
    specialty = await specialty_service.update_specialty(
        db=db, specialty_id=id, specialty_in=specialty_in, user_id=current_user.id
    )
    return create_api_response(
        data=specialty, message="Specialty updated successfully."
    )


@router.delete("/{id}", response_model=ApiResponse[Specialty])
async def delete_specialty_by_id(
    *,
    id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = admin_user_dependency,
) -> Any:
    """
    Delete a specialty by id.
    """
    deleted_specialty = await specialty_service.remove_specialty(db=db, specialty_id=id)
    return create_api_response(
        data=deleted_specialty, message="Specialty deleted successfully."
    )
