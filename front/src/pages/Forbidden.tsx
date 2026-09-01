import { useNavigate } from "react-router-dom"
import { ShieldAlert } from "lucide-react"

import { Button } from "@/components/ui"

export function ForbiddenPage() {
  const navigate = useNavigate()
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100 text-red-600">
        <ShieldAlert className="h-8 w-8" />
      </div>
      <h1 className="text-2xl font-bold text-slate-900">Acceso denegado</h1>
      <p className="mt-2 max-w-md text-sm text-slate-500">
        No tienes los permisos necesarios para acceder a esta sección. Si crees
        que esto es un error, contacta a tu administrador.
      </p>
      <div className="mt-6 flex gap-3">
        <Button onClick={() => navigate("/")}>Ir al inicio</Button>
        <Button variant="outline" onClick={() => navigate(-1)}>
          Volver
        </Button>
      </div>
    </div>
  )
}
