import { create } from "zustand"
import { createJSONStorage, persist } from "zustand/middleware"

import { api, decodeExp } from "@/lib/api"
import type { LoginPayload, TokenData, UserWithRole } from "@/types"
import type { ApiResponse } from "@/types"

export type LogoutReason = "manual" | "expired"

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  tokenExp: number | null
  user: UserWithRole | null
  // Persistencia + derivación reactiva
  isAuthenticated: boolean
  loading: boolean
  // Última razón de cierre de sesión (para feedback de UI, p.ej. sesión expirada)
  lastLogoutReason: LogoutReason | null
  login: (payload: LoginPayload) => Promise<void>
  logout: (reason?: LogoutReason) => void
  setSession: (session: {
    accessToken?: string | null
    refreshToken?: string | null
    tokenExp?: number | null
    user?: UserWithRole | null
  }) => void
  // Utilidades RBAC
  hasPermission: (code: string | string[]) => boolean
  hasAnyPermission: (codes: string[]) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      refreshToken: null,
      tokenExp: null,
      user: null,
      isAuthenticated: false,
      loading: false,
      lastLogoutReason: null,

      login: async (payload) => {
        set({ loading: true })
        try {
          const res = await api.post<ApiResponse<TokenData>>(
            "/login/access-token",
            payload,
          )
          const data = res.data.data
          const exp = decodeExp(data.access_token)
          set({
            accessToken: data.access_token,
            refreshToken: data.refresh_token,
            tokenExp: exp,
            user: data.user,
            isAuthenticated: true,
            loading: false,
            lastLogoutReason: null,
          })
        } catch (error) {
          set({ loading: false })
          throw error
        }
      },

      logout: (reason = "manual") => {
        // Revoca el refresh token en el backend (best-effort) y limpia estado
        const refreshToken = get().refreshToken
        if (refreshToken) {
          api
            .post("/logout", { refresh_token: refreshToken })
            .catch(() => undefined)
        }
        set({
          accessToken: null,
          refreshToken: null,
          tokenExp: null,
          user: null,
          isAuthenticated: false,
          lastLogoutReason: reason,
        })
      },

      setSession: (session) => {
        set({
          accessToken:
            session.accessToken === undefined
              ? get().accessToken
              : session.accessToken,
          refreshToken:
            session.refreshToken === undefined
              ? get().refreshToken
              : session.refreshToken,
          tokenExp:
            session.tokenExp === undefined ? get().tokenExp : session.tokenExp,
          user: session.user === undefined ? get().user : session.user,
          isAuthenticated:
            session.accessToken === null ? false : get().isAuthenticated,
        })
      },

      hasPermission: (codes) => {
        const user = get().user
        if (!user) return false
        const perms = user.permissions ?? []
        const list = Array.isArray(codes) ? codes : [codes]
        // Super admin debería tener todo (se asume rol con todos los permisos)
        if (user.role_name === "SUPER_ADMIN") return true
        return list.some((c) => perms.includes(c))
      },

      hasAnyPermission: (codes) => get().hasPermission(codes),
    }),
    {
      name: "pos-auth", // localStorage key
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        tokenExp: state.tokenExp,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
)
