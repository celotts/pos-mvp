import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { toast } from "sonner"
import { Plus, Trash2, Pencil, Store } from "lucide-react"

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
  listStores,
  createStore,
  updateStore,
  deleteStore,
} from "@/services/stores.service"
import { useAuthStore } from "@/store/authStore"
import { getErrorMessage } from "@/lib/api"
import type { Store as StoreType } from "@/types"

const storeSchema = z.object({
  name: z.string().min(1, "El nombre es obligatorio"),
  address: z.string().optional(),
})

type StoreForm = z.infer<typeof storeSchema>

export function StoresPage() {
  const queryClient = useQueryClient()
  const canCreate = useAuthStore((s) => s.hasPermission("store:create"))
  const canDelete = useAuthStore((s) => s.hasPermission("store:delete"))

  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<StoreType | null>(null)

  const storesQ = useQuery({ queryKey: ["stores"], queryFn: listStores })

  const form = useForm<StoreForm>({
    resolver: zodResolver(storeSchema),
    defaultValues: { name: "", address: "" },
  })

  const openCreate = () => {
    setEditing(null)
    form.reset({ name: "", address: "" })
    setOpen(true)
  }

  const openEdit = (s: StoreType) => {
    setEditing(s)
    form.reset({ name: s.name, address: s.address ?? "" })
    setOpen(true)
  }

  const save = useMutation({
    mutationFn: (values: StoreForm) =>
      editing ? updateStore(editing.id, values) : createStore(values),
    onSuccess: () => {
      toast.success(editing ? "Tienda actualizada" : "Tienda creada")
      setOpen(false)
      queryClient.invalidateQueries({ queryKey: ["stores"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const remove = useMutation({
    mutationFn: deleteStore,
    onSuccess: () => {
      toast.success("Tienda eliminada")
      queryClient.invalidateQueries({ queryKey: ["stores"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const onSubmit = form.handleSubmit((v) => save.mutate(v))

  const columns: Column<StoreType>[] = [
    {
      key: "name",
      header: "Tienda",
      render: (s) => <span className="font-medium text-slate-800">{s.name}</span>,
    },
    { key: "address", header: "Dirección", hiddenOnMobile: true, render: (s) => <span>{s.address || "—"}</span> },
    {
      key: "actions",
      header: "",
      className: "text-right",
      render: (s) => (
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="icon" onClick={() => openEdit(s)} title="Editar">
            <Pencil className="h-4 w-4" />
          </Button>
          {canDelete && (
            <Button
              variant="ghost"
              size="icon"
              className="text-red-600 hover:bg-red-50"
              onClick={() => {
                if (confirm(`¿Eliminar la tienda "${s.name}"?`)) remove.mutate(s.id)
              }}
              title="Eliminar"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <PageHeader title="Tiendas" description="Gestiona tus tiendas / sucursales">
        {canCreate && (
          <Button onClick={openCreate}>
            <Plus className="h-4 w-4" /> Nueva tienda
          </Button>
        )}
      </PageHeader>

      {storesQ.isError && <Alert variant="error">{storesQ.error.message}</Alert>}

      <DataTable
        columns={columns}
        data={storesQ.data ?? []}
        loading={storesQ.isLoading}
        keyExtractor={(s) => s.id}
        emptyTitle="Sin tiendas"
        emptyDescription="Registra una tienda para operar el punto de venta."
        emptyIcon={Store}
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={editing ? "Editar tienda" : "Nueva tienda"}
        footer={
          <>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={onSubmit} loading={save.isPending}>
              {editing ? "Guardar cambios" : "Crear tienda"}
            </Button>
          </>
        }
      >
        <form onSubmit={onSubmit} className="space-y-4" noValidate>
          <Input
            label="Nombre"
            placeholder="Nombre de la tienda"
            error={form.formState.errors.name?.message}
            {...form.register("name")}
          />
          <Input
            label="Dirección"
            placeholder="Dirección"
            error={form.formState.errors.address?.message}
            {...form.register("address")}
          />
          {save.isError && <Alert variant="error">{getErrorMessage(save.error)}</Alert>}
        </form>
      </Modal>
    </div>
  )
}
