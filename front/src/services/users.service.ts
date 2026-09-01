import { api } from "@/lib/api"
import type { User, UserCreate } from "@/types"
import type { ApiResponse } from "@/types"
import { httpGet, httpPost } from "./http"

export async function listUsers(): Promise<User[]> {
  return httpGet<User[]>("/users/")
}

export async function getCurrentUser(): Promise<User> {
  return httpGet<User>("/users/me")
}

export async function createUser(payload: UserCreate): Promise<User> {
  return httpPost<User>("/users/", payload)
}

export async function updateUser(
  id: string,
  payload: Partial<UserCreate>,
): Promise<User> {
  const res = await api.put<ApiResponse<User>>(`/users/${id}`, payload)
  return res.data.data
}

export async function deleteUser(id: string): Promise<void> {
  const res = await api.delete<ApiResponse<unknown>>(`/users/${id}`)
  if (!res.data.success) {
    throw new Error(res.data.message || "Error al eliminar el usuario")
  }
}
