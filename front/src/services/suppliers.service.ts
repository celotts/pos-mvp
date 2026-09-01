import { api } from "@/lib/api"
import type { Supplier } from "@/types"
import type { ApiResponse } from "@/types"
import { httpGet, httpPost } from "./http"

export interface SupplierPayload {
  name: string
  contact_name?: string | null
  phone?: string | null
  email?: string | null
  address?: string | null
}

export async function listSuppliers(): Promise<Supplier[]> {
  return httpGet<Supplier[]>("/suppliers/")
}

export async function createSupplier(
  payload: SupplierPayload,
): Promise<Supplier> {
  return httpPost<Supplier>("/suppliers/", payload)
}

export async function updateSupplier(
  id: string,
  payload: Partial<SupplierPayload>,
): Promise<Supplier> {
  const res = await api.put<ApiResponse<Supplier>>(
    `/suppliers/${id}`,
    payload,
  )
  return res.data.data
}

export async function deleteSupplier(id: string): Promise<void> {
  const res = await api.delete<ApiResponse<unknown>>(`/suppliers/${id}`)
  if (!res.data.success) {
    throw new Error(res.data.message || "Error al eliminar el proveedor")
  }
}
