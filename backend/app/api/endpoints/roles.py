import uuid

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from core import crud_role
from dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User as UserModel
from schemas.role import Role, RoleCreate, RoleUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

current_user_dependency = Depends(get_current_admin_user)
db_dependency = Depends(get_db)


@router.get("/", response_model=ApiResponse[list[Role]])
async def read_roles(
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
    skip: int = 0,
    limit: int = 100,
) -> ApiResponse[list[Role]]:
    """
    Obtiene una lista de roles.
    """
    roles = await crud_role.get_roles(db, skip=skip, limit=limit)
    return create_api_response(data=roles)


@router.post("/", response_model=ApiResponse[Role], status_code=status.HTTP_201_CREATED)
async def create_role(
    *,
    role_in: RoleCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> ApiResponse[Role]:
    """
    Crea un nuevo rol.
    """
    role = await crud_role.create_role(db=db, role_in=role_in)
    return create_api_response(data=role, status_code=status.HTTP_201_CREATED)


@router.put("/{role_id}", response_model=ApiResponse[Role])
async def update_role(
    *,
    role_id: uuid.UUID,
    role_in: RoleUpdate,
    current_user: UserModel = current_user_dependency,
    db: AsyncSession = db_dependency,
) -> ApiResponse[Role]:
    """
    Actualiza un rol.
    """
    db_role = await crud_role.get_role(db, role_id=role_id)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado."
        )
    role = await crud_role.update_role(db=db, db_role=db_role, role_in=role_in)
    return create_api_response(data=role)
