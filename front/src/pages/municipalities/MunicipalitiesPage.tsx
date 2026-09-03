import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { toast } from "sonner"
import { Plus, Trash2, Pencil, Landmark } from "lucide-react"

import {
  Button,
  Input,
  Modal,
  PageHeader,
  DataTable,
  Alert,
  Select,
  type Column,
} from "@/components/ui"
import {
  listStates,
  listMunicipalities,
  createMunicipality,
  updateMunicipality,
  deleteMunicipality,
} from "@/services/locations.service"
import { getErrorMessage } from "@/lib/api"
import type { Municipality } from "@/types"

const municipalitySchema = z.object({
  name: z.string().min(1, "El nombre es obligatorio"),
  state_id: z.string().min(1, "Selecciona un estado"),
})

type MunicipalityForm = z.infer<typeof municipalitySchema>

export function MunicipalitiesPage() {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Municipality | null>(null)

  const municipalitiesQ = useQuery({
    queryKey: ["municipalities"],
    queryFn: listMunicipalities,
  })
  const statesQ = useQuery({ queryKey: ["states"], queryFn: listStates })

  const states = statesQ.data ?? []
  const stateById = new Map(states.map((s) => [s.id, s.name]))

  const form = useForm<MunicipalityForm>({
    resolver: zodResolver(municipalitySchema),
    defaultValues: { name: "", state_id: "" },
  })

  const openCreate = () => {
    setEditing(null)
    form.reset({ name: "", state_id: "" })
    setOpen(true)
  }

  const openEdit = (m: Municipality) => {
    setEditing(m)
    form.reset({ name: m.name, state_id: m.state_id })
    setOpen(true)
  }

  const save = useMutation({
    mutationFn: (values: MunicipalityForm) =>
      editing
        ? updateMunicipality(editing.id, values)
        : createMunicipality(values),
    onSuccess: () => {
      toast.success(editing ? "Municipio actualizado" : "Municipio creado")
      setOpen(false)
      queryClient.invalidateQueries({ queryKey: ["municipalities"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const remove = useMutation({
    mutationFn: deleteMunicipality,
    onSuccess: () => {
      toast.success("Municipio eliminado")
      queryClient.invalidateQueries({ queryKey: ["municipalities"] })
    },
    onError: (err) => toast.error(getErrorMessage(err)),
  })

  const onSubmit = form.handleSubmit((v) => save.mutate(v))

  const columns: Column<Municipality>[] = [
    {
      key: "name",
      header: "Municipio",
      render: (m) => <span className="font-medium text-slate-800">{m.name}</span>,
    },
    {
      key: "state_id",
      header: "Estado",
      render: (m) => <span>{stateById.get(m.state_id) ?? "—"}</span>,
    },
    {
      key: "actions",
      header: "",
      className: "text-right",
      render: (m) => (
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="icon" onClick={() => openEdit(m)} title="Editar">
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-red-600 hover:bg-red-50"
            onClick={() => {
              if (confirm(`¿Eliminar el municipio "${m.name}"?`)) remove.mutate(m.id)
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
        title="Municipios"
        description="Catálogo de municipios por estado"
      >
        <Button onClick={openCreate}>
          <Plus className="h-4 w-4" /> Nuevo municipio
        </Button>
      </PageHeader>

      {municipalitiesQ.isError && (
        <Alert variant="error">{municipalitiesQ.error.message}</Alert>
      )}

      <DataTable
        columns={columns}
        data={municipalitiesQ.data ?? []}
        loading={municipalitiesQ.isLoading}
        keyExtractor={(m) => m.id}
        emptyTitle="Sin municipios"
        emptyDescription="Agrega municipios para ubicar tus tiendas."
        emptyIcon={Landmark}
      />

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title={editing ? "Editar municipio" : "Nuevo municipio"}
        footer={
          <>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={onSubmit} loading={save.isPending}>
              {editing ? "Guardar cambios" : "Crear municipio"}
            </Button>
          </>
        }
      >
        <form onSubmit={onSubmit} className="space-y-4" noValidate>
          <Input
            label="Nombre"
            placeholder="Ej. Guadalajara"
            error={form.formState.errors.name?.message}
            {...form.register("name")}
          />
          <Select
            label="Estado"
            placeholder="Selecciona"
            options={states.map((s) => ({ value: s.id, label: s.name }))}
            error={form.formState.errors.state_id?.message}
            {...form.register("state_id")}
          />
          {save.isError && <Alert variant="error">{getErrorMessage(save.error)}</Alert>}
        </form>
      </Modal>
    </div>
  )
}