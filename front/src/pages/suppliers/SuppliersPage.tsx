import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { toast } from "sonner"
import { Plus, Pencil, Trash2, Truck, Building2 } from "lucide-react"

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
  listSuppliers,
  createSupplier,
  updateSupplier,
  deleteSupplier,
} from "@/services/suppliers.service"
import { useAuthStore } from "@/store/authStore"
import { getErrorMessage } from "@/lib/api"
import { cn } from "@/lib/utils"
import type { Supplier } from "@/types"

const supplierSchema = z.object({
  name: z
    .string()
    .trim()
    .min(2, "El nombre debe tener al menos 2 caracteres")
    .max(120, "Máximo 120 caracteres"),
  contact_name: z.string().trim().optional().or(z.literal("")),
  phone: z
    .string()
    .trim()
    .max(20, "Teléfono demasiado largo")
    .refine(
      (v) => !v || /^[+\d][\d\s().-]{6,}$/.test(v),
      "Ingresa un teléfono válido, p. ej. +52 55 1234 5678",
    )
    .optional()
    .or(z.literal("")),
  email: z
    .string()
    .trim()
    .email("Ingresa un correo electrónico válido")
    .optional()
    .or(z.literal("")),
  address: z.string().trim().max(255, "Máximo 255 caracteres").optional().or(z.literal("")),
})

type SupplierForm = z.infer<typeof supplierSchema>

const defaultValues: SupplierForm = {
  name: "",
  contact_name: "",
  phone: "",
  email: "",
  address: "",
}

const inputBase =
  "h-10 w-full rounded-lg border bg-white px-3 text-sm text-slate-800 shadow-sm border-slate-300 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"

