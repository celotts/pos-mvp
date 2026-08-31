# core/rate_limit.py
"""Limitador de tasa en memoria con ventana deslizante (sin dependencias externas).

Diseñado para cargas de un solo proceso. Para desplegues con múltiples workers
o nodos habría que mover el contador a Redis u otro almacén compartido.
"""

import time
from collections import defaultdict, deque

from core.config import settings


class SlidingWindowRateLimiter:
    """Permite hasta `max_requests` llamadas por `window_seconds` por clave (IP)."""

    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque] = defaultdict(deque)

    def is_allowed(self, key: str) -> bool:
        now = time.monotonic()
        window = self._hits[key]
        while window and now - window[0] > self.window_seconds:
            window.popleft()
        if len(window) >= self.max_requests:
            return False
        window.append(now)
        return True


login_limiter = SlidingWindowRateLimiter(
    max_requests=settings.LOGIN_RATE_LIMIT_PER_MINUTE
)


def client_ip(request) -> str:
    """Devuelve la IP del cliente, respetando proxies con X-Forwarded-For."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"
