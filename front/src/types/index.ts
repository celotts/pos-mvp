// Tipos de dominio del POS — reflejan los schemas del API (OpenAPI /api/v1)

// ─── Envoltura de respuesta estándar del API ────────────────────────────────
export interface ApiResponse<T> {
  success: boolean
  status_code: number
  message: string
  data: T
  total?: number | null
}

// ─── Autenticación ──────────────────────────────────────────────────────────

export interface UserWithRole {
  id: string
  email: string
  full_name: string
  is_active: boolean
  role_id: string
  role_name: string
  permissions: string[]
}

export interface TokenData {
  access_token: string
  refresh_token: string
  token_type: string
  user: UserWithRole
}

export interface RefreshResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginPayload {
  username: string
  password: string
}

export interface RefreshPayload {
  refresh_token: string
}

// ─── Catálogos / Ubicaciones ────────────────────────────────────────────────

export interface Permission {
  id: string
  code: string
  description?: string | null
  module: string
}

export interface Role {
  id: string
  name: string
  description?: string | null
}

export interface RoleWithPermissions extends Role {
  permissions: string[] // códigos de permiso
}

// ─── Usuarios ───────────────────────────────────────────────────────────────

export interface User {
  id: string
  email: string
  full_name: string
  is_active?: boolean
}

export interface UserCreate {
  email: string
  full_name: string
  password: string
  role_id: string
}

// ─── Productos ──────────────────────────────────────────────────────────────

export interface Product {
  id: string
  name: string
  description?: string | null
  price: string | number
  sku: string
  supplier_id?: string | null
}

export interface ProductCreate {
  name: string
  description?: string | null
  price: number | string
  sku: string
  supplier_id?: string | null
}

// ─── Proveedores ────────────────────────────────────────────────────────────

export interface Supplier {
  id: string
  name: string
  contact_name?: string | null
  phone?: string | null
  email?: string | null
  address?: string | null
}

// ─── Clientes ───────────────────────────────────────────────────────────────

export interface Customer {
  id: string
  full_name?: string | null
  email?: string | null
  phone?: string | null
  address?: string | null
}

// ─── Tiendas ────────────────────────────────────────────────────────────────

export interface Store {
  id: string
  name: string
  address?: string | null
  municipality_id?: string | null
}

// ─── Terminales POS ─────────────────────────────────────────────────────────

export interface PosTerminal {
  id: string
  name?: string | null
  store_id?: string | null
}

// ─── Ventas ─────────────────────────────────────────────────────────────────

export type SaleStatus = "PENDING" | "COMPLETED" | "CANCELLED"
export type PaymentStatusType = "UNPAID" | "PAID" | "PARTIALLY_PAID"

export interface SaleItem {
  product_id: string
  quantity: number
  price_at_sale?: string
}

export interface Sale {
  id: string
  store_id: string
  total_amount: string | number
  status: SaleStatus
  sale_date: string
  user_id: string
  created_at: string
  items: SaleItem[]
}

export interface SaleCreate {
  store_id: string
  pos_terminal_id: string
  customer_id?: string | null
  items: {
    product_id: string
    quantity: number
  }[]
}

// ─── Turnos (shifts) ────────────────────────────────────────────────────────

export interface Shift {
  id: string
  pos_terminal_id: string
  store_id: string
  user_id: string
  start_time: string
  end_time?: string | null
  starting_cash: string | number
  ending_cash?: string | number | null
  status: "open" | "closed"
}

export interface ShiftOpen {
  pos_terminal_id: string
  store_id: string
  starting_cash: number | string
}

// ─── Compras ────────────────────────────────────────────────────────────────

export interface PurchaseItem {
  product_id: string
  quantity: number
  price_at_purchase?: string
}

export interface Purchase {
  id: string
  supplier_id: string
  total_amount: string | number
  total_tax_amount: string | number
  purchase_date: string
  items: PurchaseItem[]
}

export interface PurchaseCreate {
  supplier_id: string
  items: { product_id: string; quantity: number }[]
}

export interface PurchaseItemInput {
  product_id: string
  quantity: number
}

// ─── Asistente IA ───────────────────────────────────────────────────────────

export interface ChatRequest {
  message: string
  context_store_id?: string | null
}

export interface InsightRecommendation {
  category: string
  action_item?: string
  impact_level?: string
}

export interface ChatResponse {
  answer: string
  insights: InsightRecommendation[]
  raw_metrics?: unknown
}
