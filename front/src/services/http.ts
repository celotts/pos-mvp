import { api } from "@/lib/api"
import type { ApiResponse } from "@/types"

/**
 * Wrapper tipado sobre axios que extrae el payload `data` de la envoltura
 * estándar `ApiResponse`. Los interceptores del cliente ya inyectan el token
 * y gestionan el refresh automático.
 */
export async function httpGet<T>(url: string): Promise<T> {
  const res = await api.get<ApiResponse<T>>(url)
  return res.data.data
}

export async function httpPost<T>(
  url: string,
  body?: unknown,
): Promise<T> {
  const res = await api.post<ApiResponse<T>>(url, body)
  return res.data.data
}

export async function httpPut<T>(url: string, body?: unknown): Promise<T> {
  const res = await api.put<ApiResponse<T>>(url, body)
  return res.data.data
}

export async function httpDelete<T>(url: string): Promise<T> {
  const res = await api.delete<ApiResponse<T>>(url)
  return res.data.data
}
