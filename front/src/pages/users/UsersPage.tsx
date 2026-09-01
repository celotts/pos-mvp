import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { toast } from "sonner"
import { Plus, Trash2, Users } from "lucide-react"

import {
  Button,
  Input,
  Modal,
  PageHeader,
  DataTable,
  Alert,
  type Column,
} from "@/components/ui"
import { listUsers, createUser, deleteUser } from "@/services/users.service"
import { listRoles } from "@/services/roles.service"
import { useAuthStore } from "@/store/authStore"
import { getErrorMessage } from "@/lib/api"
import type { User } from "@/types"

const userSchema = z.object({
  email: z.string().email("Correo inválido"),
  full_name: z.string().min(1, "El nombre es obligatorio"),
  password: z.string().min(8, "Mínimo 8 caracteres"),
  role_id: z.string().min(1, "Selecciona un rol"),
})

type UserForm = z.infer<typeof userSchema>

export function UsersPage() {
  const queryClient = useQueryClient()
  const canCreate = useAuthStore((s) => s.hasPermission("user:create"))
  const canDelete = useAuthStore((s) => s.hasPermission("user:delete"))

  const [open, setOpen] = useState(false)

  const usersQ = useQuery({ queryKey: ["users"], queryFn: listUsers })
  const rolesQ = useQuery({ queryKey: ["roles"], queryFn: listRoles })
  const roles = rolesQ.data ?? []

  const form = useForm<UserForm>({
    resolver: zodResolver(userSchema),
    defaultValues: { email: "", full_name: "", password: "", role_id: "" },
  })

  const create = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      toast.success("Usuario creado")
      setOpen(false)
      form.reset()
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const remove = useMutation({
    mutationFn: deleteUser,
    onSuccess: () => {
      toast.success("Usuario eliminado")
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const onSubmit = form.handleSubmit((v) => create.mutate(v))

  const columns: Column<User>[] = [
    {
      key: "name",
      header: "Usuario",
      render: (u) => (
        <div>
          <p className="font-medium text-slate-800">{u.full_name}</p>
          <p className="text-xs text-slate-400">{u.email}</p>
        </div>
      ),
    },
    {
      key: "emailLabel",
      header: "Correo",
      hiddenOnMobile: true,
      render: (u) => <span>{u.email}</span>,
    },
    {
      key: "actions",
      header: "",
      className: "text-right",
      render: (u) =>
        canDelete ? (
          <div className="flex justify-end">
            <Button
              variant="ghost"
              size="icon"
              className="text-red-600 hover:bg-red-50"
              onClick={() => {
                if (confirm(`¿Eliminar a "${u.full_name}"?`)) remove.mutate(u.id)
              }}
              title="Eliminar"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ) : null,
    },
  ]

  return (
    <div className="space-y-6">
      <PageHeader title="Usuarios" description="Gestiona los usuarios del sistema">
        {canCreate && (
          <Button onClick={() => setOpen(true)}>
            <Plus className="h-4 w-4" /> Nuevo usuario
          </Button>
        )}
      </PageHeader>

      {usersQ.isError && <Alert variant="error">{usersQ.error.message}</Alert>}

      <DataTable
        columns={columns}
        data={usersQ.data ?? []}
        loading={usersQ.isLoading}
        keyExtractor={(u) => u.id}
        emptyTitle="Sin usuarios"
        emptyDescription="Crea usuarios y asigna roles."
        emptyIcon={Users}
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="Nuevo usuario"
        footer={
          <>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={onSubmit} loading={create.isPending}>
              Crear usuario
            </Button>
          </>
        }
      >
        <form onSubmit={onSubmit} className="space-y-4" noValidate>
          <Input
            label="Nombre completo"
            placeholder="Nombre"
            error={form.formState.errors.full_name?.message}
            {...form.register("full_name")}
          />
          <Input
            label="Correo"
            type="email"
            placeholder="usuario@correo.com"
            error={form.formState.errors.email?.message}
            {...form.register("email")}
          />
          <Input
            label="Contraseña"
            type="password"
            placeholder="Mínimo 8 caracteres"
            error={form.formState.errors.password?.message}
            {...form.register("password")}
          />
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-slate-700">Rol</label>
            <select
              className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              {...form.register("role_id")}
            >
              <option value="">Selecciona un rol</option>
              {roles.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </select>
            {form.formState.errors.role_id?.message && (
              <p className="text-xs text-red-600">
                {form.formState.errors.role_id.message}
              </p>
            )}
          </div>
          {create.isError && (
            <Alert variant="error">{getErrorMessage(create.error)}</Alert>
          )}
        </form>
      </Modal>
    </div>
  )
}
