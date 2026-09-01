import { useMemo, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { Plus, ShieldCheck } from "lucide-react"

import {
  Button,
  Modal,
  PageHeader,
  DataTable,
  Alert,
  Badge,
  Input,
  type Column,
} from "@/components/ui"
import {
  listRoles,
  createRole,
  assignRolePermissions,
} from "@/services/roles.service"
import { listPermissions } from "@/services/product.service"
import { useAuthStore } from "@/store/authStore"
import { getErrorMessage } from "@/lib/api"
import type { RoleWithPermissions } from "@/types"

export function RolesPage() {
  const queryClient = useQueryClient()
  const canCreate = useAuthStore((s) => s.hasPermission("role:create"))

  const [createOpen, setCreateOpen] = useState(false)
  const [newName, setNewName] = useState("")
  const [newDesc, setNewDesc] = useState("")

  const [editing, setEditing] = useState<RoleWithPermissions | null>(null)
  const [selectedCodes, setSelectedCodes] = useState<Set<string>>(new Set())

  const rolesQ = useQuery({ queryKey: ["roles"], queryFn: listRoles })
  const permsQ = useQuery({
    queryKey: ["permissions"],
    queryFn: listPermissions,
  })
  const permissions = permsQ.data ?? []

  const grouped = useMemo(() => {
    const map = new Map<string, typeof permissions>()
    for (const p of permissions) {
      if (!map.has(p.module)) map.set(p.module, [])
      map.get(p.module)!.push(p)
    }
    return Array.from(map.entries())
  }, [permissions])

  const create = useMutation({
    mutationFn: async () => {
      if (!newName.trim()) throw new Error("El nombre es obligatorio")
      return createRole({ name: newName.trim(), description: newDesc || null })
    },
    onSuccess: () => {
      toast.success("Rol creado")
      setCreateOpen(false)
      setNewName("")
      setNewDesc("")
      queryClient.invalidateQueries({ queryKey: ["roles"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const openPermissions = (r: RoleWithPermissions) => {
    setEditing(r)
    setSelectedCodes(new Set(r.permissions ?? []))
  }

  const savePermissions = useMutation({
    mutationFn: () => assignRolePermissions(editing!.id, Array.from(selectedCodes)),
    onSuccess: (updated) => {
      toast.success("Permisos actualizados")
      setEditing(null)
      queryClient.setQueryData(["roles"], (old: RoleWithPermissions[] | undefined) =>
        old?.map((r) => (r.id === updated.id ? updated : r)),
      )
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const toggle = (code: string) => {
    setSelectedCodes((prev) => {
      const next = new Set(prev)
      if (next.has(code)) next.delete(code)
      else next.add(code)
      return next
    })
  }

  const columns: Column<RoleWithPermissions>[] = [
    {
      key: "name",
      header: "Rol",
      render: (r) => (
        <div>
          <p className="font-medium text-slate-800">{r.name}</p>
          {r.description && (
            <p className="text-xs text-slate-400">{r.description}</p>
          )}
        </div>
      ),
    },
    {
      key: "perms",
      header: "Permisos",
      hiddenOnMobile: true,
      render: (r) => (
        <Badge variant="info">{r.permissions?.length ?? 0} permisos</Badge>
      ),
    },
    {
      key: "actions",
      header: "",
      className: "text-right",
      render: (r) => (
        <Button
          variant="outline"
          size="sm"
          onClick={() => openPermissions(r)}
        >
          <ShieldCheck className="h-4 w-4" /> Gestionar permisos
        </Button>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Roles y Permisos"
        description="Administra los roles y sus permisos (RBAC)"
      >
        {canCreate && (
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="h-4 w-4" /> Nuevo rol
          </Button>
        )}
      </PageHeader>

      {rolesQ.isError && <Alert variant="error">{rolesQ.error.message}</Alert>}

      <DataTable
        columns={columns}
        data={rolesQ.data ?? []}
        loading={rolesQ.isLoading}
        keyExtractor={(r) => r.id}
        emptyTitle="Sin roles"
        emptyDescription="Crea roles y asigna permisos."
        emptyIcon={ShieldCheck}
      />

      {/* Crear rol */}
      <Modal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        title="Nuevo rol"
        footer={
          <>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={() => create.mutate()} loading={create.isPending}>
              Crear rol
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label="Nombre del rol"
            placeholder="Ej. Cajero"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
          />
          <Input
            label="Descripción"
            placeholder="Descripción opcional"
            value={newDesc}
            onChange={(e) => setNewDesc(e.target.value)}
          />
          {create.isError && (
            <Alert variant="error">{getErrorMessage(create.error)}</Alert>
          )}
        </div>
      </Modal>

      {/* Gestionar permisos */}
      <Modal
        open={!!editing}
        onClose={() => setEditing(null)}
        title={`Permisos — ${editing?.name ?? ""}`}
        description="Selecciona los permisos que tendrá este rol (reemplaza la asignación actual)"
        size="xl"
        footer={
          <>
            <Button variant="outline" onClick={() => setEditing(null)}>
              Cancelar
            </Button>
            <Button
              onClick={() => savePermissions.mutate()}
              loading={savePermissions.isPending}
            >
              Guardar permisos ({selectedCodes.size})
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          {savePermissions.isError && (
            <Alert variant="error">
              {getErrorMessage(savePermissions.error)}
            </Alert>
          )}
          {grouped.map(([module, perms]) => (
            <div key={module}>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                {module.replace(":", " · ")}
              </p>
              <div className="flex flex-wrap gap-2">
                {perms.map((p) => (
                  <label
                    key={p.id}
                    className="flex cursor-pointer items-center gap-2 rounded-lg border border-slate-200 px-3 py-1.5 text-sm transition-colors hover:bg-slate-50"
                  >
                    <input
                      type="checkbox"
                      checked={selectedCodes.has(p.code)}
                      onChange={() => toggle(p.code)}
                      className="accent-brand-600"
                    />
                    {p.code}
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
      </Modal>
    </div>
  )
}
