from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from api.response_factory import ApiResponse, create_api_response
from core import refresh_token as rt
from core.config import settings
from core.crud_user import crud_user
from core.rate_limit import client_ip, login_limiter
from core.security import create_access_token
from dependencies import get_db
from models.user import User as UserModel
from schemas.token import RefreshRequest, RefreshResponse, Token, TokenData
from schemas.user import UserWithRole

router = APIRouter(tags=["Bootstrap & Auth"])

# Inyección de dependencias limpia para Ruff/FastAPI
AsyncSessionDep = Annotated[AsyncSession, Depends(get_db)]


# Esquema específico para recibir JSON en el login web
class UserLoginSchema(BaseModel):
    username: EmailStr
    password: str


def _build_user_with_role(user: UserModel) -> UserWithRole:
    """Convierte un usuario ORM en el esquema enriquecido con rol y permisos."""
    return UserWithRole(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        role_id=user.role_id,
        role_name=user.role.name if user.role else "",
        permissions=sorted(
            {p.code for p in user.role.permissions} if user.role else []
        ),
    )


def _credentials_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _locked_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_423_LOCKED,
        detail="The account is locked due to multiple failed login attempts.",
    )


async def _authenticate_with_lockout(
    db: AsyncSession, *, email: str, password: str
) -> UserModel:
    """
    Autentica un usuario aplicando la política de bloqueo por intentos fallidos:
    - 3 intentos fallidos bloquean la cuenta durante LOGIN_LOCKOUT_SECONDS.
    - Un login correcto reinicia el contador.
    """
    user = await crud_user.get_by_email(db, email=email)
    if not user:
        raise _credentials_error()
    if user.is_locked:
        raise _locked_error()
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user account is inactive.",
        )

    authenticated = await crud_user.authenticate(db, email=email, password=password)
    if not authenticated:
        user = await crud_user.register_failed_attempt(
            db,
            db_obj=user,
            max_attempts=settings.MAX_LOGIN_ATTEMPTS,
            lock_seconds=settings.LOGIN_LOCKOUT_SECONDS,
        )
        if user.is_locked:
            raise _locked_error()
        raise _credentials_error()

    await crud_user.reset_failed_attempts(db, db_obj=user)
    return user


@router.post(
    "/login/access-token",
    response_model=ApiResponse[TokenData],
    summary="Get a JWT access token via JSON",
    description="Authenticates a user via JSON payload and returns a token with user details.",
)
@login_limiter.limit(f"{settings.LOGIN_RATE_LIMIT_PER_MINUTE}/minute")
async def login_access_token(
    request: Request,
    login_data: UserLoginSchema,  # Lee payload JSON
    db: AsyncSessionDep,
) -> Any:
    user = await _authenticate_with_lockout(
        db, email=login_data.username, password=login_data.password
    )
    # Se construye el payload del usuario (con rol/permisos) ANTES del commit
    # del refresh token para evitar lazy-loading tras el expire del commit.
    user_payload = _build_user_with_role(user)

    access_token = create_access_token(subject=str(user.id))
    refresh_token = await rt.issue_refresh_token(
        db, user_id=user.id, ip=client_ip(request)
    )
    await db.commit()
    token_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user_payload,
    }

    return create_api_response(data=token_data, message="Authentication successful")


@router.post(
    "/login/swagger",
    response_model=Token,
    include_in_schema=True,
    summary="OAuth2 compatible token login for Swagger UI",
    description="Authenticates via x-www-form-urlencoded for Swagger UI Authorize dialog.",
)
@login_limiter.limit(f"{settings.LOGIN_RATE_LIMIT_PER_MINUTE}/minute")
async def login_swagger(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],  # Lee Form Data
    db: AsyncSessionDep,
) -> Any:
    user = await _authenticate_with_lockout(
        db, email=form_data.username, password=form_data.password
    )

    access_token = create_access_token(subject=str(user.id))
    await rt.issue_refresh_token(db, user_id=user.id, ip=client_ip(request))
    await db.commit()
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/login/refresh",
    response_model=ApiResponse[RefreshResponse],
    summary="Refresh the session (rotate tokens)",
    description=(
        "Recibe un refresh token, valida que no esté revocado ni expirado y "
        "rota: revoca el token actual y emite uno nuevo (access + refresh). "
        "Un refresh token reutilizado queda invalidado (rotación)."
    ),
)
@login_limiter.limit(f"{settings.LOGIN_RATE_LIMIT_PER_MINUTE}/minute")
async def login_refresh(
    request: Request,
    body: RefreshRequest,
    db: AsyncSessionDep,
) -> Any:
    try:
        new_refresh, user_id, _row = await rt.rotate_refresh_token(
            db, token=body.refresh_token, ip=client_ip(request)
        )
    except ValueError as e:
        mapping = {
            "refresh_invalid": (
                status.HTTP_401_UNAUTHORIZED,
                "Invalid refresh token.",
            ),
            "refresh_expired": (
                status.HTTP_401_UNAUTHORIZED,
                "Refresh token has expired.",
            ),
            "refresh_revoked": (
                status.HTTP_401_UNAUTHORIZED,
                "Refresh token has been revoked. Please login again.",
            ),
        }
        http_code, message = mapping.get(str(e), (status.HTTP_401_UNAUTHORIZED, "Invalid refresh token."))
        raise HTTPException(status_code=http_code, detail=message)

    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found."
        )

    access_token = create_access_token(subject=str(user_id))
    await db.commit()
    return create_api_response(
        data={
            "access_token": access_token,
            "refresh_token": new_refresh,
            "token_type": "bearer",
        },
        message="Token refreshed successfully",
    )


@router.post(
    "/logout",
    response_model=ApiResponse[None],
    summary="Logout and revoke the refresh token",
    description="Revoca el refresh token de la sesión para invalidar la re-autenticación.",
)
@login_limiter.limit(f"{settings.LOGIN_RATE_LIMIT_PER_MINUTE}/minute")
async def logout(
    request: Request,
    body: RefreshRequest,
    db: AsyncSessionDep,
) -> Any:
    revoked = await rt.revoke_refresh_token(db, token=body.refresh_token)
    await db.commit()
    message = "Logged out successfully" if revoked else "Nothing to revoke"
    return create_api_response(
        data=None, message=message, status_code=status.HTTP_200_OK
    )
