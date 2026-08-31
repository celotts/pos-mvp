import type { ComponentType } from 'react'
import {
  AlertTriangle,
  ArrowDownToLine,
  Bot,
  Box,
  Boxes,
  Calculator,
  ChartLine,
  HandCoins,
  LayoutDashboard,
  Monitor,
  Package,
  PackagePlus,
  Receipt,
  Settings,
  Shield,
  ShoppingBag,
  ShoppingCart,
  Sparkles,
  Store,
  Tags,
  Truck,
  UserCog,
  Users,
  Wallet,
  Warehouse,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

import type { MenuItem, RoleRule } from '../types'
import rawMenu from './menu.json'

const ICONS: Record<string, LucideIcon> = {
  'layout-dashboard': LayoutDashboard,
  package: Package,
  box: Box,
  users: Users,
  truck: Truck,
  store: Store,
  tags: Tags,
  'shopping-cart': ShoppingCart,
  'arrow-down-to-line': ArrowDownToLine,
  warehouse: Warehouse,
  boxes: Boxes,
  sparkles: Sparkles,
  'chart-line': ChartLine,
  'package-plus': PackagePlus,
  'shopping-bag': ShoppingBag,
  'alert-triangle': AlertTriangle,
  calculator: Calculator,
  wallet: Wallet,
  receipt: Receipt,
  'hand-coins': HandCoins,
  settings: Settings,
  'user-cog': UserCog,
  shield: Shield,
  monitor: Monitor,
  bot: Bot,
}

export type { ComponentType }

/** Devuelve el menú configurado (JSON) con sus tipos. */
export const menuConfig: { items: MenuItem[] } = rawMenu as { items: MenuItem[] }

/** Obtiene el ícono registrado para un nombre de la configuración. */
export function getMenuIcon(name?: string): LucideIcon | ComponentType {
  if (!name) return Package
  return ICONS[name] ?? Package
}

/** ¿El rol tiene acceso al ítem? "*" permite cualquier usuario autenticado. */
export function roleAllowed(roles: RoleRule[], roleName: string): boolean {
  if (roles.includes('*')) return true
  return roles.includes(roleName)
}

/**
 * Control de acceso por rol y por permiso RBAC.
 * - Si `item.roles` incluye "*" → acceso para cualquier autenticado.
 * - Si el rol está listado → acceso.
 * - Si el ítem define `permissions`, basta que el usuario tenga UNO de ellos.
 * - Los roles protegidos (SUPER_ADMIN/ADMIN) conservan acceso total.
 */
export function menuAllowed(
  item: Pick<MenuItem, 'roles' | 'permissions'>,
  roleName: string,
  permissions: string[],
): boolean {
  if (roleAllowed(item.roles, roleName)) return true
  if (item.permissions && item.permissions.length > 0) {
    return item.permissions.some((p) => permissions.includes(p))
  }
  return false
}

/** Filtra recursivamente el menú según rol + permisos del usuario. */
export function filterMenu(
  items: MenuItem[],
  roleName: string,
  permissions: string[],
): MenuItem[] {
  return items
    .filter((item) => menuAllowed(item, roleName, permissions))
    .map((item) =>
      item.children
        ? {
            ...item,
            children: filterMenu(item.children, roleName, permissions),
          }
        : item,
    )
    .filter((item) => !item.children || item.children.length > 0)
}

/** Lista plana de ítems de "hoja" (los que tienen ruta y renderizan un form). */
export function getMenuLeaves(items: MenuItem[] = menuConfig.items): MenuItem[] {
  return items.flatMap((item) =>
    item.children ? getMenuLeaves(item.children) : [item],
  )
}

/** Busca un ítem de menú por su ruta (para validar acceso en las rutas). */
export function getMenuItemByPath(path: string): MenuItem | undefined {
  return getMenuLeaves().find((item) => item.path === path)
}