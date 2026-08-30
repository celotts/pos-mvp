import { FileQuestion, Home } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Button } from '../components/ui/Button'

export function NotFoundPage() {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center text-center">
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100">
        <FileQuestion className="h-8 w-8 text-slate-500" />
      </div>
      <h1 className="text-2xl font-bold text-slate-900">Página no encontrada</h1>
      <p className="mt-2 max-w-md text-sm text-slate-600">
        La dirección que intentas abrir no existe o fue movida.
      </p>
      <Link to="/dashboard">
        <Button className="mt-6">
          <Home className="h-4 w-4" />
          Ir al inicio
        </Button>
      </Link>
    </div>
  )
}