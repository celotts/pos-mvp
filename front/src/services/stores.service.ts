import { api } from "@/lib/api"
import type { Store } from "@/types"
import type { ApiResponse } from "@/types"
import { httpGet, httpPost } from "./http"

export interface StorePayload {
  name: string
  address?: string | null
  municipality_id?: string | null
}

export async function listStores(): Promise<Store[]> {
  return httpGet<Store[]>("/stores/")
}

export async function createStore(payload: StorePayload): Promise<Store> {
  return httpPost<Store>("/stores/", payload)
}

export async function updateStore(
  id: string,
  payload: Partial<StorePayload>,
): Promise<Store> {
  const res = await api.put<ApiResponse<Store>>(`/stores/${id}`, payload)
  return res.data.data
}

export async function deleteStore(id: string): Promise<void> {
  const res = await api.delete<ApiResponse<unknown>>(`/stores/${id}`)
  if (!res.data.success) {
    throw new Error(res.data.message || "Error al eliminar la tienda")
  }
}
