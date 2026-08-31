/** Tipos compartidos del frontend (espejo de los esquemas del API). */

export interface UserWithRole {
  id: string
  email: string
  full_name: string
  is_active: boolean
  role_id: string
  role_name: string
  /** Códigos de permiso RBAC del rol (sale:create, product:read, …). */
  permissions: string[]
}

export interface LoginResponseData {
  access_token: string
  token_type: string
  user: UserWithRole
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}

/** Rol "*" permite acceso a cualquier usuario autenticado. */
export type RoleRule = '*' | string

export interface MenuItem {
  id: string
  label: string
  icon?: string
  path?: string
  /** Roles permitidos; "*" significa cualquier usuario autenticado. */
  roles: RoleRule[]
  /**
   * Permisos RBAC requeridos (cualquiera de la lista habilita el ítem).
   * Si está vacío/ausente, se ignora y solo se evalúa `roles`.
   */
  permissions?: string[]
  children?: MenuItem[]
}

export interface MenuConfig {
  items: MenuItem[]
}