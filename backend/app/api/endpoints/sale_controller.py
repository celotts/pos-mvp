from typing import Any

from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, status
from models.user import User as UserModel
from modules import sale_service
from schemas.sale import Sale, SaleCreate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["POS"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)


@router.post(
    "/",
    response_model=ApiResponse[Sale],
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una nueva Venta",
)
async def create_new_sale(
    *,
    sale_in: SaleCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Crea un nuevo registro de venta.
    - La venta se asocia automáticamente al turno abierto en la terminal especificada.
    """
    new_sale = await sale_service.create_sale(
        db=db, sale_in=sale_in, current_user=current_user
    )
    return create_api_response(data=new_sale, message="Venta registrada con éxito.")
