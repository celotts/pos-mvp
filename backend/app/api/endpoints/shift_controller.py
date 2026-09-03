import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps_auth import require_permission
from api.response_factory import ApiResponse, create_api_response
from core.tenancy import get_current_tenant
from dependencies import get_db
from models.shift import Shift as ShiftModel
from models.user import User as UserModel
from schemas.shift import Shift, ShiftClose, ShiftOpen
from service import shift_service

router = APIRouter(tags=["POS"])

db_dependency = Depends(get_db)
require_shift_open = Depends(require_permission("shift:open"))
require_shift_close = Depends(require_permission("shift:close"))


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
    current_user: UserModel = require_shift_open,
) -> Any:
    """Starts a new shift for the current user at a specific terminal,
    registering the initial cash."""
    new_shift = await shift_service.open_shift(
        db=db, shift_in=shift_in, current_user=current_user
    )
    return create_api_response(data=new_shift, message="Shift opened successfully.")


@router.get(
    "/",
    response_model=ApiResponse[list[Shift]],
    summary="List shifts (paginated)",
)
async def list_shifts(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = require_shift_open,
) -> Any:
    """Lista de turnos con paginación. Devuelve data + total."""
    stmt = select(ShiftModel)
    tenant_id = get_current_tenant()
    if tenant_id and hasattr(ShiftModel, "tenant_id"):
        stmt = stmt.where(ShiftModel.tenant_id == tenant_id)

    total_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(total_stmt)
    total = int(count_result.scalar() or 0)

    stmt = stmt.order_by(ShiftModel.start_time.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    shifts = result.scalars().all()

    return create_api_response(data=shifts, total=total)


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
    current_user: UserModel = require_shift_close,
) -> Any:
    """Closes an open shift, registering the final cash."""
    closed_shift = await shift_service.close_shift(
        db=db, shift_id=shift_id, shift_in=shift_in, current_user=current_user
    )
    return create_api_response(data=closed_shift, message="Shift closed successfully.")
