from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def _jwt_encode(claims: dict, *, now: datetime) -> str:
    """Codifica un JWT con los claims estándar de seguridad (iss/aud/iat)."""
    return jwt.encode(
        {
            **claims,
            "iat": now,
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
        },
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


def create_access_token(subject: str | int) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    return _jwt_encode({"exp": expire, "sub": str(subject)}, now=now)


def decode_access_token(token: str) -> str:
    """Decodifica un token de acceso JWT y devuelve el ID del usuario (subject).

    Valida firma, expiración, issuer y audience. Lanza una excepción
    HTTPException si el token es inválido, de otra audiencia o ha expirado.
    """
    from fastapi import HTTPException, status

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    expired_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except jwt.ExpiredSignatureError:
        raise expired_token_exception from None
    except jwt.InvalidTokenError:
        raise credentials_exception from None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
