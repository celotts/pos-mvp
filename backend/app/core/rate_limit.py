# core/rate_limit.py
"""Rate limiting del endpoint de login usando slowapi.

Límite configurable vía `LOGIN_RATE_LIMIT_PER_MINUTE` (intentos por IP).
El contador es en memoria (por proceso); para multi-worker/nodos migrar a
Redis u otro almacén distribuido mediante `Limiter(storage_uri=...)`.
"""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from core.config import settings


def client_ip(request: Request) -> str:
    """IP del cliente, respetando proxies con X-Forwarded-For."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


login_limiter = Limiter(
    key_func=client_ip,
    default_limits=[f"{settings.LOGIN_RATE_LIMIT_PER_MINUTE}/minute"],
    headers_enabled=False,
)
