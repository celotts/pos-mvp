from typing import Any

from api.response_factory import ApiResponse, create_api_response
from core.crud_user import crud_user
from core.security import create_access_token
from dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.token import TokenData
from schemas.user import User as UserSchema
from schemas.user import UserLoginRequest
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Bootstrap & Auth"])

db_dependency = Depends(get_db)


@router.post(
    "/login/access-token",
    response_model=ApiResponse[TokenData],
    summary="Get a JWT access token",
    description="Authenticates a user with email and password and returns a token.",
)
async def login_access_token(
    login_data: UserLoginRequest,
    db: AsyncSession = db_dependency,
) -> Any:
    """Authenticates a user and generates an access token.
    It uses the `response_factory` to return a standardized response
    that includes the token and user information.
    """
    user = await crud_user.authenticate(
        db,
        email=login_data.username,
        password=login_data.password.get_secret_value(),
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user account is inactive.",
        )

    access_token = create_access_token(subject=str(user.id))

    # Prepara los datos para la respuesta.
    # Convertimos explícitamente el modelo SQLAlchemy 'user' al esquema Pydantic 'User'
    # para evitar problemas de serialización con referencias circulares (user -> role -> users).
    user_data = UserSchema.model_validate(user)
    token_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data,
    }

    return create_api_response(data=token_data, message="Authentication successful")
