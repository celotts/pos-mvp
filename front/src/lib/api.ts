import axios, {
  AxiosError,
  AxiosResponse,
  type InternalAxiosRequestConfig,
} from "axios"

import { useAuthStore } from "@/store/authStore"

export interface StoredSession {
  accessToken: string | null
  refreshToken: string | null
  // exp (segundos) del access token, usado para refresh proactivo
  tokenExp?: number | null
}

/**
 * Configuración central del API.
 * En desarrollo se usa VITE_API_BASE_URL=/api que el proxy de Vite redirige
 * al host del backend (VITE_API_PROXY_TARGET). El backend expone sus rutas
 * bajo /api/v1, así que el baseURL incluye el prefijo de versión.
 */
export const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string) || "/api"

const API_VERSION_PREFIX = "/v1"

export const api = axios.create({
  baseURL: `${API_BASE_URL}${API_VERSION_PREFIX}`,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
})

// ─── Interceptor de petición: inyecta el Bearer token ─────────────────────
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const accessToken = useAuthStore.getState().accessToken
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

// Cola para encolar peticiones mientras se refresca el token
let isRefreshing = false
let pendingQueue: Array<(token: string | null) => void> = []

function flushQueue(token: string | null) {
  pendingQueue.forEach((cb) => cb(token))
  pendingQueue = []
}

/**
 * Intenta renovar la sesión con el refresh token (el backend rota el token:
 * revoca el actual y devuelve uno nuevo). Actualiza el store de auth.
 */
export async function refreshAccessToken(): Promise<string | null> {
  const { refreshToken, setSession, logout } = useAuthStore.getState()
  if (!refreshToken) {
    logout()
    return null
  }
  try {
    const res: AxiosResponse = await axios.post(
      `${API_BASE_URL}${API_VERSION_PREFIX}/login/refresh`,
      { refresh_token: refreshToken },
      { headers: { "Content-Type": "application/json" } },
    )
    const d = res.data?.data
    if (!d?.access_token) {
      logout()
      return null
    }
    setSession({
      accessToken: d.access_token,
      refreshToken: d.refresh_token,
      tokenExp: decodeExp(d.access_token),
    })
    return d.access_token
  } catch {
    logout()
    return null
  }
}

/** Decodifica el exp (epoch secs) del JWT sin validar firma (solo lectura). */
export function decodeExp(token: string): number | null {
  try {
    const parts = token.split(".")
    if (parts.length !== 3) return null
    const payload = JSON.parse(
      typeof atob === "function" ? atob(parts[1]) : Buffer.from(parts[1], "base64").toString(),
    )
    return typeof payload.exp === "number" ? payload.exp : null
  } catch {
    return null
  }
}

/**
 * Indica si el access token está próximo a expirar (o ya expiró) según el
 * margen de seguridad configurado.
 */
export const isTokenNearExpiry = (): boolean => {
  const { accessToken, tokenExp } = useAuthStore.getState()
  if (!accessToken) return true
  if (!tokenExp) return false // sin exp conocido, delegar al interceptor 401
  const margin = Number(import.meta.env.VITE_TOKEN_REFRESH_MARGIN_SECONDS || 120)
  const now = Math.floor(Date.now() / 1000)
  return now >= tokenExp - margin
}

// ─── Interceptor de respuesta: manejo global de errores y refresh en 401 ──
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
    }
    const isAuthEndpoint =
      original?.url?.includes("/login/") || original?.url?.includes("/logout")

    // 401 y no es un endpoint de login (evitar bucle) y no reintentado aún
    if (
      error.response?.status === 401 &&
      !isAuthEndpoint &&
      original &&
      !original._retry
    ) {
      original._retry = true

      // Si ya hay un refresh en curso, encolar
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingQueue.push((token) => {
            if (token) {
              original.headers.Authorization = `Bearer ${token}`
              resolve(api(original))
            } else {
              reject(error)
            }
          })
        })
      }

      isRefreshing = true
      const newToken = await refreshAccessToken()
      isRefreshing = false
      flushQueue(newToken)

      if (newToken) {
        original.headers.Authorization = `Bearer ${newToken}`
        return api(original)
      }
      // No se pudo refrescar => logout (el store ya lo hizo)
    }
    return Promise.reject(error)
  },
)

/** Extrae un mensaje de error legible a partir de una respuesta Axios. */
export function getErrorMessage(
  error: unknown,
  fallback = "Ocurrió un error inesperado",
): string {
  if (axios.isAxiosError(error)) {
    const d = (error.response?.data as { message?: string; detail?: string }) ?? {}
    // El API usa ApiResponse con `message`; FastAPI usa `detail` para validación.
    if (d.message) return d.message
    if (d.detail) return typeof d.detail === "string" ? d.detail : "Error de validación"
    if (error.code === "ECONNABORTED") return "La petición tardó demasiado en responder"
    if (!error.response) return "No se pudo conectar con el servidor"
  }
  return fallback
}
