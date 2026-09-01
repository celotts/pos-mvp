import { useMemo, useRef, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { Plus, Trash2, CheckCircle2, MonitorX, Monitor } from "lucide-react"

import {
  Button,
  Card,
  CardContent,
  PageHeader,
  Alert,
  Input,
} from "@/components/ui"
import { listStores } from "@/services/stores.service"
import { listTerminals, createTerminal } from "@/services/pos.service"
import { listProducts } from "@/services/product.service"
import { listCustomers } from "@/services/customers.service"
import { registerSale } from "@/services/sales.service"
import { useAuthStore } from "@/store/authStore"
import { formatCurrency } from "@/lib/utils"
import { getErrorMessage } from "@/lib/api"

interface Line {
  product_id: string
  quantity: number
  key: string
}

export function PosPage() {
  const queryClient = useQueryClient()
  const canRegister = useAuthStore((s) => s.hasPermission("sale:create"))
  const canCreateTerminal = useAuthStore((s) =>
    s.hasPermission("pos_terminal:create"),
  )

  const [storeId, setStoreId] = useState("")
  const [terminalId, setTerminalId] = useState("")
  const [customerId, setCustomerId] = useState("")
  const [lines, setLines] = useState<Line[]>([])
  const [showTerminalForm, setShowTerminalForm] = useState(false)
  const [termName, setTermName] = useState("")
  const [termLocation, setTermLocation] = useState("")
  const termInputRef = useRef<HTMLInputElement>(null)

  const storesQ = useQuery({ queryKey: ["stores"], queryFn: listStores })
  const terminalsQ = useQuery({
    queryKey: ["terminals"],
    queryFn: listTerminals,
  })
  const productsQ = useQuery({ queryKey: ["products"], queryFn: listProducts })
  const customersQ = useQuery({
    queryKey: ["customers"],
    queryFn: listCustomers,
  })

  const stores = storesQ.data ?? []
  const terminals = terminalsQ.data ?? []
  const products = productsQ.data ?? []
  const customers = customersQ.data ?? []

  const productsById = useMemo(
    () => new Map(products.map((p) => [p.id, p])),
    [products],
  )

  const addLine = () => {
    const first = products[0]
    setLines((prev) => [
      ...prev,
      { product_id: first?.id ?? "", quantity: 1, key: crypto.randomUUID() },
    ])
  }

  const updateLine = (key: string, patch: Partial<Line>) =>
    setLines((prev) => prev.map((l) => (l.key === key ? { ...l, ...patch } : l)))

  const removeLine = (key: string) =>
    setLines((prev) => prev.filter((l) => l.key !== key))

  const subtotal = lines.reduce((acc, l) => {
    const p = productsById.get(l.product_id)
    return acc + (p ? Number(p.price) * l.quantity : 0)
  }, 0)

  const createTerm = useMutation({
    mutationFn: () => {
      if (!termName.trim()) throw new Error("Indica un nombre para el terminal")
      return createTerminal({
        name: termName.trim(),
        location: termLocation.trim() || null,
      })
    },
    onSuccess: (term) => {
      toast.success("Terminal POS creado")
      setTerminalId(term.id)
      setShowTerminalForm(false)
      setTermName("")
      setTermLocation("")
      queryClient.invalidateQueries({ queryKey: ["terminals"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const sale = useMutation({
    mutationFn: async () => {
      if (!storeId) throw new Error("Selecciona una tienda")
      if (!terminalId) throw new Error("Selecciona o crea un terminal POS")
      const validItems = lines.filter((l) => l.product_id && l.quantity >= 1)
      if (!validItems.length) throw new Error("Agrega al menos un producto")
      return registerSale({
        store_id: storeId,
        pos_terminal_id: terminalId,
        customer_id: customerId || null,
        items: validItems.map((l) => ({
          product_id: l.product_id,
          quantity: l.quantity,
        })),
      })
    },
    onSuccess: () => {
      toast.success("Venta registrada correctamente", {
        description: `Total: ${formatCurrency(subtotal)}`,
      })
      setLines([])
      setCustomerId("")
      queryClient.invalidateQueries({ queryKey: ["sales"] })
      queryClient.invalidateQueries({ queryKey: ["stockout-risk"] })
    },
    onError: (err) =>
      toast.error(getErrorMessage(err, "No se pudo registrar la venta")),
  })

  return (
    <div className="space-y-6">
      <PageHeader
        title="Punto de Venta"
        description="Registra ventas de forma rápida"
      />

      {!canRegister && (
        <Alert variant="warning">
          No tienes permiso para registrar ventas.
        </Alert>
      )}

      <Card>
        <CardContent className="space-y-5 p-5">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-slate-700">Tienda</label>
              <select
                value={storeId}
                onChange={(e) => setStoreId(e.target.value)}
                className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="">Selecciona tienda</option>
                {stores.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-slate-700">Terminal POS</label>
              <select
                value={terminalId}
                onChange={(e) => setTerminalId(e.target.value)}
                className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="">Selecciona terminal</option>
                {terminals.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name || "Terminal"}
                  </option>
                ))}
              </select>
              {canCreateTerminal && (
                <button
                  onClick={() => {
                    setShowTerminalForm(true)
                    setTimeout(() => termInputRef.current?.focus(), 50)
                  }}
                  className="flex items-center gap-1 text-xs font-medium text-brand-600 hover:underline"
                >
                  <Monitor className="h-3.5 w-3.5" /> ¿No tienes terminal? Crea uno
                </button>
              )}
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-slate-700">
                Cliente (opcional)
              </label>
              <select
                value={customerId}
                onChange={(e) => setCustomerId(e.target.value)}
                className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="">Consumidor final</option>
                {customers.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.full_name || c.email || c.id}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {showTerminalForm && (
            <div className="rounded-lg border border-brand-200 bg-brand-50 p-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
                <div className="flex-1">
                  <Input
                    ref={termInputRef}
                    label="Nombre del terminal"
                    placeholder="Ej. Caja 1"
                    value={termName}
                    onChange={(e) => setTermName(e.target.value)}
                  />
                </div>
                <div className="flex-1">
                  <Input
                    label="Ubicación (opcional)"
                    placeholder="Ej. Mostrador"
                    value={termLocation}
                    onChange={(e) => setTermLocation(e.target.value)}
                  />
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowTerminalForm(false)}
                  >
                    Cancelar
                  </Button>
                  <Button
                    onClick={() => createTerm.mutate()}
                    loading={createTerm.isPending}
                  >
                    Crear terminal
                  </Button>
                </div>
              </div>
              {createTerm.isError && (
                <Alert variant="error" className="mt-3">
                  {getErrorMessage(createTerm.error)}
                </Alert>
              )}
            </div>
          )}

          {!showTerminalForm && terminals.length === 0 && (
            <Alert variant="warning">
              <div className="flex items-center gap-2">
                <MonitorX className="h-5 w-5 shrink-0" />
                <div>
                  No hay terminales POS registrados, y para registrar una venta{" "}
                  <b>se requiere un terminal</b>.{" "}
                  {canCreateTerminal
                    ? "Crea uno con el enlace de arriba."
                    : "Pide a un administrador que cree un terminal."}
                </div>
              </div>
            </Alert>
          )}

          <div className="flex items-center justify-between border-t border-slate-100 pt-4">
            <h3 className="text-sm font-semibold text-slate-700">
              Artículos de la venta
            </h3>
            <Button variant="outline" size="sm" onClick={addLine} disabled={!canRegister}>
              <Plus className="h-4 w-4" /> Agregar
            </Button>
          </div>

          {lines.length === 0 ? (
            <Alert variant="info">
              Agrega productos para comenzar la venta.
            </Alert>
          ) : (
            <div className="space-y-2">
              {lines.map((l) => {
                const p = productsById.get(l.product_id)
                return (
                  <div
                    key={l.key}
                    className="flex flex-wrap items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 p-2 sm:flex-nowrap"
                  >
                    <select
                      value={l.product_id}
                      onChange={(e) => updateLine(l.key, { product_id: e.target.value })}
                      className="h-9 flex-1 rounded-lg border border-slate-300 bg-white px-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                    >
                      {products.map((pr) => (
                        <option key={pr.id} value={pr.id}>
                          {pr.name} · {formatCurrency(pr.price)}
                        </option>
                      ))}
                    </select>
                    <input
                      type="number"
                      min={1}
                      value={l.quantity}
                      onChange={(e) =>
                        updateLine(l.key, { quantity: Number(e.target.value) })
                      }
                      className="h-9 w-20 rounded-lg border border-slate-300 bg-white px-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                    />
                    <span className="w-28 text-right text-sm font-semibold text-slate-700">
                      {p ? formatCurrency(Number(p.price) * l.quantity) : "—"}
                    </span>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-red-600 hover:bg-red-50"
                      onClick={() => removeLine(l.key)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                )
              })}
            </div>
          )}

          <div className="flex flex-col items-end gap-3 border-t border-slate-100 pt-4">
            <div className="text-right">
              <p className="text-sm text-slate-500">
                Subtotal ({lines.length} artículos)
              </p>
              <p className="text-3xl font-bold text-slate-900">
                {formatCurrency(subtotal)}
              </p>
            </div>
            <Button
              size="lg"
              className="w-full sm:w-auto"
              loading={sale.isPending}
              disabled={!lines.length || !storeId || !terminalId || !canRegister}
              onClick={() => sale.mutate()}
            >
              <CheckCircle2 className="h-5 w-5" /> Registrar venta
            </Button>
            {sale.isError && (
              <Alert variant="error" className="w-full">
                {getErrorMessage(sale.error)}
              </Alert>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
