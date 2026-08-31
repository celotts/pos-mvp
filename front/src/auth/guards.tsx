import { Navigate, useLocation } from 'react-router-dom'
import type { ReactNode } from 'react'

import { useAuth } from './AuthContext'
import { getMenuItemByPath, roleAllowed } from '../menu/menu'
import type { RoleRule } from '../types'

function FullScreenLoader() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50">
      <div className="flex flex-col items-center gap-3">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
        <p className="text-sm font-medium text-slate-500">Cargando sesión…</p>
      </div>
    </div>
  )
}

/** Requiere una sesión válida; redirige a /login si no la hay. */
export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { status } = useAuth()
  const location = useLocation()

  if (status === 'loading') return <FullScreenLoader />
  if (status !== 'authenticated') {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  return <>{children}</>
}

/**
 * Valida el acceso según el rol del usuario.
 * Si `allowedRoles` no se indica, resuelve los roles desde el menú JSON
 * usando la ruta actual; si la ruta no está en el menú, exige solo sesión.
 */
export function RoleRoute({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  const location = useLocation()

  if (!user) return <Navigate to="/login" replace />

  const menuItem = getMenuItemByPath(location.pathname)
  const allowedRoles: RoleRule[] | null = menuItem ? menuItem.roles : null

  if (allowedRoles && !roleAllowed(allowedRoles, user.role_name)) {
    return <Navigate to="/403" replace />
  }
  return <>{children}</>
}