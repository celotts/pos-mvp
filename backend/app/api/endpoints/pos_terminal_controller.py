import uuid
from typing import Any

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, status
from models.user import User as UserModel
from schemas.pos_terminal import (
    PosTerminal,
    PosTerminalCreate,
    PosTerminalUpdate,
)
from service import pos_terminal_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["POS"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
current_admin_user_dependency = Depends(get_current_admin_user)


@router.post(
    "/",
    response_model=ApiResponse[PosTerminal],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new POS Terminal",
)
async def create_pos_terminal(
    *,
    terminal_in: PosTerminalCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Creates a new point of sale (POS) terminal."""
    terminal = await pos_terminal_service.create_pos_terminal(
        db=db, terminal_in=terminal_in, current_user=current_user
    )
    return create_api_response(
        data=terminal,
        status_code=status.HTTP_201_CREATED,
        message="Terminal created successfully.",
    )


@router.get(
    "/",
    response_model=ApiResponse[list[PosTerminal]],
    summary="Get a list of Terminals",
)
async def read_pos_terminals(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Gets a paginated list of POS terminals."""
    terminals = await pos_terminal_service.get_pos_terminals(db, skip=skip, limit=limit)
    return create_api_response(data=terminals)


@router.get(
    "/{terminal_id}",
    response_model=ApiResponse[PosTerminal],
    summary="Get a Terminal by ID",
)
async def read_pos_terminal(
    *,
    terminal_id: uuid.UUID,
    db: AsyncSession = db_dependency,
) -> Any:
    """Gets a specific terminal by its ID."""
    terminal = await pos_terminal_service.get_pos_terminal(db, terminal_id=terminal_id)
    return create_api_response(data=terminal)


@router.put(
    "/{terminal_id}",
    response_model=ApiResponse[PosTerminal],
    summary="Update a Terminal",
)
async def update_pos_terminal(
    *,
    terminal_id: uuid.UUID,
    terminal_in: PosTerminalUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Updates a terminal by its ID."""
    updated_terminal = await pos_terminal_service.update_pos_terminal(
        db=db,
        terminal_id=terminal_id,
        terminal_in=terminal_in,
        current_user=current_user,
    )
    return create_api_response(
        data=updated_terminal, message="Terminal updated successfully."
    )


@router.delete(
    "/{terminal_id}",
    response_model=ApiResponse[PosTerminal],
    summary="Delete a Terminal",
)
async def delete_pos_terminal(
    *,
    terminal_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Deletes a terminal by its ID."""
    deleted_terminal = await pos_terminal_service.remove_pos_terminal(
        db, terminal_id=terminal_id
    )
    return create_api_response(
        data=deleted_terminal, message="Terminal deleted successfully."
    )
