import uuid
from typing import Any

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, status
from models.user import User as UserModel
from schemas.municipality import (
    Municipality,
    MunicipalityCreate,
    MunicipalityUpdate,
)
from service import municipality_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Municipalities"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
current_admin_user_dependency = Depends(get_current_admin_user)


@router.post(
    "/",
    response_model=ApiResponse[Municipality],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Municipality",
)
async def create_municipality(
    *,
    municipality_in: MunicipalityCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Creates a new municipality, associated with a state/province."""
    municipality = await municipality_service.create_municipality(
        db=db, municipality_in=municipality_in, current_user=current_user
    )
    return create_api_response(
        data=municipality,
        status_code=status.HTTP_201_CREATED,
        message="Municipality created successfully.",
    )


@router.get(
    "/",
    response_model=ApiResponse[list[Municipality]],
    summary="Get a list of Municipalities",
)
async def read_municipalities(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Gets a paginated list of municipalities."""
    municipalities = await municipality_service.get_municipalities(
        db, skip=skip, limit=limit
    )
    return create_api_response(data=municipalities)


@router.get(
    "/{municipality_id}",
    response_model=ApiResponse[Municipality],
    summary="Get a Municipality by ID",
)
async def read_municipality(
    *,
    municipality_id: uuid.UUID,
    db: AsyncSession = db_dependency,
) -> Any:
    """Gets a specific municipality by its ID."""
    municipality = await municipality_service.get_municipality(
        db, municipality_id=municipality_id
    )
    return create_api_response(data=municipality)


@router.put(
    "/{municipality_id}",
    response_model=ApiResponse[Municipality],
    summary="Update a Municipality",
)
async def update_municipality(
    *,
    municipality_id: uuid.UUID,
    municipality_in: MunicipalityUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Updates a municipality by its ID."""
    updated_municipality = await municipality_service.update_municipality(
        db=db,
        municipality_id=municipality_id,
        municipality_in=municipality_in,
        current_user=current_user,
    )
    return create_api_response(
        data=updated_municipality, message="Municipality updated successfully."
    )


@router.delete(
    "/{municipality_id}",
    response_model=ApiResponse[Municipality],
    summary="Delete a Municipality",
)
async def delete_municipality(
    *,
    municipality_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Deletes a municipality by its ID."""
    deleted_municipality = await municipality_service.remove_municipality(
        db, municipality_id=municipality_id
    )
    return create_api_response(
        data=deleted_municipality, message="Municipality deleted successfully."
    )
