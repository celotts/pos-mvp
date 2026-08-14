import uuid
from typing import Any

from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, status
from models.user import User as UserModel
from modules.accounts_receivable_service import accounts_receivable_service
from schemas.accounts_receivable import (
    AccountsReceivable,
    AccountsReceivableCreate,
    AccountsReceivableUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)


@router.post(
    "/",
    response_model=ApiResponse[AccountsReceivable],
    status_code=status.HTTP_201_CREATED,
    summary="Crear una Cuenta por Cobrar",
)
async def create_account_receivable(
    *,
    account_in: AccountsReceivableCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Crea un nuevo registro de cuenta por cobrar, generalmente asociado a una venta."""
    new_account = await accounts_receivable_service.create(db=db, obj_in=account_in)
    return create_api_response(
        data=new_account,
        status_code=status.HTTP_201_CREATED,
        message="Cuenta por cobrar creada con éxito.",
    )


@router.get(
    "/",
    response_model=ApiResponse[list[AccountsReceivable]],
    summary="Obtener lista de Cuentas por Cobrar",
)
async def read_accounts_receivable(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Obtiene una lista de todas las cuentas por cobrar."""
    accounts = await accounts_receivable_service.get_all(db, skip=skip, limit=limit)
    return create_api_response(data=accounts)


@router.get(
    "/{account_id}",
    response_model=ApiResponse[AccountsReceivable],
    summary="Obtener una Cuenta por Cobrar por ID",
)
async def read_account_receivable_by_id(
    *,
    account_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Obtiene los detalles de una cuenta por cobrar específica."""
    account = await accounts_receivable_service.get(db, id=account_id)
    return create_api_response(data=account)


@router.put(
    "/{account_id}",
    response_model=ApiResponse[AccountsReceivable],
    summary="Actualizar una Cuenta por Cobrar",
)
async def update_account_receivable(
    *,
    account_id: uuid.UUID,
    account_in: AccountsReceivableUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Actualiza los datos de una cuenta por cobrar (ej. para registrar un pago)."""
    updated_account = await accounts_receivable_service.update(
        db=db, id=account_id, obj_in=account_in
    )
    return create_api_response(
        data=updated_account, message="Cuenta por cobrar actualizada con éxito."
    )


@router.delete(
    "/{account_id}",
    response_model=ApiResponse[AccountsReceivable],
    summary="Eliminar una Cuenta por Cobrar",
)
async def delete_account_receivable(
    *,
    account_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Elimina un registro de cuenta por cobrar."""
    deleted_account = await accounts_receivable_service.remove(db, id=account_id)
    return create_api_response(
        data=deleted_account, message="Cuenta por cobrar eliminada con éxito."
    )
