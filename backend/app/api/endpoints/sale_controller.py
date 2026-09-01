import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps_auth import require_permission
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from models.user import User as UserModel
from schemas.sale import Sale, SaleCreate
from service.sale_service import sale_service

router = APIRouter(tags=["POS"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
require_sale_create = Depends(require_permission("sale:create"))
require_sale_read = Depends(require_permission("sale:read"))
require_sale_cancel = Depends(require_permission("sale:cancel"))


@router.get(
    "/", response_model=ApiResponse[list[Sale]], summary="Get list of Sales"
)
async def read_sales(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = require_sale_read,
) -> Any:
    """Gets a list of sales with their items."""
    sales = await sale_service.get_all(db, skip=skip, limit=limit)
    return create_api_response(data=sales)


@router.get(
    "/{sale_id}", response_model=ApiResponse[Sale], summary="Get a Sale by ID"
)
async def read_sale_by_id(
    *,
    sale_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = require_sale_read,
) -> Any:
    """Gets the details of a specific sale."""
    sale = await sale_service.get(db, id=sale_id)
    return create_api_response(data=sale)


@router.post(
    "/{sale_id}/return",
    response_model=ApiResponse[Sale],
    summary="Return (cancel) a Sale",
)
async def return_sale(
    *,
    sale_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = require_sale_cancel,
) -> Any:
    """Cancels (returns) a full sale, voiding its stock outflow."""
    sale = await sale_service.return_sale(
        db, sale_id=sale_id, current_user=current_user
    )
    return create_api_response(data=sale, message="Sale returned successfully.")


@router.post(
    "/",
    response_model=ApiResponse[Sale],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new Sale",
)
async def create_new_sale(
    *,
    sale_in: SaleCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = db_dependency,
    current_user: UserModel = require_sale_create,
) -> Any:
    """Creates a new sale record.
    - The sale is automatically associated with the open shift on the specified terminal.
    - Dispatches background embedding generation for vector search (RAG)."""
    new_sale = await sale_service.create_sale(
        db=db,
        sale_in=sale_in,
        current_user=current_user,
        background_tasks=background_tasks,
    )

    return create_api_response(data=new_sale, message="Sale registered successfully.")
