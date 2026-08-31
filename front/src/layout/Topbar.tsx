import { LogOut, Menu, ShieldCheck } from 'lucide-react'

import { useAuth } from '../auth/AuthContext'
import { Button } from '../components/ui/Button'

export function Topbar({ onOpenSidebar }: { onOpenSidebar: () => void }) {
  const { user, signOut } = useAuth()

  return (
    <header className="flex h-16 shrink-0 items-center gap-3 border-b border-slate-200 bg-white px-4 sm:px-6">
      <button
        type="button"
        onClick={onOpenSidebar}
        className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden"
        aria-label="Abrir menú"
      >
        <Menu className="h-5 w-5" />
      </button>

      <div className="ml-auto flex items-center gap-3">
        {user ? (
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-100 text-sm font-bold text-brand-700">
              {user.full_name
                .split(' ')
                .map((part) => part[0])
                .slice(0, 2)
                .join('')
                .toUpperCase()}
            </div>
            <div className="hidden text-sm sm:block">
              <p className="font-semibold leading-tight text-slate-900">
                {user.full_name}
              </p>
              <p className="flex items-center gap-1 text-xs text-slate-500">
                <ShieldCheck className="h-3.5 w-3.5" />
                {user.role_name}
              </p>
            </div>
          </div>
        ) : null}

        <Button
          type="button"
          variant="ghost"
          onClick={signOut}
          className="text-slate-500"
          aria-label="Cerrar sesión"
        >
          <LogOut className="h-4.5 w-4.5" />
          <span className="hidden sm:inline">Salir</span>
        </Button>
      </div>
    </header>
  )
}