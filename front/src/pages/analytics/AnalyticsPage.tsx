import { useQuery } from "@tanstack/react-query"
import {
  LineChart,
  PackageSearch,
  TrendingUp,
  ListChecks,
} from "lucide-react"

import { Card, CardContent, PageHeader, Alert, Badge } from "@/components/ui"
import { listBundles, getStockoutRisk } from "@/services/analytics.service"
import { formatCurrency } from "@/lib/utils"
import type { StockoutRiskItem } from "@/types"

function riskBadge(risk: StockoutRiskItem["risk"]) {
  switch (risk) {
    case "OUT_OF_STOCK":
      return <Badge variant="danger">Sin stock</Badge>
    case "CRITICAL":
      return <Badge variant="danger">Crítico</Badge>
    case "WARNING":
      return <Badge variant="warning">Advertencia</Badge>
    case "OK":
      return <Badge variant="success">Ok</Badge>
    default:
      return <Badge variant="outline">Sin ventas</Badge>
  }
}

export function AnalyticsPage() {
  const bundlesQ = useQuery({ queryKey: ["bundles"], queryFn: () => listBundles() })
  const stockoutQ = useQuery({
    queryKey: ["stockout-risk"],
    queryFn: () => getStockoutRisk(),
  })

  const bundles = bundlesQ.data ?? []
  const stock = stockoutQ.data?.items ?? []

  return (
    <div className="space-y-6">
      <PageHeader
        title="Analítica"
        description="Recomendaciones y prevención de desabasto"
      />

      {bundlesQ.isError && (
        <Alert variant="error">{bundlesQ.error.message}</Alert>
      )}
      {stockoutQ.isError && (
        <Alert variant="error">{stockoutQ.error.message}</Alert>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardContent className="p-5">
            <div className="mb-4 flex items-center gap-2">
              <ListChecks className="h-5 w-5 text-brand-600" />
              <h3 className="font-semibold text-slate-800">
                Productos que se compran juntos
              </h3>
            </div>
            {bundlesQ.isLoading ? (
              <p className="text-sm text-slate-500">Cargando…</p>
            ) : bundles.length === 0 ? (
              <p className="text-sm text-slate-400">Sin suficientes datos de ventas.</p>
            ) : (
              <ul className="divide-y divide-slate-100">
                {bundles.slice(0, 8).map((b, i) => (
                  <li
                    key={`${b.product_a}-${b.product_b}`}
                    className="flex items-center justify-between py-2.5 text-sm"
                  >
                    <div className="min-w-0">
                      <p className="truncate font-medium text-slate-800">
                        <span className="mr-1 text-slate-400">{i + 1}.</span>
                        {b.product_a}
                        <span className="mx-1 text-slate-400">+</span>
                        {b.product_b}
                      </p>
                      <p className="text-xs text-slate-500">
                        {b.transactions} ventas
                      </p>
                    </div>
                    <Badge variant="info">
                      lift {(Number(b.lift) || 0).toFixed(2)}
                    </Badge>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <div className="mb-4 flex items-center gap-2">
              <PackageSearch className="h-5 w-5 text-brand-600" />
              <h3 className="font-semibold text-slate-800">
                Riesgo de quedarse sin stock
              </h3>
            </div>
            {stockoutQ.isLoading ? (
              <p className="text-sm text-slate-500">Cargando…</p>
            ) : stock.length === 0 ? (
              <p className="text-sm text-slate-400">
                No hay productos con riesgo de desabasto.
              </p>
            ) : (
              <ul className="max-h-96 divide-y divide-slate-100 overflow-y-auto">
                {stock.map((s) => (
                  <li
                    key={s.product_id}
                    className="flex items-center justify-between py-2.5 text-sm"
                  >
                    <div className="min-w-0">
                      <p className="truncate font-medium text-slate-800">
                        {s.product_name}
                      </p>
                      <p className="text-xs text-slate-500">
                        {s.stock_quantity} uds · demanda {s.avg_daily_demand}/día ·
                        resto {s.days_of_stock_left} días
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      {riskBadge(s.risk)}
                      <span className="text-xs font-medium text-slate-600">
                        {formatCurrency(s.recommended_quantity, "MXN")}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="p-5">
          <div className="mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-brand-600" />
            <h3 className="font-semibold text-slate-800">
              Recomendaciones de venta cruzada
            </h3>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <LineChart className="h-4 w-4" />
            La analítica de venta cruzada está disponible en detalle por producto.
          </div>
        </CardContent>
      </Card>
    </div>
  )
}