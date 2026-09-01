import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { Plus, Trash2, Coins } from "lucide-react"

import {
  Button,
  Modal,
  PageHeader,
  Alert,
  DataTable,
  type Column,
} from "@/components/ui"
import { listPurchases, registerPurchase } from "@/services/purchases.service"
import { listProducts } from "@/services/product.service"
import { listSuppliers } from "@/services/suppliers.service"
import { useAuthStore } from "@/store/authStore"
import { formatCurrency, formatDate } from "@/lib/utils"
import { getErrorMessage } from "@/lib/api"
import type { Purchase } from "@/types"

interface LineItem {
  product_id: string
  quantity: number
  key: string
}

export function PurchasesPage() {
  const queryClient = useQueryClient()
  const canCreate = useAuthStore((s) => s.hasPermission("purchase:create"))

  const [open, setOpen] = useState(false)
  const [supplierId, setSupplierId] = useState("")
  const [items, setItems] = useState<LineItem[]>([])

  const purchasesQ = useQuery({
    queryKey: ["purchases"],
    queryFn: listPurchases,
  })
  const productsQ = useQuery({ queryKey: ["products"], queryFn: listProducts })
  const suppliersQ = useQuery({
    queryKey: ["suppliers"],
    queryFn: listSuppliers,
  })

  const products = productsQ.data ?? []
  const suppliers = suppliersQ.data ?? []

  const addItem = () => {
    const firstProduct = products[0]
    setItems((prev) => [
      ...prev,
      {
        product_id: firstProduct?.id ?? "",
        quantity: 1,
        key: crypto.randomUUID(),
      },
    ])
  }

  const updateItem = (key: string, patch: Partial<LineItem>) => {
    setItems((prev) =>
      prev.map((it) => (it.key === key ? { ...it, ...patch } : it)),
    )
  }

  const removeItem = (key: string) =>
    setItems((prev) => prev.filter((it) => it.key !== key))

  const submit = useMutation({
    mutationFn: async () => {
      const payloadItems = items
        .filter((it) => it.product_id && it.quantity >= 1)
        .map((it) => ({ product_id: it.product_id, quantity: it.quantity }))
      if (!supplierId) throw new Error("Selecciona un proveedor")
      if (!payloadItems.length) throw new Error("Agrega al menos un producto")
      return registerPurchase({ supplier_id: supplierId, items: payloadItems })
    },
    onSuccess: () => {
      toast.success("Compra registrada correctamente")
      setOpen(false)
      setItems([])
      setSupplierId("")
      queryClient.invalidateQueries({ queryKey: ["purchases"] })
      queryClient.invalidateQueries({ queryKey: ["stockout-risk"] })
      queryClient.invalidateQueries({ queryKey: ["products"] })
    },
    onError: (err) =>
      toast.error(
        getErrorMessage(err, "No se pudo registrar la compra"),
      ),
  })

  const columns: Column<Purchase>[] = [
    {
      key: "date",
      header: "Fecha",
      render: (p) => formatDate(p.purchase_date),
    },
    {
      key: "supplier",
      header: "Proveedor",
      render: (p) => {
        const s = suppliers.find((x) => x.id === p.supplier_id)
        return <span>{s?.name ?? "—"}</span>
      },
    },
    {
      key: "items",
      header: "Artículos",
      hiddenOnMobile: true,
      render: (p) => <span>{p.items?.length ?? 0}</span>,
    },
    {
      key: "total",
      header: "Total",
      className: "text-right",
      render: (p) => (
        <span className="font-semibold">{formatCurrency(p.total_amount)}</span>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Compras"
        description="Registra y consulta las compras a proveedores"
      >
        {canCreate && (
          <Button onClick={() => { setItems([]); setSupplierId(""); setOpen(true) }}>
            <Plus className="h-4 w-4" /> Nueva compra
          </Button>
        )}
      </PageHeader>

      {purchasesQ.isError && <Alert variant="error">{purchasesQ.error.message}</Alert>}

      <DataTable
        columns={columns}
        data={purchasesQ.data ?? []}
        loading={purchasesQ.isLoading}
        keyExtractor={(p) => p.id}
        emptyTitle="Sin compras"
        emptyDescription="Registra compras a proveedores para reponer inventario."
        emptyIcon={Coins}
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="Nueva compra"
        size="xl"
        footer={
          <>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button
              onClick={() => submit.mutate()}
              loading={submit.isPending}
              disabled={!items.length || !supplierId}
            >
              Registrar compra
            </Button>
          </>
        }
      >
        <div className="space-y-5">
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-slate-700">Proveedor</label>
            <select
              value={supplierId}
              onChange={(e) => setSupplierId(e.target.value)}
              className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="">Selecciona un proveedor</option>
              {suppliers.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-700">Productos</h3>
            <Button variant="outline" size="sm" onClick={addItem}>
              <Plus className="h-4 w-4" /> Agregar
            </Button>
          </div>

          {items.length === 0 ? (
            <Alert variant="info">Agrega productos a esta compra.</Alert>
          ) : (
            <div className="space-y-2">
              {items.map((it) => (
                <div
                  key={it.key}
                  className="flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 p-2"
                >
                  <select
                    value={it.product_id}
                    onChange={(e) => updateItem(it.key, { product_id: e.target.value })}
                    className="h-9 flex-1 rounded-lg border border-slate-300 bg-white px-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  >
                    <option value="">Selecciona producto</option>
                    {products.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                  <input
                    type="number"
                    min={1}
                    value={it.quantity}
                    onChange={(e) =>
                      updateItem(it.key, { quantity: Number(e.target.value) })
                    }
                    className="h-9 w-20 rounded-lg border border-slate-300 bg-white px-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-red-600 hover:bg-red-50"
                    onClick={() => removeItem(it.key)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}

          {submit.isError && (
            <Alert variant="error">{getErrorMessage(submit.error)}</Alert>
          )}
        </div>
      </Modal>
    </div>
  )
}
