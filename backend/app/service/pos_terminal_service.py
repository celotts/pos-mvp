import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.crud_pos_terminal import crud_pos_terminal
from models import PosTerminal
from models import User as UserModel
from schemas.pos_terminal import PosTerminalCreate, PosTerminalUpdate


async def get_pos_terminals(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[PosTerminal]:
    """Obtiene una lista de terminales de venta."""
    return await crud_pos_terminal.get_multi(db, skip=skip, limit=limit)


async def create_pos_terminal(
    db: AsyncSession, *, terminal_in: PosTerminalCreate, current_user: UserModel
) -> PosTerminal:
    """Crea una nueva terminal de venta."""
    try:
        return await crud_pos_terminal.create(
            db=db,
            obj_in=terminal_in,
            created_by=current_user.id,
            created_by_role_id=current_user.role_id,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A terminal with this name already exists.",
        )


async def get_pos_terminal(db: AsyncSession, *, terminal_id: uuid.UUID) -> PosTerminal:
    """Obtiene una terminal por ID."""
    db_terminal = await crud_pos_terminal.get(db=db, id=terminal_id)
    if not db_terminal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Terminal not found."
        )
    return db_terminal


async def update_pos_terminal(
    db: AsyncSession,
    *,
    terminal_id: uuid.UUID,
    terminal_in: PosTerminalUpdate,
    current_user: UserModel,
) -> PosTerminal:
    """Actualiza una terminal."""
    db_terminal = await get_pos_terminal(db=db, terminal_id=terminal_id)
    return await crud_pos_terminal.update(
        db=db,
        db_obj=db_terminal,
        obj_in=terminal_in,
        updated_by=current_user.id,
        updated_by_role_id=current_user.role_id,
    )


async def remove_pos_terminal(
    db: AsyncSession, *, terminal_id: uuid.UUID
) -> PosTerminal:
    """Elimina una terminal."""
    await get_pos_terminal(db=db, terminal_id=terminal_id)
    return await crud_pos_terminal.remove(db=db, id=terminal_id)
