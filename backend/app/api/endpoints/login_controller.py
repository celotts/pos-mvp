from api.response_factory import create_api_response
from core.crud_user import crud_user
from core.security import create_access_token
from dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.token import TokenData
from schemas.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Boostrap & Auth"])

db_dependency = Depends(get_db)
form_data_dependency = Depends()


@router.post(
    "/login/access-token",
    summary="Get a JWT access token",
    description="Authenticates a user with email and password and returns a token.",
)
async def login_access_token(
    db: AsyncSession = db_dependency,
    form_data: OAuth2PasswordRequestForm = form_data_dependency,
):
    """
    Endpoint para autenticar y generar un token de acceso.

    Utiliza el `response_factory` para devolver una respuesta estandarizada
    que incluye el token y la información del usuario.
    """
    user = await crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(user.id))

    # Prepara los datos para la respuesta estandarizada
    token_data = TokenData(
        access_token=access_token, token_type="bearer", user=User.from_orm(user)
    )

    return create_api_response(data=token_data, message="Authentication successful")
