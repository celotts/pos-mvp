import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_db
from models.user import User as UserModel
from schemas.role import Role, RoleCreate, RoleUpdate
from service import role_service

router = APIRouter(tags=["Roles"])

db_dependency = Depends(get_db)
current_admin_user_dependency = Depends(get_current_admin_user)


@router.get("/", response_model=ApiResponse[list[Role]])
async def read_roles(
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
    skip: int = 0,
    limit: int = 100,
) -> ApiResponse[list[Role]]:
    """Get a list of roles."""
    roles = await role_service.get_roles(db, skip=skip, limit=limit)
    return create_api_response(data=roles)


@router.post("/", response_model=ApiResponse[Role], status_code=status.HTTP_201_CREATED)
async def create_role(
    *,
    role_in: RoleCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> ApiResponse[Role]:
    """Create a new role."""
    role = await role_service.create_role(db=db, role_in=role_in)
    return create_api_response(data=role, status_code=status.HTTP_201_CREATED)


@router.get("/{role_id}", response_model=ApiResponse[Role])
async def read_role_by_id(
    *,
    role_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> ApiResponse[Role]:
    """Get a specific role by its ID."""
    # Llama a la función del servicio que ya maneja la lógica de búsqueda y el error 404.
    role = await role_service.get_role(db=db, role_id=role_id)
    return create_api_response(data=role)


@router.put("/{role_id}", response_model=ApiResponse[Role])
async def update_role(
    *,
    role_id: uuid.UUID,
    role_in: RoleUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> ApiResponse[Role]:
    """Update a role."""
    role = await role_service.update_role(db=db, role_id=role_id, role_in=role_in)
    return create_api_response(data=role)


@router.delete("/{role_id}", response_model=ApiResponse[Role])
async def delete_role(
    *,
    role_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> ApiResponse[Role]:
    """Delete a role.
    Protected roles like 'SUPER_ADMIN' or roles in use cannot be deleted."""
    deleted_role = await role_service.remove_role(db=db, role_id=role_id)
    return create_api_response(data=deleted_role, message="Role deleted successfully.")
