import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

import { login as apiLogin, fetchCurrentUser } from '../api/auth'
import {
  ATTEMPTS_STORAGE_KEY,
  MAX_LOGIN_ATTEMPTS,
  TOKEN_STORAGE_KEY,
} from '../config'
import type { UserWithRole } from '../types'

type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated'

interface AuthContextValue {
  user: UserWithRole | null
  status: AuthStatus
  isAuthenticated: boolean
  failedAttempts: number
  remainingAttempts: number
  isLocked: boolean
  signIn: (email: string, password: string) => Promise<void>
  signOut: () => void
  incrementAttempts: () => void
  resetAttempts: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

function readAttempts(): number {
  const raw = sessionStorage.getItem(ATTEMPTS_STORAGE_KEY)
  return raw ? Number.parseInt(raw, 10) : 0
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>(() =>
    localStorage.getItem(TOKEN_STORAGE_KEY) ? 'loading' : 'unauthenticated',
  )
  const [user, setUser] = useState<UserWithRole | null>(null)
  const [failedAttempts, setFailedAttempts] = useState(readAttempts)
  const [isLocked, setIsLocked] = useState(() => readAttempts() >= MAX_LOGIN_ATTEMPTS)

  // Restaura la sesión al recargar la página usando el token guardado.
  useEffect(() => {
    if (!localStorage.getItem(TOKEN_STORAGE_KEY)) return

    let cancelled = false
    fetchCurrentUser()
      .then((currentUser) => {
        if (cancelled) return
        setUser(currentUser)
        setStatus('authenticated')
      })
      .catch(() => {
        if (cancelled) return
        localStorage.removeItem(TOKEN_STORAGE_KEY)
        setStatus('unauthenticated')
      })

    return () => {
      cancelled = true
    }
  }, [])

  const resetAttempts = useCallback(() => {
    sessionStorage.removeItem(ATTEMPTS_STORAGE_KEY)
    setFailedAttempts(0)
    setIsLocked(false)
  }, [])

  const incrementAttempts = useCallback(() => {
    sessionStorage.setItem(ATTEMPTS_STORAGE_KEY, String(failedAttempts + 1))
    setFailedAttempts(failedAttempts + 1)
    if (failedAttempts + 1 >= MAX_LOGIN_ATTEMPTS) setIsLocked(true)
  }, [failedAttempts])

  const signIn = useCallback(
    async (email: string, password: string) => {
      const data = await apiLogin(email, password)
      localStorage.setItem(TOKEN_STORAGE_KEY, data.access_token)
      setUser(data.user)
      setStatus('authenticated')
      resetAttempts()
    },
    [resetAttempts],
  )

  const signOut = useCallback(() => {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    sessionStorage.removeItem(ATTEMPTS_STORAGE_KEY)
    setUser(null)
    setStatus('unauthenticated')
    setFailedAttempts(0)
    setIsLocked(false)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      status,
      isAuthenticated: status === 'authenticated',
      failedAttempts,
      remainingAttempts: Math.max(0, MAX_LOGIN_ATTEMPTS - failedAttempts),
      isLocked,
      signIn,
      signOut,
      incrementAttempts,
      resetAttempts,
    }),
    [
      user,
      status,
      failedAttempts,
      isLocked,
      signIn,
      signOut,
      incrementAttempts,
      resetAttempts,
    ],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth debe usarse dentro de <AuthProvider>.')
  }
  return ctx
}