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
