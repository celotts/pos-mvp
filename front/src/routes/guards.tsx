import type { ReactNode } from "react"
import { Navigate, useLocation } from "react-router-dom"
import { useState, useEffect } from "react"

import { isTokenNearExpiry, refreshAccessToken } from "@/lib/api"
import { useAuthStore } from "@/store/authStore"
import { Spinner } from "@/components/ui"

interface GuardProps {
  children: ReactNode
}

/**
 * Refresca proactivamente el access token si está próximo a expirar.
 * Devuelve true cuando la sesión es válida (o se pudo refrescar).
 */
async function ensureFreshSession(): Promise<boolean> {
  const state = useAuthStore.getState()
  if (!state.accessToken) return false
  if (isTokenNearExpiry()) {
    try {
      const ok = await refreshAccessToken()
      return Boolean(ok)
    } catch {
      return false
    }
  }
  return true
}

/** Ruta protegida por autenticación. */
export function ProtectedRoute({ children }: GuardProps) {
  const location = useLocation()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const accessToken = useAuthStore((s) => s.accessToken)
  const [checking, setChecking] = useState(!!accessToken && isAuthenticated)

  useEffect(() => {
    let cancelled = false
    // Si hay sesión pero el token pudo expirar, refrescarlo al entrar
    const run = async () => {
      if (!useAuthStore.getState().accessToken) return
      const ok = await ensureFreshSession()
      // Solo detener el spinner si el refresh fue exitoso. Si falló,
      // refreshAccessToken ya hizo logout() y el SessionListener redirige.
      if (!cancelled && ok) setChecking(false)
    }
    run()
    return () => {
      cancelled = true
    }
  }, [location.pathname])

  // Sin sesión → login
  if (!isAuthenticated && !accessToken) {
    return <Navigate to="/login" replace />
  }

  if (checking) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Spinner size="lg" />
      </div>
    )
  }

  return <>{children}</>
}

/** Ruta protegida por permiso (RBAC). Requiere que el user tenga el/los permisos. */
export function RequirePermission({
  permission,
  children,
}: {
  permission: string | string[]
  children: ReactNode
}) {
  const location = useLocation()
  const allowed = useAuthStore((s) => s.hasPermission(permission))

  if (!allowed) {
    return <Navigate to="/403" replace state={{ from: location }} />
  }
  return <>{children}</>
}
