import { useMemo, useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Search, Building2, X, Check } from "lucide-react"

import { Button, Input, Modal } from "@/components/ui"
import { listSuppliers } from "@/services/suppliers.service"

interface SupplierPickerProps {
  value?: string | null
  onChange: (supplierId: string | null) => void
}

/**
 * Selector de proveedor profesional.
 * Muestra solo el proveedor seleccionado y un botón que abre un modal
 * con búsqueda por nombre y tabla seleccionable / cancelable.
 */
export function SupplierPicker({ value, onChange }: SupplierPickerProps) {
  const [open, setOpen] = useState(false)
  const [term, setTerm] = useState("")
  const [pending, setPending] = useState<string | null>(null)

  const suppliersQ = useQuery({
    queryKey: ["suppliers"],
    queryFn: listSuppliers,
  })

  const suppliers = useMemo(() => {
    const list = suppliersQ.data ?? []
    if (!term.trim()) return list
    const q = term.trim().toLowerCase()
    return list.filter(
      (s) =>
        s.name.toLowerCase().includes(q) ||
        (s.contact_name ?? "").toLowerCase().includes(q),
    )
  }, [suppliersQ.data, term])

  const selected = suppliersQ.data?.find((s) => s.id === value) ?? null

  const openModal = () => {
    setTerm("")
    setPending(value ?? null)
    setOpen(true)
  }

  const confirm = () => {
    onChange(pending)
    setOpen(false)
  }

  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-sm font-medium text-slate-700">Proveedor</label>
      <div className="flex items-center gap-2">
        <div className="flex h-10 flex-1 items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 text-sm shadow-sm">
          {selected ? (
            <>
              <Building2 className="h-4 w-4 shrink-0 text-brand-600" />
              <span className="truncate text-slate-800">{selected.name}</span>
            </>
          ) : (
            <span className="text-slate-400">Sin proveedor asignado</span>
          )}
          {value && (
            <button
              type="button"
              onClick={() => onChange(null)}
              className="ml-auto flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-red-600"
              title="Quitar proveedor"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        <Button type="button" variant="outline" onClick={openModal} disabled={suppliersQ.isLoading}>
          <Search className="h-4 w-4" /> Seleccionar
        </Button>
      </div>

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        size="xl"
        title="Seleccionar proveedor"
        description="Busca por nombre o contacto del proveedor."
        footer={
          <>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={confirm} disabled={!pending}>
              Seleccionar proveedor
            </Button>
          </>
        }
      >
        <div className="mb-3">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <Input
              className="pl-9"
              placeholder="Buscar proveedor por nombre o contacto..."
              value={term}
              onChange={(e) => setTerm(e.target.value)}
              autoFocus
            />
          </div>
        </div>

        <div className="max-h-[50vh] overflow-auto rounded-lg border border-slate-200">
          <table className="min-w-full divide-y divide-slate-100 text-sm">
            <thead className="bg-slate-50">
              <tr className="text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                <th className="px-4 py-2.5">Proveedor</th>
                <th className="hidden px-4 py-2.5 sm:table-cell">Contacto</th>
                <th className="hidden px-4 py-2.5 lg:table-cell">Teléfono</th>
                <th className="px-4 py-2.5 text-right">Seleccionar</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50 bg-white">
              {suppliers.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-slate-500">
                    {suppliersQ.isLoading
                      ? "Cargando proveedores..."
                      : "No se encontraron proveedores."}
                  </td>
                </tr>
              ) : (
                suppliers.map((s) => {
                  const isSel = pending === s.id
                  return (
                    <tr
                      key={s.id}
                      onClick={() => setPending(s.id)}
                      className={`cursor-pointer hover:bg-brand-50/50 ${isSel ? "bg-brand-50" : ""}`}
                    >
                      <td className="px-4 py-2.5">
                        <span className="flex items-center gap-2 font-medium text-slate-800">
                          <Building2 className="h-4 w-4 text-slate-400" />
                          {s.name}
                        </span>
                      </td>
                      <td className="hidden px-4 py-2.5 text-slate-600 sm:table-cell">
                        {s.contact_name || "—"}
                      </td>
                      <td className="hidden px-4 py-2.5 tabular-nums text-slate-600 lg:table-cell">
                        {s.phone || "—"}
                      </td>
                      <td className="px-4 py-2.5 text-right">
                        <span
                          className={`inline-flex h-5 w-5 items-center justify-center rounded-full border ${
                            isSel
                              ? "border-brand-600 bg-brand-600 text-white"
                              : "border-slate-300"
                          }`}
                        >
                          {isSel && <Check className="h-3.5 w-3.5" />}
                        </span>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </Modal>
    </div>
  )
}
