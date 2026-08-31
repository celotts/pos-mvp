import { ShieldX, Home } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Button } from '../components/ui/Button'

export function ForbiddenPage() {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center text-center">
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-rose-50">
        <ShieldX className="h-8 w-8 text-rose-600" />
      </div>
      <h1 className="text-2xl font-bold text-slate-900">Acceso denegado</h1>
      <p className="mt-2 max-w-md text-sm text-slate-600">
        Tu rol no tiene permisos para ver esta sección. Si crees que es un error,
        contacta al administrador del sistema.
      </p>
      <Link to="/dashboard">
        <Button className="mt-6">
          <Home className="h-4 w-4" />
          Volver al inicio
        </Button>
      </Link>
    </div>
  )
}