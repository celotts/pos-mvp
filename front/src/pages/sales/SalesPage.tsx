import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { Undo2, Package, ReceiptText } from "lucide-react"

import {
  Button,
  Modal,
  PageHeader,
  Alert,
  Badge,
  DataTable,
  Spinner,
  type Column,
} from "@/components/ui"
import { listSales, returnSale } from "@/services/sales.service"
import { listProducts } from "@/services/product.service"
import { useAuthStore } from "@/store/authStore"
import { formatCurrency, formatDate } from "@/lib/utils"
import { getErrorMessage } from "@/lib/api"
import type { Sale, SaleStatus } from "@/types"

const STATUS_LABEL: Record<SaleStatus, string> = {
  PENDING: "Pendiente",
  COMPLETED: "Completada",
  CANCELLED: "Devuelta",
}

function StatusBadge({ status }: { status: SaleStatus }) {
  const variant =
    status === "COMPLETED"
      ? "success"
      : status === "CANCELLED"
        ? "danger"
        : "warning"
  return <Badge variant={variant}>{STATUS_LABEL[status]}</Badge>
}

export function SalesPage() {
  const queryClient = useQueryClient()
  const canCancel = useAuthStore((s) => s.hasPermission("sale:cancel"))

  const [detail, setDetail] = useState<Sale | null>(null)
  const [confirmId, setConfirmId] = useState<string | null>(null)

  const salesQ = useQuery({
    queryKey: ["sales"],
    queryFn: listSales,
  })
  const productsQ = useQuery({ queryKey: ["products"], queryFn: listProducts })

  const products = productsQ.data ?? []
  const productsById = new Map(products.map((p) => [p.id, p]))

  const returnMutation = useMutation({
    mutationFn: (id: string) => returnSale(id),
    onSuccess: (sale) => {
      toast.success("Venta devuelta", {
        description: `Se reintegró el stock de la venta ${formatCurrency(sale.total_amount)}.`,
      })
      setConfirmId(null)
      queryClient.invalidateQueries({ queryKey: ["sales"] })
      queryClient.invalidateQueries({ queryKey: ["stockout-risk"] })
    },
    onError: (err) =>
      toast.error(getErrorMessage(err, "No se pudo devolver la venta")),
  })

  const handleReturn = (sale: Sale) => {
    if (!canCancel) return
    setConfirmId(sale.id)
  }

  const columns: Column<Sale>[] = [
    {
      key: "date",
      header: "Fecha",
      render: (s) => formatDate(s.sale_date ?? s.created_at),
    },
    {
      key: "total",
      header: "Total",
      className: "text-right",
      render: (s) => (
        <span className="font-semibold">{formatCurrency(s.total_amount)}</span>
      ),
    },
    {
      key: "status",
      header: "Estado",
      render: (s) => <StatusBadge status={s.status} />,
    },
    {
      key: "items",
      header: "Artículos",
      hiddenOnMobile: true,
      render: (s) => (
        <span className="flex items-center gap-1.5">
          <Package className="h-4 w-4 text-slate-400" />
          {s.items?.length ?? 0}
        </span>
      ),
    },
    {
      key: "actions",
      header: "",
      headerClassName: "text-right",
      className: "text-right",
      render: (s) => (
        <div className="flex justify-end gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setDetail(s)}
          >
            Ver
          </Button>
          {canCancel && s.status !== "CANCELLED" && (
            <Button
              variant="ghost"
              size="sm"
              className="text-red-600 hover:bg-red-50"
              onClick={() => handleReturn(s)}
            >
              <Undo2 className="h-4 w-4" /> Devolver
            </Button>
          )}
        </div>
      ),
    },
  ]

  const detailSale = detail
  const detailProducts = detailSale?.items?.map((it) => {
    const p = productsById.get(it.product_id)
    return {
      ...it,
      name: p?.name ?? "Producto",
      subtotal: Number(it.price_at_sale ?? 0) * it.quantity,
    }
  })

  return (
    <div className="space-y-6">
      <PageHeader
        title="Ventas"
        description="Consulta el historial de ventas y gestiona devoluciones"
      />

      {salesQ.isError && <Alert variant="error">{salesQ.error.message}</Alert>}

      <DataTable
        columns={columns}
        data={salesQ.data ?? []}
        loading={salesQ.isLoading}
        keyExtractor={(s) => s.id}
        emptyTitle="Sin ventas"
        emptyDescription="Registra ventas desde el Punto de Venta."
        emptyIcon={ReceiptText}
      />

      <Modal
        open={!!detailSale}
        onClose={() => setDetail(null)}
        title="Detalle de la venta"
        size="lg"
        footer={
          <>
            <Button variant="outline" onClick={() => setDetail(null)}>
              Cerrar
            </Button>
            {canCancel && detailSale?.status !== "CANCELLED" && (
              <Button
                variant="danger"
                onClick={() => {
                  setConfirmId(detailSale?.id ?? "")
                  setDetail(null)
                }}
              >
                <Undo2 className="h-4 w-4" /> Devolver venta
              </Button>
            )}
          </>
        }
      >
        {detailSale ? (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <p className="text-sm text-slate-500">
                  Venta {detailSale.id.slice(0, 8)}
                </p>
                <p className="text-sm text-slate-500">
                  {formatDate(detailSale.sale_date ?? detailSale.created_at)}
                </p>
              </div>
              <StatusBadge status={detailSale.status} />
            </div>

            <div className="space-y-2">
              {detailProducts?.map((it) => (
                <div
                  key={it.product_id}
                  className="flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm"
                >
                  <span className="font-medium">{it.name}</span>
                  <span className="text-slate-500">
                    {it.quantity} × {formatCurrency(it.price_at_sale)}
                  </span>
                  <span className="font-semibold">
                    {formatCurrency(it.subtotal)}
                  </span>
                </div>
              ))}
            </div>

            <div className="flex items-center justify-between border-t border-slate-100 pt-3">
              <span className="text-sm font-medium text-slate-500">Total</span>
              <span className="text-2xl font-bold">
                {formatCurrency(detailSale.total_amount)}
              </span>
            </div>
          </div>
        ) : (
          <Spinner />
        )}
      </Modal>

      <Modal
        open={!!confirmId}
        onClose={() => setConfirmId(null)}
        title="Confirmar devolución"
        size="md"
        footer={
          <>
            <Button variant="outline" onClick={() => setConfirmId(null)}>
              Cancelar
            </Button>
            <Button
              variant="danger"
              loading={returnMutation.isPending}
              onClick={() => confirmId && returnMutation.mutate(confirmId)}
            >
              Confirmar devolución
            </Button>
          </>
        }
      >
        <Alert variant="warning">
          Vas a devolver (cancelar) esta venta completa. El stock de los
          productos vendidos se reintegrará al inventario.
        </Alert>
        {returnMutation.isError && (
          <Alert variant="error" className="mt-3">
            {getErrorMessage(returnMutation.error)}
          </Alert>
        )}
      </Modal>
    </div>
  )
}
