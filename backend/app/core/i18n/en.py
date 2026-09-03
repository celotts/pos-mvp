"""Mensajes de error y validación del API — INGLÉS (idioma por defecto).

Un único archivo por idioma. Las claves se organizan por módulo/dominio y
los valores son plantillas que soportan parámetros `{name}` (str.format).
"""

MESSAGES_EN: dict[str, str] = {
    # ─── AUTH ───────────────────────────────────────────────────────────────
    "AUTH.INVALID_CREDENTIALS": "Incorrect email or password.",
    "AUTH.ACCOUNT_INACTIVE": "The user account is inactive.",
    "AUTH.USER_INACTIVE": "User is inactive.",
    "AUTH.ACCOUNT_LOCKED": "The account is locked due to multiple failed login attempts.",
    "AUTH.USER_NOT_FOUND": "User not found.",
    "AUTH.INVALID_REFRESH": "Invalid refresh token.",
    "AUTH.REFRESH_EXPIRED": "Refresh token has expired.",
    "AUTH.REFRESH_REVOKED": "Refresh token has been revoked. Please login again.",
    "AUTH.CREDENTIALS_INVALID": "Could not validate credentials",

    # ─── RBAC / PERMISOS ────────────────────────────────────────────────────
    "RBAC.NO_VALID_ROLE": "The user does not have a valid role assigned or the role has been deleted.",
    "RBAC.FORBIDDEN": "The user does not have the necessary privileges.",

    # ─── NOT FOUND (recursos) ───────────────────────────────────────────────
    "NOT_FOUND.PRODUCT": "Product not found.",
    "NOT_FOUND.PRODUCT_ID": "Product with id {product_id} not found.",
    "NOT_FOUND.SUPPLIER": "Supplier not found.",
    "NOT_FOUND.SUPPLIER_ID": "Supplier with ID {supplier_id} does not exist.",
    "NOT_FOUND.CUSTOMER": "Customer not found.",
    "NOT_FOUND.STORE": "Store not found.",
    "NOT_FOUND.COUNTRY": "Country not found.",
    "NOT_FOUND.COUNTRY_ID": "Country with ID {country_id} does not exist.",
    "NOT_FOUND.STATE_PROVINCE": "State/Province not found.",
    "NOT_FOUND.STATE_PROVINCE_ID": "State/Province with ID {state_id} not found.",
    "NOT_FOUND.SPECIALTY": "Specialty not found.",
    "NOT_FOUND.TERMINAL": "Terminal not found.",
    "NOT_FOUND.SHIFT": "Shift does not exist.",
    "NOT_FOUND.SALE": "Sale does not exist.",
    "NOT_FOUND.ACCOUNT": "Account not found.",
    "NOT_FOUND.ACCOUNT_PAYABLE": "Account payable not found.",
    "NOT_FOUND.ACCOUNT_RECEIVABLE": "Account receivable not found.",
    "NOT_FOUND.ROLE": "Role not found.",
    "NOT_FOUND.ROLE_TO_DELETE": "Role not found to delete.",
    "NOT_FOUND.ROLE_ID": "Role with ID '{role_id}' not found.",
    "NOT_FOUND.USER": "User not found.",

    # ─── DUPLICADOS / CONFLICTO ─────────────────────────────────────────────
    "DUPLICATE.SKU": "A product with this SKU already exists.",
    "DUPLICATE.EMAIL": "A user with this email already exists.",
    "DUPLICATE.COUNTRY": "A country with that name or ISO code already exists.",
    "DUPLICATE.SPECIALTY": "A specialty with this name already exists.",
    "DUPLICATE.TERMINAL": "A terminal with this name already exists.",
    "DUPLICATE.ACCOUNT": "An account with this name already exists.",
    "DUPLICATE.ROLE_NAME": "A role with the name '{name}' already exists.",
    "DB.CONSTRAINT_VIOLATION": "Database integrity constraint violation.",

    # ─── VALIDACIÓN DE NEGOCIO ──────────────────────────────────────────────
    "VALIDATION.EMPTY_SALE": "A sale must have at least one product.",
    "VALIDATION.EMPTY_PURCHASE": "A purchase must have at least one product.",
    "VALIDATION.STOCK_INSUFFICIENT": "Insufficient stock for '{name}': requested {requested}, available {available}.",
    "VALIDATION.UNKNOWN_PERMISSIONS": "Unknown permission codes: {codes}",
    "VALIDATION.INACTIVE_TERMINAL": "The terminal does not exist or is not active.",

    # ─── SHIFT ──────────────────────────────────────────────────────────────
    "SHIFT.CLOSED": "The shift is already closed.",
    "SHIFT.OPEN_EXISTS_TERMINAL": "An open shift already exists at terminal '{terminal}'.",
    "SHIFT.OWN_ONLY": "You can only close your own shifts.",

    # ─── SALE ───────────────────────────────────────────────────────────────
    "SALE.CANCELLED": "The sale is already cancelled.",

    # ─── ROLE ───────────────────────────────────────────────────────────────
    "ROLE.PROTECTED_DELETE": "Role '{name}' is protected and cannot be deleted.",
    "ROLE.PROTECTED_MODIFY": "Role '{name}' is protected and cannot be modified.",
    "ROLE.DELETE_ASSIGNED": "Role '{name}' cannot be deleted because it is assigned to one or more users.",
    "ROLE.SELF_CHANGE": "You cannot change your own role.",
    "ROLE.SELF_DEACTIVATE": "You cannot deactivate your own account.",

    # ─── IA / ASISTENTE ─────────────────────────────────────────────────────
    "AI.INVENTORY_VECTORIZE_ERROR": "Could not vectorize and save the inventory analysis. Check the logs of the AI service (Ollama) and the database.",
    "AI.AGENT_PROCESS_ERROR": "Error processing the request with the agent: {error}",
    "AI.MALFORMED_RESPONSE": "Malformed response from the AI service: missing key {error}",
    "AI.DECISION_MODULE_ERROR": "Internal error in the decision module: {error}",

    # ─── DB / ERRORES GLOBALES ──────────────────────────────────────────────
    "DB.INTEGRITY_GENERIC": "Conflict: the record violates a unique constraint in the database.",
    "DB.INTEGRITY_DETAIL": "Database conflict: {detail}",
    "DB.GENERIC": "A database error occurred. Please try again.",
    "VALIDATION.ERROR": "Validation error. Check the request payload.",
    "VALIDATION.UUID_INVALID": "Field '{field}' must be a valid UUID. Received: '{value}'.",
    "VALIDATION.UUID_FIELD": "{msg}",
    "RATE_LIMIT": "Too many login attempts. Please try again later.",
    "SERVER.UNEXPECTED": "An unexpected internal error occurred.",
}
