import uuid

from core import crud_supplier
from fastapi import HTTPException, status
from models import Supplier
from models import User as UserModel
from schemas.supplier import SupplierCreate, SupplierUpdate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def get_suppliers(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Supplier]:
    """Obtiene una lista de proveedores."""
    return await crud_supplier.get_multi(db, skip=skip, limit=limit)


async def create_supplier(
    db: AsyncSession, *, supplier_in: SupplierCreate, current_user: UserModel
) -> Supplier:
    """Crea un nuevo proveedor."""
    try:
        return await crud_supplier.create(
            db=db,
            obj_in=supplier_in,
            created_by=current_user.id,
            created_by_role_id=current_user.role_id,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un proveedor con este email o RFC ya existe.",
        )


async def get_supplier(db: AsyncSession, *, supplier_id: uuid.UUID) -> Supplier:
    """Obtiene un proveedor por ID."""
    db_supplier = await crud_supplier.get(db=db, id=supplier_id)
    if not db_supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado."
        )
    return db_supplier


async def update_supplier(
    db: AsyncSession,
    *,
    supplier_id: uuid.UUID,
    supplier_in: SupplierUpdate,
    current_user: UserModel,
) -> Supplier:
    """Actualiza un proveedor."""
    db_supplier = await get_supplier(db=db, supplier_id=supplier_id)
    return await crud_supplier.update(
        db=db,
        db_obj=db_supplier,
        obj_in=supplier_in,
        updated_by=current_user.id,
        updated_by_role_id=current_user.role_id,
    )


async def remove_supplier(db: AsyncSession, *, supplier_id: uuid.UUID) -> Supplier:
    """Elimina un proveedor."""
    await get_supplier(db=db, supplier_id=supplier_id)
    return await crud_supplier.remove(db=db, id=supplier_id)
