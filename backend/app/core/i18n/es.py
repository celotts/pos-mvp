"""Mensajes de error y validación del API — ESPAÑOL.

Un único archivo por idioma. Debe mantener el mismo set de claves que
`en.py` y soportar los mismos parámetros `{name}`.
"""

MESSAGES_ES: dict[str, str] = {
    # ─── AUTH ───────────────────────────────────────────────────────────────
    "AUTH.INVALID_CREDENTIALS": "Email o contraseña incorrectos.",
    "AUTH.ACCOUNT_INACTIVE": "La cuenta de usuario está inactiva.",
    "AUTH.USER_INACTIVE": "El usuario está inactivo.",
    "AUTH.ACCOUNT_LOCKED": "La cuenta está bloqueada por múltiples intentos de inicio de sesión fallidos.",
    "AUTH.USER_NOT_FOUND": "Usuario no encontrado.",
    "AUTH.INVALID_REFRESH": "Token de refresco inválido.",
    "AUTH.REFRESH_EXPIRED": "El token de refresco ha expirado.",
    "AUTH.REFRESH_REVOKED": "El token de refresco fue revocado. Inicie sesión nuevamente.",
    "AUTH.CREDENTIALS_INVALID": "No se pudieron validar las credenciales",

    # ─── RBAC / PERMISOS ────────────────────────────────────────────────────
    "RBAC.NO_VALID_ROLE": "El usuario no tiene un rol válido asignado o el rol fue eliminado.",
    "RBAC.FORBIDDEN": "El usuario no tiene los privilegios necesarios.",

    # ─── NOT FOUND (recursos) ───────────────────────────────────────────────
    "NOT_FOUND.PRODUCT": "Producto no encontrado.",
    "NOT_FOUND.PRODUCT_ID": "Producto con id {product_id} no encontrado.",
    "NOT_FOUND.SUPPLIER": "Proveedor no encontrado.",
    "NOT_FOUND.SUPPLIER_ID": "Proveedor con ID {supplier_id} no existe.",
    "NOT_FOUND.CUSTOMER": "Cliente no encontrado.",
    "NOT_FOUND.STORE": "Tienda no encontrada.",
    "NOT_FOUND.COUNTRY": "País no encontrado.",
    "NOT_FOUND.COUNTRY_ID": "País con ID {country_id} no existe.",
    "NOT_FOUND.STATE_PROVINCE": "Estado/Provincia no encontrado.",
    "NOT_FOUND.STATE_PROVINCE_ID": "Estado/Provincia con ID {state_id} no encontrado.",
    "NOT_FOUND.SPECIALTY": "Especialidad no encontrada.",
    "NOT_FOUND.TERMINAL": "Terminal no encontrado.",
    "NOT_FOUND.SHIFT": "El turno no existe.",
    "NOT_FOUND.SALE": "La venta no existe.",
    "NOT_FOUND.ACCOUNT": "Cuenta no encontrada.",
    "NOT_FOUND.ACCOUNT_PAYABLE": "Cuenta por pagar no encontrada.",
    "NOT_FOUND.ACCOUNT_RECEIVABLE": "Cuenta por cobrar no encontrada.",
    "NOT_FOUND.ROLE": "Rol no encontrado.",
    "NOT_FOUND.ROLE_TO_DELETE": "No se encontró el rol para eliminar.",
    "NOT_FOUND.ROLE_ID": "Rol con ID '{role_id}' no encontrado.",
    "NOT_FOUND.USER": "Usuario no encontrado.",

    # ─── DUPLICADOS / CONFLICTO ─────────────────────────────────────────────
    "DUPLICATE.SKU": "Ya existe un producto con ese SKU.",
    "DUPLICATE.EMAIL": "Ya existe un usuario con ese email.",
    "DUPLICATE.COUNTRY": "Ya existe un país con ese nombre o código ISO.",
    "DUPLICATE.SPECIALTY": "Ya existe una especialidad con ese nombre.",
    "DUPLICATE.TERMINAL": "Ya existe un terminal con ese nombre.",
    "DUPLICATE.ACCOUNT": "Ya existe una cuenta con ese nombre.",
    "DUPLICATE.ROLE_NAME": "Ya existe un rol con el nombre '{name}'.",
    "DB.CONSTRAINT_VIOLATION": "Violación de restricción de base de datos.",

    # ─── VALIDACIÓN DE NEGOCIO ──────────────────────────────────────────────
    "VALIDATION.EMPTY_SALE": "Una venta debe tener al menos un producto.",
    "VALIDATION.EMPTY_PURCHASE": "Una compra debe tener al menos un producto.",
    "VALIDATION.STOCK_INSUFFICIENT": "Stock insuficiente para '{name}': solicitado {requested}, disponible {available}.",
    "VALIDATION.UNKNOWN_PERMISSIONS": "Códigos de permiso desconocidos: {codes}",
    "VALIDATION.INACTIVE_TERMINAL": "El terminal no existe o no está activo.",

    # ─── SHIFT ──────────────────────────────────────────────────────────────
    "SHIFT.CLOSED": "El turno ya está cerrado.",
    "SHIFT.OPEN_EXISTS_TERMINAL": "Ya existe un turno abierto en el terminal '{terminal}'.",
    "SHIFT.OWN_ONLY": "Solo puedes cerrar tus propios turnos.",

    # ─── SALE ───────────────────────────────────────────────────────────────
    "SALE.CANCELLED": "La venta ya está cancelada.",

    # ─── ROLE ───────────────────────────────────────────────────────────────
    "ROLE.PROTECTED_DELETE": "El rol '{name}' está protegido y no puede eliminarse.",
    "ROLE.PROTECTED_MODIFY": "El rol '{name}' está protegido y no puede modificarse.",
    "ROLE.DELETE_ASSIGNED": "El rol '{name}' no puede eliminarse porque está asignado a uno o más usuarios.",
    "ROLE.SELF_CHANGE": "No puedes cambiar tu propio rol.",
    "ROLE.SELF_DEACTIVATE": "No puedes desactivar tu propia cuenta.",

    # ─── IA / ASISTENTE ─────────────────────────────────────────────────────
    "AI.INVENTORY_VECTORIZE_ERROR": "No se pudo vectorizar y guardar el análisis de inventario. Revisa los logs del servicio de IA (Ollama) y la base de datos.",
    "AI.AGENT_PROCESS_ERROR": "Error al procesar la solicitud con el agente: {error}",
    "AI.MALFORMED_RESPONSE": "Respuesta malformada del servicio de IA: falta la clave {error}",
    "AI.DECISION_MODULE_ERROR": "Error interno en el módulo de decisiones: {error}",

    # ─── DB / ERRORES GLOBALES ──────────────────────────────────────────────
    "DB.INTEGRITY_GENERIC": "Conflicto: el registro viola una restricción única en base de datos.",
    "DB.INTEGRITY_DETAIL": "Conflicto en base de datos: {detail}",
    "DB.GENERIC": "Ocurrió un error de base de datos. Inténtalo de nuevo.",
    "VALIDATION.ERROR": "Error de validación. Revisa el payload de la solicitud.",
    "VALIDATION.UUID_INVALID": "El campo '{field}' debe ser un UUID válido. Recibido: '{value}'.",
    "VALIDATION.UUID_FIELD": "{msg}",
    "RATE_LIMIT": "Demasiados intentos de inicio de sesión. Inténtalo de nuevo más tarde.",
    "SERVER.UNEXPECTED": "Ocurrió un error interno inesperado.",
}
