from core import crud_user
from core.security import create_access_token
from dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.token import Token
from schemas.user import UserLogin
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


# @router.post(
#     "/auth/bootstrap-admin",
#     response_model=ApiResponse[User],
#     status_code=status.HTTP_201_CREATED,
# )
# async def bootstrap_admin(
#     *,
#     db: AsyncSession = Depends(get_db),
#     user_in: UserBootstrapIn,
#     bootstrap_secret: str = Header(..., alias="X-Bootstrap-Secret"),
# ) -> ApiResponse[User]:
#     """
#     Crea el primer usuario administrador.
#     Este endpoint solo funciona si no hay otros usuarios en la base de datos
#     y se proporciona el secreto de bootstrap correcto.
#     """
#     # ID del rol SUPER_ADMIN definido en V1__initial_schema.sql
#     SUPER_ADMIN_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
#
#     # 1. Validar el secreto
#     if bootstrap_secret != settings.BOOTSTRAP_SECRET_KEY:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Secreto de bootstrap incorrecto.",
#         )
#
#     # 2. Verificar que no existan usuarios
#     users = await crud_user.get_users(db, limit=1)
#     if users:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="El sistema ya ha sido inicializado. No se pueden crear más administradores por esta vía.",
#         )
#
#     # 3. Crear el usuario
#     user_create = UserCreate(**user_in.model_dump(), role_id=SUPER_ADMIN_ROLE_ID)
#     try:
#         user = await crud_user.create_user(db=db, user_in=user_create)
#     except IntegrityError:
#         raise HTTPException(status_code=400, detail="El email ya está registrado.")
#     return create_api_response(
#         data=user, status_code=status.HTTP_201_CREATED, message="Administrador creado."
#     )


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_db),
):
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
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }
