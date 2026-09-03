import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { toast } from "sonner"
import { Plus, Trash2, Pencil, Sparkles } from "lucide-react"

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
  listSpecialties,
  createSpecialty,
  updateSpecialty,
  deleteSpecialty,
} from "@/services/locations.service"
import { getErrorMessage } from "@/lib/api"
import type { Specialty } from "@/types"

const specialtySchema = z.object({
  name: z.string().min(1, "El nombre es obligatorio"),
  description: z.string().optional(),
})

type SpecialtyForm = z.infer<typeof specialtySchema>

export function SpecialtiesPage() {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Specialty | null>(null)

  const specialtiesQ = useQuery({
    queryKey: ["specialties"],
    queryFn: listSpecialties,
  })

  const form = useForm<SpecialtyForm>({
    resolver: zodResolver(specialtySchema),
    defaultValues: { name: "", description: "" },
  })

  const openCreate = () => {
    setEditing(null)
    form.reset({ name: "", description: "" })
    setOpen(true)
  }

  const openEdit = (s: Specialty) => {
    setEditing(s)
    form.reset({ name: s.name, description: s.description ?? "" })
    setOpen(true)
  }

  const save = useMutation({
    mutationFn: (values: SpecialtyForm) =>
      editing ? updateSpecialty(editing.id, values) : createSpecialty(values),
    onSuccess: () => {
      toast.success(editing ? "Especialidad actualizada" : "Especialidad creada")
      setOpen(false)
      queryClient.invalidateQueries({ queryKey: ["specialties"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const remove = useMutation({
    mutationFn: deleteSpecialty,
    onSuccess: () => {
      toast.success("Especialidad eliminada")
      queryClient.invalidateQueries({ queryKey: ["specialties"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const onSubmit = form.handleSubmit((v) => save.mutate(v))

  const columns: Column<Specialty>[] = [
    {
      key: "name",
      header: "Especialidad",
      render: (s) => <span className="font-medium text-slate-800">{s.name}</span>,
    },
    {
      key: "description",
      header: "Descripción",
      hiddenOnMobile: true,
      render: (s) => <span>{s.description || "—"}</span>,
    },
    {
      key: "actions",
      header: "",
      className: "text-right",
      render: (s) => (
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="icon" onClick={() => openEdit(s)} title="Editar">
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-red-600 hover:bg-red-50"
            onClick={() => {
              if (confirm(`¿Eliminar la especialidad "${s.name}"?`)) remove.mutate(s.id)
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
        title="Especialidades"
        description="Catálogo de especialidades del negocio"
      >
        <Button onClick={openCreate}>
          <Plus className="h-4 w-4" /> Nueva especialidad
        </Button>
      </PageHeader>

      {specialtiesQ.isError && <Alert variant="error">{specialtiesQ.error.message}</Alert>}

      <DataTable
        columns={columns}
        data={specialtiesQ.data ?? []}
        loading={specialtiesQ.isLoading}
        keyExtractor={(s) => s.id}
        emptyTitle="Sin especialidades"
        emptyDescription="Agrega especialidades para categorizar tu catálogo."
        emptyIcon={Sparkles}
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={editing ? "Editar especialidad" : "Nueva especialidad"}
        footer={
          <>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={onSubmit} loading={save.isPending}>
              {editing ? "Guardar cambios" : "Crear especialidad"}
            </Button>
          </>
        }
      >
        <form onSubmit={onSubmit} className="space-y-4" noValidate>
          <Input
            label="Nombre"
            placeholder="Ej. Farmacia / Abarrotes"
            error={form.formState.errors.name?.message}
            {...form.register("name")}
          />
          <Input
            label="Descripción (opcional)"
            placeholder="Breve descripción"
            error={form.formState.errors.description?.message}
            {...form.register("description")}
          />
          {save.isError && <Alert variant="error">{getErrorMessage(save.error)}</Alert>}
        </form>
      </Modal>
    </div>
  )
}