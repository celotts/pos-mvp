import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { toast } from "sonner"
import { Plus, Pencil, Trash2, Package } from "lucide-react"

import {
  Button,
  Input,
  Modal,
  PageHeader,
  DataTable,
  Alert,
  type Column,
} from "@/components/ui"
import {
  listProducts,
  createProduct,
  updateProduct,
  deleteProduct,
} from "@/services/product.service"
import { listSuppliers } from "@/services/suppliers.service"
import { SupplierPicker } from "@/components/suppliers/SupplierPicker"
import { useAuthStore } from "@/store/authStore"
import { formatCurrency } from "@/lib/utils"
import { getErrorMessage } from "@/lib/api"
import type { Product } from "@/types"

const productSchema = z.object({
  name: z.string().min(1, "El nombre es obligatorio"),
  description: z.string().optional(),
  price: z.coerce.number().min(0, "El precio debe ser mayor o igual a 0"),
  sku: z.string().min(1, "El SKU es obligatorio"),
  supplier_id: z.string().optional(),
})

type ProductForm = z.infer<typeof productSchema>

export function ProductsPage() {
  const queryClient = useQueryClient()
  const canCreate = useAuthStore((s) => s.hasPermission("product:create"))
  const canUpdate = useAuthStore((s) => s.hasPermission("product:update"))
  const canDelete = useAuthStore((s) => s.hasPermission("product:delete"))

  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Product | null>(null)

  const productsQ = useQuery({ queryKey: ["products"], queryFn: listProducts })
  const suppliersQ = useQuery({
    queryKey: ["suppliers"],
    queryFn: listSuppliers,
  })

  const suppliers = suppliersQ.data ?? []

  const form = useForm<ProductForm>({
    resolver: zodResolver(productSchema),
    defaultValues: { price: 0, description: "", supplier_id: "" },
  })

  const openCreate = () => {
    setEditing(null)
    form.reset({ name: "", description: "", price: 0, sku: "", supplier_id: "" })
    setOpen(true)
  }

  const openEdit = (p: Product) => {
    setEditing(p)
    form.reset({
      name: p.name,
      description: p.description ?? "",
      price: Number(p.price),
      sku: p.sku,
      supplier_id: p.supplier_id ?? "",
    })
    setOpen(true)
  }

  const saveMutation = useMutation({
    mutationFn: (values: ProductForm) =>
      editing
        ? updateProduct(editing.id, {
            ...values,
            supplier_id: values.supplier_id || null,
          })
        : createProduct({
            ...values,
            supplier_id: values.supplier_id || null,
          }),
    onSuccess: (saved) => {
      toast.success(editing ? "Producto actualizado" : "Producto creado")
      setOpen(false)
      queryClient.invalidateQueries({ queryKey: ["products"] })
      void saved
    },
    onError: (err) =>
      toast.error(getErrorMessage(err, "No se pudo guardar el producto")),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteProduct,
    onSuccess: () => {
      toast.success("Producto eliminado")
      queryClient.invalidateQueries({ queryKey: ["products"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const onSubmit = form.handleSubmit((values) => saveMutation.mutate(values))

  // Éxito del form sin getErrorMessageFallback real
  const columns: Column<Product>[] = [
    { key: "name", header: "Producto", render: (p) => (
      <div>
        <p className="font-medium text-slate-800">{p.name}</p>
        {p.sku && <p className="text-xs text-slate-400">{p.sku}</p>}
      </div>
    )},
    { key: "supplier", header: "Proveedor", hiddenOnMobile: true, render: (p) => {
      const s = suppliers.find((x) => x.id === p.supplier_id)
      return <span>{s?.name ?? "—"}</span>
    }},
    { key: "price", header: "Precio", className: "text-right", render: (p) => (
      <span className="font-semibold">{formatCurrency(p.price)}</span>
    )},
    { key: "actions", header: "", className: "text-right", render: (p) => (
      <div className="flex justify-end gap-1">
        {canUpdate && (
          <Button variant="ghost" size="icon" onClick={() => openEdit(p)} title="Editar">
            <Pencil className="h-4 w-4" />
          </Button>
        )}
        {canDelete && (
          <Button
            variant="ghost"
            size="icon"
            className="text-red-600 hover:bg-red-50"
            onClick={() => {
              if (confirm(`¿Eliminar "${p.name}"?`)) deleteMutation.mutate(p.id)
            }}
            title="Eliminar"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        )}
      </div>
    )},
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Productos"
        description="Gestiona el catálogo de productos del negocio"
      >
        {canCreate && (
          <Button onClick={openCreate}>
            <Plus className="h-4 w-4" /> Nuevo producto
          </Button>
        )}
      </PageHeader>

      {productsQ.isError && (
        <Alert variant="error">{productsQ.error.message}</Alert>
      )}

      <DataTable
        columns={columns}
        data={productsQ.data ?? []}
        loading={productsQ.isLoading}
        keyExtractor={(p) => p.id}
        emptyTitle="Sin productos"
        emptyDescription="Crea tu primer producto para comenzar a vender."
        emptyIcon={Package}
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={editing ? "Editar producto" : "Nuevo producto"}
        size="lg"
        footer={
          <>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button
              onClick={onSubmit}
              loading={saveMutation.isPending}
            >
              {editing ? "Guardar cambios" : "Crear producto"}
            </Button>
          </>
        }
      >
        <form id="product-form" onSubmit={onSubmit} className="space-y-4" noValidate>
          <Input
            label="Nombre"
            placeholder="Nombre del producto"
            error={form.formState.errors.name?.message}
            {...form.register("name")}
          />
          <Input
            label="Descripción"
            placeholder="Descripción opcional"
            error={form.formState.errors.description?.message}
            {...form.register("description")}
          />
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Input
              label="Precio"
              type="number"
              step="0.01"
              min="0"
              error={form.formState.errors.price?.message}
              {...form.register("price")}
            />
            <Input
              label="SKU"
              placeholder="Código SKU"
              error={form.formState.errors.sku?.message}
              {...form.register("sku")}
            />
          </div>
          <SupplierPicker
            value={form.watch("supplier_id")}
            onChange={(id) => form.setValue("supplier_id", id ?? "")}
          />
          {saveMutation.isError && (
            <Alert variant="error">
              {getErrorMessage(saveMutation.error)}
            </Alert>
          )}
        </form>
      </Modal>
    </div>
  )
}
