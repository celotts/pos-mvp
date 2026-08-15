import uuid

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from core import crud_customer
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User as UserModel
from schemas.customer import Customer, CustomerCreate, CustomerUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Customers"])

# Dependencias a nivel de módulo para un código más limpio y sin advertencias del linter
db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
current_admin_user_dependency = Depends(get_current_admin_user)


@router.post(
    "/", response_model=ApiResponse[Customer], status_code=status.HTTP_201_CREATED
)
async def create_customer(
    *,
    customer_in: CustomerCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> ApiResponse[Customer]:
    """
    Crea un nuevo cliente. Solo para administradores.
    """
    customer = await crud_customer.create_customer(
        db=db, customer_in=customer_in, user_id=current_user.id
    )
    return create_api_response(
        data=customer,
        status_code=status.HTTP_201_CREATED,
        message="Cliente creado con éxito.",
    )


@router.get("/", response_model=ApiResponse[list[Customer]])
async def read_customers(
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
    skip: int = 0,
    limit: int = 100,
) -> ApiResponse[list[Customer]]:
    """
    Obtiene una lista de clientes.
    """
    customers = await crud_customer.get_customers(db, skip=skip, limit=limit)
    return create_api_response(data=customers)


@router.get("/{customer_id}", response_model=ApiResponse[Customer])
async def read_customer(
    *,
    customer_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> ApiResponse[Customer]:
    """
    Obtiene un cliente por su ID.
    """
    customer = await crud_customer.get_customer(db, customer_id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    return create_api_response(data=customer)


@router.put("/{customer_id}", response_model=ApiResponse[Customer])
async def update_customer(
    *,
    customer_id: uuid.UUID,
    customer_in: CustomerUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> ApiResponse[Customer]:
    """
    Actualiza un cliente. Solo para administradores.
    """
    db_customer = await crud_customer.get_customer(db, customer_id=customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    customer = await crud_customer.update_customer(
        db=db, db_customer=db_customer, customer_in=customer_in, user_id=current_user.id
    )
    return create_api_response(data=customer, message="Cliente actualizado con éxito.")


@router.delete("/{customer_id}", response_model=ApiResponse[Customer])
async def delete_customer(
    *,
    customer_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> ApiResponse[Customer]:
    """
    Elimina un cliente. Solo para administradores.
    """
    customer = await crud_customer.remove_customer(db, customer_id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado.")
    return create_api_response(data=customer, message="Cliente eliminado con éxito.")
