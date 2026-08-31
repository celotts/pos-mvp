
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps_auth import require_permission
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_db
from models.user import User as UserModel
from schemas.permission import Permission, RolePermissionsUpdate
from schemas.role import Role, RoleCreate, RoleUpdate, RoleWithPermissions
from service import role_service

router = APIRouter(tags=["Roles & Permisos"])

db_dependency = Depends(get_db)

require_role_read = Depends(require_permission("role:read"))
require_role_create = Depends(require_permission("role:create"))
require_role_update = Depends(require_permission("role:update"))
require_role_delete = Depends(require_permission("role:delete"))
require_role_assign = Depends(require_permission("role:assign_permissions"))
require_permission_read = Depends(require_permission("permission:read"))


@router.get("/", response_model=ApiResponse[list[RoleWithPermissions]])
async def read_roles(
    db: AsyncSession = db_dependency,
    current_user: UserModel = require_role_read,
    skip: int = 0,
    limit: int = 100,
) -> ApiResponse[list[RoleWithPermissions]]:
    """Get a list of roles with their permissions."""
    roles = await role_service.get_roles(db, skip=skip, limit=limit)
    return create_api_response(data=roles)


@router.post(
    "/", response_model=ApiResponse[Role], status_code=status.HTTP_201_CREATED
)
async def create_role(
    *,
    role_in: RoleCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = require_role_create,
) -> ApiResponse[Role]:
    """Create a new role."""
    role = await role_service.create_role(db=db, role_in=role_in)
    return create_api_response(data=role, status_code=status.HTTP_201_CREATED)


@router.get("/{role_id}", response_model=ApiResponse[RoleWithPermissions])
async def read_role_by_id(
    *,
    role_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = require_role_read,
) -> ApiResponse[RoleWithPermissions]:
    """Get a specific role with its permissions by its ID."""
    role = await role_service.get_role(db=db, role_id=role_id)
    return create_api_response(data=role)


@router.put("/{role_id}", response_model=ApiResponse[Role])
async def update_role(
    *,
    role_id: uuid.UUID,
    role_in: RoleUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = require_role_update,
) -> ApiResponse[Role]:
    """Update a role."""
    role = await role_service.update_role(db=db, role_id=role_id, role_in=role_in)
    return create_api_response(data=role)


@router.put(
    "/{role_id}/permissions",
    response_model=ApiResponse[RoleWithPermissions],
    summary="Replace the permissions of a role",
)
async def replace_role_permissions(
    *,
    role_id: uuid.UUID,
    body: RolePermissionsUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = require_role_assign,
) -> ApiResponse[RoleWithPermissions]:
    """Reemplaza el conjunto de permisos de un rol no protegido."""
    role = await role_service.assign_permissions_to_role(
        db=db, role_id=role_id, permission_codes=body.permission_codes
    )
    return create_api_response(data=role, message="Permissions updated successfully.")


@router.delete("/{role_id}", response_model=ApiResponse[Role])
async def delete_role(
    *,
    role_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = require_role_delete,
) -> ApiResponse[Role]:
    """Delete a role.
    Protected roles like 'SUPER_ADMIN' or roles in use cannot be deleted."""
    deleted_role = await role_service.remove_role(db=db, role_id=role_id)
    return create_api_response(data=deleted_role, message="Role deleted successfully.")


@router.get(
    "/catalog/permissions",
    response_model=ApiResponse[list[Permission]],
    summary="List all permissions (RBAC catalog)",
)
async def list_permissions(
    db: AsyncSession = db_dependency,
    current_user: UserModel = require_permission_read,
) -> ApiResponse[list[Permission]]:
    """Devuelve todos los permisos del catálogo (para administrar roles)."""
    permissions = await role_service.get_permissions(db)
    return create_api_response(data=permissions)
