import { useMemo, useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Boxes, AlertTriangle } from "lucide-react"

import {
  PageHeader,
  DataTable,
  Badge,
  Alert,
  Card,
  CardContent,
  type Column,
} from "@/components/ui"
import { getStockoutRisk, type StockoutRiskItem } from "@/services/inventory.service"

const riskTone: Record<string, "danger" | "warning" | "success" | "default"> = {
  OUT_OF_STOCK: "danger",
  CRITICAL: "danger",
  WARNING: "warning",
  OK: "success",
  NO_SALES: "default",
}

const riskLabel: Record<string, string> = {
  OUT_OF_STOCK: "Agotado",
  CRITICAL: "Crítico",
  WARNING: "Advertencia",
  OK: "OK",
  NO_SALES: "Sin ventas",
}

export function InventoryPage() {
  const [minRisk, setMinRisk] = useState("")

  const stockoutQ = useQuery({
    queryKey: ["stockout-risk"],
    queryFn: getStockoutRisk,
  })

  const items = stockoutQ.data?.items ?? []

  const filtered = useMemo(
    () => (minRisk ? items.filter((i) => riskTone[i.risk] === minRisk) : items),
    [items, minRisk],
  )

  const criticalCount = items.filter((i) =>
    ["OUT_OF_STOCK", "CRITICAL"].includes(i.risk),
  ).length
  const warningCount = items.filter((i) => i.risk === "WARNING").length

  const columns: Column<StockoutRiskItem>[] = [
    {
      key: "product",
      header: "Producto",
      render: (i) => <span className="font-medium text-slate-800">{i.product_name}</span>,
    },
    {
      key: "stock",
      header: "Stock",
      render: (i) => (
        <span className={i.stock_quantity <= 0 ? "font-semibold text-red-600" : ""}>
          {i.stock_quantity}
        </span>
      ),
    },
    {
      key: "demand",
      header: "Demanda diaria",
      hiddenOnMobile: true,
      render: (i) => <span>{i.avg_daily_demand.toFixed(2)}</span>,
    },
    {
      key: "days",
      header: "Días de stock",
      hiddenOnMobile: true,
      render: (i) => (i.days_of_stock_left != null ? i.days_of_stock_left.toFixed(1) : "—"),
    },
    {
      key: "recommended",
      header: "Reposición sugerida",
      hiddenOnMobile: true,
      render: (i) => (i.recommended_quantity ? i.recommended_quantity : "—"),
    },
    {
      key: "risk",
      header: "Riesgo",
      render: (i) => <Badge variant={riskTone[i.risk]}>{riskLabel[i.risk]}</Badge>,
    },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Inventario"
        description="Niveles de stock y riesgo de desabasto"
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-50 text-brand-600">
              <Boxes className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Productos</p>
              <p className="text-2xl font-bold text-slate-900">{items.length}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-red-50 text-red-600">
              <AlertTriangle className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Críticos / agotados</p>
              <p className="text-2xl font-bold text-red-600">{criticalCount}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
              <Boxes className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm text-slate-500">En advertencia</p>
              <p className="text-2xl font-bold text-slate-900">{warningCount}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="flex items-center gap-3">
        <label className="text-sm font-medium text-slate-700">Filtrar por riesgo</label>
        <select
          value={minRisk}
          onChange={(e) => setMinRisk(e.target.value)}
          className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
        >
          <option value="">Todos</option>
          <option value="danger">Crítico / agotado</option>
          <option value="warning">Advertencia</option>
          <option value="success">OK</option>
        </select>
      </div>

      {stockoutQ.isError && (
        <Alert variant="error">{stockoutQ.error.message}</Alert>
      )}

      {stockoutQ.data && (
        <p className="text-xs text-slate-400">
          Horizonte de análisis: {stockoutQ.data.horizon_days} días · Tiempo de
          entrega: {stockoutQ.data.lead_time_days} días
        </p>
      )}

      <DataTable
        columns={columns}
        data={filtered}
        loading={stockoutQ.isLoading}
        keyExtractor={(i) => i.product_id}
        emptyTitle="Sin productos"
        emptyDescription="No hay productos para analizar el inventario."
        emptyIcon={Boxes}
      />
    </div>
  )
}
