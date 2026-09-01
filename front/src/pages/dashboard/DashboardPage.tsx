import { useQuery } from "@tanstack/react-query"
import {
  DollarSign,
  ShoppingBag,
  Package,
  Users,
  TrendingUp,
} from "lucide-react"

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Spinner,
  Alert,
} from "@/components/ui"
import { listSales } from "@/services/sales.service"
import { listProducts } from "@/services/product.service"
import { listCustomers } from "@/services/customers.service"
import { listSuppliers } from "@/services/suppliers.service"
import { formatCurrency, formatDate } from "@/lib/utils"

function StatCard({
  title,
  value,
  icon: Icon,
  hint,
}: {
  title: string
  value: string
  icon: React.ComponentType<{ className?: string }>
  hint?: string
}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 p-5">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand-50 text-brand-600">
          <Icon className="h-6 w-6" />
        </div>
        <div className="min-w-0">
          <p className="truncate text-sm text-slate-500">{title}</p>
          <p className="text-2xl font-bold text-slate-900">{value}</p>
          {hint && <p className="text-xs text-slate-400">{hint}</p>}
        </div>
      </CardContent>
    </Card>
  )
}

export function DashboardPage() {
  const salesQ = useQuery({ queryKey: ["sales"], queryFn: listSales })
  const productsQ = useQuery({ queryKey: ["products"], queryFn: listProducts })
  const customersQ = useQuery({
    queryKey: ["customers"],
    queryFn: listCustomers,
  })
  const suppliersQ = useQuery({
    queryKey: ["suppliers"],
    queryFn: listSuppliers,
  })

  const loading = salesQ.isLoading || productsQ.isLoading

  const sales = salesQ.data ?? []
  const totalRevenue = sales.reduce(
    (acc, s) => acc + Number(s.total_amount || 0),
    0,
  )
  const recentSales = [...sales]
    .sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
    )
    .slice(0, 5)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          Dashboard
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Resumen general del negocio
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center py-16">
          <Spinner size="lg" />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              title="Ventas totales"
              value={formatCurrency(totalRevenue)}
              icon={DollarSign}
              hint={`${sales.length} ventas registradas`}
            />
            <StatCard
              title="Tickets"
              value={String(sales.length)}
              icon={ShoppingBag}
              hint="Ventas totales"
            />
            <StatCard
              title="Productos"
              value={String(productsQ.data?.length ?? 0)}
              icon={Package}
              hint="En catálogo"
            />
            <StatCard
              title="Clientes"
              value={String(customersQ.data?.length ?? 0)}
              icon={Users}
              hint={`${suppliersQ.data?.length ?? 0} proveedores`}
            />
          </div>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-brand-600" />
                Últimas ventas
              </CardTitle>
            </CardHeader>
            <CardContent>
              {recentSales.length === 0 ? (
                <Alert variant="info">
                  Aún no hay ventas registradas. Comienza vendiendo desde el
                  módulo de Punto de Venta.
                </Alert>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-slate-100 text-sm">
                    <thead>
                      <tr className="text-left text-xs font-semibold text-slate-500">
                        <th className="px-4 py-2">Fecha</th>
                        <th className="px-4 py-2">ID</th>
                        <th className="px-4 py-2 text-right">Total</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                      {recentSales.map((s) => (
                        <tr key={s.id} className="hover:bg-slate-50">
                          <td className="px-4 py-2.5">
                            {formatDate(s.created_at)}
                          </td>
                          <td className="px-4 py-2.5 font-mono text-xs">
                            {s.id.slice(0, 8)}
                          </td>
                          <td className="px-4 py-2.5 text-right font-semibold">
                            {formatCurrency(s.total_amount)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
