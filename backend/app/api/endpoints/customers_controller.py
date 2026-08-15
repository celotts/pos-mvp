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
    """Create a new customer. For administrators only."""
    customer = await crud_customer.create_customer(
        db=db, customer_in=customer_in, user_id=current_user.id
    )
    return create_api_response(
        data=customer,
        status_code=status.HTTP_201_CREATED,
        message="Customer created successfully.",
    )


@router.get("/", response_model=ApiResponse[list[Customer]])
async def read_customers(
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
    skip: int = 0,
    limit: int = 100,
) -> ApiResponse[list[Customer]]:
    """Get a list of customers."""
    customers = await crud_customer.get_customers(db, skip=skip, limit=limit)
    return create_api_response(data=customers)


@router.get("/{customer_id}", response_model=ApiResponse[Customer])
async def read_customer(
    *,
    customer_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> ApiResponse[Customer]:
    """Get a customer by its ID."""
    customer = await crud_customer.get_customer(db, customer_id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return create_api_response(data=customer)


@router.put("/{customer_id}", response_model=ApiResponse[Customer])
async def update_customer(
    *,
    customer_id: uuid.UUID,
    customer_in: CustomerUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> ApiResponse[Customer]:
    """Update a customer. For administrators only."""
    db_customer = await crud_customer.get_customer(db, customer_id=customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found.")
    customer = await crud_customer.update_customer(
        db=db, db_customer=db_customer, customer_in=customer_in, user_id=current_user.id
    )
    return create_api_response(data=customer, message="Customer updated successfully.")


@router.delete("/{customer_id}", response_model=ApiResponse[Customer])
async def delete_customer(
    *,
    customer_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> ApiResponse[Customer]:
    """Delete a customer. For administrators only."""
    customer = await crud_customer.remove_customer(db, customer_id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")
    return create_api_response(data=customer, message="Customer deleted successfully.")
