from api.response_factory import ApiResponse, create_api_response
from core.crud_user import crud_user
from core.security import create_access_token
from dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.token import Token
from schemas.user import UserLogin
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

db_dependency = Depends(get_db)


@router.post("/login/access-token", response_model=ApiResponse[Token])
async def login_access_token(
    *,
    user_in: UserLogin,
    db: AsyncSession = db_dependency,
) -> ApiResponse[Token]:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await crud_user.authenticate(
        db, email=user_in.email, password=user_in.password.get_secret_value()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
        )
    token_data = {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }
    return create_api_response(data=token_data, message="Inicio de sesión exitoso.")
