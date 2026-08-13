import uuid
from typing import Any

from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, status
from models.user import User as UserModel
from modules import shift_service
from schemas.shift import Shift, ShiftClose, ShiftOpen
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)


@router.post(
    "/open",
    response_model=ApiResponse[Shift],
    status_code=status.HTTP_201_CREATED,
    summary="Abrir un nuevo Turno",
)
async def open_new_shift(
    *,
    shift_in: ShiftOpen,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Inicia un nuevo turno para el usuario actual en una terminal específica,
    registrando el efectivo inicial.
    """
    new_shift = await shift_service.open_shift(
        db=db, shift_in=shift_in, current_user=current_user
    )
    return create_api_response(data=new_shift, message="Turno abierto con éxito.")


@router.put(
    "/{shift_id}/close",
    response_model=ApiResponse[Shift],
    summary="Cerrar un Turno existente",
)
async def close_existing_shift(
    *,
    shift_id: uuid.UUID,
    shift_in: ShiftClose,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Cierra un turno abierto, registrando el efectivo final.
    """
    closed_shift = await shift_service.close_shift(
        db=db, shift_id=shift_id, shift_in=shift_in, current_user=current_user
    )
    return create_api_response(data=closed_shift, message="Turno cerrado con éxito.")
