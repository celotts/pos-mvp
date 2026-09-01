import { httpGet, httpPost } from "./http"
import type {
  ApiResponse,
  Permission,
  Product,
  ProductCreate,
} from "@/types"
import { api } from "@/lib/api"

// ─── Productos ──────────────────────────────────────────────────────────────

export async function listProducts(): Promise<Product[]> {
  return httpGet<Product[]>("/products/")
}

export async function createProduct(payload: ProductCreate): Promise<Product> {
  return httpPost<Product>("/products/", payload)
}

export async function updateProduct(
  id: string,
  payload: Partial<ProductCreate>,
): Promise<Product> {
  const res = await api.put<ApiResponse<Product>>(`/products/${id}`, payload)
  return res.data.data
}

export async function deleteProduct(id: string): Promise<void> {
  const res = await api.delete<ApiResponse<unknown>>(`/products/${id}`)
  if (!res.data.success) {
    throw new Error(res.data.message || "Error al eliminar el producto")
  }
}

// ─── Permisos (catálogo) ────────────────────────────────────────────────────

export async function listPermissions(): Promise<Permission[]> {
  return httpGet<Permission[]>("/roles/catalog/permissions")
}
