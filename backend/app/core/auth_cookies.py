"""Helpers para emitir/limpiar cookies HttpOnly de autenticación.

Mantener los tokens JWT en cookies HttpOnly (no legibles por JS) elimina la
exposición persistente en localStorage y reduce el robo por XSS. El access
token viaja en cookie siempre que el cliente use `withCredentials`.
"""

from fastapi import Response

from core.config import settings


def _cookie_kwargs(*, max_age: int) -> dict:
    return {
        "httponly": True,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
        "domain": settings.COOKIE_DOMAIN,
        "max_age": max_age,
        "path": "/",
    }


def set_auth_cookies(
    response: Response,
    *,
    access_token: str,
    refresh_token: str,
    access_max_age: int,
    refresh_max_age: int,
) -> None:
    """Escribe las cookies de acceso y refresh en la respuesta."""
    response.set_cookie(
        settings.COOKIE_ACCESS_NAME,
        access_token,
        **_cookie_kwargs(max_age=access_max_age),
    )
    response.set_cookie(
        settings.COOKIE_REFRESH_NAME,
        refresh_token,
        **_cookie_kwargs(max_age=refresh_max_age),
    )


def clear_auth_cookies(response: Response) -> None:
    """Expira y elimina las cookies de autenticación."""
    for name in (settings.COOKIE_ACCESS_NAME, settings.COOKIE_REFRESH_NAME):
        response.delete_cookie(
            name,
            path="/",
            domain=settings.COOKIE_DOMAIN,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
        )
