import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { toast } from "sonner"
import { Plus, Pencil, Trash2, Users } from "lucide-react"

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
  listCustomers,
  createCustomer,
  updateCustomer,
  deleteCustomer,
} from "@/services/customers.service"
import { useAuthStore } from "@/store/authStore"
import { getErrorMessage } from "@/lib/api"
import type { Customer } from "@/types"

const customerSchema = z.object({
  full_name: z.string().min(1, "El nombre es obligatorio"),
  email: z.string().email("Correo inválido").optional().or(z.literal("")),
  phone: z.string().optional(),
  address: z.string().optional(),
})

type CustomerForm = z.infer<typeof customerSchema>

export function CustomersPage() {
  const queryClient = useQueryClient()
  const canCreate = useAuthStore((s) => s.hasPermission("customer:create"))
  const canDelete = useAuthStore((s) => s.hasPermission("customer:delete"))

  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Customer | null>(null)

  const customersQ = useQuery({
    queryKey: ["customers"],
    queryFn: listCustomers,
  })

  const form = useForm<CustomerForm>({
    resolver: zodResolver(customerSchema),
    defaultValues: { full_name: "", email: "", phone: "", address: "" },
  })

  const openCreate = () => {
    setEditing(null)
    form.reset({ full_name: "", email: "", phone: "", address: "" })
    setOpen(true)
  }

  const openEdit = (c: Customer) => {
    setEditing(c)
    form.reset({
      full_name: c.full_name ?? "",
      email: c.email ?? "",
      phone: c.phone ?? "",
      address: c.address ?? "",
    })
    setOpen(true)
  }

  const save = useMutation({
    mutationFn: (values: CustomerForm) =>
      editing
        ? updateCustomer(editing.id, values)
        : createCustomer(values),
    onSuccess: () => {
      toast.success(editing ? "Cliente actualizado" : "Cliente creado")
      setOpen(false)
      queryClient.invalidateQueries({ queryKey: ["customers"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const remove = useMutation({
    mutationFn: deleteCustomer,
    onSuccess: () => {
      toast.success("Cliente eliminado")
      queryClient.invalidateQueries({ queryKey: ["customers"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const onSubmit = form.handleSubmit((v) => save.mutate(v))

  const columns: Column<Customer>[] = [
    {
      key: "full_name",
      header: "Nombre",
      render: (c) => <span className="font-medium text-slate-800">{c.full_name || "—"}</span>,
    },
    { key: "email", header: "Correo", hiddenOnMobile: true, render: (c) => <span>{c.email || "—"}</span> },
    { key: "phone", header: "Teléfono", hiddenOnMobile: true, render: (c) => <span>{c.phone || "—"}</span> },
    {
      key: "actions",
      header: "",
      className: "text-right",
      render: (c) => (
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="icon" onClick={() => openEdit(c)} title="Editar">
            <Pencil className="h-4 w-4" />
          </Button>
          {canDelete && (
            <Button
              variant="ghost"
              size="icon"
              className="text-red-600 hover:bg-red-50"
              onClick={() => {
                if (confirm(`¿Eliminar a "${c.full_name}"?`)) remove.mutate(c.id)
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
      <PageHeader title="Clientes" description="Gestiona tu base de clientes">
        {canCreate && (
          <Button onClick={openCreate}>
            <Plus className="h-4 w-4" /> Nuevo cliente
          </Button>
        )}
      </PageHeader>

      {customersQ.isError && <Alert variant="error">{customersQ.error.message}</Alert>}

      <DataTable
        columns={columns}
        data={customersQ.data ?? []}
        loading={customersQ.isLoading}
        keyExtractor={(c) => c.id}
        emptyTitle="Sin clientes"
        emptyDescription="Registra clientes para llevar un mejor control."
        emptyIcon={Users}
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={editing ? "Editar cliente" : "Nuevo cliente"}
        footer={
          <>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={onSubmit} loading={save.isPending}>
              {editing ? "Guardar cambios" : "Crear cliente"}
            </Button>
          </>
        }
      >
        <form onSubmit={onSubmit} className="space-y-4" noValidate>
          <Input
            label="Nombre completo"
            placeholder="Nombre del cliente"
            error={form.formState.errors.full_name?.message}
            {...form.register("full_name")}
          />
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Input
              label="Correo"
              type="email"
              placeholder="correo@ejemplo.com"
              error={form.formState.errors.email?.message}
              {...form.register("email")}
            />
            <Input
              label="Teléfono"
              placeholder="+52..."
              error={form.formState.errors.phone?.message}
              {...form.register("phone")}
            />
          </div>
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