export function SuppliersPage() {
  const queryClient = useQueryClient()
  const canCreate = useAuthStore((s) => s.hasPermission("supplier:create"))
  const canDelete = useAuthStore((s) => s.hasPermission("supplier:delete"))

  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Supplier | null>(null)

  const suppliersQ = useQuery({
    queryKey: ["suppliers"],
    queryFn: listSuppliers,
  })

  const form = useForm<SupplierForm>({
    resolver: zodResolver(supplierSchema),
    defaultValues,
    mode: "onTouched",
  })

  const { errors } = form.formState

  const openCreate = () => {
    setEditing(null)
    form.reset(defaultValues)
    setOpen(true)
  }

  const openEdit = (s: Supplier) => {
    setEditing(s)
    form.reset({
      name: s.name ?? "",
      contact_name: s.contact_name ?? "",
      phone: s.phone ?? "",
      email: s.email ?? "",
      address: s.address ?? "",
    })
    setOpen(true)
  }

  const save = useMutation({
    mutationFn: (values: SupplierForm) =>
      editing ? updateSupplier(editing.id, values) : createSupplier(values),
    onSuccess: () => {
      toast.success(editing ? "Proveedor actualizado" : "Proveedor creado")
      setOpen(false)
      queryClient.invalidateQueries({ queryKey: ["suppliers"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const remove = useMutation({
    mutationFn: deleteSupplier,
    onSuccess: () => {
      toast.success("Proveedor eliminado")
      queryClient.invalidateQueries({ queryKey: ["suppliers"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const onSubmit = form.handleSubmit((v) => save.mutate(v))

  const columns: Column<Supplier>[] = [
    {
      key: "name",
      header: "Proveedor",
      render: (s) => (
        <span className="flex items-center gap-2">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-50 text-brand-600">
            <Building2 className="h-4 w-4" />
          </span>
          <span className="font-medium text-slate-800">{s.name}</span>
        </span>
      ),
    },
    {
      key: "contact",
      header: "Contacto",
      hiddenOnMobile: true,
      render: (s) => <span>{s.contact_name || "—"}</span>,
    },
    {
      key: "phone",
      header: "Teléfono",
      hiddenOnMobile: true,
      render: (s) => <span className="tabular-nums">{s.phone || "—"}</span>,
    },
    {
      key: "email",
      header: "Correo",
      hiddenOnMobile: true,
      render: (s) => <span>{s.email || "—"}</span>,
    },
    {
      key: "actions",
      header: "",
      className: "text-right",
      headerClassName: "text-right",
      render: (s) => (
        <div className="flex justify-end gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => openEdit(s)}
            title="Editar"
          >
            <Pencil className="h-4 w-4" />
          </Button>
          {canDelete && (
            <Button
              variant="ghost"
              size="icon"
              className="text-red-600 hover:bg-red-50"
              onClick={() => {
                if (confirm(`¿Eliminar a "${s.name}"?`)) remove.mutate(s.id)
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

  const fieldLabel = (label: string, required = false) => (
    <span className="flex items-center gap-0.5">
      {label}
      {required && <span className="text-red-500">*</span>}
    </span>
  )

  return (
    <div className="space-y-6">
      <PageHeader
        title="Proveedores"
        description="Gestiona los proveedores que abastecen tu negocio"
      >
        {canCreate && (
          <Button onClick={openCreate}>
            <Plus className="h-4 w-4" /> Nuevo proveedor
          </Button>
        )}
      </PageHeader>

      {suppliersQ.isError && (
        <Alert variant="error">{suppliersQ.error.message}</Alert>
      )}

      <DataTable
        columns={columns}
        data={suppliersQ.data ?? []}
        loading={suppliersQ.isLoading}
        keyExtractor={(s) => s.id}
        emptyTitle="Sin proveedores"
        emptyDescription="Registra proveedores para asociar a tus entradas de mercancía."
        emptyIcon={Truck}
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        size="lg"
        title={editing ? "Editar proveedor" : "Nuevo proveedor"}
        description="Los campos marcados con * son obligatorios."
        footer={
          <>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={onSubmit} loading={save.isPending}>
              {editing ? "Guardar cambios" : "Crear proveedor"}
            </Button>
          </>
        }
      >
        <form onSubmit={onSubmit} className="space-y-5" noValidate>
          <div className="space-y-1.5">
            <p className="flex items-center gap-2 text-sm font-semibold text-slate-800">
              <Building2 className="h-4 w-4 text-brand-600" />
              Información del proveedor
            </p>
            <div className="space-y-4">
              <Input
                label="Nombre *"
                placeholder="Nombre o razón social"
                autoComplete="organization"
                error={errors.name?.message}
                {...form.register("name")}
              />
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <Input
                  label="Contacto"
                  placeholder="Nombre del contacto"
                  autoComplete="name"
                  error={errors.contact_name?.message}
                  {...form.register("contact_name")}
                />
                <Input
                  label="Teléfono"
                  placeholder="+52 55 1234 5678"
                  type="tel"
                  inputMode="tel"
                  autoComplete="tel"
                  error={errors.phone?.message}
                  {...form.register("phone")}
                />
              </div>
              <Input
                label="Correo electrónico"
                placeholder="contacto@proveedor.com"
                type="email"
                inputMode="email"
                autoComplete="email"
                error={errors.email?.message}
                {...form.register("email")}
              />
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-slate-700">
                  Dirección
                </label>
                <textarea
                  className={cn(inputBase, "h-auto min-h-[80px] py-2 resize-none", errors.address?.message && "border-red-500 focus:ring-red-500 focus:border-red-500")}
                  placeholder="Calle, número, colonia, ciudad"
                  autoComplete="street-address"
                  rows={3}
                  {...form.register("address")}
                />
                {errors.address && (
                  <p className="text-xs text-red-600">{errors.address.message}</p>
                )}
              </div>
            </div>
          </div>

          {save.isError && (
            <Alert variant="error">{getErrorMessage(save.error)}</Alert>
          )}
        </form>
      </Modal>
    </div>
  )
}
