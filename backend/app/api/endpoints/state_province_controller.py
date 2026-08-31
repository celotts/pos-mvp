import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from models.user import User as UserModel
from schemas.state_province import (
    StateProvince,
    StateProvinceCreate,
    StateProvinceUpdate,
)
from service.state_province_service import state_province_service

router = APIRouter(tags=["States & Provinces"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
current_admin_user_dependency = Depends(get_current_admin_user)


@router.post(
    "/",
    response_model=ApiResponse[StateProvince],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new State/Province",
)
async def create_state_province(
    *,
    state_in: StateProvinceCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Creates a new state or province, associated with a country."""
    state = await state_province_service.create(db=db, obj_in=state_in)
    return create_api_response(
        data=state,
        status_code=status.HTTP_201_CREATED,
        message="State/Province created successfully.",
    )


@router.get(
    "/",
    response_model=ApiResponse[list[StateProvince]],
    summary="Get a list of States/Provinces",
)
async def read_states_provinces(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Gets a paginated list of states and provinces."""
    states = await state_province_service.get_all(db, skip=skip, limit=limit)
    return create_api_response(data=states)


@router.get(
    "/{state_id}",
    response_model=ApiResponse[StateProvince],
    summary="Get a State/Province by ID",
)
async def read_state_province(
    *,
    state_id: uuid.UUID,
    db: AsyncSession = db_dependency,
) -> Any:
    """Gets a specific state or province by its ID."""
    state = await state_province_service.get_by_id(db, id=state_id)
    return create_api_response(data=state)


@router.put(
    "/{state_id}",
    response_model=ApiResponse[StateProvince],
    summary="Update a State/Province",
)
async def update_state_province(
    *,
    state_id: uuid.UUID,
    state_in: StateProvinceUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Updates a state or province by its ID."""
    updated_state = await state_province_service.update(
        db=db, id=state_id, obj_in=state_in
    )
    return create_api_response(
        data=updated_state, message="State/Province updated successfully."
    )


@router.delete(
    "/{state_id}",
    response_model=ApiResponse[StateProvince],
    summary="Delete a State/Province",
)
async def delete_state_province(
    *,
    state_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Deletes a state or province by its ID."""
    deleted_state = await state_province_service.delete(db, id=state_id)
    return create_api_response(
        data=deleted_state, message="State/Province deleted successfully."
    )
