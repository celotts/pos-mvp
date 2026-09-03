"""Internacionalización de mensajes de error/validación del API.

Dos archivos de diccionario: `en.py` (inglés, por defecto) y `es.py`
(español). La función `tr()` traduce una clave al idioma detectado del
header `Accept-Language`, interpolando los parámetros de la plantilla.

Uso:
    raise HTTPException(
        status_code=404,
        detail=tr("NOT_FOUND.PRODUCT_ID", product_id=str(pid)),
    )

El idioma se detecta una vez por request (recomendado: en un middleware,
llamando a `set_current_lang(detect_lang(accept_language))`) y queda
disponible en todo el request vía ContextVar, como en `core.tenancy`.
"""

from contextvars import ContextVar

from .en import MESSAGES_EN
from .es import MESSAGES_ES

__all__ = [
    "MESSAGES_EN",
    "MESSAGES_ES",
    "detect_lang",
    "get_current_lang",
    "set_current_lang",
    "tr",
]

_current_lang: ContextVar[str] = ContextVar("current_lang", default="en")


def set_current_lang(lang: str) -> None:
    """Establece el idioma activo del request en curso ('en' o 'es')."""
    _current_lang.set("es" if lang == "es" else "en")


def get_current_lang() -> str:
    """Devuelve el idioma activo del request (por defecto 'en')."""
    return _current_lang.get()


def _format(template: str, params: dict) -> str:
    """Interpola la plantilla con los parámetros de forma segura."""
    if not params:
        return template
    try:
        return template.format(**params)
    except (KeyError, IndexError):
        return template


def detect_lang(accept_language: str | None) -> str:
    """Resuelve el idioma desde el header Accept-Language. Default 'en'."""
    if not accept_language:
        return "en"
    for part in accept_language.split(","):
        tag = part.split(";")[0].strip().lower()
        lang = tag.split("-")[0].strip()
        if lang == "es":
            return "es"
    return "en"


def tr(key: str, *, lang: str | None = None, **params) -> str:
    """Devuelve el mensaje traducido para la clave dada.

    - Si `lang` se omite, se usa el idioma del request (`get_current_lang()`).
    - Si la clave no existe en el idioma objetivo (ES), se cae a inglés.
    - Si tampoco existe en inglés, se devuelve la propia clave (fallo visible).
    """
    target = lang or get_current_lang()
    table = MESSAGES_ES if target == "es" else MESSAGES_EN
    template = table.get(key)
    if template is None and target == "es":
        template = MESSAGES_EN.get(key)
    if template is None:
        return key
    return _format(template, params)
