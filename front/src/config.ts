/** Constantes de entorno y configuración del frontend. */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'

/** Intentos máximos de login antes del bloqueo (política espejo del backend). */
export const MAX_LOGIN_ATTEMPTS = 3

/** Clave de sesión para el contador de intentos fallidos. */
export const ATTEMPTS_STORAGE_KEY = 'pos.login_attempts'

/** Clave de almacenamiento del token JWT. */
export const TOKEN_STORAGE_KEY = 'pos.access_token'