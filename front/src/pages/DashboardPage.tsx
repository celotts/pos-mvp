import {
  ArrowDownToLine,
  Banknote,
  Boxes,
  ShoppingCart,
  Sparkles,
} from 'lucide-react'

import { useAuth } from '../auth/AuthContext'
import { Alert } from '../components/ui/Alert'
import { Card } from '../components/ui/Card'
import { PageHeader } from '../components/ui/brand'

const STATS = [
  {
    icon: ShoppingCart,
    label: 'Ventas hoy',
    value: '—',
    tone: 'bg-brand-50 text-brand-700',
  },
  {
    icon: ArrowDownToLine,
    label: 'Compras este mes',
    value: '—',
    tone: 'bg-emerald-50 text-emerald-700',
  },
  {
    icon: Boxes,
    label: 'Productos en catálogo',
    value: '—',
    tone: 'bg-violet-50 text-violet-700',
  },
  {
    icon: Banknote,
    label: 'Ingresos (30 días)',
    value: '—',
    tone: 'bg-amber-50 text-amber-700',
  },
]

export function DashboardPage() {
  const { user } = useAuth()
  const firstName = user?.full_name?.split(' ')[0] ?? ''

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Hola, ${firstName} 👋`}
        subtitle="Resumen general de tu punto de venta. Conecta el resto de módulos para ver datos reales."
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {STATS.map(({ icon: Icon, label, value, tone }) => (
          <Card key={label}>
            <div className="flex items-center gap-4">
              <span
                className={`flex h-11 w-11 items-center justify-center rounded-xl ${tone}`}
              >
                <Icon className="h-5 w-5" />
              </span>
              <div className="min-w-0">
                <p className="truncate text-xs font-medium text-slate-500">{label}</p>
                <p className="text-xl font-bold text-slate-900">{value}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Alert kind="info" title="Próximos módulos">
        Desde el menú lateral puedes navegar por catálogo, ventas, compras,
        inventario y analítica comercial. Cada sección se muestra según tu rol (
        {user?.role_name ?? 'sin rol'}).
      </Alert>

      <Card
        header={
          <div className="flex items-center gap-2">
            <Sparkles className="h-4.5 w-4.5 text-brand-600" />
            <p className="font-semibold text-slate-900">Bienvenido a tu panel</p>
          </div>
        }
      >
        <p className="text-sm text-slate-600">
          Tu rol define qué opciones ves en el menú y a qué formularios tienes
          acceso. Si algo no aparece, contacta al administrador.
        </p>
      </Card>
    </div>
  )
}