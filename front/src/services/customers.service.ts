import { api } from "@/lib/api"
import type { Customer } from "@/types"
import type { ApiResponse } from "@/types"
import { httpGet, httpPost } from "./http"

export interface CustomerPayload {
  full_name: string
  email?: string | null
  phone?: string | null
  address?: string | null
}

export async function listCustomers(): Promise<Customer[]> {
  return httpGet<Customer[]>("/customers/")
}

export async function createCustomer(
  payload: CustomerPayload,
): Promise<Customer> {
  return httpPost<Customer>("/customers/", payload)
}

export async function updateCustomer(
  id: string,
  payload: Partial<CustomerPayload>,
): Promise<Customer> {
  const res = await api.put<ApiResponse<Customer>>(`/customers/${id}`, payload)
  return res.data.data
}

export async function deleteCustomer(id: string): Promise<void> {
  const res = await api.delete<ApiResponse<unknown>>(`/customers/${id}`)
  if (!res.data.success) {
    throw new Error(res.data.message || "Error al eliminar el cliente")
  }
}
