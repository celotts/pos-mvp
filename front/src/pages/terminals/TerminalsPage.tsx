import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { toast } from "sonner"
import { Plus, Trash2, Pencil, Monitor } from "lucide-react"

import {
  Button,
  Input,
  Modal,
  PageHeader,
  DataTable,
  Alert,
  Badge,
  type Column,
} from "@/components/ui"
import {
  listTerminals,
  createTerminal,
  updateTerminal,
  deleteTerminal,
} from "@/services/pos.service"
import { getErrorMessage } from "@/lib/api"
import type { PosTerminal } from "@/types"

const terminalSchema = z.object({
  name: z.string().min(1, "El nombre es obligatorio"),
  location: z.string().optional(),
})

type TerminalForm = z.infer<typeof terminalSchema>

export function TerminalsPage() {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<PosTerminal | null>(null)

  const terminalsQ = useQuery({ queryKey: ["terminals"], queryFn: listTerminals })

  const form = useForm<TerminalForm>({
    resolver: zodResolver(terminalSchema),
    defaultValues: { name: "", location: "" },
  })

  const openCreate = () => {
    setEditing(null)
    form.reset({ name: "", location: "" })
    setOpen(true)
  }

  const openEdit = (t: PosTerminal) => {
    setEditing(t)
    form.reset({ name: t.name ?? "", location: t.location ?? "" })
    setOpen(true)
  }

  const save = useMutation({
    mutationFn: (values: TerminalForm) =>
      editing
        ? updateTerminal(editing.id, values)
        : createTerminal(values),
    onSuccess: () => {
      toast.success(editing ? "Terminal actualizado" : "Terminal creado")
      setOpen(false)
      queryClient.invalidateQueries({ queryKey: ["terminals"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const remove = useMutation({
    mutationFn: deleteTerminal,
    onSuccess: () => {
      toast.success("Terminal eliminado")
      queryClient.invalidateQueries({ queryKey: ["terminals"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const onSubmit = form.handleSubmit((v) => save.mutate(v))

  const columns: Column<PosTerminal>[] = [
    {
      key: "name",
      header: "Terminal",
      render: (t) => (
        <span className="font-medium text-slate-800">{t.name || "Terminal"}</span>
      ),
    },
    {
      key: "location",
      header: "Ubicación",
      hiddenOnMobile: true,
      render: (t) => <span>{t.location || "—"}</span>,
    },
    {
      key: "is_active",
      header: "Estado",
      render: (t) =>
        t.is_active ? (
          <Badge variant="success">Activo</Badge>
        ) : (
          <Badge variant="outline">Inactivo</Badge>
        ),
    },
    {
      key: "actions",
      header: "",
      className: "text-right",
      render: (t) => (
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="icon" onClick={() => openEdit(t)} title="Editar">
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-red-600 hover:bg-red-50"
            onClick={() => {
              if (confirm(`¿Eliminar el terminal "${t.name}"?`)) remove.mutate(t.id)
            }}
            title="Eliminar"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Terminales POS"
        description="Administra las cajas o terminales de punto de venta"
      >
        <Button onClick={openCreate}>
          <Plus className="h-4 w-4" /> Nuevo terminal
        </Button>
      </PageHeader>

      {terminalsQ.isError && (
        <Alert variant="error">{terminalsQ.error.message}</Alert>
      )}

      <DataTable
        columns={columns}
        data={terminalsQ.data ?? []}
        loading={terminalsQ.isLoading}
        keyExtractor={(t) => t.id}
        emptyTitle="Sin terminales"
        emptyDescription="Crea un terminal para poder registrar ventas."
        emptyIcon={Monitor}
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={editing ? "Editar terminal" : "Nuevo terminal"}
        footer={
          <>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={onSubmit} loading={save.isPending}>
              {editing ? "Guardar cambios" : "Crear terminal"}
            </Button>
          </>
        }
      >
        <form onSubmit={onSubmit} className="space-y-4" noValidate>
          <Input
            label="Nombre"
            placeholder="Ej. Caja 1"
            error={form.formState.errors.name?.message}
            {...form.register("name")}
          />
          <Input
            label="Ubicación (opcional)"
            placeholder="Ej. Mostrador"
            error={form.formState.errors.location?.message}
            {...form.register("location")}
          />
          {save.isError && <Alert variant="error">{getErrorMessage(save.error)}</Alert>}
        </form>
      </Modal>
    </div>
  )
}