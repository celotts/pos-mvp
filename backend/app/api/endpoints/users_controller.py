import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps_auth import require_permission
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from models.user import User as UserModel
from schemas.user import User, UserCreate, UserUpdate, UserWithRole
from service import user_service

router = APIRouter(tags=["Users"])

get_db_dependency = Depends(get_db)
get_current_user_dependency = Depends(get_current_user)
require_user_read = Depends(require_permission("user:read"))
require_user_create = Depends(require_permission("user:create"))
require_user_update = Depends(require_permission("user:update"))
require_user_delete = Depends(require_permission("user:delete"))


@router.get(
    "/me",
    response_model=ApiResponse[UserWithRole],
    summary="Get the current logged-in user with its role",
)
async def read_me(
    current_user: UserModel = get_current_user_dependency,
) -> ApiResponse[UserWithRole]:
    """Returns the authenticated user enriched with its role (for dynamic menus)."""
    return create_api_response(
        data=UserWithRole(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            is_active=current_user.is_active,
            role_id=current_user.role_id,
            role_name=current_user.role.name if current_user.role else "",
        )
    )


@router.get(
    "/",
    response_model=ApiResponse[list[User]],
    summary="Get a list of users",
)
async def read_users(
    db: AsyncSession = get_db_dependency,
    current_user: UserModel = require_user_read,
    skip: int = 0,
    limit: int = 100,
) -> ApiResponse[list[User]]:
    """Get a list of users."""
    users = await user_service.get_users(db, skip=skip, limit=limit)
    return create_api_response(data=users)


@router.post(
    "/",
    response_model=ApiResponse[User],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(
    *,
    user_in: UserCreate,
    current_user: UserModel = require_user_create,
    db: AsyncSession = get_db_dependency,
) -> ApiResponse[User]:
    user = await user_service.create_user_with_logic(db=db, user_in=user_in)
    return create_api_response(
        data=user,
        status_code=status.HTTP_201_CREATED,
        message="User created successfully.",
    )


@router.get(
    "/{user_id}",
    response_model=ApiResponse[User],
    summary="Get a user by ID",
)
async def read_user_by_id(
    user_id: uuid.UUID,
    db: AsyncSession = get_db_dependency,
    current_user: UserModel = require_user_read,
) -> ApiResponse[User]:
    """Get a user by ID."""
    user = await user_service.get_user(db=db, user_id=user_id)
    return create_api_response(data=user)


@router.put(
    "/{user_id}",
    response_model=ApiResponse[User],
    summary="Update an existing user",
)
async def update_user(
    *,
    user_id: uuid.UUID,
    user_in: UserUpdate,
    current_user: UserModel = require_user_update,
    db: AsyncSession = get_db_dependency,
) -> ApiResponse[User]:
    """Update a user."""
    user = await user_service.update_user(
        db=db, user_id=user_id, user_in=user_in, current_user=current_user
    )
    return create_api_response(data=user, message="User updated successfully.")


@router.delete(
    "/{user_id}",
    response_model=ApiResponse[User],
    summary="Delete a user",
)
async def delete_user(
    *,
    user_id: uuid.UUID,
    current_user: UserModel = require_user_delete,
    db: AsyncSession = get_db_dependency,
) -> ApiResponse[User]:
    """Delete a user."""
    user = await user_service.remove_user(db=db, user_id=user_id)
    return create_api_response(data=user, message="User deleted successfully.")
