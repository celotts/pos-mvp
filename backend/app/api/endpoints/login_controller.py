from typing import Annotated, Any

from api.response_factory import ApiResponse, create_api_response
from core.crud_user import crud_user
from core.security import create_access_token
from dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from schemas.token import Token, TokenData
from schemas.user import User as UserSchema
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Bootstrap & Auth"])

# Inyección de dependencias limpia para Ruff/FastAPI
AsyncSessionDep = Annotated[AsyncSession, Depends(get_db)]


# Esquema específico para recibir JSON en el login web
class UserLoginSchema(BaseModel):
    username: EmailStr
    password: str


@router.post(
    "/login/access-token",
    response_model=ApiResponse[TokenData],
    summary="Get a JWT access token via JSON",
    description="Authenticates a user via JSON payload and returns a token with user details.",
)
async def login_access_token(
    login_data: UserLoginSchema,  # Lee payload JSON
    db: AsyncSessionDep,
) -> Any:
    user = await crud_user.authenticate(
        db,
        email=login_data.username,
        password=login_data.password,
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
    user_data = UserSchema.model_validate(user)
    token_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data,
    }

    return create_api_response(data=token_data, message="Authentication successful")


@router.post(
    "/login/swagger",
    response_model=Token,
    include_in_schema=True,
    summary="OAuth2 compatible token login for Swagger UI",
    description="Authenticates via x-www-form-urlencoded for Swagger UI Authorize dialog.",
)
async def login_swagger(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],  # Lee Form Data
    db: AsyncSessionDep,
) -> Any:
    user = await crud_user.authenticate(
        db,
        email=form_data.username,
        password=form_data.password,
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
    return {"access_token": access_token, "token_type": "bearer"}
