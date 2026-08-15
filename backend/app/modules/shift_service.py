import uuid
from datetime import datetime, timezone

from core import crud_pos_terminal, crud_shift
from fastapi import HTTPException, status
from models import Shift
from models import User as UserModel
from models.shift import ShiftStatus
from schemas.shift import ShiftClose, ShiftOpen
from sqlalchemy.ext.asyncio import AsyncSession


async def open_shift(
    db: AsyncSession, *, shift_in: ShiftOpen, current_user: UserModel
) -> Shift:
    """Abre un nuevo turno para un usuario en una terminal."""
    # 1. Verificar que la terminal existe y está activa
    terminal = await crud_pos_terminal.get(db, id=shift_in.pos_terminal_id)
    if not terminal or not terminal.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The terminal does not exist or is not active.",
        )

    # 2. Verificar que no haya ya un turno abierto en esa terminal
    existing_shift = await crud_shift.get_open_shift_by_terminal(
        db, terminal_id=shift_in.pos_terminal_id
    )
    if existing_shift:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An open shift already exists at terminal '{terminal.name}'.",
        )

    # 3. Crear el nuevo turno
    shift_to_create = Shift(
        user_id=current_user.id,
        pos_terminal_id=shift_in.pos_terminal_id,
        starting_cash=shift_in.starting_cash,
        status=ShiftStatus.OPEN,
        created_by=current_user.id,
    )
    db.add(shift_to_create)
    await db.commit()
    await db.refresh(shift_to_create)
    return shift_to_create


async def close_shift(
    db: AsyncSession,
    *,
    shift_id: uuid.UUID,
    shift_in: ShiftClose,
    current_user: UserModel,
) -> Shift:
    """Cierra un turno existente."""
    # 1. Obtener el turno
    db_shift = await crud_shift.get(db, id=shift_id)
    if not db_shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Shift does not exist."
        )

    # 2. Validar que el turno esté abierto y que el usuario sea el correcto (o un admin)
    if db_shift.status != ShiftStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The shift is already closed.",
        )

    # (Opcional) Añadir lógica para permitir que solo el propio usuario o un admin cierre el turno

    # 3. Actualizar el turno para cerrarlo
    db_shift.ending_cash = shift_in.ending_cash
    db_shift.end_time = datetime.now(timezone.utc)
    db_shift.status = ShiftStatus.CLOSED
    db_shift.updated_by = current_user.id
    await db.commit()
    await db.refresh(db_shift)
    return db_shift
