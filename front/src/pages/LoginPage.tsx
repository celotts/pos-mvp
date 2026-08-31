import { useState, type FormEvent } from 'react'
import {
  Eye,
  EyeOff,
  KeyRound,
  Lock,
  Loader2,
  Mail,
  ShieldCheck,
  Sparkles,
  Store,
  TrendingUp,
} from 'lucide-react'
import { useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../auth/AuthContext'
import { ApiError } from '../api/client'
import { Alert } from '../components/ui/Alert'
import { Button } from '../components/ui/Button'
import { Field } from '../components/ui/Field'
import { Logo } from '../components/ui/brand'
import { MAX_LOGIN_ATTEMPTS } from '../config'

const FEATURES = [
  { icon: Store, text: 'Gestión de catálogo, ventas, compras e inventario' },
  { icon: TrendingUp, text: 'Analítica comercial: cross-selling y market basket' },
  { icon: Sparkles, text: 'Asistente de IA integrado para recomendaciones' },
]

export function LoginPage() {
  const { signIn, incrementAttempts, resetAttempts, remainingAttempts, isLocked } =
    useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (submitting || isLocked) return

    setError(null)
    setSubmitting(true)
    try {
      await signIn(email.trim(), password)
      resetAttempts()
      navigate(from ?? '/dashboard', { replace: true })
    } catch (err) {
      const apiError = err as ApiError
      if (apiError.status === 423 || isLocked) {
        setError(
          'Cuenta bloqueada por demasiados intentos fallidos. Solicítalo al administrador.',
        )
      } else {
        incrementAttempts()
        if (apiError instanceof ApiError && apiError.message) {
          setError(apiError.message)
        } else {
          setError('Credenciales incorrectas.')
        }
      }
    } finally {
      setSubmitting(false)
    }
  }

  const lockedNow = isLocked || MAX_LOGIN_ATTEMPTS - remainingAttempts >= MAX_LOGIN_ATTEMPTS

  return (
    <div className="grid min-h-screen bg-slate-50 lg:grid-cols-2">
      {/* Panel de marca */}
      <div className="relative hidden flex-col justify-between overflow-hidden bg-gradient-to-br from-brand-700 via-brand-600 to-violet-600 p-12 text-white lg:flex">
        <div className="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-white/10 blur-2xl" />
        <div className="absolute -bottom-32 -left-16 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
        <div className="relative">
          <div className="flex items-center gap-2.5 text-white">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/20 text-xl font-black">
              P
            </div>
            <p className="text-lg font-bold">Punto de Venta</p>
          </div>
        </div>
        <div className="relative space-y-6">
          <h1 className="text-3xl font-bold leading-tight">
            Todo tu negocio en un solo lugar
          </h1>
          <p className="max-w-md text-white/85">
            Ventas, compras, inventario y analítica comercial con inteligencia
            artificial para tu tienda.
          </p>
          <ul className="space-y-3">
            {FEATURES.map(({ icon: Icon, text }) => (
              <li key={text} className="flex items-center gap-3 text-sm text-white/90">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/15">
                  <Icon className="h-4.5 w-4.5" />
                </span>
                {text}
              </li>
            ))}
          </ul>
        </div>
        <div className="relative flex items-center gap-2 text-sm text-white/70">
          <ShieldCheck className="h-4 w-4" />
          Inicio de sesión protegido · 3 intentos por cuenta
        </div>
      </div>

      {/* Formulario */}
      <div className="flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-sm">
          <div className="mb-8 lg:hidden">
            <Logo />
          </div>

          <h2 className="text-2xl font-bold text-slate-900">Iniciar sesión</h2>
          <p className="mt-1 text-sm text-slate-500">
            Usa tus credenciales para acceder al sistema.
          </p>

          <form className="mt-8 space-y-4" onSubmit={handleSubmit} noValidate>
            {lockedNow ? (
              <Alert kind="warning" title="Cuenta bloqueada">
                Superaste los {MAX_LOGIN_ATTEMPTS} intentos permitidos. Contacta a un
                administrador para desbloquear tu cuenta.
              </Alert>
            ) : null}

            {error && !lockedNow ? <Alert kind="error">{error}</Alert> : null}

            <Field
              id="email"
              label="Correo electrónico"
              type="email"
              autoComplete="email"
              placeholder="tucorreo@empresa.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              error={error && !error.includes('bloqueada') ? error : undefined}
            />

            <div className="flex flex-col gap-1.5">
              <label
                className="text-sm font-medium text-slate-700"
                htmlFor="password"
              >
                Contraseña
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={lockedNow}
                  className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-10 text-sm text-slate-900 shadow-sm outline-none transition focus:ring-2 focus:ring-brand-500"
                />
                <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <button
                  type="button"
                  onClick={() => setShowPassword((value) => !value)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={submitting || lockedNow || !email || !password}
            >
              {submitting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <KeyRound className="h-4 w-4" />
              )}
              {submitting ? 'Verificando…' : 'Entrar'}
            </Button>

            {!lockedNow && remainingAttempts < MAX_LOGIN_ATTEMPTS ? (
              <p className="flex items-center justify-center gap-1.5 text-xs text-amber-700">
                <Lock className="h-3.5 w-3.5" />
                Te quedan {remainingAttempts} intento{remainingAttempts === 1 ? '' : 's'} antes del bloqueo.
              </p>
            ) : null}
          </form>

          <p className="mt-8 text-center text-xs text-slate-400">
            © {new Date().getFullYear()} POS · Punto de Venta
          </p>
        </div>
      </div>
    </div>
  )
}