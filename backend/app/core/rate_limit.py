# core/rate_limit.py
"""Rate limiting de la API usando slowapi.

Un único `Limiter` global con límite por defecto (protección anti-DoS/abuso
por IP para toda la API). Los endpoints sensibles (autenticación) pueden
sobrescribir el límite con `@api_limiter.limit(...)` aplicando un tope
más estricto (brute-force).

* Límite GLOBAL: `API_RATE_LIMIT_PER_MINUTE` (se aplica a todas las rutas).
* Límite de LOGIN: `LOGIN_RATE_LIMIT_PER_MINUTE` (más estricto, decoradores).

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


api_limiter = Limiter(
    key_func=client_ip,
    default_limits=[f"{settings.API_RATE_LIMIT_PER_MINUTE}/minute"],
    headers_enabled=False,
)

# Alias semántico para los decoradores específicos de autenticación.
# Mantiene compatibilidad con los imports actuales (@login_limiter.limit(...)).
login_limiter = api_limiter