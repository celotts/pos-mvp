"""Gestión de refresh tokens (C.3): emisión, rotación y revocación.

Un refresh token es un JWT con `type=refresh`, `sub` = user_id y un `jti`
único. Solo se persiste el hash SHA-256 del `jti` en `refresh_tokens`, nunca
el token en claro. Rotación: cada uso revoca el token anterior y emite uno
nuevo; si un token ya revocado vuelve a usarse, se rechaza (señal de robo).
"""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.security import ALGORITHM
from models.refresh_token import RefreshToken

TYPE_CLAIM = "refresh"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _hash_jti(jti: str) -> str:
    return hashlib.sha256(jti.encode()).hexdigest()


def create_refresh_token_payload(user_id: uuid.UUID) -> tuple[str, str]:
    """Genera el JWT de refresco y devuelve (token, jti)."""
    jti = str(uuid.uuid4())
    expire = _now() + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS)
    claims = {
        "sub": str(user_id),
        "jti": jti,
        "type": TYPE_CLAIM,
        "exp": expire,
        "iat": _now(),
    }
    token = jwt.encode(claims, settings.SECRET_KEY, algorithm=ALGORITHM)
    return token, jti


def _decode_refresh_token(token: str):
    """Decodifica y valida el refresh JWT. Lanza ValueError si es inválido/expirado."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM], options={"verify_sub": False}
        )
    except ExpiredSignatureError:
        raise ValueError("refresh_expired") from None
    except JWTError:
        raise ValueError("refresh_invalid") from None
    if payload.get("type") != TYPE_CLAIM or not payload.get("jti") or not payload.get("sub"):
        raise ValueError("refresh_invalid")
    return payload


async def issue_refresh_token(
    db: AsyncSession, *, user_id: uuid.UUID, ip: str | None = None
) -> str:
    """Crea y persiste un refresh token nuevo para el usuario."""
    token, jti = create_refresh_token_payload(user_id)
    row = RefreshToken(
        token_hash=_hash_jti(jti),
        user_id=user_id,
        expires_at=_now() + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS),
        ip=ip,
    )
    db.add(row)
    await db.flush()
    return token


async def _load_current(
    db: AsyncSession, *, jti: str, user_id: uuid.UUID
) -> RefreshToken | None:
    query = select(RefreshToken).where(
        RefreshToken.token_hash == _hash_jti(jti),
        RefreshToken.user_id == user_id,
    )
    result = await db.execute(query)
    return result.scalars().first()


async def rotate_refresh_token(
    db: AsyncSession, *, token: str, ip: str | None = None
) -> tuple[str, uuid.UUID, RefreshToken]:
    """Valida y rota un refresh token.

    Reglas:
    - Token inválido/desconocido        -> ValueError("refresh_invalid")
    - Token expirado                    -> ValueError("refresh_expired")
    - Token ya revocado (reutilizado)   -> ValueError("refresh_revoked")

    Devuelve (nuevo_token, user_id, fila_rotada). La fila antigua queda revocada.
    """
    payload = _decode_refresh_token(token)

    user_id = uuid.UUID(payload["sub"])
    jti = payload["jti"]

    row = await _load_current(db, jti=jti, user_id=user_id)
    if row is None:
        raise ValueError("refresh_invalid")

    expire = row.expires_at.replace(tzinfo=timezone.utc) if row.expires_at.tzinfo is None else row.expires_at
    if expire < _now():
        row.revoked = True
        row.revoked_at = _now()
        raise ValueError("refresh_expired")

    if row.revoked:
        raise ValueError("refresh_revoked")

    # Rotación: revoca el actual y emite uno nuevo.
    row.revoked = True
    row.revoked_at = _now()

    new_token = await issue_refresh_token(db, user_id=user_id, ip=ip)
    await db.flush()
    return new_token, user_id, row


async def revoke_refresh_token(db: AsyncSession, *, token: str) -> bool:
    """Revoca el refresh token (logout). Devuelve True si se encontró y revocó."""
    try:
        payload = _decode_refresh_token(token)
    except ValueError:
        return False
    row = await _load_current(
        db, jti=payload["jti"], user_id=uuid.UUID(payload["sub"])
    )
    if row is None or row.revoked:
        return False
    row.revoked = True
    row.revoked_at = _now()
    await db.flush()
    return True
