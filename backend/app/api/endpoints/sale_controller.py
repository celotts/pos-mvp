from typing import Any

from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, BackgroundTasks, Depends, status
from models.user import User as UserModel
from schemas.sale import Sale, SaleCreate
from service import sale_service
from service.ai_service import ai_service  # ✅ Import desde modules
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["POS"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)


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
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Creates a new sale record.
    - The sale is automatically associated with the open shift on the specified terminal.
    - Dispatches background embedding generation for vector search (RAG)."""
    new_sale = await sale_service.create_sale(
        db=db, sale_in=sale_in, current_user=current_user
    )

    # ✅ Programar tarea en segundo plano
    background_tasks.add_task(
        ai_service.create_and_store_sale_embedding, sale_id=new_sale.id
    )

    return create_api_response(data=new_sale, message="Sale registered successfully.")
