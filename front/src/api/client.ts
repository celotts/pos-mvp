import { API_BASE_URL, TOKEN_STORAGE_KEY } from '../config'

interface RequestOptions {
  method?: string
  body?: unknown
}

/** Error tipado del API con su código HTTP. */
export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function authHeader(): Record<string, string> {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY)
  return token ? { Authorization: `Bearer ${token}` } : {}
}

/** Cliente HTTP genérico que normaliza errores y extrae el campo `data`. */
export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...authHeader(),
  }
  let body: string | undefined
  if (options.body !== undefined && options.body !== null) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(options.body)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? 'GET',
    headers,
    body,
  })

  let payload: Record<string, unknown> | null = null
  const rawText = await response.text()
  if (rawText) {
    try {
      payload = JSON.parse(rawText)
    } catch {
      payload = null
    }
  }

  if (!response.ok) {
    const detail = payload?.detail ?? payload?.message
    const message =
      typeof detail === 'string' && detail
        ? detail
        : 'No se pudo completar la solicitud.'
    throw new ApiError(message, response.status)
  }

  // La mayoría de los endpoints envuelven en { success, data, ... }.
  return (payload?.data as T) ?? (payload as unknown as T)
}