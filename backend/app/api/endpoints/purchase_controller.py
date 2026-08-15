import uuid
from typing import Any

from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, status
from models.user import User as UserModel
from modules.purchase_service import purchase_service
from schemas.purchase import Purchase, PurchaseCreate, PurchaseUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Purchases"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)


@router.post(
    "/",
    response_model=ApiResponse[Purchase],
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva Compra",
)
async def create_purchase(
    *,
    purchase_in: PurchaseCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Crea un nuevo registro de compra a un proveedor."""
    new_purchase = await purchase_service.create(db=db, obj_in=purchase_in)
    return create_api_response(
        data=new_purchase,
        status_code=status.HTTP_201_CREATED,
        message="Compra creada con éxito.",
    )


@router.get(
    "/", response_model=ApiResponse[list[Purchase]], summary="Obtener lista de Compras"
)
async def read_purchases(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Obtiene una lista de todas las compras."""
    purchases = await purchase_service.get_all(db, skip=skip, limit=limit)
    return create_api_response(data=purchases)


@router.get(
    "/{purchase_id}",
    response_model=ApiResponse[Purchase],
    summary="Obtener una Compra por ID",
)
async def read_purchase_by_id(
    *,
    purchase_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Obtiene los detalles de una compra específica."""
    purchase = await purchase_service.get(db, id=purchase_id)
    return create_api_response(data=purchase)


@router.put(
    "/{purchase_id}",
    response_model=ApiResponse[Purchase],
    summary="Actualizar una Compra",
)
async def update_purchase(
    *,
    purchase_id: uuid.UUID,
    purchase_in: PurchaseUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Actualiza los datos de una compra existente."""
    updated_purchase = await purchase_service.update(
        db=db, id=purchase_id, obj_in=purchase_in
    )
    return create_api_response(
        data=updated_purchase, message="Compra actualizada con éxito."
    )


@router.delete(
    "/{purchase_id}",
    response_model=ApiResponse[Purchase],
    summary="Eliminar una Compra",
)
async def delete_purchase(
    *,
    purchase_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Elimina un registro de compra."""
    deleted_purchase = await purchase_service.remove(db, id=purchase_id)
    return create_api_response(
        data=deleted_purchase, message="Compra eliminada con éxito."
    )
