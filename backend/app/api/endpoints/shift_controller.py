import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from models.user import User as UserModel
from schemas.shift import Shift, ShiftClose, ShiftOpen
from service import shift_service

router = APIRouter(tags=["POS"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)


@router.post(
    "/open",
    response_model=ApiResponse[Shift],
    status_code=status.HTTP_201_CREATED,
    summary="Open a new Shift",
)
async def open_new_shift(
    *,
    shift_in: ShiftOpen,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Starts a new shift for the current user at a specific terminal,
    registering the initial cash."""
    new_shift = await shift_service.open_shift(
        db=db, shift_in=shift_in, current_user=current_user
    )
    return create_api_response(data=new_shift, message="Shift opened successfully.")


@router.put(
    "/{shift_id}/close",
    response_model=ApiResponse[Shift],
    summary="Close an existing Shift",
)
async def close_existing_shift(
    *,
    shift_id: uuid.UUID,
    shift_in: ShiftClose,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Closes an open shift, registering the final cash."""
    closed_shift = await shift_service.close_shift(
        db=db, shift_id=shift_id, shift_in=shift_in, current_user=current_user
    )
    return create_api_response(data=closed_shift, message="Shift closed successfully.")
