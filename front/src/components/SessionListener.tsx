import { useEffect, useRef } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { toast } from "sonner"

import { useAuthStore } from "@/store/authStore"

/**
 * Vigila la sesión del usuario de forma global.
 *
 * Cuando la sesión deja de estar autenticada porque EXPIRO (p.ej. el refresh
 * token falló), redirige de inmediato a /login e informa al usuario. Así el
 * usuario nunca permanece en una pantalla con sesión vencida intentando
 * navegar o guardar datos con un token muerto.
 *
 * El cierre de sesión manual (botón "Cerrar sesión") también navega aquí,
 * pero sin el mensaje de "sesión expirada" (else branch).
 */
export function SessionListener() {
  const navigate = useNavigate()
  const location = useLocation()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const lastLogoutReason = useAuthStore((s) => s.lastLogoutReason)
  const prevAuth = useRef(isAuthenticated)

  useEffect(() => {
    const wasAuth = prevAuth.current
    prevAuth.current = isAuthenticated

    // Ignorar el primer render (estado inicial cargado de persistencia).
    if (wasAuth === isAuthenticated) return
    // Solo reaccionar ante una transición autenticado -> no autenticado.
    if (wasAuth && !isAuthenticated) {
      if (lastLogoutReason === "expired") {
        toast.error(
          "Tu sesión ha expirado. Inicia sesión de nuevo para continuar.",
        )
      }
      // Redirige siempre (manual o expirado). replace evita volver atrás.
      if (location.pathname !== "/login") {
        navigate("/login", { replace: true })
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, lastLogoutReason])

  return null
}