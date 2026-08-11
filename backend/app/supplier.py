import uuid
from typing import Any

from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_admin_user, get_current_user, get_db
from fastapi import APIRouter, Depends, status
from models.user import User as UserModel
from modules import supplier_service
from schemas.supplier import Supplier, SupplierCreate, SupplierUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
current_admin_user_dependency = Depends(get_current_admin_user)


@router.post(
    "/",
    response_model=ApiResponse[Supplier],
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo Proveedor",
)
async def create_supplier(
    *,
    supplier_in: SupplierCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Crea un nuevo proveedor."""
    supplier = await supplier_service.create_supplier(
        db=db, supplier_in=supplier_in, current_user=current_user
    )
    return create_api_response(
        data=supplier,
        status_code=status.HTTP_201_CREATED,
        message="Proveedor creado con éxito.",
    )


@router.get(
    "/",
    response_model=ApiResponse[list[Supplier]],
    summary="Obtener una lista de Proveedores",
)
async def read_suppliers(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Obtiene una lista paginada de proveedores."""
    suppliers = await supplier_service.get_suppliers(db, skip=skip, limit=limit)
    return create_api_response(data=suppliers)


@router.get(
    "/{supplier_id}",
    response_model=ApiResponse[Supplier],
    summary="Obtener un Proveedor por ID",
)
async def read_supplier(
    *,
    supplier_id: uuid.UUID,
    db: AsyncSession = db_dependency,
) -> Any:
    """Obtiene un proveedor específico por su ID."""
    supplier = await supplier_service.get_supplier(db, supplier_id=supplier_id)
    return create_api_response(data=supplier)


@router.put(
    "/{supplier_id}",
    response_model=ApiResponse[Supplier],
    summary="Actualizar un Proveedor",
)
async def update_supplier(
    *,
    supplier_id: uuid.UUID,
    supplier_in: SupplierUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Actualiza un proveedor por su ID."""
    updated_supplier = await supplier_service.update_supplier(
        db=db,
        supplier_id=supplier_id,
        supplier_in=supplier_in,
        current_user=current_user,
    )
    return create_api_response(
        data=updated_supplier, message="Proveedor actualizado con éxito."
    )


@router.delete(
    "/{supplier_id}",
    response_model=ApiResponse[Supplier],
    summary="Eliminar un Proveedor",
)
async def delete_supplier(
    *,
    supplier_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Elimina un proveedor por su ID."""
    deleted_supplier = await supplier_service.remove_supplier(
        db, supplier_id=supplier_id
    )
    return create_api_response(
        data=deleted_supplier, message="Proveedor eliminado con éxito."
    )
