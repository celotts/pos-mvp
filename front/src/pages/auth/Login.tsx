import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useNavigate, useLocation } from "react-router-dom"
import { toast } from "sonner"
import { ShoppingCart, Eye, EyeOff } from "lucide-react"

import { Button, Input, Alert } from "@/components/ui"
import { useAuthStore } from "@/store/authStore"
import { getErrorMessage } from "@/lib/api"

const loginSchema = z.object({
  username: z.string().email("Ingresa un correo electrónico válido"),
  password: z.string().min(1, "La contraseña es obligatoria"),
})

type LoginForm = z.infer<typeof loginSchema>

export function LoginPage() {
  const login = useAuthStore((s) => s.login)
  const loading = useAuthStore((s) => s.loading)
  const navigate = useNavigate()
  const location = useLocation()
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  })

  const from = (location.state as { from?: string } | null)?.from || "/"

  const onSubmit = async (values: LoginForm) => {
    setError(null)
    try {
      await login(values)
      toast.success("¡Bienvenido de nuevo!")
      navigate(from, { replace: true })
    } catch (err) {
      const msg = getErrorMessage(err, "No se pudo iniciar sesión")
      // 423 -> cuenta bloqueada (lockout)
      const status = (err as { response?: { status?: number } })?.response?.status
      setError(
        status === 423
          ? "Cuenta bloqueada temporalmente por intentos fallidos. Intenta más tarde."
          : msg,
      )
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 p-4">
      <div className="w-full max-w-md">
        <div className="mb-6 flex flex-col items-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-600 text-white shadow-lg">
            <ShoppingCart className="h-7 w-7" />
          </div>
          <h1 className="mt-4 text-2xl font-bold text-slate-900">POS Pro</h1>
          <p className="text-sm text-slate-500">
            Sistema de Punto de Venta
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-card">
          <h2 className="text-lg font-semibold text-slate-800">
            Iniciar sesión
          </h2>
          <p className="mb-4 text-sm text-slate-500">
            Accede a tu panel de control
          </p>

          {error && (
            <Alert variant="error" className="mb-4">
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
            <Input
              label="Correo electrónico"
              type="email"
              autoComplete="email"
              placeholder="tu@correo.com"
              error={errors.username?.message}
              {...register("username")}
            />

            <div className="flex flex-col gap-1.5">
              <label
                htmlFor="password"
                className="text-sm font-medium text-slate-700"
              >
                Contraseña
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  placeholder="••••••••"
                  className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 pr-10 text-sm text-slate-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
                  {...register("password")}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600"
                  aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>
              {errors.password?.message && (
                <p className="text-xs text-red-600">{errors.password.message}</p>
              )}
            </div>

            <Button
              type="submit"
              className="w-full"
              size="lg"
              loading={loading}
            >
              {loading ? "Ingresando…" : "Ingresar"}
            </Button>
          </form>
        </div>

        <p className="mt-4 text-center text-xs text-slate-400">
          Acceso seguro. Tu sesión se valida en cada operación.
        </p>
      </div>
    </div>
  )
}
